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

from django.conf.urls import url

from blueapps.account import views

app_name = "account"  # pylint: disable=invalid-name

urlpatterns = [
    url(r"^login_success/$", views.login_success, name="login_success"),
    url(r"^login_page/$", views.login_page, name="login_page"),
    url(r"^send_code/$", views.send_code_view, name="send_code"),
    url(r"^get_user_info/$", views.get_user_info, name="get_user_info"),
]
