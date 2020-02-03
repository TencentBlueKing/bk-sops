# -*- coding: utf-8 -*-
from django.apps import AppConfig
from version_log.utils import get_latest_version
import version_log.config as config


class VersionLogAppConfig(AppConfig):
    name = 'version_log'
    verbose_name = "Version Log"

    def ready(self):
        config.LATEST_VERSION = get_latest_version()
