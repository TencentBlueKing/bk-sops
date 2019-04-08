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

import requests
import ujson as json
import traceback


def post(url, params, logger):
    return http_do('post', url, params, logger)


def get(url, params, logger):
    return http_do('get', url, params, logger)


def http_do(method, url, params, logger):
    try:
        resp = getattr(requests, method)(url, data=json.dumps(params))
    except Exception as e:
        logger.error(traceback.format_exc())
        return False, {'result': False, 'message': e.message}

    if not resp.ok:
        return False, {'result': False, 'message': 'request error, status code: {}'.format(resp.status_code)}

    try:
        json_data = resp.json()
    except Exception as e:
        logger.error(traceback.format_exc())
        return False, {'result': False, 'message': e.message}

    return True, json_data
