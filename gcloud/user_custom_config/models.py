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


class UserConfManager(models.Manager):
    DEFAULT_TEMPLATE_ORDERING = "-pipeline_template__edit_time"

    def set_userconf(self, **kwargs):
        username = kwargs.pop("username") if "username" in kwargs.keys() else None
        project_id = kwargs.pop("project_id") if "project_id" in kwargs.keys() else None
        user_conf = self.get_or_create(username=username, project_id=project_id)[0]
        for key, value in kwargs.items():
            setattr(user_conf, key, value)
        user_conf.save()
        return user_conf

    def get_conf(self, **kwargs):
        username = kwargs.get("username")
        project_id = kwargs.get("project_id")
        try:
            user_conf = self.get(username=username, project_id=project_id)
        except self.model.DoesNotExist:
            user_conf = self.model(
                username=username, project_id=project_id, task_template_ordering=self.DEFAULT_TEMPLATE_ORDERING
            )
        return user_conf


class UserCustomProjectConfig(models.Model):
    username = models.CharField(_("用户名"), max_length=255)
    project_id = models.IntegerField(_("所属项目ID"))
    task_template_ordering = models.CharField(_("模板列表默认排序字段"), max_length=255, default="-id")

    objects = UserConfManager()

    class Meta:
        index_together = ["username", "project_id"]
