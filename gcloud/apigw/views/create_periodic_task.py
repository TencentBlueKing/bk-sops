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


import jsonschema
import ujson as json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.apigw.schemas import APIGW_CREATE_PERIODIC_TASK_PARAMS
from gcloud.commons.template.models import CommonTemplate
from gcloud.commons.template.utils import replace_template_id
from gcloud.constants import PROJECT
from gcloud.periodictask.models import PeriodicTask
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.constants import NON_COMMON_TEMPLATE_TYPES
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.apigw.views.utils import logger, info_data_from_period_task
from gcloud.apigw.validators import CreatePriodicTaskValidator
from gcloud.utils.decorators import request_validate
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import CreatePeriodicTaskInterceptor

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@request_validate(CreatePriodicTaskValidator)
@iam_intercept(CreatePeriodicTaskInterceptor())
def create_periodic_task(request, template_id, project_id):
    project = request.project
    params = json.loads(request.body)
    template_source = params.get("template_source", PROJECT)
    logger.info(
        "[API] apigw create_periodic_task info, "
        "template_id: {template_id}, project_id: {project_id}, params: {params}".format(
            template_id=template_id, project_id=project.id, params=params
        )
    )

    if template_source in NON_COMMON_TEMPLATE_TYPES:
        template_source = PROJECT
        try:
            template = TaskTemplate.objects.get(pk=template_id, project_id=project.id, is_deleted=False)
        except TaskTemplate.DoesNotExist:
            result = {
                "result": False,
                "message": "template[id={template_id}] of project[project_id={project_id} , biz_id{biz_id}] "
                "does not exist".format(template_id=template_id, project_id=project.id, biz_id=project.bk_biz_id,),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
            return JsonResponse(result)

    else:
        try:
            template = CommonTemplate.objects.get(id=template_id, is_deleted=False)
        except CommonTemplate.DoesNotExist:
            result = {
                "result": False,
                "message": "common template[id={template_id}] does not exist".format(template_id=template_id),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
            return JsonResponse(result)

    params.setdefault("constants", {})
    params.setdefault("exclude_task_nodes_id", [])
    try:
        jsonschema.validate(params, APIGW_CREATE_PERIODIC_TASK_PARAMS)
    except jsonschema.ValidationError as e:
        logger.warning("[API] create_periodic_task raise prams error: %s" % e)
        message = "task params is invalid: %s" % e
        return JsonResponse({"result": False, "message": message, "code": err_code.REQUEST_PARAM_INVALID.code})

    exclude_task_nodes_id = params["exclude_task_nodes_id"]
    pipeline_tree = template.pipeline_tree
    try:
        TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)
    except Exception as e:
        logger.exception("[API] create_periodic_task preview tree error: {}".format(e))
        return JsonResponse({"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code})

    for key, val in list(params["constants"].items()):
        if key in pipeline_tree["constants"]:
            pipeline_tree["constants"][key]["value"] = val

    name = params["name"]
    cron = params["cron"]

    try:
        replace_template_id(TaskTemplate, pipeline_tree)
    except Exception as e:
        logger.exception("[API] create_periodic_task replace id error: {}".format(e))
        return JsonResponse({"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code})

    try:
        task = PeriodicTask.objects.create(
            project=project,
            template=template,
            template_source=template_source,
            name=name,
            cron=cron,
            pipeline_tree=pipeline_tree,
            creator=request.user.username,
        )
    except Exception as e:
        logger.exception("[API] create_periodic_task create error: {}".format(e))
        return JsonResponse({"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code})

    data = info_data_from_period_task(task)
    return JsonResponse({"result": True, "data": data, "code": err_code.SUCCESS.code})
