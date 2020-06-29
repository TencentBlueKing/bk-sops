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


import logging

import requests
import curlify

logger = logging.getLogger("iam")


def _gen_header():
    headers = {
        "Content-Type": "application/json",
    }
    return headers


def _http_request(
    method, url, headers=None, data=None, verify=False, cert=None, timeout=None, cookies=None,
):
    resp = requests.Response()
    try:
        if method == "GET":
            resp = requests.get(
                url=url, headers=headers, params=data, verify=verify, cert=cert, timeout=timeout, cookies=cookies,
            )
        elif method == "HEAD":
            resp = requests.head(url=url, headers=headers, verify=verify, cert=cert, timeout=timeout, cookies=cookies,)
        elif method == "POST":
            resp = requests.post(
                url=url, headers=headers, json=data, verify=verify, cert=cert, timeout=timeout, cookies=cookies,
            )
        elif method == "DELETE":
            resp = requests.delete(
                url=url, headers=headers, json=data, verify=verify, cert=cert, timeout=timeout, cookies=cookies,
            )
        elif method == "PUT":
            resp = requests.put(
                url=url, headers=headers, json=data, verify=verify, cert=cert, timeout=timeout, cookies=cookies,
            )
        else:
            return False, None
    except requests.exceptions.RequestException:
        logger.exception("http error! request: [method=`%s`, url=`%s`, data=`%s`]", method, url, data)
        return False, None
    else:
        request_id = resp.headers.get("X-Request-Id")

        content = resp.content if resp.content else ""
        if not logger.isEnabledFor(logging.DEBUG) and len(content) > 200:
            content = content[:200] + b"......"

        message_format = (
            "request: [method=`%s`, url=`%s`, data=`%s`] response: [status_code=`%s`, request_id=`%s`, content=`%s`]"
        )

        if resp.status_code != 200:
            logger.error(message_format % (method, url, str(data), resp.status_code, request_id, content))
            return False, None

        logger.info(message_format % (method, url, str(data), resp.status_code, request_id, content))
        return True, resp.json()
    finally:
        if resp.request is None:
            resp.request = requests.Request(method, url, headers=headers, data=data, cookies=cookies).prepare()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "the request_id: `%s`. curl: `%s`",
                resp.headers.get("X-Request-Id", ""),
                curlify.to_curl(resp.request, verify=False),
            )


def http_get(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="GET", url=url, headers=headers, data=data, verify=verify, cert=cert, timeout=timeout, cookies=cookies,
    )


def http_post(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="POST", url=url, headers=headers, data=data, verify=verify, cert=cert, timeout=timeout, cookies=cookies,
    )


def http_put(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="PUT", url=url, headers=headers, data=data, verify=verify, cert=cert, timeout=timeout, cookies=cookies,
    )


def http_delete(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="DELETE",
        url=url,
        headers=headers,
        data=data,
        verify=verify,
        cert=cert,
        timeout=timeout,
        cookies=cookies,
    )
