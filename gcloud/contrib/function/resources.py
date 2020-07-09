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

import logging

from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from auth_backend.plugins.tastypie.authorization import BkSaaSLooseReadOnlyAuthorization
from auth_backend.plugins.tastypie.inspect import ResourceInspect
from auth_backend.backends.utils import get_backend_from_config

from gcloud.taskflow3.permissions import taskflow_resource
from gcloud.webservice3.resources import GCloudModelResource
from gcloud.taskflow3.resources import TaskFlowInstanceResource
from gcloud.contrib.function.models import FunctionTask

backend = get_backend_from_config()

logger = logging.getLogger("root")


class FunctionTaskResourceInspect(ResourceInspect):
    def scope_id(self, bundle):
        return None

    def resource_id(self, bundle):
        return bundle.obj.task.id

    def instance(self, bundle):
        return bundle.obj.task


class FunctionTaskAuthorization(BkSaaSLooseReadOnlyAuthorization):
    def create_detail(self, object_list, bundle):
        return True

    def read_detail(self, object_list, bundle):
        return self.is_allow(bundle, [self.read_action_id], instance=bundle.obj.task)

    def update_detail(self, object_list, bundle):
        return False

    def delete_detail(self, object_list, bundle):
        return False


class FunctionTaskResource(GCloudModelResource):
    task = fields.ForeignKey(TaskFlowInstanceResource, "task", full=True)
    creator_name = fields.CharField(attribute="creator_name", readonly=True, null=True)
    editor_name = fields.CharField(attribute="editor_name", readonly=True, null=True)
    status_name = fields.CharField(attribute="status_name", readonly=True, null=True)

    class Meta(GCloudModelResource.Meta):
        queryset = FunctionTask.objects.filter(task__is_deleted=False)
        resource_name = "function_task"
        auth_resource = taskflow_resource
        authorization = FunctionTaskAuthorization(
            auth_resource=auth_resource, read_action_id="view", update_action_id="edit", resource_f="task"
        )
        inspect = FunctionTaskResourceInspect()

        filtering = {
            "task": ALL_WITH_RELATIONS,
            "creator": ALL,
            "editor": ALL,
            "status": ALL,
            "create_time": ["gte", "lte"],
            "claim_time": ["gte", "lte"],
        }
        q_fields = ["task__pipeline_instance__name"]
