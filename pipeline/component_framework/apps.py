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

from django.apps import AppConfig
from django.db.utils import ProgrammingError

from pipeline.conf import settings
from pipeline.utils.register import autodiscover_collections


class ComponentFrameworkConfig(AppConfig):
    name = 'pipeline.component_framework'
    verbose_name = 'PipelineComponentFramework'

    def ready(self):
        """
        @summary: 注册公共部分和当前RUN_VER下的标准插件到数据库
        @return:
        """

        for path in settings.COMPONENT_AUTO_DISCOVER_PATH:
            autodiscover_collections(path)

        from pipeline.component_framework.models import ComponentModel
        from pipeline.component_framework.library import ComponentLibrary
        try:
            ComponentModel.objects.exclude(code__in=ComponentLibrary.components.keys()).update(status=False)
        except ProgrammingError:
            # first migrate
            pass
