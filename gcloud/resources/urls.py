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

from gcloud.clocked_task.viewset import ClockedTaskViewSet
from gcloud.tasktmpl3.apis.drf.viewsets.collection_template import CollectionTemplateViewSet
from gcloud.core.apis.drf.viewsets import (
    ProjectConfigViewSet,
    ResourceConfigViewSet,
    StaffGroupSetViewSet,
    BusinessSetViewSet,
    ComponentModelSetViewSet,
    ProjectSetViewSet,
    UserProjectSetViewSet,
    CommonProjectViewSet,
    LabelViewSet,
    PackageSourceViewSet,
    SyncTaskViewSet,
    CollectionViewSet,
    FunctionTaskViewSet,
    VariableViewSet,
    TaskTemplateViewSet,
    AppmakerListViewSet,
    PeriodicTaskViewSet,
    CommonTemplateViewSet as V3CommonTemplateViewSet,
    TaskFlowInstanceViewSet,
)

from gcloud.template_base.apis.drf.viewsets import TemplateSchemeViewSet
from gcloud.contrib.operate_record.apis.drf.viewsets import TaskOperateRecordSetViewSet, TemplateOperateRecordSetViewSet
from gcloud.label.viewsets import NewLabelViewSet
from gcloud.project_constants.apis.drf.viewsets import ProjectConstantsViewSet


from gcloud.template_base.apis.drf.viewsets.template import ProjectTemplateViewSet, CommonTemplateViewSet
from gcloud.user_custom_config.viewsets.user_custom_config import UserCustomConfViewset
from gcloud.user_custom_config.viewsets.user_custom_config_options import UserCustomConfigOptions


drf_router = DefaultRouter()
drf_router.register(r"project_config", ProjectConfigViewSet)
drf_router.register(r"resource_config", ResourceConfigViewSet)
drf_router.register(r"staff_group", StaffGroupSetViewSet)
drf_router.register(r"operate_record_task", TaskOperateRecordSetViewSet)
drf_router.register(r"operate_record_template", TemplateOperateRecordSetViewSet)
drf_router.register(r"new_label", NewLabelViewSet)
drf_router.register(r"scheme", TemplateSchemeViewSet)
drf_router.register(r"project_constants", ProjectConstantsViewSet)
drf_router.register(r"collection_template", CollectionTemplateViewSet)
drf_router.register(r"business", BusinessSetViewSet)
drf_router.register(r"component", ComponentModelSetViewSet)
drf_router.register(r"project", ProjectSetViewSet)
drf_router.register(r"user_project", UserProjectSetViewSet)
drf_router.register(r"common_project", CommonProjectViewSet)
drf_router.register(r"label", LabelViewSet)
drf_router.register(r"package_source", PackageSourceViewSet, basename="package_source")
drf_router.register(r"sync_task", SyncTaskViewSet)
drf_router.register(r"collection", CollectionViewSet)
drf_router.register(r"function_task", FunctionTaskViewSet)
drf_router.register(r"variable", VariableViewSet)
drf_router.register(r"template", TaskTemplateViewSet)
drf_router.register(r"appmaker", AppmakerListViewSet, basename="appmaker")
drf_router.register(r"periodic_task", PeriodicTaskViewSet)
drf_router.register(r"common_template", V3CommonTemplateViewSet)
drf_router.register(r"taskflow", TaskFlowInstanceViewSet)


v4_drf_router = DefaultRouter()
v4_drf_router.register(r"project_template/(?P<project_id>\d+)", ProjectTemplateViewSet, basename="project_template")
v4_drf_router.register(r"common_template", CommonTemplateViewSet, basename="common_template")
v4_drf_router.register(r"clocked_task", ClockedTaskViewSet, basename="clocked_task")
v4_drf_router.register(r"user_custom_config/(?P<project_id>\d+)", UserCustomConfViewset, basename="user_custom_config")
v4_drf_router.register(
    r"user_custom_config_options/(?P<project_id>\d+)", UserCustomConfigOptions, basename="user_custom_config_options"
)

# Standard bits...
urlpatterns = [
    url(r"^api/v3/", include(drf_router.urls)),
    url(r"^api/v4/", include(v4_drf_router.urls)),
    url(r"^api/auto_test/", include("gcloud.auto_test.urls")),
]
