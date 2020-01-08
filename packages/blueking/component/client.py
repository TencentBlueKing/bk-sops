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

import time
import random
import logging
import urlparse

import ujson as json
import requests

from . import conf
from . import collections
from .utils import get_signature

# shutdown urllib3's warning
try:
    requests.packages.urllib3.disable_warnings()
except Exception:
    pass


logger = logging.getLogger('component')


class BaseComponentClient(object):
    """Base client class for component"""

    @classmethod
    def setup_components(cls, components):
        cls.available_collections = components

    def __init__(self, app_code=None, app_secret=None, common_args=None, use_test_env=False, language=None,
                 bk_app_code=None, bk_app_secret=None):
        """
        :param str app_code: App code to use
        :param str app_secret: App secret to use
        :param dict common_args: Args that will apply to every request
        :param bool use_test_env: whether use test version of components
        """
        self.app_code = bk_app_code or app_code or conf.APP_CODE
        self.app_secret = bk_app_secret or app_secret or conf.SECRET_KEY
        self.bk_api_ver = conf.DEFAULT_BK_API_VER
        self.common_args = common_args or {}
        self._cached_collections = {}
        self.use_test_env = use_test_env
        self.language = language or self.get_cur_language()

    def set_use_test_env(self, use_test_env):
        """Change the value of use_test_env

        :param bool use_test_env: whether use test version of components
        """
        self.use_test_env = use_test_env

    def set_language(self, language):
        self.language = language

    def get_cur_language(self):
        try:
            from django.utils import translation
            return translation.get_language()
        except Exception:
            return None

    def set_bk_api_ver(self, bk_api_ver):
        self.bk_api_ver = bk_api_ver

    def get_bk_api_ver(self):
        return self.bk_api_ver

    def merge_params_data_with_common_args(self, method, params, data, enable_app_secret=False):
        """get common args when request
        """
        common_args = dict(bk_app_code=self.app_code, **self.common_args)
        if enable_app_secret:
            common_args['bk_app_secret'] = self.app_secret
        if method == 'GET':
            _params = common_args.copy()
            _params.update(params or {})
            params = _params
        elif method == 'POST':
            _data = common_args.copy()
            _data.update(data or {})
            data = json.dumps(_data)
        return params, data

    def request(self, method, url, params=None, data=None, **kwargs):
        """Send request
        """
        # determine whether access test environment of third-party system
        headers = kwargs.pop('headers', {})
        if self.use_test_env:
            headers['x-use-test-env'] = '1'
        if self.language:
            headers['blueking-language'] = self.language

        params, data = self.merge_params_data_with_common_args(method, params, data, enable_app_secret=True)
        logger.debug('Calling %s %s with params=%s, data=%s, headers=%s', method, url, params, data, headers)
        return requests.request(method, url, params=params, data=data, verify=False,
                                headers=headers, **kwargs)

    def __getattr__(self, key):
        if key not in self.available_collections:
            return getattr(super(BaseComponentClient, self), key)

        if key not in self._cached_collections:
            collection = self.available_collections[key]
            self._cached_collections[key] = collection(self)
        return self._cached_collections[key]


class ComponentClientWithSignature(BaseComponentClient):
    """Client class for component with signature"""

    def request(self, method, url, params=None, data=None, **kwargs):
        """Send request, will add "signature" parameter.
        """
        # determine whether access test environment of third-party system
        headers = kwargs.pop('headers', {})
        if self.use_test_env:
            headers['x-use-test-env'] = '1'
        if self.language:
            headers['blueking-language'] = self.language

        params, data = self.merge_params_data_with_common_args(method, params, data, enable_app_secret=False)
        if method == 'POST':
            params = {}

        url_path = urlparse.urlparse(url).path
        # signature always in GET params
        params.update({
            'bk_timestamp': int(time.time()),
            'bk_nonce': random.randint(1, 2147483647),
        })
        params['bk_signature'] = get_signature(method, url_path, self.app_secret, params=params, data=data)

        logger.debug('Calling %s %s with params=%s, data=%s', method, url, params, data)
        return requests.request(method, url, params=params, data=data, verify=False,
                                headers=headers, **kwargs)


# 根据是否开启signature来判断使用的Client版本
if conf.CLIENT_ENABLE_SIGNATURE:
    ComponentClient = ComponentClientWithSignature
else:
    ComponentClient = BaseComponentClient

ComponentClient.setup_components(collections.AVAILABLE_COLLECTIONS)
