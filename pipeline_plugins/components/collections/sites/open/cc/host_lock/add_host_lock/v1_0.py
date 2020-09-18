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
from django.utils.translation import ugettext_lazy as _

from gcloud.conf import settings

from pipeline.component_framework.component import Component
from pipeline_plugins.components.collections.sites.open.cc.host_lock.base import (
    CCHostLockBaseService,
    HostLockTypeService,
)

__group_name__ = _("配置平台(CMDB)")
VERSION = "v1.0"


class AddHostLockMixin(HostLockTypeService):
    def host_lock_method(self):
        return "add_host_lock"


class CmdbAddHostLockService(AddHostLockMixin, CCHostLockBaseService):
    pass


class CmdbAddHostLockComponent(Component):
    name = _("主机加锁")
    code = "cmdb_add_host_lock"
    bound_service = CmdbAddHostLockService
    form = "%scomponents/atoms/cc/cmdb_add_host_lock/v1_0.js" % settings.STATIC_URL

    version = VERSION
