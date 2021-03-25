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

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from blueapps.account.sites.default import ConfFixture as default_fixture


class _ConfFixture(object):
    def __init__(self, fixture_module):
        # store the module
        self._fixture = import_string(fixture_module)

    def __getattr__(self, name):
        # first, site fixture
        if hasattr(self._fixture, name):
            return getattr(self._fixture, name)

        # next, default fixture
        if hasattr(default_fixture, name):
            setting = getattr(default_fixture, name)
            if setting is None:
                raise ImproperlyConfigured(
                    "Requested %s, but ConfFixture are not configured. "
                    "You must set options in ConfFixture in right site.conf.py" % name
                )
            return setting

        raise KeyError("%s not exist" % name)


MOD = "blueapps.account.sites.{VER}.conf.ConfFixture".format(VER=settings.RUN_VER)
ConfFixture = _ConfFixture(MOD)

AUTH_USER_MODEL = "account.User"

######################
# 二次验证配置默认参数 #
######################

# 短信验证有效时间
SECOND_VERIFY_CONF = {
    "VALID_MINUTES": 5,
    "RETRY_MINUTES": 3,
    "SMS_FORMAT": _(u"您正在蓝鲸应用上执行敏感操作，验证码：{}"),
    "CODE_NAME": "bk_verify_code",
}
