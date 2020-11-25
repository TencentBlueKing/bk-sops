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

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Node(models.Model):
    node_id = models.CharField(_('节点ID'), max_length=32)
    node_type = models.CharField(_('节点类型'), max_length=100)
    create_time = models.DateTimeField(_('创建时间'), auto_now_add=True)
    edit_time = models.DateTimeField(_('修改时间'), auto_now=True)

    class Meta:
        # abstract would not be inherited automatically
        abstract = True
        ordering = ['-id']


class NodeAttr(object):

    node_in_template_attr = {}
    node_in_instance_attr = {}

    @classmethod
    def register_template_attr(cls, attr_model):
        cls.node_in_template_attr[attr_model._attr] = attr_model
        return attr_model

    @classmethod
    def register_instance_attr(cls, attr_model):
        cls.node_in_instance_attr[attr_model._attr] = attr_model
        return attr_model

    @classmethod
    def get_nodes_attr(cls, nodes, model_type):
        node_attr_lib = cls.node_in_template_attr if model_type == 'template' else cls.node_in_instance_attr
        for node in nodes:
            if not hasattr(node, 'attrs'):
                setattr(node, 'attrs', {})

        for attr, attr_model in node_attr_lib.items():
            attr_model.objects.batch_update_nodes_attr(nodes, attr)

        nodes_attr = {node.node_id: node.attrs for node in nodes}
        return nodes_attr
