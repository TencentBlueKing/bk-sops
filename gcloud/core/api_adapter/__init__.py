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

app_maker = importlib.import_module('gcloud.core.api_adapter.sites.%s.app_maker' % settings.RUN_VER)
user_role = importlib.import_module('gcloud.core.api_adapter.sites.%s.user_role' % settings.RUN_VER)
user_info = importlib.import_module('gcloud.core.api_adapter.sites.%s.user_info' % settings.RUN_VER)
business_location = importlib.import_module('gcloud.core.api_adapter.sites.%s.business_location' % settings.RUN_VER)

app_maker_funcs = ['create_maker_app', 'edit_maker_app', 'del_maker_app', 'modify_app_logo', 'get_app_logo_url']
for func_name in app_maker_funcs:
    locals()[func_name] = getattr(app_maker, func_name)

user_role_funcs = ['get_operate_user_list', 'get_auditor_user_list', 'is_user_functor', 'is_user_auditor']
for func_name in user_role_funcs:
    locals()[func_name] = getattr(user_role, func_name)

user_info_funcs = ['get_user_info', 'get_all_users']
for func_name in user_info_funcs:
    locals()[func_name] = getattr(user_info, func_name)

business_location_funcs = ['fetch_business_location']
for func_name in business_location_funcs:
    locals()[func_name] = getattr(business_location, func_name)

__all__ = app_maker_funcs + user_role_funcs + user_info_funcs + business_location_funcs
