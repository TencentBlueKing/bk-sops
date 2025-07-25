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

from django.urls import re_path

from gcloud.periodictask import api

urlpatterns = [
    re_path(r"^api/enabled/(?P<project_id>\d+)/(?P<task_id>\d+)/$", api.set_enabled_for_periodic_task),
    re_path(r"^api/cron/(?P<project_id>\d+)/(?P<task_id>\d+)/$", api.modify_cron),
    re_path(r"^api/constants/(?P<project_id>\d+)/(?P<task_id>\d+)/$", api.modify_constants),
]
