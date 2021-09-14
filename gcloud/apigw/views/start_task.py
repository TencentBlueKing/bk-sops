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

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import env
from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.celery.tasks import prepare_and_start_task
from gcloud.taskflow3.domains.queues import PrepareAndStartTaskQueueResolver
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskOperateInterceptor
from gcloud.utils.throttle import check_task_operation_throttle
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.contrib.operate_record.constants import RecordType, OperateType, OperateSource
from packages.bkoauth.decorators import apigw_required


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskOperateInterceptor())
@record_operation(RecordType.task.name, OperateType.start.name, OperateSource.api.name)
def start_task(request, task_id, project_id):
    username = request.user.username
    project = request.project

    if env.TASK_OPERATION_THROTTLE and not check_task_operation_throttle(project.id, "start"):
        return {
            "result": False,
            "message": "project id: {} reach the limit of starting tasks".format(project.id),
            "code": err_code.INVALID_OPERATION.code,
        }

    if TaskFlowInstance.objects.is_task_started(project_id=project.id, id=task_id):
        return {"result": False, "code": err_code.INVALID_OPERATION.code, "message": "task already started"}

    queue, routing_key = PrepareAndStartTaskQueueResolver(
        settings.API_TASK_QUEUE_NAME_V2
    ).resolve_task_queue_and_routing_key()

    prepare_and_start_task.apply_async(
        kwargs=dict(task_id=task_id, project_id=project.id, username=username), queue=queue, routing_key=routing_key
    )

    return {
        "task_url": TaskFlowInstance.task_url(project_id=project.id, task_id=task_id),
        "result": True,
        "code": err_code.SUCCESS.code,
    }
