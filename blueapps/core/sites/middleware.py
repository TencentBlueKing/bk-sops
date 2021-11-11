# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.http.request import split_domain_port, validate_host
from django.utils.module_loading import import_module

from blueapps.conf import settings


class UserAgentMiddleware(object):
    def process_request(self, request):
        request.is_mobile = lambda: bool(
            settings.RE_MOBILE.search(request.META.get("HTTP_USER_AGENT", ""))
        )

        request.is_rio = lambda: bool(
            request.META.get("HTTP_STAFFNAME", "")
            and settings.RIO_TOKEN
            and settings.RE_WECHAT.search(request.META.get("HTTP_USER_AGENT", ""))
        )

        request.is_wechat = lambda: bool(
            settings.RE_WECHAT.search(request.META.get("HTTP_USER_AGENT", ""))
            and not request.is_rio()
        )

        request.is_bk_jwt = lambda: bool(request.META.get("HTTP_X_BKAPI_JWT", ""))


class SiteUrlconfMiddleware(object):
    top_module = "conf.sites"

    def process_request(self, request):
        domain, _ = split_domain_port(request.get_host())

        for site in settings.SITES:
            site = site.copy()
            try:
                if validate_host(domain, site["HOSTS"]):
                    urlconf = ".".join([self.top_module, site["NAME"], "urls"])
                    import_module(urlconf)
                    break
            except ImportError:
                pass
            except Exception:  # pylint: disable=broad-except
                pass
        else:
            urlconf = settings.ROOT_URLCONF

        request.urlconf = urlconf


class SiteSettingsMiddleware(object):
    top_module = "conf.sites"

    def _enter(self, module):
        for key in dir(module):
            if not key.startswith("_") and key == key.upper():
                self._changes[key] = {}
                if hasattr(settings, key):
                    self._changes[key]["func"] = setattr
                    self._changes[key]["args"] = [key, getattr(settings, key)]
                else:
                    self._changes[key]["func"] = delattr
                    self._changes[key]["args"] = [key]

                setattr(settings, key, getattr(module, key))

    def _exit(self):
        for key in self._changes:
            self._changes[key]["func"](settings, *self._changes[key]["args"])

    def process_request(self, request):
        domain, _ = split_domain_port(request.get_host())

        self._changes = {}

        for site in settings.SITES:
            site = site.copy()
            try:
                if validate_host(domain, site["HOSTS"]):
                    site_settings = ".".join(
                        [self.top_module, site["NAME"], "settings"]
                    )
                    self._enter(import_module(site_settings))
                    break
            except ImportError:
                pass

    def process_response(self, request, response):
        self._exit()
        return response

    def process_exception(self, request, exception):
        self._exit()
