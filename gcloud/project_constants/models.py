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


class ProjectConstant(models.Model):
    id = models.BigAutoField(primary_key=True)
    project_id = models.BigIntegerField(verbose_name=_("项目 ID"), blank=False)
    name = models.CharField(verbose_name=_("变量名"), max_length=255)
    key = models.CharField(verbose_name=_("变量唯一键"), max_length=255)
    value = models.TextField(verbose_name=_("变量值"))
    desc = models.TextField(verbose_name=_("变量描述"))
    create_by = models.CharField(verbose_name=_("创建人"), max_length=255)
    create_at = models.DateTimeField(verbose_name=_("创建时间"), auto_now_add=True)
    update_by = models.CharField(verbose_name=_("更新人"), max_length=255)
    update_at = models.DateTimeField(verbose_name=_("更新时间"), auto_now=True)

    class Meta:
        unique_together = (("project_id", "key"),)
