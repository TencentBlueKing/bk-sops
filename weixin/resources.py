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

from django.http.response import HttpResponseForbidden
from tastypie.authorization import ReadOnlyAuthorization

from gcloud.contrib.collection.resources import CollectionResources
from gcloud.core.resources import VariableModelResource, ComponentModelResource, UserProjectResource, ProjectResource
from gcloud.iam_auth import IAMMeta
from gcloud.tasktmpl3.apis.tastypie.resources import TaskTemplateResource, TemplateSchemeResource
from gcloud.taskflow3.apis.tastypie.resources import TaskFlowInstanceResource
from weixin.utils import iam_based_object_list_filter


class WxUserProjectResource(UserProjectResource):
    class Meta(UserProjectResource.Meta):
        resource_name = "weixin_user_project"
        authorization = ReadOnlyAuthorization()


class WxProjectResource(ProjectResource):
    def get_object_list(self, request):
        """
        fetching all projects list is forbidden
        """
        return HttpResponseForbidden()

    class Meta(ProjectResource.Meta):
        resource_name = "weixin_project"
        authorization = ReadOnlyAuthorization()


class WxTaskTemplateResource(TaskTemplateResource):
    def alter_list_data_to_serialize(self, request, data):
        super(WxTaskTemplateResource, self).alter_list_data_to_serialize(request, data)
        data = iam_based_object_list_filter(data, [IAMMeta.FLOW_VIEW_ACTION, IAMMeta.FLOW_CREATE_TASK_ACTION])
        return data

    class Meta(TaskTemplateResource.Meta):
        resource_name = "weixin_template"


class WxTaskFlowInstanceResource(TaskFlowInstanceResource):
    def alter_list_data_to_serialize(self, request, data):
        super(WxTaskFlowInstanceResource, self).alter_list_data_to_serialize(request, data)
        data = iam_based_object_list_filter(data, [IAMMeta.TASK_VIEW_ACTION, IAMMeta.TASK_OPERATE_ACTION])
        return data

    def obj_delete(self, bundle, **kwargs):
        """
        obj delete is forbidden
        """
        return HttpResponseForbidden()

    class Meta(TaskFlowInstanceResource.Meta):
        resource_name = "weixin_taskflow"


class WxTemplateSchemeResource(TemplateSchemeResource):
    class Meta(TemplateSchemeResource.Meta):
        resource_name = "weixin_scheme"
        authorization = ReadOnlyAuthorization()


class WxComponentModelResource(ComponentModelResource):
    class Meta(ComponentModelResource.Meta):
        resource_name = "weixin_component"


class WxVariableModelResource(VariableModelResource):
    class Meta(VariableModelResource.Meta):
        resource_name = "weixin_variable"


class WxCollectionResource(CollectionResources):
    def alter_list_data_to_serialize(self, request, data):
        super(WxCollectionResource, self).alter_list_data_to_serialize(request, data)
        data = iam_based_object_list_filter(data, [IAMMeta.FLOW_VIEW_ACTION, IAMMeta.FLOW_CREATE_TASK_ACTION])
        data["objects"] = list(filter(lambda bundle: bundle.obj.category == "flow", data["objects"]))
        return data

    class Meta(CollectionResources.Meta):
        resource_name = "weixin_collection"
