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


from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.apigw.views.utils import format_task_list_data, paginate_list_data
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@iam_intercept(ProjectViewInterceptor())
def get_task_list(request, project_id):
    project = request.project
    keyword = request.GET.get("keyword")
    is_started = request.GET.get("is_started")
    is_finished = request.GET.get("is_finished")

    filter_kwargs = dict(is_deleted=False, project_id=project.id)
    if keyword:
        filter_kwargs["pipeline_instance__name__contains"] = keyword
    if is_started is not None:
        filter_kwargs["pipeline_instance__is_started"] = is_started
    if is_finished is not None:
        filter_kwargs["pipeline_instance__is_finished"] = is_finished

    tasks = TaskFlowInstance.objects.select_related("pipeline_instance").filter(**filter_kwargs)

    try:
        tasks, count = paginate_list_data(request, tasks)
    except Exception as e:
        return {"result": False, "data": "", "message": e, "code": err_code.INVALID_OPERATION.code}

    response = {
        "result": True,
        "data": format_task_list_data(tasks, project),
        "count": count,
        "code": err_code.SUCCESS.code,
    }
    return response
