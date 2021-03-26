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

from version_log.utils import is_later_version
from version_log.config import NO_VERSION_CONSTANT


class VersionLogVisitedManager(models.Manager):
    def has_visit_latest(self, username, latest_version):
        """判断用户是否访问过最新版本日志，同时更新数据库记录"""
        if not self.filter(username=username).exists():
            return False
        user_version = self.get(username=username).visited_version
        user_version = None if user_version == NO_VERSION_CONSTANT else user_version
        if is_later_version(latest_version, user_version):
            return False
        if is_later_version(user_version, latest_version):
            self.update_visit_version(username, latest_version)
        return True

    def update_visit_version(self, username, visit_version):
        """更新用户访问版本记录"""
        if visit_version is None:
            visit_version = NO_VERSION_CONSTANT
        self.update_or_create(username=username, defaults={'visited_version': visit_version})


class VersionLogVisited(models.Model):
    username = models.CharField(primary_key=True, max_length=50, verbose_name=_(u'用户名'))
    visited_version = models.CharField(max_length=20, verbose_name=_(u'访问版本'))

    objects = VersionLogVisitedManager()

    class Meta:
        verbose_name = verbose_name_plural = _(u'版本日志访问记录')
