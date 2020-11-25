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

from pipeline_web.label.models import (
    Label,
    NodeInTemplateAttrLabel,
    NodeInInstanceAttrLabel
)

logger = logging.getLogger('root')


def node_in_save(node_in_model, nodes_objs, nodes_info):
    nodes_pk_to_node_id = {node.pk: node.node_id for node in nodes_objs}
    # update when exist
    nodes_attr_label_to_update = node_in_model.objects.select_related('node').filter(
        node__pk__in=set(nodes_pk_to_node_id.keys()))
    for node_attr_label in nodes_attr_label_to_update:
        node_attr_label.labels.clear()

    # add when not exist
    nodes_obj_to_add = nodes_objs.exclude(pk__in=set(nodes_attr_label_to_update.values_list('node__pk', flat=True)))
    nodes_attr_label_to_add = [node_in_model(node=node_obj) for node_obj in nodes_obj_to_add]
    node_in_model.objects.bulk_create(nodes_attr_label_to_add)

    nodes_attr_label_all = node_in_model.objects.select_related('node').filter(
        node__pk__in=set(nodes_pk_to_node_id.keys()))
    for node_attr_label in nodes_attr_label_all:
        node_info = nodes_info[node_attr_label.node.node_id]
        for label_info in node_info.get('labels', []):
            try:
                label_obj = Label.objects.get(code=label_info['label'], group__code=label_info['group'])
            except Label.DoesNotExist:
                logger.warning('Label[code={label}, group_code={group_code}] does not exist'.format(
                    label=label_info['label'], group_code=label_info['group']))
            else:
                node_attr_label.labels.add(label_obj)


def node_in_template_save_handle(sender, nodes_objs, nodes_info, **kwargs):
    node_in_save(NodeInTemplateAttrLabel, nodes_objs, nodes_info)


def node_in_template_delete_handle(sender, nodes_objs, **kwargs):
    NodeInTemplateAttrLabel.objects.filter(node__in=nodes_objs).delete()


def node_in_instance_save_handle(sender, nodes_objs, nodes_info, **kwargs):
    node_in_save(NodeInInstanceAttrLabel, nodes_objs, nodes_info)
