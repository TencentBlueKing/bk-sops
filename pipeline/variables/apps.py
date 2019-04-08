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


class VariablesConfig(AppConfig):
    name = 'pipeline.variables'
    verbose_name = 'PipelineVariables'

    def ready(self):
        """
        @summary: 注册公共部分和OPEN_VER下的变量到数据库
        @return:
        """
        from pipeline.variables.signals.handlers import *  # noqa
        for path in settings.VARIABLE_AUTO_DISCOVER_PATH:
            autodiscover_collections(path)

        from pipeline.models import VariableModel
        from pipeline.core.data.library import VariableLibrary
        try:
            VariableModel.objects.exclude(code__in=VariableLibrary.variables.keys()).update(status=False)
        except ProgrammingError:
            # first migrate
            pass
