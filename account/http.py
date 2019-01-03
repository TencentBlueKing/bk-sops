# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
请求登录的http基础方法

Rules:
1. POST/DELETE/PUT: json in - json out, 如果resp.json报错, 则是登录接口问题
2. GET带参数 HEAD不带参数
3. 以统一的header头发送请求
"""

import requests

from django.conf import settings

from common.log import logger


def _gen_header():
    headers = {
        "Content-Type": "application/json",
        "X-APP-CODE": settings.APP_ID,
        "X-APP-TOKEN": settings.APP_TOKEN,
    }
    return headers


def _http_request(method, url, headers=None, data=None):
    try:
        if method == "GET":
            resp = requests.get(url=url, headers=headers, params=data, verify=False)
        elif method == "HEAD":
            resp = requests.head(url=url, headers=headers, verify=False)
        elif method == "POST":
            resp = requests.post(url=url, headers=headers, json=data, verify=False)
        elif method == "DELETE":
            resp = requests.delete(url=url, headers=headers, json=data, verify=False)
        elif method == "PUT":
            resp = requests.put(url=url, headers=headers, json=data, verify=False)
        else:
            return False, None
    # except requests.exceptions.RequestException:  # no catch at all
    except requests.exceptions.MissingSchema:
        logger.exception("login http request error! type: %s, url: %s, data: %s" % (method, url, str(data)))
        return False, None
    else:
        if resp.status_code != 200:
            content = resp.content[:100] if resp.content else ''
            logger.error("login http request error! type: %s, url: %s, data: %s, response_status_code: %s, response_content: %s"
                         % (method, url, str(data), resp.status_code, content))
            return False, None

        return True, resp.json()


def http_get(url, data):
    headers = _gen_header()
    return _http_request(method="GET", url=url, headers=headers, data=data)


def http_post(url, data):
    headers = _gen_header()
    return _http_request(method="POST", url=url, headers=headers, data=data)


def http_delete(url, data):
    headers = _gen_header()
    return _http_request(method="DELETE", url=url, headers=headers, data=data)
