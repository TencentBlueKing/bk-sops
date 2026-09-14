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
import time
from enum import Enum

from blueapps.contrib.celery_tools.periodic import periodic_task
from celery.schedules import crontab
from django.conf import settings
from django.db import transaction
from django.db.models import Q
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


def delete_records(queryset, field_name, tenant_id=None):
    """
    带重试机制的删除操作，处理Lock wait timeout
    """
    tenant_prefix = f"[tenant {tenant_id}] " if tenant_id else ""
    try:
        deleted_count = queryset.delete()[0]
        logger.info(f"{tenant_prefix}[clean_expired_v2_task_data] Deleted {deleted_count} records from {field_name}")
        return deleted_count
    except Exception as e:
        error_msg = str(e)
        logger.exception(f"{tenant_prefix}[clean_expired_v2_task_data] Failed to delete {field_name}: {error_msg}")
    return 0


def filter_clean_task_instances(tenant_settings, tenant_id=None):
    """
    过滤需要清理的任务实例
    优化后的版本：使用单次查询获取所有符合条件的任务，避免 N+1 查询问题

    Args:
        tenant_settings: 租户配置字典
        tenant_id: 租户ID，用于日志记录
    """
    validity_day = tenant_settings.get(CleanExpiredV2TaskConfig.V2_TASK_VALIDITY_DAY.value)
    expire_time = timezone.now() - timezone.timedelta(days=validity_day)
    batch_num = tenant_settings.get(CleanExpiredV2TaskConfig.CLEAN_EXPIRED_V2_TASK_BATCH_NUM.value)
    create_methods = tenant_settings.get(CleanExpiredV2TaskConfig.CLEAN_EXPIRED_V2_TASK_CREATE_METHODS.value, [])
    target_projects = tenant_settings.get(CleanExpiredV2TaskConfig.CLEAN_EXPIRED_V2_TASK_PROJECTS.value)

    tenant_prefix = f"[tenant {tenant_id}] " if tenant_id else ""

    # 获取所有项目的任务清理配置
    project_clean_configs = {}
    for config in ProjectConfig.objects.filter(task_clean_configs__isnull=False).values(
        "project_id", "task_clean_configs"
    ):
        if config["task_clean_configs"] and isinstance(config["task_clean_configs"], dict):
            project_create_methods = config["task_clean_configs"].get("create_methods", [])
            if project_create_methods:  # 只保存有效的配置
                project_clean_configs[config["project_id"]] = project_create_methods

    if project_clean_configs:
        logger.info(
            f"{tenant_prefix}[clean_expired_v2_task_data] Found {len(project_clean_configs)} "
            f"projects with custom clean configs: {list(project_clean_configs.keys())}"
        )

    # 构建基础查询条件
    base_q = Q(
        pipeline_instance__create_time__lt=expire_time,
        engine_ver=2,
        pipeline_instance__is_expired=False,
    )

    # 如果配置了项目范围，添加项目过滤
    if target_projects:
        base_q &= Q(project_id__in=target_projects)

    # 构建查询条件：使用 Q 对象组合所有项目的条件，实现单次查询
    query_conditions = Q()

    # 添加有特殊配置的项目条件
    for project_id, project_create_methods in project_clean_configs.items():
        # 跳过不在目标项目范围内的项目
        if target_projects and project_id not in target_projects:
            continue

        # 为每个项目创建独立的查询条件
        project_q = Q(project_id=project_id, create_method__in=project_create_methods)
        query_conditions |= project_q

    # 添加使用默认配置的项目条件
    configured_project_ids = list(project_clean_configs.keys())
    if configured_project_ids:
        # 排除已有特殊配置的项目，使用租户配置的create_methods
        default_q = Q(create_method__in=create_methods) & ~Q(project_id__in=configured_project_ids)
    else:
        # 所有项目都使用租户配置的create_methods
        default_q = Q(create_method__in=create_methods)

    query_conditions |= default_q

    # 执行单次查询，按创建时间排序确保公平性
    # 使用 id 排序而不是创建时间，因为 id 有索引，性能更好
    qs = (
        TaskFlowInstance.objects.filter(base_q & query_conditions)
        .order_by("id")
        .values("id", "pipeline_instance__instance_id", "project_id")[:batch_num]
    )

    ids = list(qs)

    # 记录统计信息
    if ids:
        # 统计每个项目清理的任务数
        project_stats = {}
        for item in ids:
            project_id = item["project_id"]
            project_stats[project_id] = project_stats.get(project_id, 0) + 1

        logger.info(
            f"{tenant_prefix}[clean_expired_v2_task_data] Total {len(ids)} "
            f"tasks to clean from {len(project_stats)} projects"
        )
        for project_id, count in sorted(project_stats.items()):
            config_info = (
                f"custom config (create_methods={project_clean_configs[project_id]})"
                if project_id in project_clean_configs
                else f"tenant config (create_methods={create_methods})"
            )
            logger.info(
                f"{tenant_prefix}[clean_expired_v2_task_data] Project {project_id}: {count} tasks ({config_info})"
            )

    return ids


@periodic_task(run_every=(crontab(*settings.CLEAN_EXPIRED_V2_TASK_CRON)), ignore_result=True, queue="task_data_clean")
@time_record(logger)
def clean_expired_v2_task_data():
    """
    清除过期的任务数据 - 优化版本

    优化点：
    1. 按依赖关系顺序删除，避免外键冲突
    2. 分小批次处理，减少单次锁定的数据量
    3. 添加重试机制，处理临时锁冲突
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

        logger.info(f"Start clean expired task data for tenant {tenant_id} (optimized)...")
        try:
            ids = filter_clean_task_instances(tenant_settings, tenant_id)
            if not ids:
                logger.info(f"[clean_expired_v2_task_data][tenant {tenant_id}] No tasks to clean")
                continue

            task_ids = [item["id"] for item in ids]
            pipeline_instance_ids = [item["pipeline_instance__instance_id"] for item in ids]

            logger.info(
                f"[clean_expired_v2_task_data][tenant {tenant_id}] Total {len(task_ids)} tasks to clean, "
                f"task_ids: {task_ids[:10]}{'...' if len(task_ids) > 10 else ''}"
            )

            # 🔧 优化1: 分小批次处理任务，避免一次性处理太多
            task_batch_size = 20

            for i in range(0, len(pipeline_instance_ids), task_batch_size):
                batch_pipeline_ids = pipeline_instance_ids[i : i + task_batch_size]
                batch_task_ids = task_ids[i : i + task_batch_size]

                logger.info(
                    f"[clean_expired_v2_task_data][tenant {tenant_id}] Processing batch {i//task_batch_size + 1}/"
                    f"{(len(task_ids) + task_batch_size - 1)//task_batch_size}, "
                    f"task_ids: {batch_task_ids}"
                )

                try:
                    with transaction.atomic():
                        _clean_task_batch(
                            batch_pipeline_ids,
                            batch_task_ids,
                            tenant_settings,
                            tenant_id,
                        )
                except Exception as e:
                    logger.exception(
                        f"[clean_expired_v2_task_data][tenant {tenant_id}] Error cleaning batch {batch_task_ids}: {e}"
                    )
                    # 继续处理下一批，不要因为一批失败而停止所有清理
                    continue

                # 批次间短暂休息，释放数据库压力
                time.sleep(0.5)

            logger.info(f"[clean_expired_v2_task_data][tenant {tenant_id}] All batches processed")
        except Exception as e:
            logger.exception(f"[clean_expired_v2_task_data][tenant {tenant_id}] error: {e}")


def _clean_task_batch(pipeline_instance_ids, task_ids, tenant_settings=None, tenant_id=None):
    """
    清理一批任务数据

    核心优化：
    1. 按正确顺序删除表，避免外键冲突和死锁
    2. 添加重试机制处理临时锁冲突

    Args:
        pipeline_instance_ids: pipeline实例ID列表
        task_ids: 任务ID列表
        tenant_settings: 租户配置字典，如果为None则使用全局配置
        tenant_id: 租户ID，用于日志记录
    """
    tenant_prefix = f"[tenant {tenant_id}] " if tenant_id else ""
    data_to_clean = get_clean_pipeline_instance_data(pipeline_instance_ids)
    tasks = TaskFlowInstance.objects.filter(id__in=task_ids)
    data_to_clean.update({"tasks": tasks})

    # 发送预删除信号
    pre_delete_pipeline_instance_data.send(sender=TaskFlowInstance, data=data_to_clean)

    instance_fields = ["tasks", "pipeline_instances"]

    # 判断是否删除实例：优先使用租户配置，否则使用全局配置
    clean_instance = False
    if tenant_settings:
        clean_instance = tenant_settings.get(CleanExpiredV2TaskConfig.CLEAN_EXPIRED_V2_TASK_INSTANCE.value, False)
    else:
        clean_instance = getattr(settings, "CLEAN_EXPIRED_V2_TASK_INSTANCE", False)

    # 🔧 优化2: 定义删除顺序，按依赖关系从叶子到根
    # 先删除依赖表（子表），再删除主表，避免外键冲突和死锁
    delete_order = [
        # 1. 节点相关的详细数据（最底层）
        "callback_data",
        "log_entry",
        "schedules_list",
        "execution_history_list",
        "execution_data_list",
        "state_list",
        "data_list",
        # 2. 节点配置和策略
        "retry_node_list",
        "timeout_node_list",
        "node_list",
        # 3. 上下文和进程数据
        "context_value",
        "context_outputs",
        "process",
        # 4. 周期任务和业务层数据
        "periodic_task_history",
        "nodes_in_pipeline",
        # 5. 快照和树信息
        "execution_snapshot",
        "tree_info",
        # 6. 最后处理实例和任务
        "tasks",
        "pipeline_instances",
    ]

    for field_name in delete_order:
        if field_name not in data_to_clean:
            continue

        qs_or_list = data_to_clean[field_name]

        # 处理列表类型（分批的QuerySet）
        if field_name.endswith("_list") and isinstance(qs_or_list, list):
            logger.info(
                f"{tenant_prefix}[clean_expired_v2_task_data] clean field: {field_name}, "
                f"{len(qs_or_list)} batch data"
            )

            # 🔧 修复: 使用循环而不是列表推导式，避免内存问题
            for idx, qs in enumerate(qs_or_list):
                delete_records(qs, f"{field_name}[{idx}]", tenant_id)

        # 处理pipeline_instances - 只标记过期，不删除
        elif field_name == "pipeline_instances":
            updated_count = qs_or_list.update(is_expired=True)
            logger.info(f"{tenant_prefix}[clean_expired_v2_task_data] Updated {updated_count} pipeline_instances")

        # 处理需要删除的表
        elif field_name not in instance_fields or clean_instance:
            logger.info(f"{tenant_prefix}[clean_expired_v2_task_data] clean field: {field_name}")
            delete_records(qs_or_list, field_name, tenant_id)

    logger.info(f"{tenant_prefix}[clean_expired_v2_task_data] Successfully cleaned batch: {task_ids}")


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
