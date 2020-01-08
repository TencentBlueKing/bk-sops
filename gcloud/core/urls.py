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

from django.conf.urls import url
from django.views.i18n import javascript_catalog

from gcloud.core import views, api, command

urlpatterns = [
    url(r'^$', views.home),
    url(r'^business/home/(?P<biz_cc_id>\d+)/$', views.biz_home),
    url(r'^set_lang/$', views.set_language),

    url(r'^core/api/get_basic_info/$', api.get_basic_info),
    url(r'^core/api/change_default_business/(?P<biz_cc_id>\d+)/$', api.change_default_business),
    url(r'^core/api/get_roles_and_personnel/(?P<biz_cc_id>\d+)/$', api.get_roles_and_personnel),

    url(r'^core/get_cache_key/(?P<key>\w+)/$', command.get_cache_key),
    url(r'^core/delete_cache_key/(?P<key>\w+)/$', command.delete_cache_key),
    url(r'^core/get_settings/$', command.get_settings),

    # i18n
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog),
]
