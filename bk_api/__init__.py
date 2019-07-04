# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import importlib

from django.conf import settings

app_maker = importlib.import_module('bk_api.sites.%s.app_maker' % settings.RUN_VER)
user_role = importlib.import_module('bk_api.sites.%s.user_role' % settings.RUN_VER)

for func_name in ['create_maker_app', 'edit_maker_app', 'del_maker_app', 'modify_app_logo']:
    locals()[func_name] = getattr(app_maker, func_name)

for func_name in ['get_operate_user_list', 'get_auditor_user_list', 'is_user_functor', 'is_user_auditor']:
    locals()[func_name] = getattr(user_role, func_name)

__all__ = ['create_maker_app', 'edit_maker_app', 'del_maker_app', 'get_operate_user_list',
           'get_auditor_user_list', 'is_user_functor', 'is_user_auditor', 'modify_app_logo']
