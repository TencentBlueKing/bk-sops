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

import base64
import hashlib
import hmac
import random
import urlparse
import time
import json
import logging

import httplib2
from django.conf import settings
from django.utils.http import urlencode
from django.utils.translation import ugettext as _


logger = logging.getLogger("root")


def compute_signature(method, host, url, params, secret_key):
    # 加密时80端口接口方使用get_host()获取不到80端口（其他端口可以）
    if host.endswith(':80'):
        host = host[:-3]
    params = '&'.join(['%s=%s' % (i, params[i]) for i in sorted(params)])
    message = '%s%s%s?%s' % (method, host, url, params)
    digest_make = hmac.new(str(secret_key), str(message), hashlib.sha1).digest()
    _signature = base64.b64encode(digest_make)
    return _signature


def http_request_workbench(url, http_method, data=None):
    """
            发起GET/POST等各种请求
    @note: httplib2的post里的数据值必须转成utf8编码
    @note: 优先选用django的querydict的urlencode, urllib的urlencode会出现编码问题。
    @note: 请求参数query中的参数项如果是json, 请不要传入python dict, 一定要传入json字符串, 否则服务端将无法解析json(单双引号问题)
    @return: 直接返回原始响应数据(包含result,data,message的字典)
    """
    if data is None:
        data = {}
    data = json.dumps(data)
    nonce = random.randint(1, 100000)
    timestamp = str(int(time.time()))

    # 签名校验通用参数
    query = {
        'app_code': settings.APP_CODE,
        'Nonce': nonce,
        'Timestamp': timestamp,
        'Data': data
    }

    url_parse = urlparse.urlparse(url)
    url_host = url_parse.netloc
    url_path = url_parse.path
    # 签名
    signature = compute_signature(http_method, url_host, url_path, query, settings.SECRET_KEY)
    query['Signature'] = signature
    query.pop('Data', None)
    query = urlencode(query)

    if http_method == 'POST':
        url = 'http://%s%s?%s' % (url_host, url_path, query)
        # post 请求 也需要在get参数中添加 signature 参数
        logger.info('httplib2.Http().request url, http_method, body, %s, %s, %s' % (
            url, http_method, data))
        resp, content = httplib2.Http().request(url, http_method, body=data)
    else:
        uri = '%s?%s' % (url, query) if query else url
        resp, content = httplib2.Http().request(uri, 'GET')

    if resp.status == 200:
        # 成功，返回content
        try:
            content_dict = json.loads(content)
            return content_dict
        except Exception:
            logger.error(_(u"请求返回数据格式错误!"))
            return {'result': 0, 'message': _(u"调用远程服务失败，Http请求返回数据格式错误!")}
    else:
        err = _(u"调用远程服务失败，Http请求错误状态码：%(code)s， 请求url：%(url)s") % {'code': resp.status, 'url': url}
        logger.error(err)
        return {'result': 0, 'message': err}
