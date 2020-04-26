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
from tastypie.api import Api

from gcloud.contrib.admin import views

from gcloud.contrib.admin.resources import (
    AdminTaskTemplateResource,
    AdminTaskFlowInstanceResource,
    AdminPeriodicTaskResource,
    AdminPeriodicTaskHistoryResource,
)

v3_api = Api(api_name='v3')
v3_api.register(AdminTaskTemplateResource())
v3_api.register(AdminTaskFlowInstanceResource())
v3_api.register(AdminPeriodicTaskResource())
v3_api.register(AdminPeriodicTaskHistoryResource())

urlpatterns = [
    url(r'^api/', include(v3_api.urls)),
    url(r'^template/restore', views.restore_template),
    url(r'^taskflow/detail', views.get_taskflow_detail),
    url(r'^taskflow/node/detail', views.get_taskflow_node_detail),
    url(r'^taskflow/node/history/log', views.get_node_history_log),
    url(r'^taskflow/node/force_fail', views.force_fail_node),
    url(r'^search', views.search),
]
