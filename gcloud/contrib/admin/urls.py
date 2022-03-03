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

from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from gcloud.contrib.admin import views, migration_api
from gcloud.contrib.admin.viewsets import (
    PeriodicTaskHistoryViewSet,
    AdminTaskFlowInstanceViewSet,
    AdminPeriodicTaskViewSet,
    AdminTaskTemplateViewSet,
)

v3_drf_api = DefaultRouter()
v3_drf_api.register(r"periodic_task_history", PeriodicTaskHistoryViewSet)
v3_drf_api.register(r"taskflow", AdminTaskFlowInstanceViewSet)
v3_drf_api.register(r"template", AdminTaskTemplateViewSet)
v3_drf_api.register(r"periodic_task", AdminPeriodicTaskViewSet)


urlpatterns = [
    url(r"^api/v3/", include(v3_drf_api.urls)),
    url(r"^template/restore", views.restore_template),
    url(r"^template/refresh_template_notify_type/$", views.refresh_template_notify_type),
    url(r"^template/make_template_notify_type_loadable/$", views.make_template_notify_type_loadable),
    url(r"^taskflow/detail", views.get_taskflow_detail),
    url(r"^taskflow/node/detail", views.get_taskflow_node_detail),
    url(r"^taskflow/node/history/log", views.get_node_history_log),
    url(r"^taskflow/node/force_fail", views.force_fail_node),
    url(r"^search", views.search),
    url(r"^command/get_cache_key/(?P<key>\w+)/$", views.get_cache_key),
    url(r"^command/delete_cache_key/(?P<key>\w+)/$", views.delete_cache_key),
    url(r"^command/get_settings/$", views.get_settings),
    url(r"^command/upsert_iam_system_provider_config/$", views.upsert_iam_system_provider_config),
    url(r"^command/migrate_pipeline_parent_data/$", views.migrate_pipeline_parent_data),
    url(r"^migration/register_resource_config/$", migration_api.register_resource_config),
    url(r"^migration/migrate_app_maker/$", migration_api.migrate_app_maker),
    url(r"^migration/migrate_staff_group/$", migration_api.migrate_staff_group),
    url(r"^migration/migrate_template_category/$", migration_api.migrate_template_category),
    url(r"^migration/fix_engine_version_zero_task/$", migration_api.fix_engine_version_zero_task),
]
