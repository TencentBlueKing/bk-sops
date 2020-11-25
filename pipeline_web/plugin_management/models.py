# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


from django.db import models
from django.utils.translation import ugettext_lazy as _


class DeprecatedPluginManager(models.Manager):
    def get_components_phase_dict(self):
        """获取类型为 components 的插件当前生命周期字典，按照 code, version 聚合

        :return: {
            "code": {
                "v1": 0,
                "v2": 1,
                ...
            },
            ...
        }
        :rtype: dict
        """
        code_version_dict = {}
        components = self.filter(type=DeprecatedPlugin.PLUGIN_TYPE_COMPONENT)

        for comp in components:
            code_version_dict.setdefault(comp.code, {})[comp.version] = comp.phase

        return code_version_dict

    def get_variables_phase_dict(self):
        """获取类型为 variable 的插件当前生命周期字典，按照 code, version 聚合

        :return: {
            "code": {
                "v1": 0,
                "v2": 1,
                ...
            },
            ...
        }
        :rtype: dict
        """
        code_version_dict = {}
        variables = self.filter(type=DeprecatedPlugin.PLUGIN_TYPE_VARIABLE)

        for var in variables:
            code_version_dict.setdefault(var.code, {})[var.version] = var.phase

        return code_version_dict


class DeprecatedPlugin(models.Model):
    PLUGIN_TYPE_COMPONENT = 1
    PLUGIN_TYPE_VARIABLE = 2

    plugin_types = ((PLUGIN_TYPE_COMPONENT, "component"), (PLUGIN_TYPE_VARIABLE, "variable"))

    PLUGIN_PHASE_AVAILABLE = 0
    PLUGIN_PHASE_WILL_BE_DEPRECATED = 1
    PLUGIN_PHASE_DEPRECATED = 2

    plugin_phase = ((PLUGIN_PHASE_WILL_BE_DEPRECATED, "will be deprecated"), (PLUGIN_PHASE_DEPRECATED, "deprecated"))

    code = models.CharField(_("插件编码"), max_length=255)
    version = models.CharField(_("插件版本"), max_length=64)
    type = models.PositiveIntegerField(_("插件类型"), choices=plugin_types)
    phase = models.PositiveIntegerField(_("生命周期"), choices=plugin_phase)

    objects = DeprecatedPluginManager()
