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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from gcloud.constants import TASK_CATEGORY, TASK_CREATE_METHOD


class TemplateNodeStatistics(models.Model):
    id = models.BigAutoField(_("id"), primary_key=True)
    component_code = models.CharField(_("组件编码"), max_length=255, db_index=True)
    template_id = models.BigIntegerField(_("Pipeline模板ID"), db_index=True)
    task_template_id = models.BigIntegerField(_("Task模板ID"), db_index=True)
    project_id = models.IntegerField(_("项目 ID"), default=-1, help_text="模板所属project id", db_index=True)
    category = models.CharField(_("模板类型"), choices=TASK_CATEGORY, max_length=255, default="Default")
    node_id = models.CharField(_("节点ID"), max_length=32)
    is_sub = models.BooleanField(_("是否子流程引用"), default=False)
    subprocess_stack = models.TextField(_("子流程堆栈"), default="[]", help_text=_("JSON 格式的列表"))
    version = models.CharField(_("插件版本"), max_length=255, default="legacy")
    template_creator = models.CharField(_("创建者"), max_length=255, null=True, blank=True)
    template_create_time = models.DateTimeField(_("模版创建时间"), null=True)
    template_edit_time = models.DateTimeField(_("模板最近编辑时间"), null=True)
    is_remote = models.BooleanField(_("是否第三方插件"), default=False)

    class Meta:
        verbose_name = _("Pipeline标准插件被引用数据")
        verbose_name_plural = _("Pipeline标准插件被引用数据")

    def __unicode__(self):
        return "{}_{}".format(self.component_code, self.template_id)


class TaskflowExecutedNodeStatistics(models.Model):
    id = models.BigAutoField(_("id"), primary_key=True)
    component_code = models.CharField(_("组件编码"), max_length=255, db_index=True)
    instance_id = models.BigIntegerField(_("Pipeline实例ID"), db_index=True)
    task_instance_id = models.BigIntegerField(_("Task实例ID"), db_index=True)
    node_id = models.CharField(_("节点ID"), max_length=32)
    is_sub = models.BooleanField(_("是否子流程引用"), default=False)
    subprocess_stack = models.TextField(_("子流程堆栈"), default="[]", help_text=_("JSON 格式的列表"))
    started_time = models.DateTimeField(_("标准插件执行开始时间"))
    archived_time = models.DateTimeField(_("标准插件执行结束时间"), null=True, blank=True)
    elapsed_time = models.IntegerField(_("标准插件执行耗时(s)"), null=True, blank=True)
    status = models.BooleanField(_("是否执行成功"), default=False)
    is_skip = models.BooleanField(_("是否跳过"), default=False)
    is_retry = models.BooleanField(_("是否重试记录"), default=False)
    version = models.CharField(_("插件版本"), max_length=255, default="legacy")
    template_id = models.CharField(_("Pipeline模板ID"), max_length=32)
    task_template_id = models.CharField(_("Task模板ID"), max_length=32)
    project_id = models.IntegerField(_("项目 ID"), default=-1, help_text="模板所属project id", db_index=True)
    instance_create_time = models.DateTimeField(_("Pipeline实例创建时间"), db_index=True)
    instance_start_time = models.DateTimeField(_("Pipeline实例启动时间"), null=True, blank=True)
    instance_finish_time = models.DateTimeField(_("Pipeline实例结束时间"), null=True, blank=True)
    is_remote = models.BooleanField(_("是否第三方插件"), default=False)

    class Meta:
        verbose_name = _("Pipeline标准插件执行数据")
        verbose_name_plural = _("Pipeline标准插件执行数据")

    def __unicode__(self):
        return "{}_{}".format(self.component_code, self.instance_id)


class TemplateStatistics(models.Model):
    id = models.BigAutoField(_("id"), primary_key=True)
    template_id = models.BigIntegerField(_("Pipeline模板ID"), db_index=True)
    task_template_id = models.BigIntegerField(_("Task模板ID"), db_index=True)
    atom_total = models.IntegerField(_("标准插件总数"))
    subprocess_total = models.IntegerField(_("子流程总数"))
    gateways_total = models.IntegerField(_("网关总数"))
    project_id = models.IntegerField(_("项目 ID"), default=-1, help_text="模板所属project id", db_index=True)
    category = models.CharField(_("模板类型"), choices=TASK_CATEGORY, max_length=255, default="Default")
    template_creator = models.CharField(_("创建者"), max_length=255, null=True, blank=True)
    template_create_time = models.DateTimeField(_("创建时间"), null=True, db_index=True)
    template_edit_time = models.DateTimeField(_("最近编辑时间"), null=True)
    output_count = models.IntegerField(_("输出变量数"), default=-1)
    input_count = models.IntegerField(_("输入变量数"), default=-1)

    class Meta:
        verbose_name = _("Pipeline模板引用数据")
        verbose_name_plural = _("Pipeline模板引用数据")

    def __unicode__(self):
        return "{}_{}_{}_{}".format(self.template_id, self.atom_total, self.subprocess_total, self.gateways_total)


class TaskflowStatistics(models.Model):
    id = models.BigAutoField(_("id"), primary_key=True)
    instance_id = models.BigIntegerField(_("Pipeline实例ID"), db_index=True)
    task_instance_id = models.BigIntegerField(_("Task实例ID"), db_index=True)
    atom_total = models.IntegerField(_("标准插件总数"))
    subprocess_total = models.IntegerField(_("子流程总数"))
    gateways_total = models.IntegerField(_("网关总数"))
    project_id = models.IntegerField(_("项目 ID"), default=-1, help_text="模板所属project id")
    category = models.CharField(_("模板类型"), choices=TASK_CATEGORY, max_length=255, default="Default")
    template_id = models.CharField(_("Pipeline模板ID"), max_length=255, db_index=True)
    task_template_id = models.CharField(_("Task模板ID"), max_length=255, db_index=True)
    creator = models.CharField(_("创建者"), max_length=32, blank=True)
    create_time = models.DateTimeField(_("创建时间"), db_index=True)
    start_time = models.DateTimeField(_("启动时间"), null=True, blank=True)
    finish_time = models.DateTimeField(_("结束时间"), null=True, blank=True)
    elapsed_time = models.IntegerField(_("实例执行耗时(s)"), null=True, blank=True)
    create_method = models.CharField(_("实例创建方式"), max_length=30, choices=TASK_CREATE_METHOD, default="app")

    class Meta:
        verbose_name = _("Pipeline实例引用数据")
        verbose_name_plural = _("Pipeline实例引用数据")

    def __unicode__(self):
        return "{}_{}_{}_{}".format(self.instance_id, self.atom_total, self.subprocess_total, self.gateways_total)


class ProjectStatisticsDimension(models.Model):
    dimension_id = models.CharField(verbose_name="统计维度id(cmdb业务模型属性id)", max_length=32, null=False)
    dimension_name = models.CharField(verbose_name="统计维度名称(cmdb业务模型属性名称)", max_length=32, null=False)

    class Meta:
        verbose_name = _("业务统计数据维度")
        verbose_name_plural = _("业务统计数据维度")


class TaskTmplExecuteTopN(models.Model):
    topn = models.IntegerField(verbose_name="流程执行次数topn")

    class Meta:
        verbose_name = _("流程执行次数topn统计面板配置")
        verbose_name_plural = _("流程执行次数topn统计面板配置")
