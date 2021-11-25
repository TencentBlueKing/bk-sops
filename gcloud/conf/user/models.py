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

from gcloud.conf.user.constants import UserConfOption


class UserConfManager(models.Manager):
    def set_userconf(self, username, project_id, field, value):
        user_conf = self.get_or_create(username=username, project_id=project_id)[0]
        if not hasattr(user_conf, field):
            return False, f"Field:{field} is not exists!"
        setattr(user_conf, field, value)
        user_conf.save()
        return True, None

    def get_conf_by_user(self, username, project_id, field_list):
        user_conf = self.get_or_create(username=username, project_id=project_id)[0]
        for field_name in field_list:
            if not hasattr(user_conf, field_name):
                return False, f"Field:{field_name} is not exists!"
        content = {
            field_name: {
                "value": getattr(user_conf, field_name),
                "name": field_name,
                "options": UserConfOption.get(field_name, {}),
            }
            for field_name in field_list
        }
        return True, content


class UserConf(models.Model):
    username = models.CharField(_("用户名"), max_length=255)
    project_id = models.IntegerField(_("所属项目ID"))
    tasktmpl_ordering = models.CharField(_("模板列表默认排序字段"), max_length=255, default="-id")

    objects = UserConfManager()
