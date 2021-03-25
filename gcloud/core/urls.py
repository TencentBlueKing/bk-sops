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


from django.conf.urls import include, url

try:
    from django.views.i18n import JavaScriptCatalog

    javascript_catalog = JavaScriptCatalog.as_view()
except ImportError:  # Django < 2.0
    from django.views.i18n import javascript_catalog

from blueapps.account.decorators import login_exempt
from gcloud.core import api, views
from gcloud.iam_auth.resource_api import dispatcher
from version_log import config as version_log_config

urlpatterns = [
    url(r"^$", views.home),
    url(r"^set_lang/$", views.set_language),
    url(r"^core/api/change_default_project/(?P<project_id>\d+)/$", api.change_default_project),
    url(r"^core/api/get_roles_and_personnel/(?P<biz_cc_id>\d+)/$", api.get_roles_and_personnel),
    url(r"^core/api/get_basic_info/$", api.get_basic_info),
    url(r"^core/api/get_user_list/$", api.get_user_list),
    url(r"^core/footer/$", api.get_footer),
    url(r"^core/api/get_user_list/$", api.get_user_list),
    url(r"^core/api/get_msg_types/$", api.get_msg_types),
    url(r"^core/healthz", api.healthz),
    # i18n
    url(r"^jsi18n/(?P<packages>\S+?)/$", javascript_catalog),
    # version log
    url(r"^{}".format(version_log_config.ENTRANCE_URL), include("version_log.urls")),
    # iam resource api
    url(r"^iam/resource/api/v1/$", dispatcher.as_view([login_exempt])),
    # iam api
    url(r"^iam/api/", include("gcloud.iam_auth.urls")),
]
