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

import sys
import logging
import traceback

from django.apps import AppConfig
from django.conf import settings
from django.db.utils import ProgrammingError

logger = logging.getLogger('root')

DJANGO_MANAGE_CMD = 'manage.py'
DEFAULT_TRIGGERS = {'runserver', 'celery', 'worker', 'uwsgi', 'shell'}


class ExternalPluginsConfig(AppConfig):
    name = 'pipeline.contrib.external_plugins'
    label = 'pipeline_external_plugins'
    verbose_name = 'PipelineExternalPlugins'

    def ready(self):
        from pipeline.contrib.external_plugins import loader  # noqa
        from pipeline.contrib.external_plugins.models import ExternalPackageSource  # noqa

        # load external components when start command in trigger list
        if self.should_load_external_module():
            try:
                logger.info('Start to update package source from config file...')
                ExternalPackageSource.update_package_source_from_config(getattr(settings,
                                                                                'COMPONENTS_PACKAGE_SOURCES',
                                                                                {}))
            except ProgrammingError:
                logger.warning('update package source failed, maybe first migration? '
                               'exception: {traceback}'.format(traceback=traceback.format_exc()))
                # first migrate
                return

            logger.info('Start to load external modules...')

            loader.load_external_modules()

    @staticmethod
    def should_load_external_module():
        triggers = getattr(settings, 'EXTERNAL_COMPONENTS_LOAD_TRIGGER', DEFAULT_TRIGGERS)
        if sys.argv and sys.argv[0] == DJANGO_MANAGE_CMD:
            try:
                command = sys.argv[1]
                logger.info('current django manage command: {cmd}, triggers: {triggers}'.format(
                    cmd=command,
                    triggers=triggers))

                return command in triggers
            except Exception:
                logger.error('get django start up command error with argv: {argv}, traceback: {traceback}'.format(
                    argv=sys.argv,
                    traceback=traceback.format_exc()))

                return True

        logger.info('app is not start with django manage command, current argv: {argv}'.format(argv=sys.argv))
        return True
