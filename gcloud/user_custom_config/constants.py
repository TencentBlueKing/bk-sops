# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.utils.translation import ugettext_lazy as _


TASKTMPL_ORDERBY_OPTIONS = [
    {"name": _("模板ID"), "value": "id"},
    {"name": _("创建时间"), "value": "pipeline_template__create_time"},
    {"name": _("更新时间"), "value": "pipeline_template__edit_time"},
    {"name": _("模板类型"), "value": "category"},
]

UserConfOption = {
    "task_template_ordering": TASKTMPL_ORDERBY_OPTIONS,
}


def get_options_by_fileds(configs=None):
    data = {}
    if not configs:
        return UserConfOption
    for key in configs:
        data[key] = UserConfOption[key]
    return data
