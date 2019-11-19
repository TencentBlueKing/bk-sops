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

import importlib

from django.conf import settings

common_utils = importlib.import_module('gcloud.core.utils.common')
common_exports = [
    'name_handler',
    'pipeline_node_name_handle',
    'camel_case_to_underscore_naming',
    'timestamp_to_datetime',
    'format_datetime',
    'gen_day_dates',
    'get_month_dates',
    'time_now_str',
    'check_and_rename_params',
    'apply_permission_url'
]
for func in common_exports:
    locals()[func] = getattr(common_utils, func)

ver_utils = importlib.import_module('gcloud.core.utils.sites.%s.utils' % settings.RUN_VER)
ver_exports = [
    'convert_group_name',
    'convert_readable_username',
    'get_user_business_list',
    'get_all_business_list'
]
for func in ver_exports:
    locals()[func] = getattr(ver_utils, func)

__all__ = common_exports + ver_exports
