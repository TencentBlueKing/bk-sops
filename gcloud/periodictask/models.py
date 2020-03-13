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

import logging

import ujson as json
from django.db import models
from django.utils.translation import ugettext_lazy as _

from gcloud.commons.template.models import CommonTemplate
from gcloud.taskflow3.constants import TEMPLATE_SOURCE, PROJECT, COMMON
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from pipeline.contrib.periodic_task.models import PeriodicTaskHistory as PipelinePeriodicTaskHistory
from pipeline_web.wrapper import PipelineTemplateWebWrapper

from gcloud.core.models import Project
from gcloud.periodictask.exceptions import InvalidOperationException
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.constants import NON_COMMON_TEMPLATE_TYPES
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.shortcuts.cmdb import get_business_group_members

logger = logging.getLogger("root")


# Create your models here.

class PeriodicTaskManager(models.Manager):
    def create(self, **kwargs):
        template_source = kwargs.get('template_source', PROJECT)
        task = self.create_pipeline_task(
            project=kwargs['project'],
            template=kwargs['template'],
            name=kwargs['name'],
            cron=kwargs['cron'],
            pipeline_tree=kwargs['pipeline_tree'],
            creator=kwargs['creator'],
            template_source=template_source
        )
        return super(PeriodicTaskManager, self).create(
            project=kwargs['project'],
            task=task,
            template_id=kwargs['template'].id,
            template_source=template_source
        )

    def create_pipeline_task(self, project, template, name, cron, pipeline_tree, creator, template_source=PROJECT):
        if template_source == PROJECT and template.project.id != project.id:
            raise InvalidOperationException('template %s do not belong to project[%s]' %
                                            (template.id,
                                             project.name))
        extra_info = {
            'project_id': project.id,
            'category': template.category,
            'template_id': template.pipeline_template.template_id,
            'template_source': template_source,
            'template_num_id': template.id
        }

        PipelineTemplateWebWrapper.unfold_subprocess(pipeline_tree)

        return PipelinePeriodicTask.objects.create_task(
            name=name,
            template=template.pipeline_template,
            cron=cron,
            data=pipeline_tree,
            creator=creator,
            timezone=project.time_zone,
            extra_info=extra_info,
            spread=True
        )


class PeriodicTask(models.Model):
    project = models.ForeignKey(Project,
                                verbose_name=_("所属项目"),
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL)
    task = models.ForeignKey(PipelinePeriodicTask, verbose_name=_("pipeline 层周期任务"))
    template_id = models.CharField(_("创建任务所用的模板ID"), max_length=255)
    template_source = models.CharField(_("流程模板来源"), max_length=32,
                                       choices=TEMPLATE_SOURCE,
                                       default=PROJECT)

    objects = PeriodicTaskManager()

    class Meta:
        verbose_name = _("周期任务 PeriodicTask")
        verbose_name_plural = _("周期任务 PeriodicTask")
        ordering = ['-id']

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
        return self.task.cron

    @property
    def total_run_count(self):
        return self.task.total_run_count

    @property
    def last_run_at(self):
        return self.task.last_run_at

    @property
    def creator(self):
        return self.task.creator

    @property
    def pipeline_tree(self):
        return self.task.execution_data

    @property
    def form(self):
        return self.task.form

    @property
    def task_template_name(self):
        name = ''
        if self.template_source in NON_COMMON_TEMPLATE_TYPES:
            try:
                template = TaskTemplate.objects.get(project=self.project, id=self.template_id)
            except TaskTemplate.DoesNotExist:
                logger.warning(_("流程模板[project={project}, id={template_id}]不存在").format(
                    project=self.project, template_id=self.template_id))
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
        self.task.modify_cron(cron, timezone)

    def modify_constants(self, constants):
        return self.task.modify_constants(constants)

    def get_stakeholders(self):
        notify_receivers = json.loads(self.template.notify_receivers)
        receiver_group = notify_receivers.get('receiver_group', [])
        receivers = [self.creator]

        if self.project.from_cmdb:
            group_members = get_business_group_members(
                self.project.bk_biz_id,
                receiver_group
            )

            receivers.extend(group_members)

        return receivers

    def get_notify_type(self):
        return json.loads(self.template.notify_type)


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
            start_success=periodic_history.start_success
        )


class PeriodicTaskHistory(models.Model):
    history = models.ForeignKey(PipelinePeriodicTaskHistory, verbose_name=_("pipeline 层周期任务历史"))
    task = models.ForeignKey(PeriodicTask, verbose_name=_("周期任务"))
    flow_instance = models.ForeignKey(TaskFlowInstance, verbose_name=_("流程实例"), null=True)
    ex_data = models.TextField(_("异常信息"))
    start_at = models.DateTimeField(_("开始时间"))
    start_success = models.BooleanField(_("是否启动成功"), default=True)

    objects = PeriodicTaskHistoryManager()
