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

from gcloud.webservice3.resources import (
    BusinessResource,
    ComponentModelResource,
    VariableModelResource
)
from gcloud.commons.template.resources import (
    CommonTemplateResource,
    CommonTemplateSchemeResource
)
from gcloud.tasktmpl3.resources import (
    TaskTemplateResource,
    TemplateSchemeResource,
)
from gcloud.taskflow3.resources import TaskFlowInstanceResource
from gcloud.contrib.appmaker.resources import AppMakerResource
from gcloud.contrib.function.resources import FunctionTaskResource
from gcloud.periodictask.resources import PeriodicTaskResource
from gcloud.external_plugins.resources import PackageSourceResource, SyncTaskResource

v3_api = Api(api_name='v3')
v3_api.register(BusinessResource())
v3_api.register(TaskTemplateResource())
v3_api.register(ComponentModelResource())
v3_api.register(VariableModelResource())
v3_api.register(TemplateSchemeResource())
v3_api.register(TaskFlowInstanceResource())
v3_api.register(AppMakerResource())
v3_api.register(FunctionTaskResource())
v3_api.register(PeriodicTaskResource())
v3_api.register(CommonTemplateResource())
v3_api.register(CommonTemplateSchemeResource())
v3_api.register(PackageSourceResource())
v3_api.register(SyncTaskResource())

# Standard bits...
urlpatterns = [
    url(r'^api/', include(v3_api.urls)),
]
