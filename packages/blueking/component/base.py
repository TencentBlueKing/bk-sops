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

import json
import logging

from .exceptions import ComponentAPIException
from .conf import COMPONENT_SYSTEM_HOST


logger = logging.getLogger('component')


class ComponentAPI(object):
    """Single API for Component"""

    HTTP_STATUS_OK = 200

    def __init__(self, client, method, path, description='', default_return_value=None):
        host = COMPONENT_SYSTEM_HOST
        # Do not use join, use '+' because path may starts with '/'
        self.host = host.rstrip('/')
        self.path = path
        self.url = ''
        self.client = client
        self.method = method
        self.default_return_value = default_return_value

    def get_url_with_api_ver(self):
        bk_api_ver = self.client.get_bk_api_ver()
        sub_path = '/{}'.format(bk_api_ver) if bk_api_ver else ''
        return self.host + self.path.format(bk_api_ver=sub_path)

    def __call__(self, *args, **kwargs):
        self.url = self.get_url_with_api_ver()
        try:
            return self._call(*args, **kwargs)
        except ComponentAPIException, e:
            # Combine log message
            log_message = [e.error_message, ]
            log_message.append('url=%(url)s' % {'url': e.api_obj.url})
            if e.resp:
                log_message.append('content: %s' % e.resp.text)

            logger.exception('\n'.join(log_message))

            # Try return error message from remote service
            if e.resp is not None:
                try:
                    return e.resp.json()
                except Exception:
                    pass
            return {'result': False, 'message': e.error_message, 'data': None}

    def _call(self, *args, **kwargs):
        params, data = {}, {}
        if args and isinstance(args[0], dict):
            params = args[0]
        params.update(kwargs)

        # Validate params for POST request
        if self.method == 'POST':
            data = params
            params = None
            try:
                json.dumps(data)
            except Exception:
                raise ComponentAPIException(self, 'Request parameter error (please pass in a dict or json string)')

        # Request remote server
        try:
            resp = self.client.request(self.method, self.url, params=params, data=data)
        except Exception, e:
            logger.exception('Error occurred when requesting method=%s url=%s',
                             self.method, self.url)
            raise ComponentAPIException(self, u'Request component error, Exception: %s' % str(e))

        # Parse result
        if resp.status_code != self.HTTP_STATUS_OK:
            message = 'Request component error, status_code: %s' % resp.status_code
            raise ComponentAPIException(self, message, resp=resp)
        try:
            # Parse response
            json_resp = resp.json()
            if not json_resp['result']:
                # 组件返回错误时，记录相应的 request_id
                log_message = (u'Component return error message: %(message)s, request_id=%(request_id)s, '
                               u'url=%(url)s, params=%(params)s, data=%(data)s, response=%(response)s') % {
                    'request_id': json_resp.get('request_id'),
                    'message': json_resp['message'],
                    'url': self.url,
                    'params': params,
                    'data': data,
                    'response': resp.text,
                }
                logger.error(log_message)

            # Return default return value
            if not json_resp and self.default_return_value is not None:
                return self.default_return_value
            return json_resp
        except Exception:
            raise ComponentAPIException(
                self, 'Return data format is incorrect, which shall be unified as json', resp=resp)
