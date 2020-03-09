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

import sys
import logging

from django.conf import settings
from django.apps import AppConfig

logger = logging.getLogger('root')

DJANGO_MANAGE_CMD = 'manage.py'
INIT_PASS_TRIGGER = {'migrate'}


class PipelinePluginsConfig(AppConfig):
    name = 'pipeline_plugins'

    def ready(self):

        if sys.argv and sys.argv[0] == DJANGO_MANAGE_CMD and sys.argv[1] in INIT_PASS_TRIGGER:
            logger.info("ignore pipeline plugins init for command: {}".format(sys.argv))
            return

        for old_path, new_path in list(getattr(settings, 'COMPATIBLE_MODULE_MAP', {}).items()):
            sys.modules[old_path] = sys.modules[new_path]
