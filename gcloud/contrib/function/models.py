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

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from gcloud.core.utils import convert_readable_username
from gcloud.taskflow3.models import TaskFlowInstance

logger = logging.getLogger("root")


FUNCTION_TASK_STATUS = [
    ("submitted", _("未认领")),
    ("claimed", _("已认领")),
    ("rejected", _("已驳回")),
    ("executed", _("已执行")),
    ("finished", _("已完成")),
]


class FunctionTask(models.Model):
    """
    职能化认领单
    """

    task = models.ForeignKey(
        TaskFlowInstance, related_name="function_task", help_text=_("职能化单"), on_delete=models.CASCADE
    )
    creator = models.CharField(_("提单人"), max_length=32)
    create_time = models.DateTimeField(_("提单时间"), auto_now_add=True)
    claimant = models.CharField(_("认领人"), max_length=32, blank=True, db_index=True)
    claim_time = models.DateTimeField(_("认领时间"), blank=True, null=True)
    rejecter = models.CharField(_("驳回人"), max_length=32, blank=True)
    reject_time = models.DateTimeField(_("驳回时间"), blank=True, null=True)
    predecessor = models.CharField(_("转单人"), max_length=32, blank=True)
    transfer_time = models.DateTimeField(_("转单时间"), blank=True, null=True)
    status = models.CharField(_("单据状态"), max_length=32, default="submitted", choices=FUNCTION_TASK_STATUS)

    def __unicode__(self):
        return "%s_%s" % (self.task, self.id)

    class Meta:
        verbose_name = _("职能化认领单 FunctionTask")
        verbose_name_plural = _("职能化认领单 FunctionTask")
        ordering = ["-id"]

    @property
    def name(self):
        return self.task.name

    @property
    def status_name(self):
        return self.get_status_display()

    @property
    def creator_name(self):
        return convert_readable_username(self.creator)

    @property
    def editor_name(self):
        return convert_readable_username(self.editor)

    def claim_task(self, username):
        if self.status != "submitted":
            message = _(f"任务认领失败: 任务已被他人认领, 请在任务列表查看[{username}] | claim_task")
            logger.error(message)
            return {"result": False, "message": message}
        self.claimant = username
        self.claim_time = timezone.now()
        self.status = "claimed"
        self.save()
        return {"result": True, "message": "success", "data": {}}

    # TODO 驳回后是否可以修改参数？还是走其他流程
    def reject_task(self, username):
        if self.status != "submitted":
            message = _(f"任务认领失败: 任务已被他人认领, 请在任务列表查看[{username}] | reject_task")
            logger.error(message)
            return {"result": False, "message": message}
        self.rejecter = username
        self.reject_time = timezone.now()
        self.status = "rejected"
        return {"result": True, "message": "success", "data": {}}

    def transfer_task(self, username, claimant):
        if self.status not in ["claimed", "executed"]:
            message = _(f"任务转交失败: 仅[{self.status}]的任务才可转交, 请检查任务状态 | transfer_task")
            logger.error(message)
            return {"result": False, "message": message}
        if self.claimant != username:
            message = _(f"任务转交失败: 仅[{claimant}]才可转交任务, 请检查是否已认领该任务")
            logger.error(message)
            return {"result": False, "message": message}
        self.predecessor = self.claimant
        self.transfer_time = timezone.now()
        self.claimant = claimant
        self.claim_time = timezone.now()
        self.save()
        return {"result": True, "message": "success", "data": {}}
