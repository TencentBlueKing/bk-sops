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


class AppExemptionManager(models.Manager):
    def check_project_exemption(self, app_code: str, project_id: str):
        """
        检查指定应用是否豁免特定项目。

        :param app_code: 应用的唯一标识
        :param project_id: 要检查的项目 ID
        :return: 如果项目豁免返回 True，否则返回 False
        """
        if not isinstance(project_id, str):
            raise TypeError("project_id must be str type")
        try:
            exemption_project = self.get(app_code=app_code)
            exempted_ids = exemption_project.exemption_projects.split(",")

            return project_id in exempted_ids
        except AppExemption.DoesNotExist:
            return True


class AppExemption(models.Model):
    app_code = models.CharField(_("应用code"), max_length=32, unique=True)
    exemption_projects = models.CharField(_("豁免项目 ID 列表"), max_length=255)
    extra_info = models.JSONField(_("额外信息"), blank=True, null=True)

    objects = AppExemptionManager()

    class Meta:
        verbose_name = _("应用豁免 AppExemption")
        verbose_name_plural = _("应用豁免 AppExemption")
