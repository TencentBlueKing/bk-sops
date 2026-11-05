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
        self._disable_pipeline_external_plugins_loading()
        self._unregister_pipeline_admin()
        # 远程插件加载功能已下架
        # 移除: from gcloud.external_plugins.signals.handlers import sync_task_post_save_handler

    @staticmethod
    def _disable_pipeline_external_plugins_loading():
        """
        禁用 pipeline.contrib.external_plugins 的自动加载

        方案: 在 gcloud.external_plugins.ready() 中替换 pipeline 的 ready() 方法
        """
        from django.apps import apps

        try:
            # 获取 pipeline.contrib.external_plugins 的 AppConfig
            # 注意：遍历所有 app 找到正确的 pipeline app，存在两个 app 是 'external_plugins'
            pipeline_app = None
            for app_config in apps.get_app_configs():
                if app_config.name == 'pipeline.contrib.external_plugins':
                    pipeline_app = app_config
                    break

            if pipeline_app is None:
                logger.warning("未找到 pipeline.contrib.external_plugins，无需禁用")
                return

            def disabled_ready():
                logger.warning(
                    "pipeline.contrib.external_plugins.ready() 已被禁用。"
                    "远程插件加载功能已下架。"
                )

            # 替换 ready() 方法
            pipeline_app.ready = disabled_ready
            logger.info("已成功替换 pipeline.contrib.external_plugins.ready() 方法")
        except Exception as e:
            # 捕获所有异常，避免影响应用启动
            logger.error(f"禁用 pipeline.contrib.external_plugins 时发生错误: {e}")
            pass

    @staticmethod
    def _unregister_pipeline_admin():
        """
        注销 pipeline.contrib.external_plugins 的 Admin 类

        必须在 ready() 中执行，因为：
        1. admin.py 模块导入时，pipeline 的 Admin 类尚未注册
        2. ready() 在所有 admin.py 导入后执行，此时 pipeline 的 Admin 已注册
        3. 可以成功注销
        """
        from django.contrib import admin

        try:
            from pipeline.contrib.external_plugins.models import S3Source, GitRepoSource, FileSystemSource
        except ImportError:
            logger.warning("无法导入 pipeline.contrib.external_plugins.models，跳过 Admin 注销")
            return

        models_to_unregister = [
            ("S3Source", S3Source),
            ("GitRepoSource", GitRepoSource),
            ("FileSystemSource", FileSystemSource),
        ]

        for model_name, model_class in models_to_unregister:
            try:
                admin.site.unregister(model_class)
                logger.info(f"已成功注销 {model_name} 的 Admin 类")
            except admin.sites.NotRegistered:
                logger.debug(f"{model_name} 未注册到 Admin，无需注销")
            except Exception as e:
                logger.error(f"注销 {model_name} Admin 时发生错误: {e}")

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
