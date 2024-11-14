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
from copy import deepcopy
from datetime import datetime

import ujson as json
from bamboo_engine import api as bamboo_engine_api
from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
from django.core.paginator import Paginator
from pipeline.component_framework.constants import LEGACY_PLUGINS_VERSION
from pipeline.contrib.statistics.utils import count_pipeline_tree_nodes
from pipeline.core.constants import PE
from pipeline.engine import api as pipeline_api
from pipeline.engine import states
from pipeline.engine.utils import calculate_elapsed_time
from pipeline.eri.runtime import BambooDjangoRuntime
from pipeline.models import PipelineTemplate

from gcloud.analysis_statistics import variable
from gcloud.analysis_statistics.models import (
    TaskflowExecutedNodeStatistics,
    TaskflowStatistics,
    TemplateCustomVariableSummary,
    TemplateNodeStatistics,
    TemplateStatistics,
    TemplateVariableStatistics,
)
from gcloud.common_template.models import CommonTemplate
from gcloud.taskflow3.domains.dispatchers.task import TaskCommandDispatcher
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate

logger = logging.getLogger("celery")


def format_date_time(time_str, time_format="%Y-%m-%d %H:%M:%S"):
    format_time_str = time_str.split("+")[0].strip()
    date_time = datetime.strptime(format_time_str, time_format)
    return date_time.replace(tzinfo=None)


def recursive_collect_components_execution(activities, status_tree, task_instance, engine_ver=1, stack=None):
    """
    @summary 递归流程树，获取所有执行结束的插件TaskflowExecutedNodeStatistics对象列表（成功/失败）
    @param activities: 当前流程树的任务节点信息
    @param status_tree: 当前流程树的任务节点状态
    @param task_instance: 根流程实例TaskFlowInstance
    @param stack: 子流程堆栈
    @param engine_ver: 流程引擎版本
    """
    instance = task_instance.pipeline_instance
    trigger_template_id = task_instance.template_id
    task_instance_id = task_instance.id
    task_template = (
        TaskTemplate.objects.filter(pipeline_template=instance.template).first()
        or CommonTemplate.objects.filter(pipeline_template=instance.template).first()
    )
    if not task_template:
        raise Exception(f"task_template with template_id {instance.template.template_id} not found")
    if stack is None:
        stack = []
        is_sub = False
    else:
        is_sub = True
    component_list = []
    for act_id, act in activities.items():
        if act_id in status_tree:
            exec_act = status_tree[act_id]
            # 标准插件节点
            if act[PE.type] == PE.ServiceActivity:
                # 结束、失败、撤销
                if exec_act["state"] in states.ARCHIVED_STATES:
                    component_code = act["component"]["code"]
                    component_version = act["component"].get("version", LEGACY_PLUGINS_VERSION)
                    is_remote = False
                    if component_code == "remote_plugin":
                        component_code = act["component"]["data"]["plugin_code"]["value"]
                        component_version = act["component"]["data"]["plugin_version"]["value"]
                        is_remote = True
                    component_kwargs = {
                        "component_code": component_code,
                        "instance_id": instance.id,
                        "task_instance_id": task_instance_id,
                        "is_sub": is_sub,
                        "template_node_id": act.get("template_node_id") or "",
                        "node_id": act_id,
                        "subprocess_stack": json.dumps(stack),
                        "started_time": format_date_time(exec_act["start_time"]),
                        "archived_time": format_date_time(exec_act["finish_time"]),
                        "elapsed_time": exec_act.get(
                            "elapsed_time",
                            calculate_elapsed_time(
                                format_date_time(exec_act["start_time"]), format_date_time(exec_act["finish_time"])
                            ),
                        ),
                        "is_skip": exec_act["skip"],
                        "is_retry": False,
                        "status": exec_act["state"] == "FINISHED",
                        "version": component_version,
                        "template_id": instance.template.id,
                        "task_template_id": task_template.id,
                        "trigger_template_id": trigger_template_id,
                        "instance_create_time": instance.create_time,
                        "instance_start_time": instance.start_time,
                        "instance_finish_time": instance.finish_time,
                        "is_remote": is_remote,
                    }
                    if getattr(task_template, "project", None):
                        component_kwargs["project_id"] = task_template.project.id
                    component_list.append(TaskflowExecutedNodeStatistics(**component_kwargs))
                    if exec_act["retry"] > 0:
                        # 有重试记录，需要从执行历史中获取数据
                        if engine_ver == 1:
                            history_list = pipeline_api.get_activity_histories(act_id)
                        else:
                            history_list_result = bamboo_engine_api.get_node_short_histories(
                                runtime=BambooDjangoRuntime(), node_id=act_id
                            )
                            history_list = history_list_result.data if history_list_result.result else []

                        for history in history_list:
                            component_kwargs.update(
                                {
                                    "started_time": history["started_time"],
                                    "archived_time": history["archived_time"],
                                    "elapsed_time": history.get(
                                        "elapsed_time",
                                        calculate_elapsed_time(history["started_time"], history["archived_time"]),
                                    ),
                                    "is_retry": True,
                                    "is_skip": False,
                                    "status": False,
                                }
                            )
                            component_list.append(TaskflowExecutedNodeStatistics(**component_kwargs))
            # 子流程的执行堆栈（子流程的执行过程）
            elif act[PE.type] == PE.SubProcess:
                sub_activities = act[PE.pipeline][PE.activities]
                # 防止stack共用
                copied_stack = deepcopy(stack)
                copied_stack.insert(0, act_id)
                component_list += recursive_collect_components_execution(
                    activities=sub_activities,
                    status_tree=exec_act["children"],
                    task_instance=task_instance,
                    stack=copied_stack,
                    engine_ver=engine_ver,
                )
    return component_list


@task
def taskflowinstance_post_save_statistics_task(task_instance_id, created):
    try:
        taskflow_instance = TaskFlowInstance.objects.get(id=task_instance_id)
        # pipeline数据
        pipeline_instance = taskflow_instance.pipeline_instance
        # template数据
        task_template = TaskTemplate.objects.get(id=taskflow_instance.template_id)
        # 统计流程标准插件个数，子流程个数，网关个数
        kwargs = {
            "instance_id": pipeline_instance.id,
            "project_id": taskflow_instance.project.id,
            "category": task_template.category,
            "template_id": task_template.pipeline_template.id,
            "task_template_id": task_template.id,
            "creator": pipeline_instance.creator,
            "create_time": pipeline_instance.create_time,
            "start_time": pipeline_instance.start_time,
            "finish_time": pipeline_instance.finish_time,
            "elapsed_time": calculate_elapsed_time(pipeline_instance.start_time, pipeline_instance.finish_time),
            "create_method": taskflow_instance.create_method,
        }
        kwargs["atom_total"], kwargs["subprocess_total"], kwargs["gateways_total"] = count_pipeline_tree_nodes(
            pipeline_instance.execution_data
        )
        if created:
            kwargs["task_instance_id"] = taskflow_instance.id
            TaskflowStatistics.objects.create(**kwargs)
        else:
            TaskflowStatistics.objects.filter(task_instance_id=taskflow_instance.id).update(**kwargs)
        return True
    except Exception as e:
        logger.exception(
            (
                "task_flow_post_handler save TaskflowStatistics[instance_id={instance_id}] " "raise error: {error}"
            ).format(instance_id=task_instance_id, error=e)
        )
        return False


@task
def tasktemplate_post_save_statistics_task(template_id):
    template = TaskTemplate.objects.get(id=template_id)
    task_template_id = template.id
    # 删除原有数据
    try:
        TemplateNodeStatistics.objects.filter(task_template_id=task_template_id).delete()
    except Exception:
        logger.exception("保存运营数据template={template}时发生未知错误,".format(template=template_id))
        return False
    data = template.pipeline_template.data
    component_list = []
    # 任务节点引用标准插件统计（包含间接通过子流程引用）
    for act_id, act in data[PE.activities].items():
        # 标准插件节点
        if act["type"] == PE.ServiceActivity:
            # 判断是否第三方插件
            component_code = act["component"]["code"]
            component_version = act["component"].get("version", LEGACY_PLUGINS_VERSION)
            is_remote = False
            if component_code == "remote_plugin":
                component_code = act["component"]["data"]["plugin_code"]["value"]
                component_version = act["component"]["data"]["plugin_version"]["value"]
                is_remote = True
            component = TemplateNodeStatistics(
                component_code=component_code,
                template_id=template.pipeline_template.id,
                task_template_id=task_template_id,
                project_id=template.project.id,
                category=template.category,
                node_id=act_id,
                version=component_version,
                template_creator=template.pipeline_template.creator,
                template_create_time=template.pipeline_template.create_time,
                template_edit_time=template.pipeline_template.edit_time,
                is_remote=is_remote,
            )
            component_list.append(component)
        # 子流程节点
        else:
            try:
                template_id = PipelineTemplate.objects.filter(template_id=act["template_id"]).values("id")[0]["id"]
            except Exception:
                logger.exception(
                    "[tasktemplate_post_save_statistics_task]template_id={}的流程保存运营数据失败".format(template.id)
                )
                return False
            components = TemplateNodeStatistics.objects.filter(template_id=template_id).values(
                "subprocess_stack", "component_code", "node_id", "version"
            )
            for component_sub in components:
                # 子流程执行堆栈信息(执行过程)
                stack = json.loads(component_sub["subprocess_stack"])
                # 添加节点id
                stack.insert(0, act_id)
                component = TemplateNodeStatistics(
                    component_code=component_sub["component_code"],
                    template_id=template.pipeline_template.id,
                    task_template_id=task_template_id,
                    project_id=template.project.id,
                    category=template.category,
                    node_id=component_sub["node_id"],
                    is_sub=True,
                    version=component_sub["version"],
                    subprocess_stack=json.dumps(stack),
                    template_creator=template.pipeline_template.creator,
                    template_create_time=template.pipeline_template.create_time,
                    template_edit_time=template.pipeline_template.edit_time,
                )
                component_list.append(component)
    TemplateNodeStatistics.objects.bulk_create(component_list)

    # 统计流程标准插件个数，子流程个数，网关个数
    atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(data)
    # 统计流程数据中全局变量输入和输出个数
    input_count = 0
    output_count = 0
    for constant in data[PE.constants].values():
        if constant["source_type"] == "component_outputs":
            output_count += 1
        else:
            input_count += 1
    # 更新TemplateStatistics
    TemplateStatistics.objects.update_or_create(
        task_template_id=task_template_id,
        defaults={
            "template_id": template.pipeline_template.id,
            "atom_total": atom_total,
            "subprocess_total": subprocess_total,
            "gateways_total": gateways_total,
            "project_id": template.project.id,
            "category": template.category,
            "template_creator": template.pipeline_template.creator,
            "template_create_time": template.pipeline_template.create_time,
            "template_edit_time": template.pipeline_template.edit_time,
            "output_count": output_count,
            "input_count": input_count,
        },
    )
    return True


@task
def pipeline_archive_statistics_task(instance_id):
    taskflow_instance = TaskFlowInstance.objects.get(pipeline_instance__instance_id=instance_id)
    # 更新taskflowinstance统计数据start_time finish_time elapsed_time
    taskflow_statistic = TaskflowStatistics.objects.filter(task_instance_id=taskflow_instance.id).first()
    if taskflow_statistic:
        start_time = taskflow_instance.pipeline_instance.start_time
        finish_time = taskflow_instance.pipeline_instance.finish_time
        taskflow_statistic.start_time = start_time
        taskflow_statistic.finish_time = finish_time
        taskflow_statistic.elapsed_time = calculate_elapsed_time(start_time, finish_time)
        taskflow_statistic.save()
    engine_ver = taskflow_instance.engine_ver
    # 获取任务实例执行树
    cmd_dispatcher = TaskCommandDispatcher(
        engine_ver, taskflow_instance.id, taskflow_instance.pipeline_instance, taskflow_instance.project.id
    )
    status_tree_result = cmd_dispatcher.get_task_status()
    if not status_tree_result["result"]:
        logger.exception("get task_status_result fail, taskflow_instace = {id}.".format(id=taskflow_instance.id))
        return False
    # 删除原有标准插件执行数据
    TaskflowExecutedNodeStatistics.objects.filter(instance_id=taskflow_instance.pipeline_instance.id).delete()
    data = taskflow_instance.pipeline_instance.execution_data
    try:
        component_list = recursive_collect_components_execution(
            activities=data[PE.activities],
            status_tree=status_tree_result["data"]["children"],
            task_instance=taskflow_instance,
            engine_ver=engine_ver,
        )
        TaskflowExecutedNodeStatistics.objects.bulk_create(component_list)
    except Exception:
        logger.exception(
            (
                "pipeline_instance_handler save TaskflowExecuteNodeStatistics[instance_id={instance_id}] raise error"
            ).format(instance_id=instance_id)
        )
        return False
    return True


@task
@periodic_task(run_every=crontab(hour="0"))
def backfill_template_variable_statistics_task():
    custom_variables_records = {}

    # process common template
    common_templates = CommonTemplate.objects.all()
    common_templates_counts = CommonTemplate.objects.all().count()
    for i, template in enumerate(common_templates, 1):
        logger.info(
            "[backfill_template_variable_statistics_task] process {}/{} common template".format(
                i, common_templates_counts
            )
        )
        if template.is_deleted:
            TemplateVariableStatistics.objects.filter(project_id=-1, template_id=template.id).delete()
        else:
            try:
                custom_constants_types = variable.update_statistics(
                    project_id=-1, template_id=template.id, pipeline_tree=template.pipeline_tree
                )
            except Exception:
                logger.exception(
                    "[backfill_template_variable_statistics_task]backfill common template {} failed".format(template.id)
                )
            else:
                for t in custom_constants_types:
                    custom_variables_records.setdefault(t, {"common": 0, "project": 0})["common"] += 1

    # process task template
    # 分页拉取，防止内存溢出
    paginator = Paginator(TaskTemplate.objects.all(), 500)
    processed_count = 0
    task_templates_counts = TaskTemplate.objects.all().count()
    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        task_templates = page.object_list

        for template in task_templates:
            processed_count += 1
            logger.info(
                "[backfill_template_variable_statistics_task] process {}/{} task template".format(
                    processed_count, task_templates_counts
                )
            )
            if template.is_deleted:
                TemplateVariableStatistics.objects.filter(
                    project_id=template.project_id, template_id=template.id
                ).delete()
            else:
                try:
                    custom_constants_types = variable.update_statistics(
                        project_id=template.project_id, template_id=template.id, pipeline_tree=template.pipeline_tree
                    )
                except Exception:
                    logger.info(
                        "[backfill_template_variable_statistics_task]backfill task template {} failed".format(
                            template.id
                        )
                    )
                else:
                    for t in custom_constants_types:
                        custom_variables_records.setdefault(t, {"common": 0, "project": 0})["project"] += 1

    # save summary
    TemplateCustomVariableSummary.objects.all().delete()
    summarys = [
        TemplateCustomVariableSummary(
            variable_type=t, task_template_refs=counts["project"], common_template_refs=counts["common"]
        )
        for t, counts in custom_variables_records.items()
    ]
    if summarys:
        TemplateCustomVariableSummary.objects.bulk_create(summarys, batch_size=100)
