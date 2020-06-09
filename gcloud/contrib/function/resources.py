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
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from iam.contrib.tastypie.authorization import ReadOnlyCompleteListIAMAuthorization

from gcloud.commons.tastypie import GCloudModelResource
from gcloud.taskflow3.resources import TaskFlowInstanceResource
from gcloud.contrib.function.models import FunctionTask
from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.resource_helpers import SimpleResourceHelper
from gcloud.iam_auth.authorization_helpers import FunctionTaskIAMAuthorizationHelper

iam = get_iam_client()


class FunctionTaskResource(GCloudModelResource):
    task = fields.ForeignKey(TaskFlowInstanceResource, "task", full=True)
    creator_name = fields.CharField(attribute="creator_name", readonly=True, null=True)
    editor_name = fields.CharField(attribute="editor_name", readonly=True, null=True)
    status_name = fields.CharField(attribute="status_name", readonly=True, null=True)

    class Meta(GCloudModelResource.Meta):
        queryset = FunctionTask.objects.filter(task__is_deleted=False)
        resource_name = "function_task"
        # iam config, use task permission
        authorization = ReadOnlyCompleteListIAMAuthorization(
            iam=iam,
            helper=FunctionTaskIAMAuthorizationHelper(
                system=IAMMeta.SYSTEM_ID,
                create_action=None,
                read_action=IAMMeta.TASK_VIEW_ACTION,
                update_action=None,
                delete_action=None,
            ),
        )
        iam_resource_helper = SimpleResourceHelper(
            type=IAMMeta.TASK_RESOURCE,
            id_field="task_id",
            creator_field="creator_name",
            name_field="name",
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            actions=[
                IAMMeta.TASK_VIEW_ACTION,
                IAMMeta.TASK_EDIT_ACTION,
                IAMMeta.TASK_OPERATE_ACTION,
                IAMMeta.TASK_CLAIM_ACTION,
                IAMMeta.TASK_DELETE_ACTION,
                IAMMeta.TASK_CLONE_ACTION,
            ],
        )

        filtering = {
            "task": ALL_WITH_RELATIONS,
            "creator": ALL,
            "editor": ALL,
            "status": ALL,
            "create_time": ["gte", "lte"],
            "claim_time": ["gte", "lte"],
        }
        q_fields = ["task__pipeline_instance__name"]
