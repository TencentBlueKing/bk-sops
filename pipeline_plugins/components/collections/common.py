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

from __future__ import absolute_import
import logging

import requests
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component

__group_name__ = _(u"蓝鲸服务(BK)")
logger = logging.getLogger(__name__)


class HttpRequestService(Service):

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs('language'):
            translation.activate(parent_data.get_one_of_inputs('language'))

        method = data.get_one_of_inputs('bk_http_request_method')
        url = data.get_one_of_inputs('bk_http_request_url')
        body = data.get_one_of_inputs('bk_http_request_body')
        other = {

        }

        if method.upper() not in ["GET", "HEAD"]:
            other["data"] = body.encode('utf-8')
            other["headers"] = {'Content-type': 'application/json'}

        self.logger.info('send %s request to %s' % (method, url))

        try:
            response = requests.request(
                method=method,
                url=url,
                verify=False,
                **other
            )
        except Exception as e:
            self.logger.error('request error: %s' % str(e))
            data.set_outputs('ex_data', _(u"请求异常，详细信息: %s") % str(e))
            return False

        try:
            resp = response.json()
        except Exception:
            try:
                content = response.content.decode(response.encoding)
                self.logger.error(u"response data is not a valid JSON: %s" % content[:500])
            except Exception:
                self.logger.error('response data is not a valid JSON')
            data.set_outputs('ex_data', _(u"请求响应数据格式非 JSON"))
            data.set_outputs('status_code', response.status_code)
            return False

        if not (200 <= response.status_code < 300):
            self.logger.error('request error with status code: %s, response %s' % (response.status_code, response))
            data.set_outputs('ex_data', _(u"请求失败，状态码: %s，响应: %s") % (response.status_code, resp))
            data.set_outputs('status_code', response.status_code)
            return False

        data.set_outputs('data', resp)
        data.set_outputs('status_code', response.status_code)
        return True

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'响应内容'), key='data', type='str'),
            self.OutputItem(name=_(u'状态码'), key='status_code', type='int')
        ]


class HttpComponent(Component):
    name = _(u'HTTP 请求')
    desc = _(u"提示: 1.请求URL需要在当前网络下可以访问，否则会超时失败 "
             u"2.响应状态码在200-300(不包括300)之间，并且相应内容是 JSON 格式才会执行成功")
    code = 'bk_http_request'
    bound_service = HttpRequestService
    form = settings.STATIC_URL + 'components/atoms/bk/http.js'
