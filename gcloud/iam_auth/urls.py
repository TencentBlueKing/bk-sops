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

from django.conf.urls import url

from gcloud.iam_auth import api

urlpatterns = [
    url(r"^meta/$", api.meta_info),
    url(r"^apply_perms_url/$", api.apply_perms_url),
    url(r"^is_allow/$", api.is_allow),
    url(r"^is_view_action_allow/$", api.is_view_action_allow),
    url(r"^is_allow/common_flow_management/$", api.is_allow_common_flow_management),
]
