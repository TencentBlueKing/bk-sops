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

from django.utils.translation import ugettext_lazy as _


# 任务流程创建方式
TASK_CREATE_METHOD = [
    ('app', _(u"手动")),
    ('api', _(u"API网关")),
    ('app_maker', _(u"轻应用")),
    ('periodic', _(u"周期任务")),
    ('mobile', _(u"移动端")),
]

# 任务引用的流程模板来源
TEMPLATE_SOURCE = [
    ('business', _(u"业务流程")),
    ('common', _(u"公共流程")),
]
