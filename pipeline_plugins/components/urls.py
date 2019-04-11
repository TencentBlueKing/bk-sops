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

from django.conf.urls import url

from pipeline_plugins.components import query
from pipeline_plugins.components.query import common_query

urlpatterns = [
    url(r'^cc_get_set_list/(?P<biz_cc_id>\d+)/$', common_query.cc_get_set_list),
    url(r'^cc_get_module_name_list/(?P<biz_cc_id>\d+)/$', common_query.cc_get_module_name_list),
    url(r'^cc_get_plat_id/(?P<biz_cc_id>\d+)/$', common_query.cc_get_plat_id),
]
urlpatterns += query.urlpatterns
