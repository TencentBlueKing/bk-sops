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


VARIABLES_COLLECTION = [
    {'name': _(u"输入框"), 'key': 'input', 'type': 'general'},
    {'name': _(u"文本框"), 'key': 'textarea', 'type': 'general'},
    {'name': _(u"日期时间"), 'key': 'datetime', 'type': 'general'},
    {'name': _(u"整数"), 'key': 'int', 'type': 'general'},
    {'name': _(u"IP选择器(简单版)"), 'key': 'ip', 'type': 'general'},
    {'name': _(u"IP选择器"), 'key': 'ip_selector', 'type': 'general'},
    {'name': _(u"密码"), 'key': 'password', 'type': 'general'},
    {'name': _(u"下拉框"), 'key': 'select', 'type': 'meta'},
]
