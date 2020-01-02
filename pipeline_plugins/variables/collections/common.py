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

from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.core.data.var import (
    SpliceVariable,
    LazyVariable,
    RegisterVariableMeta
)

logger = logging.getLogger('root')


class CommonPlainVariable(SpliceVariable):
    __metaclass__ = RegisterVariableMeta


class Input(CommonPlainVariable):
    code = 'input'
    name = _(u"输入框")
    type = 'general'
    tag = 'input.input'
    form = '%svariables/%s.js' % (settings.STATIC_URL, code)


class Textarea(CommonPlainVariable):
    code = 'textarea'
    name = _(u"文本框")
    type = 'general'
    tag = 'textarea.textarea'
    form = '%svariables/%s.js' % (settings.STATIC_URL, code)


class Datetime(CommonPlainVariable):
    code = 'datetime'
    name = _(u"日期时间")
    type = 'general'
    tag = 'datetime.datetime'
    form = '%svariables/%s.js' % (settings.STATIC_URL, code)


class Int(CommonPlainVariable):
    code = 'int'
    name = _(u"整数")
    type = 'general'
    tag = 'int.int'
    form = '%svariables/%s.js' % (settings.STATIC_URL, code)


class Password(LazyVariable):
    code = 'password'
    name = _(u"密码")
    type = 'general'
    tag = 'password.password'
    form = '%svariables/%s.js' % (settings.STATIC_URL, code)

    def get_value(self):
        return self.value


class Select(LazyVariable):
    code = 'select'
    name = _(u"下拉框")
    type = 'meta'
    tag = 'select.select'
    meta_tag = 'select.select_meta'
    form = '%svariables/%s.js' % (settings.STATIC_URL, code)

    def get_value(self):
        # multiple select
        if isinstance(self.value, list):
            return ','.join(self.value)
        # single select
        else:
            return self.value
