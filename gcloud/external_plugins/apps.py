# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger("root")


class ExternalPluginsConfig(AppConfig):
    name = "gcloud.external_plugins"
    verbose_name = "GcloudExternalPlugins"

    def ready(self):
        self._patch_django4_compat()
        from gcloud.external_plugins.signals.handlers import sync_task_post_save_handler  # noqa

    @staticmethod
    def _patch_django4_compat():
        """Patch removed Django APIs so legacy remote plugins can still be imported under Django 4.x."""
        import django.conf.urls
        import django.utils.translation

        if not hasattr(django.conf.urls, "url"):
            from django.urls import re_path

            django.conf.urls.url = re_path
            logger.info("Patched django.conf.urls.url -> django.urls.re_path for legacy remote plugins")

        if not hasattr(django.utils.translation, "ugettext_lazy"):
            django.utils.translation.ugettext_lazy = django.utils.translation.gettext_lazy
            logger.info("Patched django.utils.translation.ugettext_lazy -> gettext_lazy for legacy remote plugins")

        if not hasattr(django.utils.translation, "ugettext"):
            django.utils.translation.ugettext = django.utils.translation.gettext
            logger.info("Patched django.utils.translation.ugettext -> gettext for legacy remote plugins")
