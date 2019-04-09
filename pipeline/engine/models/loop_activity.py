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
from django.utils.translation import ugettext_lazy as _

from pipeline.engine.models.fields import IOField
from pipeline.engine.models.core import HistoryData, Status


class LoopActivityScheduleHistoryManager(models.Manager):
    def record(self, loop_service_act, schedule_service):
        return self.create(
            schedule_id=schedule_service.id,
            activity_id=schedule_service.activity_id,
            schedule_times=schedule_service.schedule_times,
            wait_callback=schedule_service.wait_callback,
            callback_data=schedule_service.callback_data,
            version=schedule_service.version,
            current_loop=loop_service_act.current_loop
        )


class LoopActivityScheduleHistory(models.Model):
    schedule_id = models.CharField(_(u"ID 节点ID+version"), max_length=64)
    activity_id = models.CharField(_(u"节点 ID"), max_length=32, db_index=True)
    schedule_times = models.IntegerField(_(u"被调度次数"), default=0)
    wait_callback = models.BooleanField(_(u"是否是回调型调度"), default=False)
    callback_data = IOField(verbose_name=_(u"回调数据"), default=None)
    version = models.CharField(_(u"Activity 的版本"), max_length=32, db_index=True)
    current_loop = models.PositiveIntegerField(_(u"当前调度所处的循环计数"))

    objects = LoopActivityScheduleHistoryManager()


class LoopActivityHistoryManager(models.Manager):

    def record(self, loop_service_act, schedule=None):
        data = HistoryData.objects.create(inputs=loop_service_act.data.get_inputs(),
                                          outputs=loop_service_act.data.get_outputs(),
                                          ex_data=loop_service_act.data.get_one_of_outputs('ex_data', ''))
        status = Status.objects.get(id=loop_service_act.id)

        return self.create(identifier=loop_service_act.id,
                           loop=loop_service_act.current_loop,
                           started_time=status.started_time,
                           archived_time=status.archived_time,
                           data=data,
                           state=status.state,
                           schedule=schedule
                           )


class LoopActivityHistory(models.Model):
    identifier = models.CharField(_(u"节点 id"), max_length=32, db_index=True)
    loop = models.PositiveIntegerField(_(u"本次循环计数"))
    started_time = models.DateTimeField(_(u"开始时间"))
    archived_time = models.DateTimeField(_(u"结束时间"))
    data = models.ForeignKey(HistoryData)
    state = models.CharField(_(u"执行状态"), max_length=10)
    schedule = models.ForeignKey(LoopActivityScheduleHistory, null=True)

    objects = LoopActivityHistoryManager()


class LoopActivityStatusManager(models.Manager):
    def refresh_status(self, loop_service_act):
        return self.update_or_create(identifier=loop_service_act.id,
                                     defaults={
                                         'current_loop': loop_service_act.current_loop,
                                         'actual_loop': loop_service_act.actual_loop,
                                         'loop_times': loop_service_act.loop_times
                                     })

    def sync_status(self, loop_service_act):
        status, created = self.get_or_create(identifier=loop_service_act.id,
                                             defaults={
                                                 'current_loop': loop_service_act.current_loop,
                                                 'actual_loop': loop_service_act.actual_loop,
                                                 'loop_times': loop_service_act.loop_times
                                             })
        if not created:
            loop_service_act.current_loop = status.current_loop
            loop_service_act.actual_loop = status.actual_loop
            loop_service_act.loop_times = status.loop_times


class LoopActivityStatus(models.Model):
    identifier = models.CharField(_(u"节点 id"), max_length=32, db_index=True)
    current_loop = models.PositiveIntegerField(_(u"本次循环次数"))
    actual_loop = models.PositiveIntegerField(_(u"实际循环次数"))
    loop_times = models.PositiveIntegerField(_(u"所需循环次数"))

    objects = LoopActivityStatusManager()
