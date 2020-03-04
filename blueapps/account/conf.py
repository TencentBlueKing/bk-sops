# -*- coding: utf-8 -*-
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

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
                    'Requested %s, but ConfFixture are not configured. '
                    'You must set options in ConfFixture in right site.conf.py'
                    % (name))
            return setting

        raise KeyError('%s not exist' % name)


mod = 'blueapps.account.sites.{VER}.conf.ConfFixture'.format(
    VER=settings.RUN_VER)
ConfFixture = _ConfFixture(mod)

AUTH_USER_MODEL = 'account.User'

######################
# 二次验证配置默认参数 #
######################

# 短信验证有效时间
SECOND_VERIFY_CONF = {
    'VALID_MINUTES': 5,
    'RETRY_MINUTES': 3,
    'SMS_FORMAT': u'您正在蓝鲸应用上执行敏感操作，验证码：{}',
    'CODE_NAME': 'bk_verify_code'
}
