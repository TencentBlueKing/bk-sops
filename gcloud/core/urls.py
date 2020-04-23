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

from django.conf.urls import url, include
from django.views.i18n import javascript_catalog

from version_log import config as version_log_config

from gcloud.core import views, api, command

urlpatterns = [
    url(r'^$', views.home),
    url(r'^set_lang/$', views.set_language),

    url(r'^core/api/change_default_project/(?P<project_id>\d+)/$', api.change_default_project),
    url(r'^core/api/get_roles_and_personnel/(?P<biz_cc_id>\d+)/$', api.get_roles_and_personnel),

    url(r'^core/api/get_basic_info/$', api.get_basic_info),
    url(r'^core/api/query_apply_permission_url/$', api.query_apply_permission_url),
    url(r'^core/api/query_resource_verify_perms/$', api.query_resource_verify_perms),
    url(r'^core/api/get_user_list/$', api.get_user_list),
    url(r'^core/footer/$', api.get_footer),

    url(r'^core/get_cache_key/(?P<key>\w+)/$', command.get_cache_key),
    url(r'^core/delete_cache_key/(?P<key>\w+)/$', command.delete_cache_key),
    url(r'^core/get_settings/$', command.get_settings),

    # i18n
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog),

    # version log
    url(r'^{}'.format(version_log_config.ENTRANCE_URL), include('version_log.urls'))
]
