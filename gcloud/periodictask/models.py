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

import ujson as json
from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from pipeline.contrib.periodic_task.models import BAMBOO_ENGINE_TRIGGER_TASK
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from pipeline.contrib.periodic_task.models import PeriodicTaskHistory as PipelinePeriodicTaskHistory
from pipeline.models import PipelineTemplate, Snapshot

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import COMMON, NON_COMMON_TEMPLATE_TYPES, PROJECT, TEMPLATE_SOURCE
from gcloud.core.models import EngineConfig, Project, StaffGroupSet
from gcloud.periodictask.exceptions import InvalidOperationException
from gcloud.shortcuts.cmdb import get_business_group_members
from gcloud.taskflow3.models import TaskConfig, TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.utils import inject_original_template_info, inject_template_node_id
from gcloud.utils.strings import django_celery_beat_cron_time_format_fit
from pipeline_plugins.components.collections.subprocess_plugin.converter import PipelineTreeSubprocessConverter
from pipeline_web.wrapper import PipelineTemplateWebWrapper

logger = logging.getLogger("root")


# Create your models here.


class PeriodicTaskManager(models.Manager):
    def fetch_values(self, id, *values):
        qs = self.filter(id=id).values(*values)

        if not qs:
            raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, id))

        return qs.first()

    def creator_for(self, id):
        qs = self.filter(id=id).values("creator")

        if not qs:
            raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, id))

        return qs.first()["creator"]

    def create(self, **kwargs):
        template_source = kwargs.get("template_source", PROJECT)
        task = self.create_or_update_pipeline_task(
            project=kwargs["project"],
            template=kwargs["template"],
            name=kwargs["name"],
            cron=kwargs["cron"],
            pipeline_tree=kwargs["pipeline_tree"],
            creator=kwargs["creator"],
            template_source=template_source,
        )
        create_params = {
            "project": kwargs["project"],
            "task": task,
            "template_id": kwargs["template"].id,
            "template_source": template_source,
            "template_version": kwargs["template_version"],
            "creator": kwargs["creator"],
        }
        if "template_scheme_ids" in kwargs:
            create_params["template_scheme_ids"] = kwargs["template_scheme_ids"]
        return super(PeriodicTaskManager, self).create(**create_params)

    def update(self, instance, **kwargs):
        template_source = kwargs.get("template_source", PROJECT)
        pipeline_periodic_task = instance.task
        with transaction.atomic():
            self.create_or_update_pipeline_task(
                project=kwargs["project"],
                template=kwargs["template"],
                name=kwargs["name"],
                cron=kwargs["cron"],
                pipeline_tree=kwargs["pipeline_tree"],
                creator=pipeline_periodic_task.creator,
                template_source=template_source,
                is_create=False,
                instance=pipeline_periodic_task,
            )
            instance.project = kwargs["project"]
            instance.template_id = kwargs["template"].id
            instance.template_source = template_source
            instance.template_version = kwargs["template_version"]
            instance.editor = kwargs["editor"]
            if "template_scheme_ids" in kwargs:
                instance.template_scheme_ids = kwargs["template_scheme_ids"]
            instance.save()
        return instance

    @staticmethod
    def create_or_update_pipeline_task(
        project, template, name, cron, pipeline_tree, creator, template_source=PROJECT, is_create=True, *args, **kwargs
    ):
        if template_source == PROJECT and template.project.id != project.id:
            raise InvalidOperationException("template %s do not belong to project[%s]" % (template.id, project.name))

        independent_subprocess = TaskConfig.objects.enable_independent_subprocess(project.id, template.id)
        if independent_subprocess:
            converter = PipelineTreeSubprocessConverter(pipeline_tree)
            converter.pre_convert()
            pipeline_tree = converter.pipeline_tree

        PipelineTemplateWebWrapper.unfold_subprocess(pipeline_tree, template.__class__)
        inject_template_node_id(pipeline_tree)

        PipelineTemplate.objects.replace_id(pipeline_tree)
        inject_original_template_info(pipeline_tree)
        if independent_subprocess:
            converter = PipelineTreeSubprocessConverter(pipeline_tree)
            converter.convert()

        extra_info = {
            "project_id": project.id,
            "category": template.category,
            "template_id": template.pipeline_template.template_id,
            "template_source": template_source,
            "template_num_id": template.id,
            "pipeline_formator": "pipeline_web.parser.format.format_web_data_to_pipeline",
            "engine_ver": EngineConfig.ENGINE_VER_V2,
        }
        queue = settings.PERIODIC_TASK_QUEUE_NAME_V2
        trigger_task = BAMBOO_ENGINE_TRIGGER_TASK

        if is_create:
            return PipelinePeriodicTask.objects.create_task(
                name=name,
                template=template.pipeline_template,
                cron=cron,
                data=pipeline_tree,
                creator=creator,
                timezone=project.time_zone,
                extra_info=extra_info,
                spread=True,
                queue=queue,
                trigger_task=trigger_task,
            )
        instance = kwargs["instance"]
        snapshot = Snapshot.objects.create_snapshot(pipeline_tree)
        instance.name = name
        instance.template = template.pipeline_template
        instance.snapshot = snapshot
        instance.extra_info = extra_info
        instance.modify_cron(cron, project.time_zone, must_disabled=False)
        instance.queue = queue
        instance.celery_task.task = trigger_task
        instance.save()
        instance.celery_task.save(update_fields=["task"])
        return instance


class PeriodicTask(models.Model):
    project = models.ForeignKey(Project, verbose_name=_("所属项目"), null=True, blank=True, on_delete=models.SET_NULL)
    task = models.ForeignKey(PipelinePeriodicTask, verbose_name=_("pipeline 层周期任务"), on_delete=models.CASCADE)
    template_id = models.CharField(_("创建任务所用的模板ID"), max_length=255)
    template_source = models.CharField(_("流程模板来源"), max_length=32, choices=TEMPLATE_SOURCE, default=PROJECT)
    template_version = models.CharField(_("创建任务时模版 version"), max_length=255, null=True, blank=True)
    template_scheme_ids = models.TextField(_("创建任务时模版执行方案id"), null=True, blank=True)
    creator = models.CharField(_("创建者"), max_length=32, default="")
    create_time = models.DateTimeField(_("创建任务时间"), null=True, auto_now_add=True)
    editor = models.CharField(_("更新者"), max_length=32, default="")
    edit_time = models.DateTimeField(_("更新任务时间"), null=True, auto_now=True)

    objects = PeriodicTaskManager()

    class Meta:
        verbose_name = _("周期任务 PeriodicTask")
        verbose_name_plural = _("周期任务 PeriodicTask")
        ordering = ["-id"]

    def __unicode__(self):
        return "{name}({id})".format(name=self.name, id=self.id)

    @property
    def enabled(self):
        return self.task.enabled

    @property
    def name(self):
        return self.task.name

    @property
    def cron(self):
        return django_celery_beat_cron_time_format_fit(self.task.cron)

    @property
    def total_run_count(self):
        return self.task.total_run_count

    @property
    def last_run_at(self):
        return self.task.last_run_at

    @property
    def pipeline_tree(self):
        return self.task.execution_data

    @property
    def form(self):
        return self.task.form

    @property
    def task_template_name(self):
        name = ""
        if self.template_source in NON_COMMON_TEMPLATE_TYPES:
            try:
                template = TaskTemplate.objects.get(project=self.project, id=self.template_id)
            except TaskTemplate.DoesNotExist:
                logger.warning(
                    _("流程模板[project={project}, id={template_id}]不存在").format(
                        project=self.project, template_id=self.template_id
                    )
                )
            else:
                name = template.name
        elif self.template_source == COMMON:
            try:
                template = CommonTemplate.objects.get(id=self.template_id)
            except CommonTemplate.DoesNotExist:
                logger.warning(_("公共流程模板[id={template_id}]不存在").format(template_id=self.template_id))
            else:
                name = template.name
        return name

    @property
    def template(self):
        if self.template_source in NON_COMMON_TEMPLATE_TYPES:
            return TaskTemplate.objects.get(pk=self.template_id)
        elif self.template_source == COMMON:
            return CommonTemplate.objects.get(pk=self.template_id)

    def set_enabled(self, enabled):
        self.task.set_enabled(enabled)

    def delete(self, using=None):
        self.task.delete()
        super(PeriodicTask, self).delete(using)
        PeriodicTaskHistory.objects.filter(task=self).delete()

    def modify_cron(self, cron, timezone):
        if self.task.enabled is False:
            self.task.modify_cron(cron, timezone)
            return

        # 基于celery的实现，启动中的任务直接修改时间可能导致任务立即执行，需要先关闭
        with transaction.atomic():
            self.set_enabled(False)
            self.task.modify_cron(cron, timezone)
            self.set_enabled(True)

    def modify_constants(self, constants):
        return self.task.modify_constants(constants, must_disabled=False)

    def get_stakeholders(self):
        notify_receivers = json.loads(self.template.notify_receivers)
        receiver_group = notify_receivers.get("receiver_group", [])
        receivers = [self.creator]

        if self.project.from_cmdb:
            cc_group_members = get_business_group_members(
                self.project.tenant_id, self.project.bk_biz_id, receiver_group)
            receivers.extend(cc_group_members)

        members = list(
            StaffGroupSet.objects.filter(
                project_id=self.project.id,
                is_deleted=False,
                id__in=[group for group in receiver_group if isinstance(group, int)],
            ).values_list("members", flat=True)
        )
        if members:
            members = ",".join(members).split(",")
            receivers.extend(members)

        # 这里保证执行人在列表第一位，且名单中通知人唯一，其他接收人不保证顺序
        return sorted(set(receivers), key=receivers.index)

    def get_notify_type(self):
        notify_type = json.loads(self.template.notify_type)
        return (
            notify_type
            if isinstance(notify_type, dict)
            else {"success": notify_type, "fail": notify_type, "pending_processing": notify_type}
        )


class PeriodicTaskHistoryManager(models.Manager):
    def record_history(self, periodic_history):
        task = PeriodicTask.objects.get(task=periodic_history.periodic_task)
        flow_instance = None
        if periodic_history.start_success:
            try:
                flow_instance = TaskFlowInstance.objects.get(pipeline_instance=periodic_history.pipeline_instance)
            except TaskFlowInstance.DoesNotExist as e:
                logger.error(_("获取周期任务历史相关任务实例失败：%s" % e))

        return self.create(
            history=periodic_history,
            task=task,
            flow_instance=flow_instance,
            ex_data=periodic_history.ex_data,
            start_at=periodic_history.start_at,
            start_success=periodic_history.start_success,
        )


class PeriodicTaskHistory(models.Model):
    history = models.ForeignKey(
        PipelinePeriodicTaskHistory, verbose_name=_("pipeline 层周期任务历史"), on_delete=models.CASCADE
    )
    task = models.ForeignKey(PeriodicTask, verbose_name=_("周期任务"), on_delete=models.CASCADE)
    flow_instance = models.ForeignKey(TaskFlowInstance, verbose_name=_("流程实例"), null=True, on_delete=models.CASCADE)
    ex_data = models.TextField(_("异常信息"))
    start_at = models.DateTimeField(_("开始时间"))
    start_success = models.BooleanField(_("是否启动成功"), default=True)

    objects = PeriodicTaskHistoryManager()
