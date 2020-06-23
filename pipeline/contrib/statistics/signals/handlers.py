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
from copy import deepcopy

import ujson as json
from django.db.models.signals import post_save
from django.dispatch import receiver

from pipeline.component_framework.constants import LEGACY_PLUGINS_VERSION
from pipeline.contrib.statistics.models import (
    ComponentExecuteData,
    ComponentInTemplate,
    InstanceInPipeline,
    TemplateInPipeline,
)
from pipeline.core.constants import PE
from pipeline.engine import states
from pipeline.engine.api import get_activity_histories, get_status_tree
from pipeline.models import PipelineInstance, PipelineTemplate

logger = logging.getLogger("root")


def count_pipeline_tree_nodes(pipeline_tree):
    gateways_total = len(pipeline_tree["gateways"])
    activities = pipeline_tree["activities"]
    atom_total = len([act for act in activities.values() if act["type"] == PE.ServiceActivity])
    subprocess_total = len([act for act in activities.values() if act["type"] == PE.SubProcess])
    return atom_total, subprocess_total, gateways_total


@receiver(post_save, sender=PipelineTemplate)
def template_post_save_handler(sender, instance, created, **kwargs):
    """
    模板执行保存处理
    :param sender:
    :param instance: 任务实例 Instance.Object对象
    :param created: 是否是创建（可为更新）
    :param kwargs: 参数序列
    :return:
    """
    template = instance
    template_id = template.template_id
    # 删除原先该项模板数据（无论是更新还是创建，都需要重新创建统计数据）
    ComponentInTemplate.objects.filter(template_id=template_id).delete()
    data = template.data
    component_list = []
    # 任务节点引用标准插件统计（包含间接通过子流程引用）
    for act_id, act in data[PE.activities].items():
        # 标准插件节点直接引用
        if act["type"] == PE.ServiceActivity:
            component = ComponentInTemplate(
                component_code=act["component"]["code"],
                template_id=template_id,
                node_id=act_id,
                version=act["component"].get("version", LEGACY_PLUGINS_VERSION),
            )
            component_list.append(component)
        # 子流程节点间接引用
        else:
            components = ComponentInTemplate.objects.filter(template_id=act["template_id"]).values(
                "subprocess_stack", "component_code", "node_id", "version"
            )
            for component_sub in components:
                # 子流程的执行堆栈（子流程的执行过程）
                stack = json.loads(component_sub["subprocess_stack"])
                # 添加节点id
                stack.insert(0, act_id)
                component = ComponentInTemplate(
                    component_code=component_sub["component_code"],
                    template_id=template_id,
                    node_id=component_sub["node_id"],
                    is_sub=True,
                    subprocess_stack=json.dumps(stack),
                    version=component_sub["version"],
                )
                component_list.append(component)
    ComponentInTemplate.objects.bulk_create(component_list)

    # 统计流程标准插件个数，子流程个数，网关个数
    atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(template.data)
    TemplateInPipeline.objects.update_or_create(
        template_id=template_id,
        defaults={"atom_total": atom_total, "subprocess_total": subprocess_total, "gateways_total": gateways_total},
    )


def recursive_collect_components(activities, status_tree, instance_id, stack=None):
    """
    @summary 递归流程树，获取所有执行成功/失败的插件
    @param activities: 当前流程树的任务节点信息
    @param status_tree: 当前流程树的任务节点状态
    @param instance_id: 根流程的示例 instance_id
    @param stack: 子流程堆栈
    """
    if stack is None:
        stack = []
        is_sub = False
    else:
        is_sub = True
    component_list = []
    for act_id, act in activities.items():
        # 只有执行了才会查询到 status，兼容中途撤销的任务
        if act_id in status_tree:
            exec_act = status_tree[act_id]
            # 属于标准插件节点
            if act[PE.type] == PE.ServiceActivity:
                if exec_act["state"] in states.ARCHIVED_STATES:
                    create_kwargs = {
                        "component_code": act["component"]["code"],
                        "instance_id": instance_id,
                        "is_sub": is_sub,
                        "node_id": act_id,
                        "subprocess_stack": json.dumps(stack),
                        "started_time": exec_act["started_time"],
                        "archived_time": exec_act["archived_time"],
                        "elapsed_time": exec_act["elapsed_time"],
                        "is_skip": exec_act["skip"],
                        "is_retry": False,
                        "status": exec_act["state"] == "FINISHED",
                        "version": act["component"].get("version", LEGACY_PLUGINS_VERSION),
                    }
                    component_list.append(ComponentExecuteData(**create_kwargs))
                    if exec_act["retry"] > 0:
                        # 需要通过执行历史获得
                        history_list = get_activity_histories(act_id)
                        for history in history_list:
                            create_kwargs.update(
                                {
                                    "started_time": history["started_time"],
                                    "archived_time": history["archived_time"],
                                    "elapsed_time": history["elapsed_time"],
                                    "is_retry": True,
                                    "is_skip": False,
                                    "status": False,
                                }
                            )
                            component_list.append(ComponentExecuteData(**create_kwargs))
            # 子流程的执行堆栈（子流程的执行过程）
            elif act[PE.type] == PE.SubProcess:
                # 递归子流程树
                sub_activities = act[PE.pipeline][PE.activities]
                # 防止stack共用
                copied_stack = deepcopy(stack)
                copied_stack.insert(0, act_id)
                component_list += recursive_collect_components(
                    sub_activities, exec_act["children"], instance_id, copied_stack
                )
    return component_list


@receiver(post_save, sender=PipelineInstance)
def pipeline_post_save_handler(sender, instance, created, **kwargs):
    instance_id = instance.instance_id
    # 任务必须是执行完成，由 celery 触发
    if not created and (instance.is_finished or instance.is_revoked):
        # 获得任务实例的执行树
        status_tree = get_status_tree(instance_id, 99)
        # 删除原有标准插件数据
        ComponentExecuteData.objects.filter(instance_id=instance_id).delete()
        # 获得任务实例的执行数据
        data = instance.execution_data
        try:
            component_list = recursive_collect_components(data[PE.activities], status_tree["children"], instance_id)
            ComponentExecuteData.objects.bulk_create(component_list)
        except Exception as e:
            logger.error(
                (
                    "pipeline_post_save_handler save ComponentExecuteData[instance_id={instance_id}] "
                    "raise error: {error}"
                ).format(instance_id=instance_id, error=e)
            )

    # 统计流程标准插件个数，子流程个数，网关个数
    try:
        atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(instance.execution_data)
        InstanceInPipeline.objects.update_or_create(
            instance_id=instance_id,
            defaults={"atom_total": atom_total, "subprocess_total": subprocess_total, "gateways_total": gateways_total},
        )
    except Exception as e:
        logger.error(
            (
                "pipeline_post_save_handler save InstanceInPipeline[instance_id={instance_id}] " "raise error: {error}"
            ).format(instance_id=instance_id, error=e)
        )
