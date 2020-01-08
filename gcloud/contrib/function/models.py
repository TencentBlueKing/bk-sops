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
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from gcloud.core.utils import convert_readable_username
from gcloud.taskflow3.models import TaskFlowInstance


FUNCTION_TASK_STATUS = [
    ('submitted', _(u"未认领")),
    ('claimed', _(u"已认领")),
    ('rejected', _(u"已驳回")),
    ('executed', _(u"已执行")),
    ('finished', _(u"已完成")),
]


class FunctionTask(models.Model):
    """
    职能化认领单
    """
    task = models.ForeignKey(TaskFlowInstance, related_name='function_task', help_text=_(u"职能化单"))
    creator = models.CharField(_(u"提单人"), max_length=32)
    create_time = models.DateTimeField(_(u"提单时间"), auto_now_add=True)
    claimant = models.CharField(_(u"认领人"), max_length=32, blank=True)
    claim_time = models.DateTimeField(_(u"认领时间"), blank=True, null=True)
    rejecter = models.CharField(_(u"驳回人"), max_length=32, blank=True)
    reject_time = models.DateTimeField(_(u"驳回时间"), blank=True, null=True)
    predecessor = models.CharField(_(u"转单人"), max_length=32, blank=True)
    transfer_time = models.DateTimeField(_(u"转单时间"), blank=True, null=True)
    status = models.CharField(_(u"单据状态"), max_length=32, default='submitted', choices=FUNCTION_TASK_STATUS)

    def __unicode__(self):
        return u"%s_%s" % (self.task, self.id)

    class Meta:
        verbose_name = _(u"职能化认领单 FunctionTask")
        verbose_name_plural = _(u"职能化认领单 FunctionTask")
        ordering = ['-id']

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
        if self.status != 'submitted':
            return {'result': False, 'message': 'task has been claimed by others'}
        self.claimant = username
        self.claim_time = timezone.now()
        self.status = 'claimed'
        self.save()
        return {'result': True, 'message': 'success', 'data': {}}

    # TODO 驳回后是否可以修改参数？还是走其他流程
    def reject_task(self, username):
        if self.status != 'submitted':
            return {'result': False, 'message': 'task has been claimed by others'}
        self.rejecter = username
        self.reject_time = timezone.now()
        self.status = 'rejected'
        return {'result': True, 'message': 'success', 'data': {}}

    def transfer_task(self, username, claimant):
        if self.status not in ['claimed', 'executed']:
            return {'result': False, 'message': 'task with status:%s cannot be transferred' % self.status}
        if self.claimant != username:
            return {'result': False, 'message': 'task can only be transferred by claimant'}
        self.predecessor = self.claimant
        self.transfer_time = timezone.now()
        self.claimant = claimant
        self.claim_time = timezone.now()
        self.save()
        return {'result': True, 'message': 'success', 'data': {}}
