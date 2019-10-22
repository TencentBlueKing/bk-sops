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


class BkSopsError(Exception):
    pass


class Unauthorized(BkSopsError):
    pass


class Forbidden(BkSopsError):
    pass


class NotFound(BkSopsError):
    pass


class APIError(BkSopsError):

    def __init__(self, system, api, message, result=None):
        self.system = system
        self.api = api
        self.message = message
        self.result = result
        super(APIError, self).__init__(message)

    @property
    def error(self):
        return '%s【%s】%s【%s】%s【%s】%s' % (
            _('请求第三方系统'),
            self.system,
            _('接口'),
            self.api,
            _('异常'),
            self.message,
            _('请联系第三方系统负责人处理'))


class BadTaskOperation(BkSopsError):
    pass


class BadResourceClass(BkSopsError):
    pass


class FlowExportError(BkSopsError):
    pass
