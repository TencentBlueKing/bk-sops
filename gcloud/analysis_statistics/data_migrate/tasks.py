# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


import logging

from celery.task import periodic_task
from django.db import transaction
from django.db.models import Q
from pipeline.contrib.periodic_task.djcelery.tzcrontab import TzAwareCrontab
from pipeline.contrib.statistics.models import (
    ComponentExecuteData,
    ComponentInTemplate,
    InstanceInPipeline,
    TemplateInPipeline,
)
from pipeline.core.constants import PE
from pipeline.engine.utils import calculate_elapsed_time
from pipeline.models import PipelineInstance, PipelineTemplate

from gcloud.analysis_statistics.data_migrate.models import MigrateLog
from gcloud.analysis_statistics.models import (
    TaskflowExecutedNodeStatistics,
    TaskflowStatistics,
    TemplateNodeStatistics,
    TemplateStatistics,
)
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate

logger = logging.getLogger("celery")


def migrate_template(start, end):
    """
    @summary: 执行“TemplateInPipeline-->TemplateStatistics”的迁移
    param start:TemplateInPipeline表的主键
    param end:TemplateInPipeline表的主键
    return success:是否成功
    """
    # 查询出所有目标记录
    condition = Q()
    condition.children.append(("id__gte", start))
    condition.children.append(("id__lt", end))
    template_in_pipeline_records = TemplateInPipeline.objects.filter(condition)

    # 构造数据源字典
    data_source_list = []
    for template_in_pipeline_inst in template_in_pipeline_records:
        try:
            template_id = template_in_pipeline_inst.template_id
            pipeline_template = PipelineTemplate.objects.get(template_id=template_id)
            task_template = TaskTemplate.objects.get(pipeline_template__id=pipeline_template.id)
            data_source_list.append(
                {
                    "template_in_pipeline_inst": template_in_pipeline_inst,
                    "pipeline_template": pipeline_template,
                    "task_template": task_template,
                }
            )
        except Exception:
            logger.exception(f"[migrate_template] dirty data error template_id={template_id}")
            continue

    for data_source_item in data_source_list:
        try:
            pipeline_template = data_source_item["pipeline_template"]
            template_in_pipeline_inst = data_source_item["template_in_pipeline_inst"]
            task_template = data_source_item["task_template"]
            kwargs = {
                "template_id": pipeline_template.id,
                "task_template_id": task_template.id,
                "atom_total": template_in_pipeline_inst.atom_total,
                "subprocess_total": template_in_pipeline_inst.subprocess_total,
                "gateways_total": template_in_pipeline_inst.gateways_total,
                "project_id": task_template.project.id,
                "category": task_template.category,
                "template_creator": pipeline_template.creator,
                "template_create_time": pipeline_template.create_time,
                "template_edit_time": pipeline_template.edit_time,
            }
        except Exception:
            template_id = pipeline_template.id
            logger.exception(f"[migrate_template] unkwon error template_id={template_id}")
            continue
        # 计算输入输出变量个数
        input_count = 0
        output_count = 0
        data = pipeline_template.data
        try:
            for constant in data[PE.constants].values():
                if constant["source_type"] == "component_outputs":
                    output_count += 1
                else:
                    input_count += 1
        except KeyError:
            pass
        kwargs["input_count"] = input_count
        kwargs["output_count"] = output_count
        try:
            with transaction.atomic():
                TemplateStatistics.objects.filter(template_id=kwargs["template_id"]).delete()
                template_statistics = TemplateStatistics.objects.create(**kwargs)
                template_statistics.save()
        except Exception:
            template_id = kwargs["template_id"]
            logger.exception(f"[migrate_template] template_id={template_id}的数据插入失败，自动回滚")

    return True


def migrate_component(start, end):
    """
    @summary: 执行“ComponentInTemplate-->TemplateNodeStatistics”的迁移
    param start:ComponentInTemplate表的主键
    param end:ComponentInTemplate表的主键
    return success:是否成功
    """

    # 查询出所有目标记录
    condition = Q()
    condition.children.append(("id__gte", start))
    condition.children.append(("id__lt", end))
    component_in_template_records = ComponentInTemplate.objects.filter(condition)
    # 构建数据源
    data_source_list = []
    for component_in_template_inst in component_in_template_records:
        try:
            template_id = component_in_template_inst.template_id
            pipeline_template = PipelineTemplate.objects.get(template_id=template_id)
            task_template = TaskTemplate.objects.get(pipeline_template__id=pipeline_template.id)
            data_source_list.append(
                {
                    "pipeline_template": pipeline_template,
                    "task_template": task_template,
                    "component_in_template_inst": component_in_template_inst,
                }
            )
        except Exception:
            logger.exception(f"[migrate_component] dirty data error template_id={template_id}")
            continue

    # 迁移
    for data_source_item in data_source_list:
        try:
            component = data_source_item["component_in_template_inst"]
            pipeline_template = data_source_item["pipeline_template"]
            task_template = data_source_item["task_template"]
            kwargs = dict(
                component_code=component.component_code,
                template_id=pipeline_template.id,
                task_template_id=task_template.id,
                project_id=task_template.project.id,
                category=task_template.category,
                node_id=component.node_id,
                is_sub=component.is_sub,
                subprocess_stack=component.subprocess_stack,
                version=component.version,
                template_creator=pipeline_template.creator,
                template_create_time=pipeline_template.create_time,
                template_edit_time=pipeline_template.edit_time,
            )
        except Exception:
            template_id = pipeline_template.id
            node_id = component.id
            logger.exception(f"[migrate_component] unkwon error template_id={template_id},node_id={node_id}")
            continue
        try:
            with transaction.atomic():
                TemplateNodeStatistics.objects.filter(
                    task_template_id=kwargs["task_template_id"], node_id=kwargs["node_id"]
                ).delete()
                template_node_statistics = TemplateNodeStatistics.objects.create(**kwargs)
                template_node_statistics.save()
        except Exception:
            template_id = kwargs["template_id"]
            node_id = kwargs["node_id"]
            logger.exception(f"[migrate_component] template_id={template_id},node_id={node_id}的数据插入失败，自动回滚")

    return True


def migrate_instance(start, end):
    """
    @summary: 执行“InstanceInPipeline-->TaskflowStatistics”的迁移
    param start:InstanceInPipeline表的主键
    param end:InstanceInPipeline表的主键
    return success:是否成功
    """

    # 查询出所有目标记录
    condition = Q()
    condition.children.append(("id__gte", start))
    condition.children.append(("id__lt", end))
    instance_in_pipeline_records = InstanceInPipeline.objects.filter(condition)

    # 构建数据源字典
    data_source_list = []
    for instance_in_pipeline in instance_in_pipeline_records:
        try:
            instance_id = instance_in_pipeline.instance_id
            pipeline_instance = PipelineInstance.objects.get(instance_id=instance_id)
            taskflow_instance = TaskFlowInstance.objects.get(pipeline_instance__id=pipeline_instance.id)
            pipeline_template = taskflow_instance.pipeline_instance.template
            task_template = TaskTemplate.objects.get(pipeline_template=pipeline_template)
            data_source_list.append(
                {
                    "pipeline_instance": pipeline_instance,
                    "taskflow_instance": taskflow_instance,
                    "pipeline_template": pipeline_template,
                    "task_template": task_template,
                    "instance_in_pipeline": instance_in_pipeline,
                }
            )
        except Exception:
            logger.exception(f"[migrate_instance] dirty data error template_id={instance_id}")
            continue
    # 构建目标数据对象
    for data_source_item in data_source_list:
        try:
            instance = data_source_item["pipeline_instance"]
            taskflow_instance = data_source_item["taskflow_instance"]
            task_template = data_source_item["task_template"]
            instance_in_pipeline = data_source_item["instance_in_pipeline"]
            pipeline_template = data_source_item["pipeline_template"]
            kwargs = dict(
                instance_id=instance.id,
                task_instance_id=taskflow_instance.id,
                atom_total=instance_in_pipeline.atom_total,
                subprocess_total=instance_in_pipeline.subprocess_total,
                gateways_total=instance_in_pipeline.gateways_total,
                project_id=taskflow_instance.project.id,
                category=task_template.category,
                template_id=pipeline_template.id,
                task_template_id=task_template.id,
                creator=instance.creator,
                create_time=instance.create_time,
                start_time=instance.start_time,
                finish_time=instance.finish_time,
                elapsed_time=calculate_elapsed_time(instance.start_time, instance.finish_time),
                create_method=taskflow_instance.create_method,
            )
        except Exception:
            instance_id = instance.id
            logger.exception(f"[migrate_instance] unkwon error instance_id={instance_id}")
            continue
        try:
            with transaction.atomic():
                TaskflowStatistics.objects.filter(instance_id=kwargs["instance_id"]).delete()
                taslflowstatistics = TaskflowStatistics.objects.create(**kwargs)
                taslflowstatistics.save()
        except Exception:
            instance_id = kwargs["instance_id"]
            logger.exception(f"[migrate_instance] instance_id={instance_id}的数据插入失败，自动回滚")

    return True


def migrate_component_execute_data(start, end):
    """
    @summary: 执行“ComponentExecuteData-->TaskflowExecutedNodeStatistics”的迁移
    param start:ComponentExecuteData表的主键
    param end:ComponentExecuteData表的主键
    return success:是否成功
    """

    # 查询出所有目标记录
    condition = Q()
    condition.children.append(("id__gte", start))
    condition.children.append(("id__lt", end))
    component_execute_data_records = ComponentExecuteData.objects.filter(condition)

    for component in component_execute_data_records:
        try:
            pipeline_instance = PipelineInstance.objects.get(instance_id=component.instance_id)
            taskflow_instance = TaskFlowInstance.objects.get(pipeline_instance=pipeline_instance)
            pipeline_template = pipeline_instance.template
            task_template = TaskTemplate.objects.get(pipeline_template=pipeline_template)
            kwargs = dict(
                component_code=component.component_code,
                instance_id=pipeline_instance.id,
                task_instance_id=taskflow_instance.id,
                node_id=component.node_id,
                is_sub=component.is_sub,
                subprocess_stack=component.subprocess_stack,
                started_time=component.started_time,
                archived_time=component.archived_time,
                elapsed_time=component.elapsed_time,
                status=component.status,
                is_skip=component.is_skip,
                is_retry=component.is_retry,
                version=component.version,
                template_id=pipeline_template.id,
                task_template_id=task_template.id,
                project_id=taskflow_instance.project.id,
                instance_create_time=pipeline_instance.create_time,
                instance_start_time=pipeline_instance.start_time,
                instance_finish_time=pipeline_instance.finish_time,
            )
        except Exception:
            instance_id = pipeline_instance.id
            node_id = component.node_id
            logger.exception(
                f"[migrate_component_execute_data] unkwon error instance_id={instance_id},node_id={node_id}"
            )
            continue
        try:
            with transaction.atomic():
                TaskflowExecutedNodeStatistics.objects.filter(
                    task_instance_id=kwargs["task_instance_id"], node_id=kwargs["node_id"]
                ).delete()
                taskflowexcutednodestatistics = TaskflowExecutedNodeStatistics.objects.create(**kwargs)
                taskflowexcutednodestatistics.save()
        except Exception:
            instance_id = kwargs["instance_id"]
            node_id = kwargs["node_id"]
            logger.exception(
                f"[migrate_component_execute_data] instance_id={instance_id},node_id={node_id}的数据插入失败，自动回滚"
            )
    return True


def format_process(process_num):
    if process_num > 100:
        return 100
    return process_num


@periodic_task(run_every=TzAwareCrontab(minute="*/10"))
def migrate_schedule():
    logger.info("[migrate_schedule] start the statistics migrate schedule ·········")

    migrate_log = MigrateLog.objects.filter(id=1).first()
    # 判断是否允许迁移
    if migrate_log and not migrate_log.migrate_switch:
        logger.info("[migrate_schedule] the migrate_switch is closed!")
        return

    # 获取迁移上下文
    migrate_log, created = MigrateLog.objects.get_or_create(
        id=1,
        defaults={
            "template_in_pipeline_count": TemplateInPipeline.objects.count(),
            "component_in_template_count": ComponentInTemplate.objects.count(),
            "instance_in_pipeline_count": InstanceInPipeline.objects.count(),
            "component_execute_data_count": ComponentExecuteData.objects.count(),
        },
    )
    if created:
        logger.info("[migrate_schedule] start the statistics migrate ··········")
    else:
        logger.info("[migrate_schedule] continue the statistics migrate ·········")

    # 打印开始迁移日志
    logger.info("[migrate_schedule] migrate process have started.")

    # TemplateInPipeline迁移并更新上下文
    if not migrate_log.template_in_pipeline_finished:
        if migrate_template(migrate_log.template_in_pipeline_start, migrate_log.template_in_pipeline_end):
            migrate_log.template_in_pipeline_start = migrate_log.template_in_pipeline_end
            migrate_log.template_in_pipeline_end += migrate_log.migrate_num_once
            migrate_log.template_in_pipeline_migrated += migrate_log.migrate_num_once
            migrate_log.save()
            # 如果起点大于总量就标记完成
            if migrate_log.template_in_pipeline_start > migrate_log.template_in_pipeline_count:
                migrate_log.template_in_pipeline_finished = True
                migrate_log.save()

    # ComponentInTemplate迁移并更新上下文
    if not migrate_log.component_in_template_finished:
        if migrate_component(migrate_log.component_in_template_start, migrate_log.component_in_template_end):
            migrate_log.component_in_template_start = migrate_log.component_in_template_end
            migrate_log.component_in_template_end += migrate_log.migrate_num_once
            migrate_log.component_in_template_migrated += migrate_log.migrate_num_once
            migrate_log.save()
            # 如果起点大于总量就标记完成
            if migrate_log.component_in_template_start > migrate_log.component_in_template_count:
                migrate_log.component_in_template_finished = True
                migrate_log.save()

    # InstanceInPipeline迁移并更新上下文
    if not migrate_log.instance_in_pipeline_finished:
        if migrate_instance(migrate_log.instance_in_pipeline_start, migrate_log.instance_in_pipeline_end):
            migrate_log.instance_in_pipeline_start = migrate_log.instance_in_pipeline_end
            migrate_log.instance_in_pipeline_end += migrate_log.migrate_num_once
            migrate_log.instance_in_pipeline_migrated += migrate_log.migrate_num_once
            migrate_log.save()
            # 如果起点大于总量就标记完成
            if migrate_log.instance_in_pipeline_start > migrate_log.instance_in_pipeline_count:
                migrate_log.instance_in_pipeline_finished = True
                migrate_log.save()

    # ComponentExecuteData迁移并更新上下文
    if not migrate_log.component_execute_data_finished:
        if migrate_component_execute_data(
            migrate_log.component_execute_data_start, migrate_log.component_execute_data_end
        ):
            migrate_log.component_execute_data_start = migrate_log.component_execute_data_end
            migrate_log.component_execute_data_end += migrate_log.migrate_num_once
            migrate_log.component_execute_data_migrated += migrate_log.migrate_num_once
            migrate_log.save()
            # 如果起点大于总量就标记完成
            if migrate_log.component_execute_data_start > migrate_log.component_execute_data_count:
                migrate_log.component_execute_data_finished = True
                migrate_log.save()

    # 如果所有表都迁移完成就关掉迁移任务
    finished = all(
        (
            migrate_log.template_in_pipeline_finished,
            migrate_log.component_in_template_finished,
            migrate_log.instance_in_pipeline_finished,
            migrate_log.component_execute_data_finished,
        )
    )

    # 计算各表迁移进度百分比
    template_migrate_process = format_process(
        round(migrate_log.template_in_pipeline_migrated / migrate_log.template_in_pipeline_count, 2) * 100
    )
    component_migrate_process = format_process(
        round(migrate_log.component_in_template_migrated / migrate_log.component_in_template_count, 2) * 100
    )
    instance_migrate_process = format_process(
        round(migrate_log.instance_in_pipeline_migrated / migrate_log.instance_in_pipeline_count, 2) * 100
    )
    component_execute_migrate_process = format_process(
        round(migrate_log.component_execute_data_migrated / migrate_log.component_execute_data_count, 2) * 100
    )
    logger.info(
        f"""
        [statistics_migrate_process] migrated templateInPipeline({template_migrate_process}%)
        ComponentInTemplate({component_migrate_process}%)
        InstanceInPipeline({instance_migrate_process}%)
        ComponentExecuteData({component_execute_migrate_process}%)
        """
    )

    if finished:
        migrate_log.migrate_switch = False
        migrate_log.save()
        logger.info("[migrate_schedule] migrate process has finished ! ")
        return

    logger.info("[migrate_schedule] waiting next migrate process·····")
