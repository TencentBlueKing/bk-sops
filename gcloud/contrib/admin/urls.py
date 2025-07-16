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

from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from gcloud.contrib.admin import migration_api, views
from gcloud.contrib.admin.views import (
    batch_delete_project_based_component,
    batch_insert_project_based_component,
    batch_revoke_task,
)
from gcloud.contrib.admin.viewsets import (
    AdminPeriodicTaskViewSet,
    AdminTaskFlowInstanceViewSet,
    AdminTaskTemplateViewSet,
    PeriodicTaskHistoryViewSet,
)

v3_drf_api = DefaultRouter()
v3_drf_api.register(r"periodic_task_history", PeriodicTaskHistoryViewSet)
v3_drf_api.register(r"taskflow", AdminTaskFlowInstanceViewSet)
v3_drf_api.register(r"template", AdminTaskTemplateViewSet)
v3_drf_api.register(r"periodic_task", AdminPeriodicTaskViewSet)


urlpatterns = [
    re_path(r"^api/v3/", include(v3_drf_api.urls)),
    re_path(r"^template/restore", views.restore_template),
    re_path(r"^template/refresh_template_notify_type/$", views.refresh_template_notify_type),
    re_path(r"^template/make_template_notify_type_loadable/$", views.make_template_notify_type_loadable),
    re_path(r"^taskflow/upsert_context", views.upsert_taskflow_v2_context),
    re_path(r"^taskflow/detail", views.get_taskflow_v1_detail),
    re_path(r"^taskflow/node/detail", views.get_taskflow_v1_node_detail),
    re_path(r"^taskflow/node/history/log", views.get_node_v1_history_log),
    re_path(r"^search", views.search),
    re_path(r"^command/get_cache_key/(?P<key>\w+)/$", views.get_cache_key),
    re_path(r"^command/delete_cache_key/(?P<key>\w+)/$", views.delete_cache_key),
    re_path(r"^command/get_settings/$", views.get_settings),
    re_path(r"^command/upsert_iam_system_provider_config/$", views.upsert_iam_system_provider_config),
    re_path(r"^command/migrate_pipeline_parent_data/$", views.migrate_pipeline_parent_data),
    re_path(r"^migration/register_resource_config/$", migration_api.register_resource_config),
    re_path(r"^migration/migrate_app_maker/$", migration_api.migrate_app_maker),
    re_path(r"^migration/migrate_staff_group/$", migration_api.migrate_staff_group),
    re_path(r"^migration/migrate_template_category/$", migration_api.migrate_template_category),
    re_path(r"^migration/fix_engine_version_zero_task/$", migration_api.fix_engine_version_zero_task),
    re_path(r"^batch_insert_project_based_component/$", batch_insert_project_based_component),
    re_path(r"^batch_delete_project_based_component/$", batch_delete_project_based_component),
    re_path(r"^batch_revoke_task/$", batch_revoke_task),
    re_path(r"^command/get_enabled_periodic_task/$", views.get_enabled_periodic_task),
]
