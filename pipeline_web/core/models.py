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

from django.db import models, transaction
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from pipeline_web.constants import PWE
from pipeline_web.core.abstract import Node
from pipeline_web.core.signals import (
    node_in_template_post_save,
    node_in_template_delete,
    node_in_instance_post_save
)
from pipeline_web.parser.format import get_all_nodes


class NodeInTemplateManager(models.Manager):

    def create_nodes_in_template(self, pipeline_template, pipeline_tree):
        new_nodes = get_all_nodes(pipeline_tree)
        nodes_info = []
        for node_id, node in new_nodes.items():
            nodes_info.append(self.model(
                node_id=node_id,
                node_type=node[PWE.type],
                template_id=pipeline_template.template_id,
                version=pipeline_template.version
            ))
        self.model.objects.bulk_create(nodes_info)
        # send signal
        node_objs = self.model.objects.filter(template_id=pipeline_template.template_id,
                                              version=pipeline_template.version)
        for node_obj in node_objs:
            node_in_template_post_save.send(sender=self.model, node_obj=node_obj, node_info=new_nodes[node_obj.node_id])

    @transaction.atomic()
    def update_nodes_in_template(self, pipeline_template, pipeline_tree):
        nodes = self.select_for_update().filter(template_id=pipeline_template.template_id,
                                                version=pipeline_template.version)
        if not nodes.exists():
            self.create_nodes_in_template(pipeline_template, pipeline_tree)

        # 更新当前版本的流程模板
        new_nodes = get_all_nodes(pipeline_tree)
        nodes_for_delete = nodes.exclude(node_id__in=set(new_nodes.keys()))
        nodes_for_update = nodes.filter(node_id__in=set(new_nodes.keys()))
        nodes_for_update_ids = set(nodes_for_update.values_list('node_id', flat=True))
        nodes_for_add = []
        for node_id, node in new_nodes.items():
            if node_id not in nodes_for_update_ids:
                nodes_for_add.append(self.model(
                    node_id=node_id,
                    node_type=node[PWE.type],
                    template_id=pipeline_template.template_id,
                    version=pipeline_template.version
                ))
        # send signal
        for node_obj in nodes_for_delete:
            node_in_template_delete.send(sender=self.model, node_obj=node_obj)
        nodes_for_delete.delete()

        nodes_for_update.update(edit_time=now())
        self.bulk_create(nodes_for_add)
        # send signal
        node_objs = self.filter(template_id=pipeline_template.template_id,
                                version=pipeline_template.version)
        for node_obj in node_objs:
            node_in_template_post_save.send(sender=self.model, node_obj=node_obj, node_info=new_nodes[node_obj.node_id])

    def nodes_in_template(self, template_id, version):
        return self.filter(template_id=template_id, version=version)


class NodeInTemplate(Node):
    """
    :summary: 流程模板变动，会导致数据频繁增删改
    """
    template_id = models.CharField(_('所属模板ID'), max_length=32, db_index=True)
    version = models.CharField(_('所属模板版本'), max_length=32)

    objects = NodeInTemplateManager()

    class Meta(Node.Meta):
        verbose_name = _('流程模板节点 NodeInTemplate')
        verbose_name_plural = _('流程模板节点 NodeInTemplate')
        unique_together = ['node_id', 'template_id', 'version']
        index_together = ['template_id', 'version']


class NodeInTemplateAttr(models.Model):
    node = models.ForeignKey(NodeInTemplate, verbose_name=_('流程模板节点'))

    class Meta:
        # abstract would not be inherited automatically
        abstract = True
        ordering = ['-id']


class NodeInInstanceManager(models.Manager):

    def create_nodes_in_instance(self, pipeline_instance, pipeline_tree):
        new_nodes = get_all_nodes(pipeline_tree)
        nodes_info = []
        for node_id, node in new_nodes.items():
            nodes_info.append(self.model(
                node_id=node_id,
                node_type=node[PWE.type],
                instance_id=pipeline_instance.instance_id
            ))
        self.model.objects.bulk_create(nodes_info)
        # send signal
        node_objs = self.filter(instance_id=pipeline_instance.instance_id)
        for node_obj in node_objs:
            node_in_instance_post_save.send(sender=self.model, node_obj=node_obj, node_info=new_nodes[node_obj.node_id])

    def nodes_in_instance(self, instance_id):
        return self.filter(instance_id=instance_id)


class NodeInInstance(Node):
    """
    :summary: 任务一旦创建，该表数据入库后不会变更
    """
    instance_id = models.CharField(_('所属实例ID'), max_length=32, db_index=True)

    objects = NodeInInstanceManager()

    class Meta(Node.Meta):
        verbose_name = _('流程实例节点 NodeInInstance')
        verbose_name_plural = _('流程实例节点 NodeInInstance')
        unique_together = ['node_id', 'instance_id']


class NodeInInstanceAttr(models.Model):
    node = models.ForeignKey(NodeInInstance, verbose_name=_('流程实例节点'))

    class Meta:
        # abstract would not be inherited automatically
        abstract = True
        ordering = ['-id']
