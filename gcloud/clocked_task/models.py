# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
import logging

from django.db import models, transaction
from django_celery_beat.models import (
    PeriodicTask as DjangoCeleryBeatPeriodicTask,
    ClockedSchedule as DjangoCeleryBeatClockedSchedule,
)

from gcloud.constants import TEMPLATE_SOURCE, PROJECT
from gcloud.utils.unique import uniqid

logger = logging.getLogger("root")


class ClockedTaskManager(models.Manager):
    def create_task(self, **kwargs):
        task_name = kwargs["task_name"]
        plan_start_time = kwargs["plan_start_time"]
        creator = kwargs["creator"]
        project_id = kwargs["project_id"]
        template_id = kwargs["template_id"]
        task_params = kwargs["task_params"]
        template_name = kwargs["template_name"]
        with transaction.atomic():
            clocked, _ = DjangoCeleryBeatClockedSchedule.objects.get_or_create(clocked_time=plan_start_time)
            task = ClockedTask.objects.create(
                project_id=project_id,
                template_id=template_id,
                task_name=task_name,
                template_name=template_name,
                creator=creator,
                plan_start_time=plan_start_time,
                task_params=task_params,
            )
            clocked_task_kwargs = {"clocked_task_id": task.id}
            clocked_task = DjangoCeleryBeatPeriodicTask.objects.create(
                clocked=clocked,
                name=task_name + uniqid(),
                task="gcloud.clocked_task.tasks.clocked_task_start",
                one_off=True,
                kwargs=json.dumps(clocked_task_kwargs),
            )
            task.clocked_task_id = clocked_task.id
            task.save()
        return task

    def fetch_values(self, clocked_task_id, *values):
        qs = self.filter(id=clocked_task_id).values(*values)

        if not qs:
            raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, id))

        return qs.first()


class ClockedTask(models.Model):
    project_id = models.IntegerField(help_text="计划任务所属项目 ID")
    task_id = models.IntegerField(help_text="taskflow 任务 ID", null=True)
    task_name = models.CharField(help_text="任务名称", max_length=128)
    template_id = models.IntegerField(help_text="任务模版 ID")
    template_name = models.CharField(help_text="流程名称", max_length=128)
    template_source = models.CharField(help_text="流程模板来源", max_length=32, choices=TEMPLATE_SOURCE, default=PROJECT)
    clocked_task_id = models.IntegerField(help_text="计划任务 Celery任务 ID", null=True)
    creator = models.CharField(help_text="计划任务创建人", max_length=32)
    plan_start_time = models.DateTimeField(help_text="计划任务启动时间", db_index=True)
    task_params = models.TextField(help_text="任务创建相关数据", null=True)

    objects = ClockedTaskManager()

    class Meta:
        verbose_name = verbose_name_plural = "计划任务"
        ordering = ["-id"]

    def modify_clock(self, new_plan_start_time):
        clocked_task = DjangoCeleryBeatPeriodicTask.objects.get(id=self.clocked_task_id)
        new_clocked, _ = DjangoCeleryBeatClockedSchedule.objects.get_or_create(clocked_time=new_plan_start_time)
        clocked_task.clocked = new_clocked
        clocked_task.save()
        self.plan_start_time = new_plan_start_time
        self.save(update_fields=["plan_start_time"])

    def delete(self):
        DjangoCeleryBeatPeriodicTask.objects.get(id=self.clocked_task_id).delete()
        return super(ClockedTask, self).delete()
