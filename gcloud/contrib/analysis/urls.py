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
from gcloud.contrib.analysis import views

urlpatterns = [
    url(r'^query_instance_by_group/$', views.query_instance_by_group),
    url(r'^query_template_by_group/$', views.query_template_by_group),
    url(r'^query_atom_by_group/$', views.query_atom_by_group),
    url(r'^query_appmaker_by_group/$', views.query_appmaker_by_group),
    url(r'^template/$', views.analysis_home),
    url(r'^instance/$', views.analysis_home),
    url(r'^appmaker/$', views.analysis_home),
    url(r'^atom/$', views.analysis_home),
    url(r'^get_task_category/$', views.get_task_category),
]
