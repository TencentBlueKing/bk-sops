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

from pipeline_web.core.models import NodeInTemplateAttr, NodeInInstanceAttr
from pipeline_web.core.abstract import NodeAttr


class LabelGroup(models.Model):
    code = models.CharField(_('标签分组编码'), max_length=255, db_index=True)
    name = models.CharField(_('标签分组名称'), max_length=255)

    class Meta:
        verbose_name = _('标签分组 LabelGroup')
        verbose_name_plural = _('标签分组 LabelGroup')

    def __unicode__(self):
        return '{}_{}'.format(self.code, self.name)

    def __str__(self):
        return '{}_{}'.format(self.code, self.name)


class Label(models.Model):
    group = models.ForeignKey(LabelGroup)
    code = models.CharField(_('标签编码'), max_length=255, db_index=True)
    name = models.CharField(_('标签名称'), max_length=255)

    class Meta:
        verbose_name = _('标签 Label')
        verbose_name_plural = _('标签 Label')

    def __unicode__(self):
        return '{}_{}'.format(self.code, self.name)

    def __str__(self):
        return '{}_{}'.format(self.code, self.name)

    @property
    def value(self):
        return {'label': self.code, 'group': self.group.code}


class NodeAttrLabelManager(models.Manager):
    def batch_update_nodes_attr(self, nodes, attr):
        nodes_pks = set(nodes.values_list('pk', flat=True))
        nodes_attrs = self.select_related('node').filter(node__pk__in=nodes_pks).prefetch_related('labels')
        nodes_to_attr = {node.node.pk: [label.value for label in node.labels.all()] for node in nodes_attrs}
        for node in nodes:
            node.attrs.update({attr: nodes_to_attr.get(node.pk, [])})


@NodeAttr.register_template_attr
class NodeInTemplateAttrLabel(NodeInTemplateAttr):
    _attr = 'labels'

    labels = models.ManyToManyField(Label, verbose_name=_('节点标签'), blank=True)

    objects = NodeAttrLabelManager()

    class Meta:
        verbose_name = _('流程模板节点标签 NodeInTemplateAttrLabel')
        verbose_name_plural = _('流程模板节点标签 NodeInTemplateAttrLabel')


@NodeAttr.register_instance_attr
class NodeInInstanceAttrLabel(NodeInInstanceAttr):
    _attr = 'labels'

    labels = models.ManyToManyField(Label, verbose_name=_('节点标签'), blank=True)

    objects = NodeAttrLabelManager()

    class Meta:
        verbose_name = _('流程实例节点标签 NodeInInstanceAttrLabel')
        verbose_name_plural = _('流程实例节点标签 NodeInInstanceAttrLabel')
