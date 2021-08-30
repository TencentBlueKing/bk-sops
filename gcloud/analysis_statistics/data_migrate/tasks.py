# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


import logging

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from celery.task import periodic_task

from pipeline.contrib.statistics.models import (
    TemplateInPipeline,
    ComponentInTemplate,
    InstanceInPipeline,
    ComponentExecuteData,
)
from pipeline.models import PipelineInstance, PipelineTemplate
from pipeline.core.constants import PE
from pipeline.engine.utils import calculate_elapsed_time
from pipeline.contrib.periodic_task.djcelery.tzcrontab import TzAwareCrontab

from gcloud.analysis_statistics.models import (
    TemplateInStatistics,
    TemplateNodeTemplate,
    TaskflowExecutedNodeStatistics,
    TaskflowStatistics,
)
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.analysis_statistics.data_migrate.models import MigrateLog
from gcloud.analysis_statistics.data_migrate.models import MIGRATE_NUM

logger = logging.getLogger("celery")


def migrate_template(start, end):
    """
    @summary: 执行“TemplateInPipeline-->TemplateInStatistics”的迁移
    param start:TemplateInPipeline表的主键
    param end:TemplateInPipeline表的主键
    return success:是否成功
    """

    # 查询出所有目标记录
    filter = Q()
    filter.children.append(("id__gte", start))
    filter.children.append(("id__lt", end))
    template_in_pipeline_records = TemplateInPipeline.objects.filter(filter)

    # 构造新的数据对象
    template_id_list = template_in_pipeline_records.values_list("template_id", flat=True)
    pipeline_template_list = PipelineTemplate.objects.filter(template_id__in=template_id_list)
    task_template_list = TaskTemplate.objects.filter(pipeline_template__in=pipeline_template_list)

    template_in_statistics_instance = []
    for pipeline_template in pipeline_template_list:
        try:
            template_in_pipeline = template_in_pipeline_records.get(template_id=pipeline_template.template_id)
            task_template = task_template_list.get(pipeline_template=pipeline_template)
            project = task_template.project
        except ObjectDoesNotExist:
            continue
        kwargs = {
            "template_id": pipeline_template.id,
            "task_template_id": task_template.id,
            "atom_total": template_in_pipeline.atom_total,
            "subprocess_total": template_in_pipeline.subprocess_total,
            "gateways_total": template_in_pipeline.gateways_total,
            "project_id": project.id,
            "category": task_template.category,
            "template_creator": pipeline_template.creator,
            "template_create_time": pipeline_template.create_time,
            "template_edit_time": pipeline_template.edit_time,
        }
        # 计算输入输出变量个数
        input_count = 0
        output_count = 0
        data = pipeline_template.data
        for constant in data[PE.constants].values():
            if constant["source_type"] == "component_outputs":
                output_count += 1
            else:
                input_count += 1
        kwargs["input_count"] = input_count
        kwargs["output_count"] = output_count

        template_in_statistics_instance.append(TemplateInStatistics(**kwargs))
    try:
        TemplateInStatistics.objects.bulk_create(template_in_statistics_instance)
        return True
    except Exception:
        logger.error("migrate TemplateInPipeline fail, from {start} to {end}".format(start=start, end=end))
        return False


def migrate_component(start, end):
    """
    @summary: 执行“ComponentInTemplate-->TemplateNodeTemplate”的迁移
    param start:ComponentInTemplate表的主键
    param end:ComponentInTemplate表的主键
    return success:是否成功
    """

    # 查询出所有目标记录
    filter = Q()
    filter.children.append(("id__gte", start))
    filter.children.append(("id__lt", end))
    component_in_template_records = ComponentInTemplate.objects.filter(filter)
    template_id_list = component_in_template_records.values_list("template_id", flat=True)
    pipeline_template_list = PipelineTemplate.objects.filter(template_id__in=template_id_list)

    component_in_template_instance = []
    for pipeline_template in pipeline_template_list:
        try:
            # 根据pipeline_template查询到task_template
            task_template = TaskTemplate.objects.get(pipeline_template=pipeline_template)
            component_in_template_datas = component_in_template_records.filter(
                template_id=pipeline_template.template_id
            ).values("component_code", "template_id", "node_id", "is_sub", "subprocess_stack", "version")
        except ObjectDoesNotExist:
            continue
        components = [
            TemplateNodeTemplate(
                component_code=component["component_code"],
                template_id=pipeline_template.id,
                task_template_id=task_template.id,
                project_id=task_template.project.id,
                category=task_template.category,
                node_id=component["node_id"],
                is_sub=component["is_sub"],
                subprocess_stack=component["subprocess_stack"],
                version=component["version"],
                template_creator=pipeline_template.creator,
                template_create_time=pipeline_template.create_time,
                template_edit_time=pipeline_template.edit_time,
            )
            for component in component_in_template_datas
        ]

        component_in_template_instance.extend(components)

    try:
        TemplateNodeTemplate.objects.bulk_create(component_in_template_instance)
        return True
    except Exception:
        logger.error("migrate TemplateNodeTemplate fail, from {start} to {end}".format(start=start, end=end))
        return False


def migrate_instance(start, end):
    """
    @summary: 执行“InstanceInPipeline-->TaskflowStatistics”的迁移
    param start:InstanceInPipeline表的主键
    param end:InstanceInPipeline表的主键
    return success:是否成功
    """

    # 查询出所有目标记录
    filter = Q()
    filter.children.append(("id__gte", start))
    filter.children.append(("id__lt", end))
    instance_in_pipeline_records = InstanceInPipeline.objects.filter(filter)
    instance_id_list = instance_in_pipeline_records.values_list("instance_id", flat=True)
    instance_list = PipelineInstance.objects.filter(instance_id__in=instance_id_list)

    taskflow_statistics_instance = []
    for instance in instance_list:
        try:
            taskflow_instance = TaskFlowInstance.objects.get(pipeline_instance=instance)
            pipeline_template = taskflow_instance.pipeline_instance.template
            task_template = TaskTemplate.objects.get(pipeline_template=pipeline_template)
        except ObjectDoesNotExist:
            continue
        taskflow_statistics_data = [
            TaskflowStatistics(
                instance_id=instance.id,
                task_instance_id=taskflow_instance.id,
                atom_total=instance_in_pipeline.atom_total,
                subprocess_total=instance_in_pipeline.subprocess_total,
                gateways_total=instance_in_pipeline.gateways_total,
                project_id=taskflow_instance.project.id,
                category=task_template.category,
                template_id=pipeline_template.id,
                creator=instance.creator,
                create_time=instance.create_time,
                start_time=instance.start_time,
                finish_time=instance.finish_time,
                elapsed_time=calculate_elapsed_time(instance.start_time, instance.finish_time),
                create_method=taskflow_instance.create_method,
            )
            for instance_in_pipeline in instance_in_pipeline_records
        ]
        taskflow_statistics_instance.extend(taskflow_statistics_data)
    try:
        TaskflowStatistics.objects.bulk_create(taskflow_statistics_instance)
        return True
    except Exception:
        logger.error("migrate TaskflowStatistics fail, from {start} to {end}".format(start=start, end=end))
        return False


def migrate_componentExecuteData(start, end):
    """
    @summary: 执行“ComponentExecuteData-->TaskflowExecutedNodeStatistics”的迁移
    param start:ComponentExecuteData表的主键
    param end:ComponentExecuteData表的主键
    return success:是否成功
    """

    # 查询出所有目标记录
    filter = Q()
    filter.children.append(("id__gte", start))
    filter.children.append(("id__lt", end))
    component_execute_data_records = ComponentExecuteData.objects.filter(filter)
    component_instance = []
    for component in component_execute_data_records:
        try:
            pipeline_instance = PipelineInstance.objects.get(instance_id=component.instance_id)
            taskflow_instance = TaskFlowInstance.objects.get(pipeline_instance=pipeline_instance)
            pipeline_template = pipeline_instance.template
            task_template = TaskTemplate.objects.get(pipeline_template=pipeline_template)
        except ObjectDoesNotExist:
            continue
        component_list = [
            TaskflowExecutedNodeStatistics(
                component_code=component.component_code,
                instance_id=component.instance_id,
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
        ]
        component_instance.extend(component_list)
    try:
        TaskflowExecutedNodeStatistics.objects.bulk_create(component_instance)
        return True
    except Exception:
        logger.error("migrate TaskflowExecutedNodeStatistics fail, from {start} to {end}".format(start=start, end=end))
        return False


@periodic_task(run_every=TzAwareCrontab(minute="*/2"))
def migrate_schedule():
    logger.info("start migrate process·····")
    # 获取迁移上下文
    try:
        migrate_log = MigrateLog.objects.get(id=1)
    except ObjectDoesNotExist:
        # 初始化MigrateLog
        templateInPipeline_count = TemplateInPipeline.objects.count()
        componentInTemplate_count = ComponentInTemplate.objects.count()
        instanceInPipeline_count = InstanceInPipeline.objects.count()
        componenetExecuteData_count = ComponentExecuteData.objects.count()
        migrate_log = MigrateLog.objects.create(
            templateInPipeline_count=templateInPipeline_count,
            componentInTemplate_count=componentInTemplate_count,
            instanceInPipeline_count=instanceInPipeline_count,
            componenetExecuteData_count=componenetExecuteData_count,
        )
        migrate_log.save()

    # TemplateInPipeline迁移并更新上下文
    if not migrate_log.templateInPipeline_finished:
        if migrate_template(migrate_log.templateInPipeline_start, migrate_log.templateInPipeline_end):
            migrate_log.templateInPipeline_start = migrate_log.templateInPipeline_end
            migrate_log.templateInPipeline_end += MIGRATE_NUM
            migrate_log.save()
            # 如果起点大于总量就标记完成
            if migrate_log.templateInPipeline_start > migrate_log.templateInPipeline_count:
                migrate_log.templateInPipeline_finished = True

    # ComponentInTemplate迁移并更新上下文
    if not migrate_log.componentInTemplate_finished:
        if migrate_component(migrate_log.componentInTemplate_start, migrate_log.componentInTemplate_end):
            migrate_log.componentInTemplate_start = migrate_log.componentInTemplate_end
            migrate_log.componentInTemplate_end += MIGRATE_NUM
            migrate_log.save()
            # 如果起点大于总量就标记完成
            if migrate_log.componentInTemplate_start > migrate_log.componentInTemplate_count:
                migrate_log.componentInTemplate_finished = True

    # InstanceInPipeline迁移并更新上下文
    if not migrate_log.instanceInPipeline_finished:
        if migrate_instance(migrate_log.instanceInPipeline_start, migrate_log.instanceInPipeline_end):
            migrate_log.instanceInPipeline_start = migrate_log.instanceInPipeline_end
            migrate_log.instanceInPipeline_end += MIGRATE_NUM
            migrate_log.save()
            # 如果起点大于总量就标记完成
            if migrate_log.instanceInPipeline_start > migrate_log.instanceInPipeline_count:
                migrate_log.instanceInPipeline_finished = True

    # ComponentExecuteData迁移并更新上下文
    if not migrate_log.componenetExecuteData_finished:
        if migrate_componentExecuteData(migrate_log.componentExecuteData_start, migrate_log.componenetExecuteData_end):
            migrate_log.componentExecuteData_start = migrate_log.componenetExecuteData_end
            migrate_log.componenetExecuteData_end += MIGRATE_NUM
            migrate_log.save()
            # 如果起点大于总量就标记完成
            if migrate_log.componentExecuteData_start > migrate_log.componenetExecuteData_count:
                migrate_log.componenetExecuteData_finished = True

    logger.info("waiting next migrate process·····")
