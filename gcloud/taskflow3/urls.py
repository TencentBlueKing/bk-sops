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

from django.conf.urls import include, url
from django.urls import path

from gcloud.taskflow3.apis.django import api
from gcloud.taskflow3.apis.django.v4.urls import v4_urlpatterns
from gcloud.taskflow3.apis.drf.viewsets.engine_v2_node_log import EngineV2NodeLogView
from gcloud.taskflow3.apis.drf.viewsets.preview_task_tree import PreviewTaskTreeWithSchemesView
from gcloud.taskflow3.apis.drf.viewsets.render_current_constants import RenderCurrentConstantsView
from gcloud.taskflow3.apis.drf.viewsets.update_task_constants import UpdateTaskConstantsView

urlpatterns = [
    url(r"^api/context/$", api.context),
    url(r"^api/status/(?P<project_id>\d+)/$", api.status),
    url(r"^api/batch_status/(?P<project_id>\d+)/$", api.batch_status),
    url(r"^api/clone/(?P<project_id>\d+)/$", api.task_clone),
    url(r"^api/action/(?P<action>\w+)/(?P<project_id>\d+)/$", api.task_action),
    url(r"^api/flow/claim/(?P<project_id>\d+)/$", api.task_func_claim),
    url(r"^api/nodes/action/(?P<action>\w+)/(?P<project_id>\d+)/$", api.nodes_action),
    url(r"^api/nodes/data/(?P<project_id>\d+)/$", api.data),
    url(r"^api/nodes/detail/(?P<project_id>\d+)/$", api.detail),
    url(r"^api/nodes/get_job_instance_log/(?P<biz_cc_id>\d+)/$", api.get_job_instance_log),
    url(r"^api/nodes/spec/timer/reset/(?P<project_id>\d+)/$", api.spec_nodes_timer_reset),
    url(r"^api/preview_task_tree/(?P<project_id>\d+)/$", api.preview_task_tree),
    url(r"^api/query_task_count/(?P<project_id>\d+)/$", api.query_task_count),
    url(r"^api/nodes/log/(?P<project_id>\d+)/(?P<node_id>\w+)/$", api.get_node_log),
    url(r"^api/get_task_create_method/$", api.get_task_create_method),
    url(r"^api/nodes/callback/(?P<token>.+)/$", api.node_callback),
    url(r"^api/v4/", include(v4_urlpatterns)),
    path(r"api/render_current_constants/<int:task_id>/", RenderCurrentConstantsView.as_view()),
    path(
        r"api/engine_v2/node_log/<int:project_id>/<int:task_id>/<str:node_id>/<str:version>/",
        EngineV2NodeLogView.as_view(),
    ),
    path(r"api/preview_task_tree_with_schemes/", PreviewTaskTreeWithSchemesView.as_view()),
    path(r"api/update_task_constants/<int:task_id>/", UpdateTaskConstantsView.as_view()),
]
