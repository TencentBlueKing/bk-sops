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

from __future__ import absolute_import
import logging
import traceback

from requests import request
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.utils.boolrule import BoolRule
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, IntItemSchema, ObjectItemSchema, ArrayItemSchema
from pipeline.component_framework.component import Component

__group_name__ = _(u"蓝鲸服务(BK)")
logger = logging.getLogger(__name__)


class HttpRequestService(Service):

    def inputs_format(self):
        return [
            self.InputItem(name=_(u'HTTP 请求方法'),
                           key='bk_http_request_method',
                           type='string',
                           schema=StringItemSchema(description=_(u'HTTP 请求方法'))),
            self.InputItem(name=_(u'HTTP 请求目标地址'),
                           key='bk_http_request_url',
                           type='string',
                           schema=StringItemSchema(description=_(u'HTTP 请求目标地址'))),
            self.InputItem(name=_(u'HTTP 请求 header'),
                           key='bk_http_request_header',
                           type='array',
                           schema=ArrayItemSchema(
                               description=_(u'HTTP 请求头部列表'),
                               item_schema=ObjectItemSchema(
                                   description=_(u'单个头部信息'),
                                   property_schemas={'name': StringItemSchema(description=_(u'请求头名称')),
                                                     'value': StringItemSchema(description=_(u'请求头值'))}))),
            self.InputItem(name=_(u'HTTP 请求 body'),
                           key='bk_http_request_body',
                           type='string',
                           schema=StringItemSchema(description=_(u'HTTP 请求 body'))),
            self.InputItem(name=_(u'HTTP 请求超时时间'),
                           key='bk_http_request_timeout',
                           type='int',
                           schema=IntItemSchema(description=_(u'HTTP 请求超时时间'))),
            self.InputItem(name=_(u'HTTP 请求成功条件'),
                           key='bk_http_success_exp',
                           type='string',
                           schema=StringItemSchema(description=_(u'根据返回的 JSON 的数据来控制节点的成功或失败, '
                                                                 u'使用 resp 引用返回的 JSON 对象，例 resp.result==True')))
        ]

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'响应内容'),
                            key='data',
                            type='object',
                            schema=ObjectItemSchema(description=_(u'HTTP 请求响应内容，内部结构不固定'),
                                                    property_schemas={})),
            self.OutputItem(name=_(u'状态码'),
                            key='status_code',
                            type='int',
                            schema=IntItemSchema(description=_(u'HTTP 请求响应状态码')))]

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs('language'):
            translation.activate(parent_data.get_one_of_inputs('language'))

        method = data.inputs.bk_http_request_method
        url = data.inputs.bk_http_request_url
        body = data.inputs.bk_http_request_body
        request_header = data.inputs.bk_http_request_header
        timeout = abs(int(data.inputs.bk_http_timeout))
        success_exp = data.inputs.bk_http_success_exp.strip()
        other = {"headers": {}}

        if method.upper() not in ["GET", "HEAD"]:
            other["data"] = body.encode('utf-8')
            other["headers"] = {'Content-type': 'application/json'}

        if request_header:
            headers = {header['name']: header['value'] for header in request_header}
            other["headers"].update(headers)

        if timeout:
            other["timeout"] = timeout

        self.logger.info('send {} request to {}'.format(method, url))

        try:
            response = request(
                method=method,
                url=url,
                verify=False,
                **other
            )
        except Exception as e:
            err = _(u"请求异常，详细信息: {}")
            self.logger.error(err.format(traceback.format_exc()))
            data.outputs.ex_data = err.format(e)
            return False

        data.outputs.status_code = response.status_code

        try:
            resp = response.json()
        except Exception:
            try:
                content = response.content.decode(response.encoding)
                self.logger.error(u"response data is not a valid JSON: {}".format(content[:500]))
            except Exception:
                self.logger.error('response data is not a valid JSON')
            data.outputs.ex_data = _(u"请求响应数据格式非 JSON")
            return False

        data.outputs.data = resp

        if not (200 <= response.status_code < 300):
            err = _(u"请求失败，状态码: {}，响应: {}").format(response.status_code, resp)
            self.logger.error(err)
            data.outputs.ex_data = err
            return False

        if success_exp:
            try:
                rule = BoolRule(success_exp)
                if not rule.test(context={'resp': resp}):
                    data.outputs.ex_data = _(u'请求成功判定失败')
                    return False
            except Exception as e:
                err = _(u'请求成功条件判定出错: {}')
                self.logger.error(err.format(traceback.format_exc()))
                data.outputs.ex_data = err.format(e)
                return False

        return True


class HttpComponent(Component):
    name = _(u'HTTP 请求')
    desc = _(u"提示: 1.请求URL需要在当前网络下可以访问，否则会超时失败 "
             u"2.响应状态码在200-300(不包括300)之间，并且相应内容是 JSON 格式才会执行成功")
    code = 'bk_http_request'
    bound_service = HttpRequestService
    form = settings.STATIC_URL + 'components/atoms/bk/v1.0/http.js'
    version = 'v1.0'
