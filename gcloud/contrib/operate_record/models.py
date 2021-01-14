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

from .constants import OPERATE_TYPE, OPERATE_SOURCE


class BaseOperateRecord(models.Model):
    instance_id = models.IntegerField(_("记录对象实例ID"))
    name = models.CharField(_("记录对象名称"), max_length=255)
    project = models.CharField(_("所属项目"), max_length=128, blank=True, default="")
    project_id = models.IntegerField(_("所属项目id"), blank=True, default=-1)
    operator = models.CharField(_("操作人"), max_length=128)
    operate_date = models.DateTimeField(_("操作时间"), auto_now_add=True)
    operate_type = models.CharField(_("操作类型"), choices=OPERATE_TYPE, max_length=64)
    operate_source = models.CharField(_("操作来源"), choices=OPERATE_SOURCE, max_length=64)

    class Meta:
        abstract = True


class TaskOperateRecord(BaseOperateRecord):
    """任务操作记录"""

    node_id = models.CharField(_("任务实例节点ID"), max_length=255, blank=True, default="")
    node_name = models.CharField(_("任务实例节点名称"), max_length=255, blank=True, default="")

    class Meta:
        verbose_name = _("任务操作记录")
        verbose_name_plural = _("任务操作记录")
        indexes = [models.Index(fields=["instance_id", "node_id"])]

    def __str__(self):
        return "{}_{}_{}_{}".format(self.operate_date, self.operator, self.operate_type, self.instance_id)


class TemplateOperateRecord(BaseOperateRecord):
    """模版操作记录"""

    pass

    class Meta:
        verbose_name = _("模版操作记录")
        verbose_name_plural = _("模版操作记录")
        indexes = [models.Index(fields=["instance_id"])]

    def __str__(self):
        return "{}_{}_{}_{}".format(self.operate_date, self.operator, self.operate_type, self.instance_id)
