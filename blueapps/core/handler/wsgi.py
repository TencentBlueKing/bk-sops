# -*- coding: utf-8 -*-
from django.core.handlers.wsgi import WSGIHandler
from django.conf import settings


class BkWSGIHandler(WSGIHandler):
    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME')
        if script_name is not None:
            if script_name == '/':
                # '/'的含义：独立域名，不启用script_name
                script_name = ''
            environ['SCRIPT_NAME'] = script_name
            settings.FORCE_SCRIPT_NAME = settings.SITE_URL = '%s/' % script_name

            # 如果没有独立域名的配置，需要不断的适配，否则可以直接使用
            if not settings.STATIC_URL.startswith("http"):
                settings.STATIC_URL = '%sstatic/' % settings.SITE_URL
        return super(BkWSGIHandler, self).__call__(environ, start_response)
