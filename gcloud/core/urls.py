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
from blueapps.account.decorators import login_exempt
from django.apps import apps
from django.urls import include, re_path
from django.views.i18n import JavaScriptCatalog
from version_log import config as version_log_config

from gcloud.core import api, views
from gcloud.iam_auth.resource_api import dispatcher

javascript_catalog = JavaScriptCatalog.as_view(
    packages=[app_config.name for app_config in apps.get_app_configs() if app_config.name.startswith("gcloud")]
)


urlpatterns = [
    re_path(r"^$", views.home),
    re_path(r"^logout$", views.user_exit),
    re_path(r"^core/api/change_default_project/(?P<project_id>\d+)/$", api.change_default_project),
    re_path(r"^core/api/get_roles_and_personnel/(?P<biz_cc_id>\d+)/$", api.get_roles_and_personnel),
    re_path(r"^core/api/get_basic_info/$", api.get_basic_info),
    re_path(r"^core/footer/$", api.get_footer),
    re_path(r"^core/footer_info/$", api.get_footer_info),
    re_path(r"^core/api/get_user_list/$", api.get_user_list),
    re_path(r"^core/api/get_msg_types/$", api.get_msg_types),
    re_path(r"^core/healthz", api.healthz),
    re_path(r"^core/api/check_variable_key", api.check_variable_key),
    # i18n
    re_path(r"^jsi18n/gcloud/$", javascript_catalog),
    # version log
    re_path(r"^{}".format(version_log_config.ENTRANCE_URL), include("version_log.urls")),
    # iam resource api
    re_path(r"^iam/resource/api/v1/$", dispatcher.as_view([login_exempt])),
    # iam api
    re_path(r"^iam/api/", include("gcloud.iam_auth.urls")),
    # django prom
    re_path(r"^metrics/$", views.metrics),
]
