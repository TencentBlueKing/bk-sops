# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging

from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from pipeline.contrib.periodic_task.models import PeriodicTaskHistory
from pipeline.contrib.statistics.models import ComponentExecuteData
from pipeline.models import PipelineInstance

from gcloud.analysis_statistics.models import TaskflowExecutedNodeStatistics, TaskflowStatistics
from gcloud.contrib.cleaner.models import ArchivedTaskInstance
from gcloud.contrib.cleaner.pipeline.bamboo_engine_tasks import get_clean_pipeline_instance_data
from gcloud.contrib.cleaner.signals import pre_delete_pipeline_instance_data
from gcloud.core.models import ProjectConfig
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.utils.decorators import time_record

logger = logging.getLogger("root")


def filter_clean_task_instances():
    """
    过滤需要清理的任务实例
    """
    validity_day = settings.V2_TASK_VALIDITY_DAY
    expire_time = timezone.now() - timezone.timedelta(days=validity_day)

    batch_num = settings.CLEAN_EXPIRED_V2_TASK_BATCH_NUM

    # 获取所有项目的任务清理配置
    project_clean_configs = {}
    for config in ProjectConfig.objects.filter(task_clean_configs__isnull=False).values(
        "project_id", "task_clean_configs"
    ):
        if config["task_clean_configs"] and isinstance(config["task_clean_configs"], dict):
            project_clean_configs[config["project_id"]] = config["task_clean_configs"]

    if project_clean_configs:
        logger.info(
            f"[clean_expired_v2_task_data] Found {len(project_clean_configs)}"
            f"projects with custom clean configs: {list(project_clean_configs.keys())}"
        )

    # 构建基础查询条件
    base_filter = {
        "pipeline_instance__create_time__lt": expire_time,
        "engine_ver": 2,
        "pipeline_instance__is_expired": False,
    }

    # 如果配置了全局项目范围，先获取需要清理的项目列表
    target_projects = settings.CLEAN_EXPIRED_V2_TASK_PROJECTS if settings.CLEAN_EXPIRED_V2_TASK_PROJECTS else None

    # 收集所有符合条件的任务ID
    all_ids = []

    # 处理有特殊配置的项目
    for project_id, clean_config in project_clean_configs.items():
        # 如果设置了全局项目范围，且当前项目不在范围内，跳过
        if target_projects and project_id not in target_projects:
            continue

        # 获取项目特定的 create_methods 配置
        project_create_methods = clean_config.get("create_methods", [])
        if not project_create_methods:
            continue

        project_filter = base_filter.copy()
        project_filter["project_id"] = project_id
        project_filter["create_method__in"] = project_create_methods

        project_qs = TaskFlowInstance.objects.filter(**project_filter)
        project_ids = list(project_qs.order_by("id").values("id", "pipeline_instance__instance_id")[:batch_num])
        if project_ids:
            logger.info(
                f"[clean_expired_v2_task_data] Project {project_id} with custom config "
                f"(create_methods={project_create_methods}), "
                f"found {len(project_ids)} tasks to clean"
            )
        all_ids.extend(project_ids)

        # 如果已经收集到足够的任务，退出循环
        if len(all_ids) >= batch_num:
            break

    # 处理没有特殊配置的项目（使用全局配置）
    if len(all_ids) < batch_num:
        remaining_num = batch_num - len(all_ids)

        # 构建已有特殊配置的项目ID列表
        configured_project_ids = list(project_clean_configs.keys())

        default_filter = base_filter.copy()
        default_filter["create_method__in"] = settings.CLEAN_EXPIRED_V2_TASK_CREATE_METHODS

        # 排除已有特殊配置的项目
        if configured_project_ids:
            default_qs = TaskFlowInstance.objects.filter(**default_filter).exclude(
                project_id__in=configured_project_ids
            )
        else:
            default_qs = TaskFlowInstance.objects.filter(**default_filter)

        # 如果设置了全局项目范围，进一步过滤
        if target_projects:
            default_qs = default_qs.filter(project_id__in=target_projects)

        default_ids = list(default_qs.order_by("id").values("id", "pipeline_instance__instance_id")[:remaining_num])
        if default_ids:
            logger.info(
                f"[clean_expired_v2_task_data] Projects with default config "
                f"(create_methods={settings.CLEAN_EXPIRED_V2_TASK_CREATE_METHODS}), "
                f"found {len(default_ids)} tasks to clean"
            )
        all_ids.extend(default_ids)

    # 限制最终结果数量
    ids = all_ids[:batch_num]
    return ids


@periodic_task(run_every=(crontab(*settings.CLEAN_EXPIRED_V2_TASK_CRON)), ignore_result=True, queue="task_data_clean")
@time_record(logger)
def clean_expired_v2_task_data():
    """
    清除过期的任务数据
    """
    if not settings.ENABLE_CLEAN_EXPIRED_V2_TASK:
        logger.info("Skip clean expired task data")
        return

    logger.info("Start clean expired task data...")
    try:
        ids = filter_clean_task_instances()
        task_ids = [item["id"] for item in ids]
        logger.info(f"[clean_expired_v2_task_data] Total {len(task_ids)} tasks to clean, task_ids: {task_ids}")
        pipeline_instance_ids = [item["pipeline_instance__instance_id"] for item in ids]
        data_to_clean = get_clean_pipeline_instance_data(pipeline_instance_ids)
        tasks = TaskFlowInstance.objects.filter(id__in=task_ids)
        data_to_clean.update({"tasks": tasks})

        pre_delete_pipeline_instance_data.send(sender=TaskFlowInstance, data=data_to_clean)

        instance_fields = ["tasks", "pipeline_instances"]
        with transaction.atomic():
            for field, qs in data_to_clean.items():
                if field.endswith("_list") and isinstance(qs, list):
                    logger.info(
                        f"[clean_expired_v2_task_data] clean field: {field}, {len(qs)} batch data, "
                        f"e.x.: {qs[0].values_list('pk', flat=True)[:10] if len(qs) > 0 else None}..."
                    )
                    [q.delete() for q in qs]
                elif field not in instance_fields or settings.CLEAN_EXPIRED_V2_TASK_INSTANCE:
                    logger.info(
                        f"[clean_expired_v2_task_data] clean field: {field}, "
                        f"qs ids: {qs.values_list('pk', flat=True)[:10]}..."
                    )
                    qs.delete()
                elif field == "pipeline_instances":
                    qs.update(is_expired=True)
        logger.info(f"[clean_expired_v2_task_data] success clean tasks: {task_ids}")
    except Exception as e:
        logger.exception(f"[clean_expired_v2_task_data] error: {e}")


@periodic_task(run_every=(crontab(*settings.ARCHIVE_EXPIRED_V2_TASK_CRON)), ignore_result=True, queue="task_data_clean")
@time_record(logger)
def archive_expired_v2_task_data():
    """
    归档过期任务数据
    """
    if not settings.ENABLE_ARCHIVE_EXPIRED_V2_TASK:
        logger.info("Skip archive expired v2 task data")
        return

    logger.info("Start archive expired task data...")
    try:
        validity_day = settings.V2_TASK_VALIDITY_DAY
        expire_time = timezone.now() - timezone.timedelta(days=validity_day)

        batch_num = settings.ARCHIVE_EXPIRED_V2_TASK_BATCH_NUM

        tasks = (
            TaskFlowInstance.objects.select_related("pipeline_instance")
            .filter(pipeline_instance__create_time__lt=expire_time, engine_ver=2, pipeline_instance__is_expired=1)
            .order_by("id")[:batch_num]
        )
        if not tasks:
            logger.info("No expired task data to archive")
            return
        archived_task_objs = [
            ArchivedTaskInstance(
                task_id=task.id,
                project_id=task.project_id,
                name=task.pipeline_instance.name,
                template_id=task.pipeline_instance.template_id,
                task_template_id=task.template_id,
                template_source=task.template_source,
                create_method=task.create_method,
                create_info=task.create_info,
                creator=task.pipeline_instance.creator,
                create_time=task.pipeline_instance.create_time,
                executor=task.pipeline_instance.executor,
                recorded_executor_proxy=task.recorded_executor_proxy,
                start_time=task.pipeline_instance.start_time,
                finish_time=task.pipeline_instance.finish_time,
                is_started=task.pipeline_instance.is_started,
                is_finished=task.pipeline_instance.is_finished,
                is_revoked=task.pipeline_instance.is_revoked,
                engine_ver=task.engine_ver,
                is_child_taskflow=task.is_child_taskflow,
                snapshot_id=task.pipeline_instance.snapshot_id,
                current_flow=task.current_flow,
                is_deleted=task.is_deleted,
                extra_info=task.extra_info,
            )
            for task in tasks
        ]
        task_ids = [item.id for item in tasks]
        pipeline_ids = [item.pipeline_instance_id for item in tasks]
        pipeline_instance_ids = [item.pipeline_instance.instance_id for item in tasks]
        with transaction.atomic():
            # PeriodicTaskHistory 对 PipelineInstance 有 do nothing 外键，需要保证引用关系被清除，避免外键约束导致清理失败
            # 过期任务的 periodic_task_history 必定可清理
            periodic_task_history_qs = PeriodicTaskHistory.objects.filter(
                pipeline_instance_id__in=pipeline_instance_ids
            )
            if periodic_task_history_qs:
                logger.info(
                    f"[archive_expired_v2_task_data] delete periodic task nums: {len(periodic_task_history_qs)}, "
                    f"e.x.: {periodic_task_history_qs.values_list('pk', flat=True)[:3]}..."
                )
                periodic_task_history_qs.delete()
            archived_task_instances = ArchivedTaskInstance.objects.bulk_create(archived_task_objs)
            logger.info(f"[archive_expired_v2_task_data] archived nums: {len(archived_task_instances)}")
            TaskFlowInstance.objects.filter(id__in=task_ids).delete()
            logger.info(f"[archive_expired_v2_task_data] delete task nums: {len(task_ids)}, e.x.: {task_ids[:3]}...")
            PipelineInstance.objects.filter(id__in=pipeline_ids).delete()
            logger.info(
                f"[archive_expired_v2_task_data] delete pipeline nums: {len(pipeline_ids)}, "
                f"e.x.: {pipeline_ids[:3]}..."
            )
        logger.info(f"[archive_expired_v2_task_data] success archive tasks: {task_ids[:3]}...")
    except Exception as e:
        logger.exception(f"[archive_expired_v2_task_data] error: {e}")


@periodic_task(
    run_every=(crontab(*settings.CLEAN_EXPIRED_STATISTICS_CRON)), ignore_result=True, queue="task_data_clean"
)
@time_record(logger)
def clear_statistics_info():
    """
    清除过期的统计信息
    """
    if not settings.ENABLE_CLEAN_EXPIRED_STATISTICS:
        logger.info("Skip clean expired statistics data")
        return

    logger.info("Start clean expired statistics data...")
    try:
        validity_day = settings.STATISTICS_VALIDITY_DAY
        expire_time = timezone.now() - timezone.timedelta(days=validity_day)
        batch_num = settings.CLEAN_EXPIRED_STATISTICS_BATCH_NUM

        data_to_clean = [
            {"model": TaskflowStatistics, "time_field": "create_time", "order_field": "create_time"},
            {
                "model": TaskflowExecutedNodeStatistics,
                "time_field": "instance_create_time",
                "order_field": "instance_create_time",
            },
            {"model": ComponentExecuteData, "time_field": "archived_time", "order_field": "id"},
        ]
        for data in data_to_clean:
            model = data["model"]
            time_field = data["time_field"]
            order_field = data["order_field"]
            qs = model.objects.filter(**{f"{time_field}__lt": expire_time}).order_by(order_field)[:batch_num]
            ids_to_delete = list(qs.values_list("id", flat=True))
            if ids_to_delete:
                model.objects.filter(id__in=ids_to_delete).delete()
                logger.info(
                    f"[clear_statistics_info] clean model {model.__name__} deleted nums: {len(ids_to_delete)}, "
                    f"e.x.: {ids_to_delete[:3]}..."
                )
        logger.info("[clear_statistics_info] success clean statistics")
    except Exception as e:
        logger.exception(f"Failed to clear expired statistics data: {e}")
