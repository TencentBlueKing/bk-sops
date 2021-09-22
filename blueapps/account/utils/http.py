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

import json
import logging
import traceback

import requests
from django.http import QueryDict
from django.shortcuts import resolve_url
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from django.utils.translation import gettext_lazy as _

from blueapps.core.exceptions.base import ApiNetworkError, ApiResultError

logger = logging.getLogger("component")


def send(url, method, params, timeout=None, **kwargs):
    """
    统一请求处理，定制化参数， GET 参数使用 form-data，POST 参数使用 json 字符串，返回内容
    要求为 JSON 格式

    @exception
        ApiResultError：非 JSON 返回，抛出 ApiResultError
        ApiNetworkError： 请求服务端超时

    @param url：string，请求 URL
    @param method：string，请求方法，目前仅支持 GET、POST
    @param params：dict，请求参数 KV 结构
    @param timeout: float，服务器在 timeout 秒内没有应答，将会引发一个异常
    """
    session = requests.session()

    try:
        if method.upper() == "GET":
            response = session.request(
                method="GET", url=url, params=params, timeout=timeout, **kwargs
            )
        elif method.upper() == "POST":
            session.headers.update({"Content-Type": "application/json; chartset=utf-8"})
            response = session.request(
                method="POST",
                url=url,
                data=json.dumps(params),
                timeout=timeout,
                **kwargs
            )
        else:
            raise Exception(_(u"异常请求方式，%s") % method)
    except requests.exceptions.Timeout:
        err_msg = _(u"请求超时，url=%s，method=%s，params=%s，timeout=%s") % (
            url,
            method,
            params,
            timeout,
        )
        raise ApiNetworkError(err_msg)

    logger.debug(
        "请求记录, url={}, method={}, params={}, response={}".format(
            url, method, params, response
        )
    )

    if response.status_code != requests.codes.ok:
        err_msg = _(u"返回异常状态码，status_code=%s，url=%s，method=%s，" u"params=%s") % (
            response.status_code,
            url,
            method,
            json.dumps(params),
        )
        raise ApiResultError(err_msg)

    try:
        return response.json()
    except Exception:  # pylint: disable=broad-except
        err_msg = _(
            u"返回内容不符合 JSON 格式，url=%s，method=%s，params=%s，error=%s，" u"response=%s"
        ) % (
            url,
            method,
            json.dumps(params),
            traceback.format_exc(),
            response.text[:1000],
        )
        raise ApiResultError(err_msg)


def build_redirect_url(next_url, current_url, redirect_field_name, extra_args=None):
    """
    即将访问的 CUR_URL 页面， 加上下一步要跳转的 NEXT 页面
    @param {string} next_url 页面链接，比如 http://a.com/page1/
    @param {string} current_url
    """
    resolved_url = resolve_url(current_url)

    login_url_parts = list(urlparse(resolved_url))

    querystring = QueryDict(login_url_parts[4], mutable=True)
    querystring[redirect_field_name] = next_url

    if extra_args:
        querystring.update(extra_args)

    login_url_parts[4] = querystring.urlencode(safe="/")

    return urlunparse(login_url_parts)
