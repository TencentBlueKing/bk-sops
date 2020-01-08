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

from gcloud.apigw import views

urlpatterns = [
    url(r'^get_template_list/(?P<bk_biz_id>\d+)/$', views.get_template_list),
    url(r'^get_template_info/(?P<template_id>\d+)/(?P<bk_biz_id>\d+)/$', views.get_template_info),
    url(r'^get_common_template_list/$', views.get_common_template_list),
    url(r'^get_common_template_info/(?P<template_id>\d+)/$', views.get_common_template_info),
    url(r'^create_task/(?P<template_id>\d+)/(?P<bk_biz_id>\d+)/$', views.create_task),
    url(r'^start_task/(?P<task_id>\d+)/(?P<bk_biz_id>\d+)/$', views.start_task),
    url(r'^operate_task/(?P<task_id>\d+)/(?P<bk_biz_id>\d+)/$', views.operate_task),
    url(r'^get_task_status/(?P<task_id>\d+)/(?P<bk_biz_id>\d+)/$', views.get_task_status),
    url(r'^query_task_count/(?P<bk_biz_id>\d+)/$', views.query_task_count),
    url(r'^get_periodic_task_list/(?P<bk_biz_id>\d+)/$', views.get_periodic_task_list),
    url(r'^get_periodic_task_info/(?P<task_id>\d+)/(?P<bk_biz_id>\d+)/$', views.get_periodic_task_info),
    url(r'^create_periodic_task/(?P<template_id>\d+)/(?P<bk_biz_id>\d+)/$', views.create_periodic_task),
    url(r'^set_periodic_task_enabled/(?P<task_id>\d+)/(?P<bk_biz_id>\d+)/$', views.set_periodic_task_enabled),
    url(r'^modify_cron_for_periodic_task/(?P<task_id>\d+)/(?P<bk_biz_id>\d+)/$', views.modify_cron_for_periodic_task),
    url(r'^modify_constants_for_periodic_task/(?P<task_id>\d+)/(?P<bk_biz_id>\d+)/$',
        views.modify_constants_for_periodic_task),
    url(r'^get_task_detail/(?P<task_id>\d+)/(?P<bk_biz_id>\d+)/$', views.get_task_detail),
    url(r'^get_task_node_detail/(?P<task_id>\d+)/(?P<bk_biz_id>\d+)/$', views.get_task_node_detail),
    url(r'^node_callback/(?P<task_id>\d+)/(?P<bk_biz_id>\d+)/$', views.node_callback),
    url(r'^import_common_template/$', views.import_common_template),
]
