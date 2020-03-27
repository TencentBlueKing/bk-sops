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

from django.db import models


class Node(models.Model):
    node_id = models.CharField(_("节点ID"), max_length=32, unique=True)
    create_time = models.DateTimeField(_("创建时间"), auto_now_add=True)
    edit_time = models.DateTimeField(_("修改时间"), auto_now=True)

    class Meta:
        # abstract would not be inherited automatically
        abstract = True
        ordering = ["-id"]


class NodeInTemplate(Node):
    """
    :summary: 流程模板变动，会导致数据频繁增删改
    """
    template_id = models.CharField(_("所属模板ID"), max_length=32, db_index=True)

    class Meta(Node.Meta):
        verbose_name = _("流程模板节点 NodeInTemplate")
        verbose_name_plural = _("流程模板节点 NodeInTemplate")


class NodeInInstance(Node):
    """
    :summary: 任务一旦创建，该表数据入库后不会变更
    """
    instance_id = models.CharField(_("所属实例ID"), max_length=32, db_index=True)

    class Meta(Node.Meta):
        verbose_name = _("流程实例节点 NodeInInstance")
        verbose_name_plural = _("流程实例节点 NodeInInstance")
