# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import json
from copy import deepcopy

from django.db.models.signals import post_save
from django.dispatch import receiver

from pipeline.engine.api import get_status_tree, get_activity_histories
from pipeline.models import PipelineTemplate, PipelineInstance
from pipeline.contrib.statistics.models import (
    ComponentInTemplate,
    ComponentExecuteData,
    TemplateInPipeline, InstanceInPipeline)
from pipeline.core.constants import PE

logger = logging.getLogger('root')


def count_pipeline_tree_nodes(pipeline_tree):
    gateways_total = len(pipeline_tree["gateways"])
    activities = pipeline_tree["activities"]
    atom_total = len([act for act in activities.values() if act['type'] == PE.ServiceActivity])
    subprocess_total = len([act for act in activities.values() if act['type'] == PE.SubProcess])
    return atom_total, subprocess_total, gateways_total


@receiver(post_save, sender=PipelineTemplate)
def template_post_save_handler(sender, instance, created, **kwargs):
    """
    模板执行保存处理
    :param sender:
    :param instance: 任务实例 Instance.Ojbect对象
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
        if act['type'] == PE.ServiceActivity:
            component = ComponentInTemplate(
                component_code=act['component']['code'],
                template_id=template_id,
                node_id=act_id,
            )
            component_list.append(component)
        # 子流程节点间接引用
        else:
            print act
            print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
            components = ComponentInTemplate.objects.filter(template_id=act['template_id']).values('subprocess_stack',
                                                                                                   'component_code',
                                                                                                   'node_id')
            for component_sub in components:
                # 子流程的执行堆栈（子流程的执行过程）
                stack = json.loads(component_sub['subprocess_stack'])
                # 添加节点id
                stack.insert(0, act_id)
                component = ComponentInTemplate(
                    component_code=component_sub['component_code'],
                    template_id=template_id,
                    node_id=component_sub['node_id'],
                    is_sub=True,
                    subprocess_stack=json.dumps(stack)
                )
                component_list.append(component)
    ComponentInTemplate.objects.bulk_create(component_list)

    # 统计流程标准插件个数，子流程个数，网关个数
    atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(template.data)
    TemplateInPipeline.objects.update_or_create(template_id=template_id,
                                                defaults={
                                                    'atom_total': atom_total,
                                                    'subprocess_total': subprocess_total,
                                                    'gateways_total': gateways_total
                                                })


def recursive_subprocess_tree(children_tree_dict, act_id, instance_id, component_list, activities=None, stack=None):
    """
    @summary 递归子流程树
    :param children_tree_dict: 执行树的 children 节点
    :param act_id: 上一个流程 id
    :param instance_id: 实例 id
    :param activities: 子流程模板中标准插件信息
    :param stack: 子流程堆栈信息
    :param component_list: 存放执行的标准插件数据，用于批量插入
    :return:
    """
    if stack is None:
        stack = []
    # 防止stack共用
    copied_stack = deepcopy(stack)
    # 插入上一个模板的id
    copied_stack.insert(0, act_id)
    for act_id, act in activities.items():
        is_skip = False
        is_retry = False
        # 属于标准插件节点
        if act["type"] == PE.ServiceActivity:
            # 标准插件重试
            if children_tree_dict[act_id]["retry"] > 0:
                # 需要通过执行历史获得
                history_list = get_activity_histories(act_id)
                for history in history_list:
                    started_time = history["started_time"]
                    archived_time = history["archived_time"]
                    elapsed_time = history["elapsed_time"]
                    is_retry = True
            # 标准插件未重试
            else:
                started_time = children_tree_dict[act_id]["started_time"]
                archived_time = children_tree_dict[act_id]["archived_time"]
                elapsed_time = children_tree_dict[act_id]["elapsed_time"]
                is_skip = children_tree_dict[act_id]["skip"]
            status = True if children_tree_dict[act_id]["state"] == "FINISHED" else False
            # 创建对象
            component = ComponentExecuteData(
                component_code=act['component']['code'],
                instance_id=instance_id,
                node_id=act_id,
                is_sub=True,
                subprocess_stack=json.dumps(copied_stack),
                started_time=started_time,
                archived_time=archived_time,
                elapsed_time=elapsed_time,
                status=status,
                is_skip=is_skip,
                is_retry=is_retry
            )
            component_list.append(component)
        # 子流程的执行堆栈（子流程的执行过程）
        # 添加节点id
        elif act["type"] == PE.SubProcess:
            # 重新子流程获取 children 节点的信息
            other_children_tree_dict = children_tree_dict[act_id]["children"]
            # 递归子流程树
            component_list = recursive_subprocess_tree(other_children_tree_dict,
                                                       act_id,
                                                       instance_id,
                                                       component_list,
                                                       act[PE.pipeline][PE.activities],
                                                       copied_stack)
    return component_list


@receiver(post_save, sender=PipelineInstance)
def pipeline_post_save_handler(sender, instance, created, **kwargs):
    instance_id = instance.instance_id
    # 任务必须是执行完成，由 celery 触发
    if not created and instance.is_finished:
        # 获得任务实例的执行树
        status_tree = get_status_tree(instance_id, 99)
        # 删除原有标准插件数据
        ComponentExecuteData.objects.filter(instance_id=instance_id).delete()
        # 获得任务实例的执行数据
        data = instance.execution_data
        component_list = []
        # act_id 节点 act 标准插件数据
        for act_id, act in data[PE.activities].items():
            is_retry = False
            if act['type'] == PE.ServiceActivity:
                # 标准插件重试
                status_act = status_tree["children"].get(act_id)
                if status_act is None:
                    continue
                if status_act["retry"] > 0:
                    # 需要通过执行历史获得
                    history_list = get_activity_histories(act_id)
                    for history in history_list:
                        start_time = history["started_time"]
                        archived_time = history["archived_time"]
                        elapsed_time = history["elapsed_time"]
                        is_retry = True
                else:
                    # 标准插件没有重试
                    # 执行树的相关内容
                    start_time = status_tree["started_time"]
                    archived_time = status_tree["archived_time"]
                    elapsed_time = status_tree["elapsed_time"]
                status = True if status_tree["state"] == "FINISHED" else False
                # 创建对象
                component = ComponentExecuteData(
                    component_code=act['component']['code'],
                    instance_id=instance_id,
                    node_id=act_id,
                    started_time=start_time,
                    archived_time=archived_time,
                    elapsed_time=elapsed_time,
                    status=status,
                    is_skip=status_tree["skip"],
                    is_retry=is_retry
                )
                component_list.append(component)
            else:
                # 传递流程数据
                children_tree_dict = status_tree["children"][act_id]["children"]
                component_list = recursive_subprocess_tree(children_tree_dict,
                                                           act_id,
                                                           instance_id,
                                                           component_list,
                                                           act[PE.pipeline][PE.activities])
        ComponentExecuteData.objects.bulk_create(component_list)

    # 统计流程标准插件个数，子流程个数，网关个数
    atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(instance.execution_data)
    InstanceInPipeline.objects.update_or_create(instance_id=instance_id,
                                                defaults={
                                                    'atom_total': atom_total,
                                                    'subprocess_total': subprocess_total,
                                                    'gateways_total': gateways_total
                                                })
