# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ComponentInTemplate(models.Model):
    component_code = models.CharField(_(u"组件编码"), max_length=255)
    template_id = models.CharField(_(u"模板ID"), max_length=32)
    node_id = models.CharField(_(u"节点ID"), max_length=32)
    is_sub = models.BooleanField(_(u"是否子流程引用"), default=False)
    subprocess_stack = models.TextField(_(u"子流程堆栈"), default="[]", help_text=_(u"JSON 格式的列表"))

    class Meta:
        verbose_name = _(u"Pipeline原子引用数据")
        verbose_name_plural = _(u"Pipeline原子引用数据")

    def __unicode__(self):
        return u"%s_%s" % (self.component_code, self.template_id)


class ComponentExecuteData(models.Model):
    component_code = models.CharField(_(u"组件编码"), max_length=255)
    instance_id = models.CharField(_(u"实例ID"), max_length=32)
    node_id = models.CharField(_(u"节点ID"), max_length=32)
    is_sub = models.BooleanField(_(u"是否子流程引用"), default=False)
    subprocess_stack = models.TextField(_(u"子流程堆栈"), default="[]", help_text=_(u"JSON 格式的列表"))
    started_time = models.DateTimeField(_(u"原子执行开始时间"))
    archived_time = models.DateTimeField(_(u"原子执行结束时间"), null=True, blank=True)
    elapsed_time = models.IntegerField(_(u"原子执行耗时(s)"), null=True, blank=True)
    status = models.BooleanField(_(u"是否执行成功"), default=False)
    is_skip = models.BooleanField(_(u"是否跳过"), default=False)
    is_retry = models.BooleanField(_(u'是否重试记录'), default=False)

    class Meta:
        verbose_name = u"Pipeline原子执行数据"
        verbose_name_plural = u"Pipeline原子执行数据"
        ordering = ["-id"]

    def __unicode__(self):
        return u"%s_%s" % (self.component_code, self.instance_id)
