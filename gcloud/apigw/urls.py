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

from gcloud.apigw.views.claim_functionalization_task import claim_functionalization_task
from gcloud.apigw.views.create_periodic_task import create_periodic_task
from gcloud.apigw.views.create_task import create_task
from gcloud.apigw.views.fast_create_task import fast_create_task
from gcloud.apigw.views.get_common_template_info import get_common_template_info
from gcloud.apigw.views.get_common_template_list import get_common_template_list
from gcloud.apigw.views.get_periodic_task_info import get_periodic_task_info
from gcloud.apigw.views.get_periodic_task_list import get_periodic_task_list
from gcloud.apigw.views.get_plugin_list import get_plugin_list
from gcloud.apigw.views.get_task_list import get_task_list
from gcloud.apigw.views.get_task_detail import get_task_detail
from gcloud.apigw.views.get_task_node_data import get_task_node_data
from gcloud.apigw.views.get_task_node_detail import get_task_node_detail
from gcloud.apigw.views.get_task_status import get_task_status
from gcloud.apigw.views.get_template_info import get_template_info
from gcloud.apigw.views.get_template_list import get_template_list
from gcloud.apigw.views.get_template_schemes import get_template_schemes
from gcloud.apigw.views.get_user_project_detail import get_user_project_detail
from gcloud.apigw.views.get_user_project_list import get_user_project_list
from gcloud.apigw.views.import_common_template import import_common_template
from gcloud.apigw.views.modify_constants_for_periodic_task import modify_constants_for_periodic_task
from gcloud.apigw.views.modify_constants_for_task import modify_constants_for_task
from gcloud.apigw.views.modify_cron_for_periodic_task import modify_cron_for_periodic_task
from gcloud.apigw.views.node_callback import node_callback
from gcloud.apigw.views.operate_node import operate_node
from gcloud.apigw.views.operate_task import operate_task
from gcloud.apigw.views.plugin_proxy import dispatch_plugin_query
from gcloud.apigw.views.preview_task_tree import preview_task_tree
from gcloud.apigw.views.query_task_count import query_task_count
from gcloud.apigw.views.set_periodic_task_enabled import set_periodic_task_enabled
from gcloud.apigw.views.start_task import start_task
from gcloud.apigw.views.get_tasks_status import get_tasks_status
from gcloud.apigw.views.import_project_template import import_project_template

urlpatterns = [
    url(r"^dispatch_plugin_query/$", dispatch_plugin_query),
    url(r"^get_template_list/(?P<project_id>\d+)/$", get_template_list),
    url(r"^get_template_info/(?P<template_id>\d+)/(?P<project_id>\d+)/$", get_template_info,),
    url(r"^get_common_template_list/$", get_common_template_list),
    url(r"^get_common_template_info/(?P<template_id>\d+)/$", get_common_template_info),
    url(r"^create_task/(?P<template_id>\d+)/(?P<project_id>\d+)/$", create_task),
    url(r"^fast_create_task/(?P<project_id>\d+)/$", fast_create_task),
    url(r"^start_task/(?P<task_id>\d+)/(?P<project_id>\d+)/$", start_task),
    url(r"^operate_task/(?P<task_id>\d+)/(?P<project_id>\d+)/$", operate_task),
    url(r"^get_task_status/(?P<task_id>\d+)/(?P<project_id>\d+)/$", get_task_status),
    url(r"^query_task_count/(?P<project_id>\d+)/$", query_task_count),
    url(r"^get_periodic_task_list/(?P<project_id>\d+)/$", get_periodic_task_list),
    url(r"^get_periodic_task_info/(?P<task_id>\d+)/(?P<project_id>\d+)/$", get_periodic_task_info,),
    url(r"^create_periodic_task/(?P<template_id>\d+)/(?P<project_id>\d+)/$", create_periodic_task,),
    url(r"^set_periodic_task_enabled/(?P<task_id>\d+)/(?P<project_id>\d+)/$", set_periodic_task_enabled,),
    url(r"^modify_cron_for_periodic_task/(?P<task_id>\d+)/(?P<project_id>\d+)/$", modify_cron_for_periodic_task,),
    url(r"^modify_constants_for_task/(?P<task_id>\d+)/(?P<project_id>\d+)/$", modify_constants_for_task),
    url(
        r"^modify_constants_for_periodic_task/(?P<task_id>\d+)/(?P<project_id>\d+)/$",
        modify_constants_for_periodic_task,
    ),
    url(r"^get_task_list/(?P<project_id>\d+)/$", get_task_list),
    url(r"^get_task_detail/(?P<task_id>\d+)/(?P<project_id>\d+)/$", get_task_detail),
    url(r"^get_task_node_detail/(?P<task_id>\d+)/(?P<project_id>\d+)/$", get_task_node_detail,),
    url(r"^node_callback/(?P<task_id>\d+)/(?P<project_id>\d+)/$", node_callback),
    url(r"^import_common_template/$", import_common_template),
    url(r"^get_plugin_list/(?P<project_id>\d+)/$", get_plugin_list),
    url(r"^get_user_project_list/$", get_user_project_list),
    url(r"^get_user_project_detail/(?P<project_id>\d+)/$", get_user_project_detail),
    url(r"^get_template_schemes/(?P<project_id>\d+)/(?P<template_id>\d+)/$", get_template_schemes,),
    url(r"^preview_task_tree/(?P<project_id>\d+)/(?P<template_id>\d+)/$", preview_task_tree,),
    url(r"^get_task_node_data/(?P<project_id>\d+)/(?P<task_id>\d+)/$", get_task_node_data,),
    url(r"^operate_node/(?P<project_id>\d+)/(?P<task_id>\d+)/$", operate_node),
    url(r"^get_tasks_status/(?P<project_id>\d+)/$", get_tasks_status),
    url(r"^import_project_template/(?P<project_id>\d+)/$", import_project_template),
    url(r"^claim_functionalization_task/(?P<task_id>\d+)/(?P<project_id>\d+)/$", claim_functionalization_task),
]
