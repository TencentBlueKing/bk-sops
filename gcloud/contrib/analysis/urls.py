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

from django.urls import path, re_path

from gcloud.contrib.analysis import views

urlpatterns = [
    re_path(r"^query_instance_by_group/$", views.query_instance_by_group),
    re_path(r"^query_template_by_group/$", views.query_template_by_group),
    re_path(r"^query_atom_by_group/$", views.query_atom_by_group),
    re_path(r"^query_appmaker_by_group/$", views.query_appmaker_by_group),
    re_path(r"^template/$", views.analysis_home),
    re_path(r"^instance/$", views.analysis_home),
    re_path(r"^appmaker/$", views.analysis_home),
    re_path(r"^atom/$", views.analysis_home),
    re_path(r"^get_task_category/$", views.get_task_category),
    re_path(r"^get_biz_useage/(?P<query>\w+)/$", views.get_biz_useage),
    path(r"get_component_list/", views.get_component_list),
]
