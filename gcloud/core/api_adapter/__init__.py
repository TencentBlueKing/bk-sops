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
user_adapter = importlib.import_module('gcloud.core.api_adapter.sites.%s.user_adapter' % settings.RUN_VER)

for func_name in ['create_maker_app', 'edit_maker_app', 'del_maker_app', 'modify_app_logo', 'get_app_logo_url']:
    locals()[func_name] = getattr(app_maker, func_name)

for func_name in ['get_operate_user_list', 'get_auditor_user_list', 'is_user_functor', 'is_user_auditor']:
    locals()[func_name] = getattr(user_role, func_name)

for func_name in ['get_user_info']:
    locals()[func_name] = getattr(user_info, func_name)

for func_name in ['adapt_get_user_data']:
    locals()[func_name] = getattr(user_adapter, func_name)

__all__ = ['create_maker_app', 'edit_maker_app', 'del_maker_app', 'get_operate_user_list',
           'get_auditor_user_list', 'is_user_functor', 'is_user_auditor', 'modify_app_logo',
           'get_user_info', 'adapt_get_user_data', 'get_app_logo_url']
