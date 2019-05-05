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
import traceback

from django.apps import AppConfig
from django.conf import settings
from django.db.utils import ProgrammingError

logger = logging.getLogger('root')


class ExternalPluginsConfig(AppConfig):
    name = 'pipeline.contrib.external_plugins'
    label = 'gcloud_external_plugins'
    verbose_name = 'PipelineExternalPlugins'

    def ready(self):
        from pipeline.contrib.external_plugins import loader  # noqa
        from pipeline.contrib.external_plugins.models import ExternalPackageSource  # noqa

        triggers = getattr(settings, 'EXTERNAL_COMPONENTS_LOAD_TRIGGER', {'runserver', 'celery', 'worker'})
        command = sys.argv[1]

        if command in triggers:
            try:
                logger.info('Start to update package source from config file...')
                ExternalPackageSource.update_package_source_from_config(getattr(settings,
                                                                                'COMPONENTS_PACKAGE_SOURCES',
                                                                                {}))
            except ProgrammingError:
                logger.warning('update package source failed, maybe first migration? exception: %s' %
                               traceback.format_exc())
                # first migrate
                return

            logger.info('Start to load external modules...')

            loader.load_external_modules()
