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
from django.utils import timezone

from gcloud.core.utils import convert_readable_username

RUNNING = 'RUNNING'
SUCCEEDED = 'SUCCEEDED'
FAILED = 'FAILED'

SYNC_TASK_STATUS = [
    (RUNNING, _(u"执行中")),
    (SUCCEEDED, _(u"成功")),
    (FAILED, _(u"失败"))
]

SYNC_TASK_CREATED = [
    ('manual', _(u"手动触发")),
    ('auto', _(u"部署自动触发"))
]


class SyncTask(models.Model):
    creator = models.CharField(_(u"执行者"), max_length=32, blank=True)
    create_method = models.CharField(_(u"创建方式"), max_length=32, default='manual', choices=SYNC_TASK_CREATED)
    start_time = models.DateTimeField(_(u"启动时间"), auto_now_add=True)
    finish_time = models.DateTimeField(_(u"结束时间"), null=True, blank=True)
    status = models.CharField(_(u"同步状态"), max_length=32, default=RUNNING, choices=SYNC_TASK_STATUS)
    details = models.TextField(_(u"同步详情信息"), blank=True)

    class Meta:
        verbose_name = _(u"远程包源同步任务 SyncTask")
        verbose_name_plural = _(u"远程包源同步任务 SyncTask")
        ordering = ['-id']

    @property
    def creator_name(self):
        return convert_readable_username(self.creator)

    @property
    def status_display(self):
        return self.get_status_display()

    def finish_task(self, status, details=None):
        self.status = status
        self.finish_time = timezone.now()
        if details:
            self.details = details
        self.save()
