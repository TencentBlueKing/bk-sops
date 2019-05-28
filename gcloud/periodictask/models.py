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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from pipeline.contrib.periodic_task.models import PeriodicTaskHistory as PipelinePeriodicTaskHistory
from pipeline_web.wrapper import PipelineTemplateWebWrapper

from gcloud.core.models import Business
from gcloud.periodictask.exceptions import InvalidOperationException
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.taskflow3.models import TaskFlowInstance

logger = logging.getLogger("root")


# Create your models here.

class PeriodicTaskManager(models.Manager):
    def create(self, **kwargs):
        task = self.create_pipeline_task(
            business=kwargs['business'],
            template=kwargs['template'],
            name=kwargs['name'],
            cron=kwargs['cron'],
            pipeline_tree=kwargs['pipeline_tree'],
            creator=kwargs['creator']
        )
        return super(PeriodicTaskManager, self).create(
            business=kwargs['business'],
            task=task,
            template_id=kwargs['template'].id)

    def create_pipeline_task(self, business, template, name, cron, pipeline_tree, creator):
        if template.business.id != business.id:
            raise InvalidOperationException('template %s do not belong to business[%s]' %
                                            (template.id,
                                             business.cc_name))
        extra_info = {
            'business_id': business.id,
            'category': template.category,
            'template_id': template.pipeline_template.template_id,
            'template_num_id': template.id}

        PipelineTemplateWebWrapper.unfold_subprocess(pipeline_tree)

        return PipelinePeriodicTask.objects.create_task(
            name=name,
            template=template.pipeline_template,
            cron=cron,
            data=pipeline_tree,
            creator=creator,
            timezone=business.time_zone,
            extra_info=extra_info,
            spread=True
        )


class PeriodicTask(models.Model):
    business = models.ForeignKey(Business,
                                 verbose_name=_(u"业务"),
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL)
    task = models.ForeignKey(PipelinePeriodicTask, verbose_name=_(u"pipeline 层周期任务"))
    template_id = models.CharField(_(u"创建任务所用的模板ID"), max_length=255)

    objects = PeriodicTaskManager()

    class Meta:
        verbose_name = _(u"周期任务 PeriodicTask")
        verbose_name_plural = _(u"周期任务 PeriodicTask")
        ordering = ['-id']

    def __unicode__(self):
        return u"{name}({id})".format(name=self.name, id=self.id)

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
        task_template = None
        try:
            task_template = TaskTemplate.objects.get(id=self.template_id).name
        except Exception as e:
            logger.warning(_(u"模板不存在，错误信息：%s") % e)
        finally:
            return task_template

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


class PeriodicTaskHistoryManager(models.Manager):

    def record_history(self, periodic_history):
        task = PeriodicTask.objects.get(task=periodic_history.periodic_task)
        flow_instance = None
        if periodic_history.start_success:
            flow_instance = TaskFlowInstance.objects.get(
                pipeline_instance=periodic_history.pipeline_instance)

        return self.create(
            history=periodic_history,
            task=task,
            flow_instance=flow_instance,
            ex_data=periodic_history.ex_data,
            start_at=periodic_history.start_at,
            start_success=periodic_history.start_success
        )


class PeriodicTaskHistory(models.Model):
    history = models.ForeignKey(PipelinePeriodicTaskHistory, verbose_name=_(u"pipeline 层周期任务历史"))
    task = models.ForeignKey(PeriodicTask, verbose_name=_(u"周期任务"))
    flow_instance = models.ForeignKey(TaskFlowInstance, verbose_name=_(u"流程实例"), null=True)
    ex_data = models.TextField(_(u"异常信息"))
    start_at = models.DateTimeField(_(u"开始时间"))
    start_success = models.BooleanField(_(u"是否启动成功"), default=True)

    objects = PeriodicTaskHistoryManager()
