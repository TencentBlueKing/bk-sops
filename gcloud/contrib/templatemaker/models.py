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


from django.db import models
from django.utils.translation import ugettext_lazy as _

from gcloud.constants import TEMPLATE_SOURCE, PROJECT


class TemplateSharedRecord(models.Model):
    project_id = models.IntegerField(_("项目 ID"), default=-1, help_text="项目 ID")
    template_id = models.IntegerField(_("模版ID"), db_index=True)
    template_source = models.CharField(_("流程模板来源"), max_length=32, choices=TEMPLATE_SOURCE, default=PROJECT)
    create = models.CharField(_("执行者"), max_length=128, help_text="执行者")
    create_time = models.DateTimeField(_("执行时间"), auto_now_add=True, help_text="执行时间")

    class Meta:
        verbose_name = _("模板共享记录 TemplateSharedRecord")
        verbose_name_plural = _("模板共享记录 TemplateSharedRecord")
        unique_together = ("project_id", "template_id")
