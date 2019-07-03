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

from __future__ import unicode_literals

import sys

from django.apps import AppConfig


class PipelinePluginsConfig(AppConfig):
    name = 'pipeline_plugins'

    compatible_module_map = {
        'pipeline.components.collections.common': 'pipeline_plugins.components.collections.common',
        'pipeline.components.collections.controller': 'pipeline_plugins.components.collections.controller',
        'pipeline.components.collections.sites.community.bk': 'pipeline_plugins.components.collections.sites.open.bk',
        'pipeline.components.collections.sites.community.cc': 'pipeline_plugins.components.collections.sites.open.cc',
        'pipeline.components.collections.sites.community.job': 'pipeline_plugins.components.collections.sites.open.job',
        'pipeline.variables.collections.common': 'pipeline_plugins.variables.collections.common',
        'pipeline.variables.collections.sites.community.cc': 'pipeline_plugins.variables.collections.sites.open.cc',
    }

    def ready(self):
        for old_path, new_path in self.compatible_module_map.items():
            sys.modules[old_path] = sys.modules[new_path]
