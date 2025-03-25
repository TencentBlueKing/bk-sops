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
from enum import Enum

from blueapps.contrib.celery_tools.periodic import periodic_task
from celery.schedules import crontab
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
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.utils.decorators import time_record

logger = logging.getLogger("root")


class CleanExpiredV2TaskConfig(Enum):
    CONFIG_KEY = "CLEAN_EXPIRED_V2_TASK_DATA_CONFIG"
    ENABLE_CLEAN_EXPIRED_V2_TASK = "ENABLE_CLEAN_EXPIRED_V2_TASK"
    V2_TASK_VALIDITY_DAY = "V2_TASK_VALIDITY_DAY"
    CLEAN_EXPIRED_V2_TASK_BATCH_NUM = "CLEAN_EXPIRED_V2_TASK_BATCH_NUM"
    CLEAN_EXPIRED_V2_TASK_CREATE_METHODS = "CLEAN_EXPIRED_V2_TASK_CREATE_METHODS"
    CLEAN_EXPIRED_V2_TASK_PROJECTS = "CLEAN_EXPIRED_V2_TASK_PROJECTS"
    CLEAN_EXPIRED_V2_TASK_INSTANCE = "CLEAN_EXPIRED_V2_TASK_INSTANCE"


class ArchiveExpiredV2TaskConfig(Enum):
    CONFIG_KEY = "ARCHIVE_EXPIRED_V2_TASK_DATA_CONFIG"
    ENABLE_ARCHIVE_EXPIRED_V2_TASK = "ENABLE_ARCHIVE_EXPIRED_V2_TASK"
    V2_TASK_VALIDITY_DAY = "V2_TASK_VALIDITY_DAY"
    ARCHIVE_EXPIRED_V2_TASK_BATCH_NUM = "ARCHIVE_EXPIRED_V2_TASK_BATCH_NUM"


class ClearStatisticsInfoConfig(Enum):
    CONFIG_KEY = "CLEAR_STATISTICS_INFO_CONFIG"
    ENABLE_CLEAN_EXPIRED_STATISTICS = "ENABLE_CLEAN_EXPIRED_STATISTICS"
    STATISTICS_VALIDITY_DAY = "STATISTICS_VALIDITY_DAY"
    CLEAN_EXPIRED_STATISTICS_BATCH_NUM = "CLEAN_EXPIRED_STATISTICS_BATCH_NUM"


def get_tenant_configs(config_key: str):
    """
    获取所有租户的配置信息
    这里需要你根据实际情况实现获取租户配置的逻辑
    clean_expired_v2_task_data 示例配置结构
    [
        {
            "tenant_id": 1,
            "settings": {
                "ENABLE_CLEAN_EXPIRED_V2_TASK": True,
                "V2_TASK_VALIDITY_DAY": 7,
                "CLEAN_EXPIRED_V2_TASK_BATCH_NUM": 100,
                "CLEAN_EXPIRED_V2_TASK_CREATE_METHODS": ["method1", "method2"],
                "CLEAN_EXPIRED_V2_TASK_PROJECTS": [1, 2, 3],
                "CLEAN_EXPIRED_V2_TASK_INSTANCE": True
            }
        },
        ...
    ]
    archive_expired_v2_task_data 示例配置结构
    [
        {
            "tenant_id": 1,
            "settings": {
                "ENABLE_ARCHIVE_EXPIRED_V2_TASK": True,
                "V2_TASK_VALIDITY_DAY": 7,
                "ARCHIVE_EXPIRED_V2_TASK_BATCH_NUM": 100
            }
        },
        ...
    ]
    clear_statistics_info 示例配置结构
    [
        {
            "tenant_id": 1,
            "settings": {
                "ENABLE_CLEAN_EXPIRED_STATISTICS": True,
                "STATISTICS_VALIDITY_DAY": 7,
                "CLEAN_EXPIRED_STATISTICS_BATCH_NUM": 100
            }
        },
        ...
    ]
    """
    return getattr(settings, config_key, [])


@periodic_task(run_every=(crontab(*settings.CLEAN_EXPIRED_V2_TASK_CRON)), ignore_result=True, queue="task_data_clean")
@time_record(logger)
def clean_expired_v2_task_data():
    """
    清除过期的任务数据
    """
    tenant_configs = get_tenant_configs(CleanExpiredV2TaskConfig.CONFIG_KEY.value)
    if not tenant_configs:
        logger.info("Skip clean expired task data")
        return

    for tenant_config in tenant_configs:
        tenant_id = tenant_config.get("tenant_id")
        tenant_settings = tenant_config.get("settings", {})

        if not tenant_settings.get(CleanExpiredV2TaskConfig.ENABLE_CLEAN_EXPIRED_V2_TASK.value, False):
            logger.info(f"Skip clean expired task data for tenant {tenant_id}")
            continue

        logger.info(f"Start clean expired task data for tenant {tenant_id}...")
        try:
            validity_day = tenant_settings.get(CleanExpiredV2TaskConfig.V2_TASK_VALIDITY_DAY.value)
            expire_time = timezone.now() - timezone.timedelta(days=validity_day)

            batch_num = tenant_settings.get(CleanExpiredV2TaskConfig.CLEAN_EXPIRED_V2_TASK_BATCH_NUM.value)

            qs = TaskFlowInstance.objects.filter(
                pipeline_instance__create_time__lt=expire_time,
                engine_ver=2,
                pipeline_instance__is_expired=False,
                create_method__in=tenant_settings.get(
                    CleanExpiredV2TaskConfig.CLEAN_EXPIRED_V2_TASK_CREATE_METHODS.value, []
                ),
            )
            if tenant_settings.get(CleanExpiredV2TaskConfig.CLEAN_EXPIRED_V2_TASK_PROJECTS.value):
                qs = qs.filter(
                    project_id__in=tenant_settings.get(CleanExpiredV2TaskConfig.CLEAN_EXPIRED_V2_TASK_PROJECTS.value)
                )
            ids = qs.order_by("id").values("id", "pipeline_instance__instance_id")[:batch_num]
            task_ids = [item["id"] for item in ids]
            logger.info(
                f"[clean_expired_v2_task_data][tenant {tenant_id}] Clean expired task data, task_ids: {task_ids}"
            )
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
                            f"[clean_expired_v2_task_data][tenant {tenant_id}] "
                            f"clean field: {field}, {len(qs)} batch data, "
                            f"e.x.: {qs[0].values_list('pk', flat=True)[:10] if len(qs) > 0 else None}..."
                        )
                        [q.delete() for q in qs]
                    elif field not in instance_fields or tenant_settings.get(
                        CleanExpiredV2TaskConfig.CLEAN_EXPIRED_V2_TASK_INSTANCE.value
                    ):
                        logger.info(
                            f"[clean_expired_v2_task_data][tenant {tenant_id}] clean field: {field}, "
                            f"qs ids: {qs.values_list('pk', flat=True)[:10]}..."
                        )
                        qs.delete()
                    elif field == "pipeline_instances":
                        qs.update(is_expired=True)
            logger.info(f"[clean_expired_v2_task_data][tenant {tenant_id}] success clean tasks: {task_ids}")
        except Exception as e:
            logger.exception(f"[clean_expired_v2_task_data][tenant {tenant_id}] error: {e}")


@periodic_task(run_every=(crontab(*settings.ARCHIVE_EXPIRED_V2_TASK_CRON)), ignore_result=True, queue="task_data_clean")
@time_record(logger)
def archive_expired_v2_task_data():
    """
    归档过期任务数据
    """
    tenant_configs = get_tenant_configs(ArchiveExpiredV2TaskConfig.CONFIG_KEY.value)
    if not tenant_configs:
        logger.info("Skip archive expired v2 task data")
        return

    for tenant_config in tenant_configs:
        tenant_id = tenant_config.get("tenant_id")
        tenant_settings = tenant_config.get("settings", {})

        if not tenant_settings.get(ArchiveExpiredV2TaskConfig.ENABLE_ARCHIVE_EXPIRED_V2_TASK.value, False):
            logger.info(f"Skip archive expired v2 task data for tenant {tenant_id}")
            continue

        logger.info(f"Start archive expired task data for tenant {tenant_id}...")
        try:
            validity_day = tenant_settings.get(ArchiveExpiredV2TaskConfig.V2_TASK_VALIDITY_DAY.value)
            expire_time = timezone.now() - timezone.timedelta(days=validity_day)

            batch_num = tenant_settings.get(ArchiveExpiredV2TaskConfig.ARCHIVE_EXPIRED_V2_TASK_BATCH_NUM.value)

            tasks = (
                TaskFlowInstance.objects.select_related("pipeline_instance")
                .filter(pipeline_instance__create_time__lt=expire_time, engine_ver=2, pipeline_instance__is_expired=1)
                .order_by("id")[:batch_num]
            )
            if not tasks:
                logger.info(f"No expired task data to archive for tenant {tenant_id}")
                continue
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
                        f"[archive_expired_v2_task_data][tenant {tenant_id}] "
                        f"delete periodic task nums: {len(periodic_task_history_qs)}, "
                        f"e.x.: {periodic_task_history_qs.values_list('pk', flat=True)[:3]}..."
                    )
                    periodic_task_history_qs.delete()
                archived_task_instances = ArchivedTaskInstance.objects.bulk_create(archived_task_objs)
                logger.info(
                    f"[archive_expired_v2_task_data][tenant {tenant_id}] archived nums: {len(archived_task_instances)}"
                )
                TaskFlowInstance.objects.filter(id__in=task_ids).delete()
                logger.info(
                    f"[archive_expired_v2_task_data][tenant {tenant_id}] "
                    f"delete task nums: {len(task_ids)}, e.x.: {task_ids[:3]}..."
                )
                PipelineInstance.objects.filter(id__in=pipeline_ids).delete()
                logger.info(
                    f"[archive_expired_v2_task_data][tenant {tenant_id}] delete pipeline nums: {len(pipeline_ids)}, "
                    f"e.x.: {pipeline_ids[:3]}..."
                )
            logger.info(f"[archive_expired_v2_task_data][tenant {tenant_id}] success archive tasks: {task_ids[:3]}...")
        except Exception as e:
            logger.exception(f"[archive_expired_v2_task_data][tenant {tenant_id}] error: {e}")


@periodic_task(
    run_every=(crontab(*settings.CLEAN_EXPIRED_STATISTICS_CRON)), ignore_result=True, queue="task_data_clean"
)
@time_record(logger)
def clear_statistics_info():
    """
    清除过期的统计信息
    """
    tenant_configs = get_tenant_configs(ClearStatisticsInfoConfig.CONFIG_KEY.value)
    if not tenant_configs:
        logger.info("Skip clean expired statistics data")
        return

    for tenant_config in tenant_configs:
        tenant_id = tenant_config.get("tenant_id")
        tenant_settings = tenant_config.get("settings", {})

        enable_clean = tenant_settings.get(ClearStatisticsInfoConfig.ENABLE_CLEAN_EXPIRED_STATISTICS.value, False)
        if not enable_clean:
            logger.info(f"Skip clean expired statistics data for tenant {tenant_id}")
            continue

        logger.info(f"Start clean expired statistics data for tenant {tenant_id}...")
        try:
            validity_day = tenant_settings.get(ClearStatisticsInfoConfig.STATISTICS_VALIDITY_DAY.value, 0)
            expire_time = timezone.now() - timezone.timedelta(days=validity_day)
            batch_num = tenant_settings.get(ClearStatisticsInfoConfig.CLEAN_EXPIRED_STATISTICS_BATCH_NUM.value, 0)

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
                        f"[clear_statistics_info][tenant {tenant_id}] clean model {model.__name__} "
                        f"deleted nums: {len(ids_to_delete)}, "
                        f"e.x.: {ids_to_delete[:3]}..."
                    )
            logger.info(f"[clear_statistics_info][tenant {tenant_id}] success clean statistics")
        except Exception as e:
            logger.exception(
                f"[clear_statistics_info][tenant {tenant_id}] Failed to clear expired statistics data: {e}"
            )
