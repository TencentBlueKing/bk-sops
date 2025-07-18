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

from gcloud.contrib.appmaker import api, views

urlpatterns = [
    # 新建、编辑轻应用
    re_path(r"^save/(?P<project_id>\d+)/$", api.save),
    # mini-app 内链接
    # 打开一个轻应用，直接进入参数填写阶段
    re_path(r"^(?P<app_id>\d+)/newtask/(?P<project_id>\d+)/selectnode/$", views.newtask_selectnode),
    re_path(r"^(?P<app_id>\d+)/newtask/(?P<project_id>\d+)/paramfill/$", views.newtask_paramfill),
    # 从轻应用的任务记录跳转到任务详情
    re_path(r"^(?P<app_id>\d+)/execute/(?P<project_id>\d+)/$", views.execute),
    # 轻应用中任务列表
    re_path(r"^(?P<app_id>\d+)/task_home/(?P<project_id>\d+)/$", views.task_home),
    re_path(r"^get_appmaker_count/(?P<project_id>\d+)/$", api.get_appmaker_count),
]
