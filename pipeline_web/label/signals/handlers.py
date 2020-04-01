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


def node_in_template_save_handle(sender, node_obj, node_info, **kwargs):
    try:
        node_attr_label = NodeInTemplateAttrLabel.objects.get(node=node_obj)
    except NodeInTemplateAttrLabel.DoesNotExist:
        node_attr_label = NodeInTemplateAttrLabel.objects.create(node=node_obj)
    else:
        node_attr_label.labels.clear()

    for label_info in node_info.get('labels', []):
        try:
            label_obj = Label.objects.get(code=label_info['label'], group__code=label_info['group'])
        except Label.DoesNotExist:
            logger.warning('Label[code={label}, group_code={group_code}] does not exist'.format(
                label=label_info['label'], group_code=label_info['group']))
        else:
            node_attr_label.labels.add(label_obj)


def node_in_template_delete_handle(sender, node_obj, **kwargs):
    NodeInTemplateAttrLabel.objects.filter(node=node_obj).delete()


def node_in_instance_save_handle(sender, node_obj, node_info, **kwargs):
    try:
        node_attr_label = NodeInInstanceAttrLabel.objects.get(node=node_obj)
    except NodeInInstanceAttrLabel.DoesNotExist:
        node_attr_label = NodeInInstanceAttrLabel.objects.create(node=node_obj)
    else:
        node_attr_label.labels.clear()

    for label_info in node_info.get('labels', []):
        try:
            label_obj = Label.objects.get(code=label_info['label'], group__code=label_info['group'])
        except Label.DoesNotExist:
            logger.warning('Label[code={label}, group_code={group_code}] does not exist'.format(
                label=label_info['label'], group_code=label_info['group']))
        else:
            node_attr_label.labels.add(label_obj)
