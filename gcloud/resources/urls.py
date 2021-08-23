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
from tastypie.api import Api
from rest_framework.routers import DefaultRouter

from gcloud.core.apis.drf.viewsets import ProjectConfigViewSet, ResourceConfigViewSet, StaffGroupSetViewSet
from gcloud.template_base.apis.drf.viewsets import TemplateSchemeViewSet
from gcloud.contrib.operate_record.apis.drf.viewsets import TaskOperateRecordSetViewSet, TemplateOperateRecordSetViewSet
from gcloud.core.resources import (
    BusinessResource,
    ProjectResource,
    ComponentModelResource,
    VariableModelResource,
    CommonProjectResource,
    LabelGroupModelResource,
    LabelModelResource,
    UserProjectResource,
)
from gcloud.common_template.apis.tastypie.resources import CommonTemplateResource, CommonTemplateSchemeResource
from gcloud.label.viewsets import LabelViewSet
from gcloud.project_constants.apis.drf.viewsets import ProjectConstantsViewSet

from gcloud.tasktmpl3.apis.tastypie.resources import (
    TaskTemplateResource,
    # TemplateSchemeResource,
)
from gcloud.taskflow3.apis.tastypie.resources import TaskFlowInstanceResource
from gcloud.contrib.appmaker.resources import AppMakerResource
from gcloud.contrib.function.resources import FunctionTaskResource
from gcloud.contrib.collection.resources import CollectionResources
from gcloud.periodictask.resources import PeriodicTaskResource
from gcloud.external_plugins.resources import PackageSourceResource, SyncTaskResource
from gcloud.template_base.apis.drf.viewsets.template import ProjectTemplateViewSet, CommonTemplateViewSet

v3_api = Api(api_name="v3")
v3_api.register(BusinessResource())
v3_api.register(ProjectResource())
v3_api.register(UserProjectResource())
v3_api.register(CommonProjectResource())
v3_api.register(TaskTemplateResource())
v3_api.register(ComponentModelResource())
v3_api.register(VariableModelResource())
# v3_api.register(TemplateSchemeResource())
v3_api.register(TaskFlowInstanceResource())
v3_api.register(AppMakerResource())
v3_api.register(FunctionTaskResource())
v3_api.register(CollectionResources())
v3_api.register(PeriodicTaskResource())
v3_api.register(CommonTemplateResource())
v3_api.register(CommonTemplateSchemeResource())
v3_api.register(PackageSourceResource())
v3_api.register(SyncTaskResource())
v3_api.register(LabelGroupModelResource())
v3_api.register(LabelModelResource())

drf_router = DefaultRouter()
drf_router.register(r"project_config", ProjectConfigViewSet)
drf_router.register(r"resource_config", ResourceConfigViewSet)
drf_router.register(r"staff_group", StaffGroupSetViewSet)
drf_router.register(r"operate_record_task", TaskOperateRecordSetViewSet)
drf_router.register(r"operate_record_template", TemplateOperateRecordSetViewSet)
drf_router.register(r"new_label", LabelViewSet)
drf_router.register(r"scheme", TemplateSchemeViewSet)
drf_router.register(r"project_constants", ProjectConstantsViewSet)

v4_drf_router = DefaultRouter()
v4_drf_router.register(r"project_template/(?P<project_id>\d+)", ProjectTemplateViewSet, basename="project_template")
v4_drf_router.register(r"common_template", CommonTemplateViewSet, basename="common_template")

# Standard bits...
urlpatterns = [
    url(r"^api/", include(v3_api.urls)),
    url(r"^api/v3/", include(drf_router.urls)),
    url(r"^api/v4/", include(v4_drf_router.urls)),
]
