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

from . import api


urlpatterns = [
    url(r"^list/$", api.get_plugin_list),
    url(r"^detail_list/$", api.get_plugin_detail_list),
    url(r"^tags/$", api.get_plugin_tags),
    url(r"^meta/$", api.get_meta),
    url(r"^detail/$", api.get_plugin_detail),
    url(r"^logs/$", api.get_logs),
    url(r"^app_detail/$", api.get_plugin_app_detail),
    url(r"^data_api/(?P<plugin_code>.+?)/(?P<data_api_path>.+)$", api.get_plugin_api_data),
]
