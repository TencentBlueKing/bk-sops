# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import importlib

from django.conf import settings

ver_utils = importlib.import_module("gcloud.core.utils.sites.%s.utils" % settings.RUN_VER)
ver_exports = [
    "convert_group_name",
    "convert_readable_username",
    "get_user_business_list",
    "get_all_business_list",
    "get_user_business_detail",
]
for func in ver_exports:
    locals()[func] = getattr(ver_utils, func)

__all__ = ver_exports
