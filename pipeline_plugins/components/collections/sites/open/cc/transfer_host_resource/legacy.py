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

import logging

from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from pipeline_plugins.components.collections.sites.open.cc.base import BaseTransferHostToModuleService

logger = logging.getLogger("celery")
__group_name__ = _("配置平台(CMDB)")


class CmdbTransferHostResourceModuleService(BaseTransferHostToModuleService):
    def execute(self, data, parent_data):
        return self.exec_transfer_host_module(data, parent_data, "transfer_host_to_resourcemodule")


class CmdbTransferHostResourceModuleComponent(Component):
    name = _("上交主机至资源池")
    code = "cmdb_transfer_host_resource"
    bound_service = CmdbTransferHostResourceModuleService
    form = "%scomponents/atoms/cc/cmdb_transfer_host_resource.js" % settings.STATIC_URL
