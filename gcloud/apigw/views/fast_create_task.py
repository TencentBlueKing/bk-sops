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


from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from pipeline.exceptions import PipelineException

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.apigw.validators import FastCreateTaskValidator
from gcloud.apigw.views.utils import logger
from gcloud.common_template.models import CommonTemplate
from gcloud.constants import ONETIME, TASK_CATEGORY, TASK_NAME_MAX_LENGTH, TaskCreateMethod
from gcloud.contrib.operate_record.constants import OperateSource, OperateType, RecordType
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import FastCreateTaskInterceptor
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.utils.decorators import request_validate
from gcloud.utils.strings import standardize_name


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@request_validate(FastCreateTaskValidator)
@iam_intercept(FastCreateTaskInterceptor())
@record_operation(RecordType.task.name, OperateType.create.name, OperateSource.api.name)
def fast_create_task(request, project_id):

    params = request.params_json
    project = request.project
    logger.info(
        "[API] fast_create_task info, project_id: {project_id}, params: {params}".format(
            project_id=project.id, params=params
        )
    )

    try:
        pipeline_tree = params["pipeline_tree"]
        pipeline_instance_kwargs = {
            "name": standardize_name(params["name"], TASK_NAME_MAX_LENGTH),
            "creator": request.user.username,
            "pipeline_tree": pipeline_tree,
            "description": params.get("description", ""),
        }
    except (KeyError, ValueError) as e:
        return {"result": False, "message": "invalid params: %s" % str(e), "code": err_code.REQUEST_PARAM_INVALID.code}

    has_common_subprocess = params.get("has_common_subprocess", False)
    try:
        template = (
            CommonTemplate(pipeline_template=None, tenant_id=request.app.tenant_id)
            if has_common_subprocess
            else TaskTemplate(pipeline_template=None)
        )
        pipeline_instance = TaskFlowInstance.objects.create_pipeline_instance(
            template=template, **pipeline_instance_kwargs
        )
    except PipelineException as e:
        message = "[API] fast_create_task create pipeline error: %s" % str(e)
        logger.exception(message)
        return {"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code}

    taskflow_kwargs = {
        "project": project,
        "pipeline_instance": pipeline_instance,
        "template_source": ONETIME,
        "create_method": TaskCreateMethod.API.value,
    }
    if params.get("category") in [cate[0] for cate in TASK_CATEGORY]:
        taskflow_kwargs["category"] = params["category"]
    # 职能化任务，新建后进入职能化认领阶段
    if params.get("flow_type", "common") == "common_func":
        taskflow_kwargs["flow_type"] = "common_func"
        taskflow_kwargs["current_flow"] = "func_claim"
    # 常规流程，新建后即可执行
    else:
        taskflow_kwargs["flow_type"] = "common"
        taskflow_kwargs["current_flow"] = "execute_task"
    task = TaskFlowInstance.objects.create(**taskflow_kwargs)
    return {
        "result": True,
        "data": {"task_id": task.id, "task_url": task.url, "pipeline_tree": task.pipeline_tree},
        "code": err_code.SUCCESS.code,
    }
