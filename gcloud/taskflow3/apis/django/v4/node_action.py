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

import ujson as json

from django.http.response import JsonResponse
from django.views.decorators.http import require_POST

from gcloud.utils.decorators import request_validate
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.apis.django.validators import NodeActionV2Validator
from gcloud.iam_auth.view_interceptors.taskflow import NodeActionV2Inpterceptor
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.contrib.operate_record.constants import RecordType, OperateType


@require_POST
@request_validate(NodeActionV2Validator)
@iam_intercept(NodeActionV2Inpterceptor())
@record_operation(RecordType.task.name, OperateType.nodes_action.name)
def node_action(request, project_id, task_id, node_id):
    data = json.loads(request.body)

    action = data["action"]
    username = request.user.username
    kwargs = {
        "data": data.get("data", {}),
        "inputs": data.get("inputs", {}),
        "flow_id": data.get("flow_id", ""),
    }
    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    ctx = task.nodes_action(action, node_id, username, **kwargs)
    return JsonResponse(ctx)
