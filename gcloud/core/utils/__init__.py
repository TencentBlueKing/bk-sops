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

import importlib

from django.conf import settings

utils = importlib.import_module('gcloud.core.utils.sites.%s.utils' % settings.RUN_VER)

export_func = {'prepare_user_business',
               'prepare_business',
               'convert_group_name',
               'strftime_with_timezone',
               'get_biz_maintainer_info',
               'convert_readable_username',
               'timestamp_to_datetime',
               'format_datetime',
               'camel_case_to_underscore_naming',
               'gen_day_dates',
               'get_month_dates',
               'get_business_obj',
               'time_now_str',
               'check_and_rename_params',
               'get_client_by_user_and_biz_id',
               'name_handler',
               'prepare_view_all_business'}

for func in export_func:
    locals()[func] = getattr(utils, func)

__all__ = export_func
