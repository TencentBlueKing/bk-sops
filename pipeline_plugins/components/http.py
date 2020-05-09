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

import requests
import ujson as json
import traceback

HTTP_GET = 'get'
HTTP_POST = 'post'


def post(url, params, logger, headers=None):
    return http_do('post', url, params, logger, headers)


def get(url, params, logger, headers=None):
    return http_do('get', url, params, logger, headers)


def http_do(method, url, params, logger, headers=None):
    session_request = requests.Session()
    if headers:
        headers.update({'Content-Type': 'application/json'})
        session_request.headers = headers
    else:
        session_request.headers = {'Content-Type': 'application/json'}
    try:
        if method == 'get':
            resp = getattr(session_request, 'get')(url, params=params)
        else:
            resp = getattr(session_request, 'post')(url, data=json.dumps(params))
    except Exception as e:
        logger.error(traceback.format_exc())
        return False, {'result': False, 'message': str(e)}

    if not resp.ok:
        return False, {'result': False, 'message': 'request error, status code: {}'.format(resp.status_code)}

    try:
        json_data = resp.json()
    except Exception as e:
        logger.error(traceback.format_exc())
        return False, {'result': False, 'message': str(e)}

    return True, json_data
