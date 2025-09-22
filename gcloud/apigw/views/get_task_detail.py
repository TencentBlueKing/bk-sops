# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from cachetools import TTLCache
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.apigw.decorators import project_inject
from gcloud.apigw.utils import bucket_cached, BucketTTLCache, api_bucket_and_key
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from apigw_manager.apigw.decorators import apigw_require
from gcloud.utils.webhook import get_webhook_delivery_history_by_delivery_id
from gcloud.apigw.serializers import IncludeOptionsSerializer


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
@bucket_cached(BucketTTLCache(TTLCache, {"maxsize": 1024, "ttl": 60}), bucket_and_key_func=api_bucket_and_key)
def get_task_detail(request, task_id, project_id):
    """
    @summary: 获取任务详细信息
    @param request:
    @param task_id:
    @param project_id:
    @return:
    """
    project = request.project
    serializer = IncludeOptionsSerializer(data=request.GET)
    if not serializer.is_valid():
        return {"result": False, "message": serializer.errors, "code": err_code.REQUEST_PARAM_INVALID.code}
    include_webhook_history = serializer.validated_data["include_webhook_history"]
    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project.id)
    except TaskFlowInstance.DoesNotExist:
        message = (
            "[API] get_task_detail task[id={task_id}] "
            "of project[project_id={project_id}, biz_id{biz_id}] does not exist".format(
                task_id=task_id, project_id=project.id, biz_id=project.bk_biz_id
            )
        )
        logger.exception(message)
        return {"result": False, "message": message, "code": err_code.CONTENT_NOT_EXIST.code}

    data = task.get_task_detail()
    if include_webhook_history:
        data["task_webhook_history"] = get_webhook_delivery_history_by_delivery_id(str(task_id))
    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
