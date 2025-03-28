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
import json
import logging

from django.apps import apps
from django.db import models, transaction
from django_celery_beat.models import ClockedSchedule as DjangoCeleryBeatClockedSchedule
from django_celery_beat.models import PeriodicTask as DjangoCeleryBeatPeriodicTask

from gcloud.constants import CLOCKED_TASK_NOT_STARTED, CLOCKED_TASK_STATE, PROJECT, TEMPLATE_SOURCE
from gcloud.core.models import Project, StaffGroupSet
from gcloud.shortcuts.cmdb import get_business_group_members
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
        notify_type = kwargs.get("notify_type", "[]")
        notify_receivers = kwargs.get("notify_receivers", "{}")

        optional_keys = ["editor", "edit_time", "create_time"]
        # 过滤 optional_keys 中不存在于 kwargs 的属性
        extra_data = {key: kwargs[key] for key in filter(lambda x: x in kwargs, optional_keys)}

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
                notify_type=notify_type,
                notify_receivers=notify_receivers,
                **extra_data,
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
    create_time = models.DateTimeField("创建任务时间", null=True, auto_now_add=True)
    editor = models.CharField("更新者", max_length=32, default="")
    edit_time = models.DateTimeField("更新任务时间", null=True, auto_now=True)
    plan_start_time = models.DateTimeField(help_text="计划任务启动时间", db_index=True)
    task_params = models.TextField(help_text="任务创建相关数据", null=True)
    notify_type = models.CharField(help_text="计划任务事件通知方式", max_length=128, default="[]")
    # 形如 json.dumps({'receiver_group': ['Maintainers'], 'more_receiver': 'username1,username2'})
    notify_receivers = models.TextField(help_text="计划任务事件通知人", default="{}")
    state = models.CharField(
        help_text="计划任务状态", max_length=64, choices=CLOCKED_TASK_STATE, default=CLOCKED_TASK_NOT_STARTED
    )

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

    def get_notify_type(self):
        # 如果没有配置，则使用模版中的配置
        if self.notify_type == "[]":
            template_cls = (
                apps.get_model("tasktmpl3", "TaskTemplate")
                if self.template_source == PROJECT
                else apps.get_model("template", "CommonTemplate")
            )
            template = template_cls.objects.filter(id=self.template_id).only("notify_type").first()
            notify_type = json.loads(template.notify_type)
        else:
            notify_type = json.loads(self.notify_type)
        logger.info(f"[clocked_task get_notify_type] success: {notify_type}")
        return (
            notify_type
            if isinstance(notify_type, dict)
            else {"success": notify_type, "fail": notify_type, "pending_processing": notify_type}
        )

    def get_stakeholders(self):
        # 如果没有配置，则使用模版中的配置
        if self.notify_receivers == "{}":
            template_cls = (
                apps.get_model("tasktmpl3", "TaskTemplate")
                if self.template_source == PROJECT
                else apps.get_model("template", "CommonTemplate")
            )
            template = template_cls.objects.filter(id=self.template_id).only("notify_receivers").first()
            notify_receivers = json.loads(template.notify_receivers)
        else:
            notify_receivers = json.loads(self.notify_receivers)
        logger.info(f"[clocked_task get_stakeholders] success: {notify_receivers}")
        receiver_group = notify_receivers.get("receiver_group", [])
        receivers = [self.creator]
        proj = Project.objects.get(id=self.project_id)
        if proj.from_cmdb:
            cc_group_members = get_business_group_members(proj.tenant_id, proj.bk_biz_id, receiver_group)
            receivers.extend(cc_group_members)

        members = list(
            StaffGroupSet.objects.filter(
                project_id=self.project_id,
                is_deleted=False,
                id__in=[group for group in receiver_group if isinstance(group, int)],
            ).values_list("members", flat=True)
        )
        if members:
            members = ",".join(members).split(",")
            receivers.extend(members)

        receivers = set(receivers).discard(self.creator)
        receivers = [] if not receivers else list(receivers)

        return [self.creator] + receivers
