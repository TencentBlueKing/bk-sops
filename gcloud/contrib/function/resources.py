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

from tastypie import fields
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from gcloud.core.api_adapter import is_user_functor

from gcloud.webservice3.resources import (
    GCloudModelResource,
    AppSerializer,
)
from gcloud.taskflow3.resources import TaskFlowInstanceResource
from gcloud.contrib.function.models import FunctionTask


class FunctionTaskResource(GCloudModelResource):
    task = fields.ForeignKey(
        TaskFlowInstanceResource,
        'task',
        full=True
    )
    creator_name = fields.CharField(
        attribute='creator_name',
        readonly=True,
        null=True
    )
    editor_name = fields.CharField(
        attribute='editor_name',
        readonly=True,
        null=True
    )
    status_name = fields.CharField(
        attribute='status_name',
        readonly=True,
        null=True
    )

    class Meta:
        queryset = FunctionTask.objects.filter(task__is_deleted=False)
        resource_name = 'function_task'
        excludes = []
        q_fields = ['task__pipeline_instance__name']
        authorization = ReadOnlyAuthorization()
        always_return_data = True
        serializer = AppSerializer()
        filtering = {
            'task': ALL_WITH_RELATIONS,
            'creator': ALL,
            'editor': ALL,
            'status': ALL,
            'create_time': ['gte', 'lte'],
            'claim_time': ['gte', 'lte']
        }
        limit = 0

    def get_object_list(self, request):
        if is_user_functor(request) or request.user.is_superuser:
            return super(FunctionTaskResource, self).get_object_list(request)
        else:
            return super(FunctionTaskResource, self).get_object_list(request).none()
