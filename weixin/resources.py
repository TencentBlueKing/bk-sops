# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.http.response import HttpResponseForbidden
from tastypie.authorization import ReadOnlyAuthorization

from gcloud.webservice3.resources import (
    BusinessResource,
    VariableModelResource,
    ComponentModelResource
)
from gcloud.tasktmpl3.resources import (
    TaskTemplateResource,
    TemplateSchemeResource
)
from gcloud.taskflow3.resources import TaskFlowInstanceResource


class WxBusinessResource(BusinessResource):
    class Meta(BusinessResource.Meta):
        authorization = ReadOnlyAuthorization()


class WxTaskTemplateResource(TaskTemplateResource):
    class Meta(TaskTemplateResource.Meta):
        authorization = ReadOnlyAuthorization()


class WxTaskFlowInstanceResource(TaskFlowInstanceResource):
    def obj_delete(self, bundle, **kwargs):
        """
        obj delete is forbidden
        """
        return HttpResponseForbidden()


class WxTemplateSchemeResource(TemplateSchemeResource):
    class Meta(TemplateSchemeResource.Meta):
        authorization = ReadOnlyAuthorization()


class WxComponentModelResource(ComponentModelResource):
    pass


class WxVariableModelResource(VariableModelResource):
    pass
