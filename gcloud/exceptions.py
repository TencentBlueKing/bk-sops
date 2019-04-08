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

from django.utils.translation import ugettext_lazy as _


class Unauthorized(Exception):
    pass


class Forbidden(Exception):
    pass


class NotFound(Exception):
    pass


class APIError(Exception):

    def __init__(self, system, api, message):
        self.system = system
        self.api = api
        self.message = message

    @property
    def error(self):
        return u'%s【%s】%s【%s】%s【%s】%s' % (
            _(u'请求第三方系统'),
            self.system,
            _(u'接口'),
            self.api,
            _(u'异常'),
            self.message,
            _(u'请联系第三方系统负责人处理'))


class BadTaskOperation(Exception):
    pass


class BadResourceClass(Exception):
    pass


class FlowExportError(Exception):
    pass
