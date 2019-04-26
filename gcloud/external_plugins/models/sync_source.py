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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from pipeline.contrib.external_plugins.models import GIT

from gcloud.external_plugins.models.sync_base import (
    SyncPackageSource,
    sync_source
)


@sync_source
class GitRepoSyncSource(SyncPackageSource):
    repo_address = models.TextField(_(u"仓库链接"))
    branch = models.CharField(_(u"分支名"), max_length=128)

    @staticmethod
    def type():
        return GIT

    def details(self):
        return {
            'repo_address': self.repo_address,
            'branch': self.branch
        }
