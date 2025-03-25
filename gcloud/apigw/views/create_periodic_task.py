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

import jsonschema
import ujson as json
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import env
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.apigw.schemas import APIGW_CREATE_PERIODIC_TASK_PARAMS
from gcloud.apigw.validators import CreatePriodicTaskValidator
from gcloud.apigw.views.utils import info_data_from_period_task, logger
from gcloud.common_template.models import CommonTemplate
from gcloud.constants import NON_COMMON_TEMPLATE_TYPES, PROJECT
from gcloud.core.models import ProjectConfig
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import CreatePeriodicTaskInterceptor
from gcloud.periodictask.models import PeriodicTask
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.utils import replace_template_id
from gcloud.utils.decorators import request_validate
from pipeline_web.preview_base import PipelineTemplateWebPreviewer


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@request_validate(CreatePriodicTaskValidator)
@iam_intercept(CreatePeriodicTaskInterceptor())
def create_periodic_task(request, template_id, project_id):
    project = request.project

    # check if the periodic task of the project reach the limit
    periodic_task_limit = env.PERIODIC_TASK_PROJECT_MAX_NUMBER
    project_config = ProjectConfig.objects.filter(project_id=project.id).only("max_periodic_task_num").first()
    if project_config and project_config.max_periodic_task_num > 0:
        periodic_task_limit = project_config.max_periodic_task_num
    if PeriodicTask.objects.filter(project__id=project.id).count() >= periodic_task_limit:
        message = "Periodic task number reaches limit: {}".format(periodic_task_limit)
        return {"result": False, "message": message, "code": err_code.INVALID_OPERATION.code}

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
                "does not exist".format(template_id=template_id, project_id=project.id, biz_id=project.bk_biz_id),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
            return result

    else:
        try:
            template = CommonTemplate.objects.get(id=template_id, is_deleted=False, tenant_id=request.app.tenant_id)
        except CommonTemplate.DoesNotExist:
            result = {
                "result": False,
                "message": "common template[id={template_id}] does not exist".format(template_id=template_id),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
            return result

    params.setdefault("constants", {})
    params.setdefault("exclude_task_nodes_id", [])
    try:
        jsonschema.validate(params, APIGW_CREATE_PERIODIC_TASK_PARAMS)
    except jsonschema.ValidationError as e:
        logger.warning("[API] create_periodic_task raise prams error: %s" % e)
        message = "task params is invalid: %s" % e
        return {"result": False, "message": message, "code": err_code.REQUEST_PARAM_INVALID.code}

    exclude_task_nodes_id = params["exclude_task_nodes_id"]
    pipeline_tree = template.pipeline_tree
    try:
        PipelineTemplateWebPreviewer.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)
    except Exception as e:
        logger.exception("[API] create_periodic_task preview tree error: {}".format(e))
        return {"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code}

    for key, val in list(params["constants"].items()):
        if key in pipeline_tree["constants"]:
            pipeline_tree["constants"][key]["value"] = val

    name = params["name"]
    cron = params["cron"]

    try:
        replace_template_id(TaskTemplate, pipeline_tree)
    except Exception as e:
        logger.exception("[API] create_periodic_task replace id error: {}".format(e))
        return {"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code}

    try:
        task = PeriodicTask.objects.create(
            project=project,
            template=template,
            template_source=template_source,
            name=name,
            cron=cron,
            pipeline_tree=pipeline_tree,
            creator=request.user.username,
            template_version=template.version,
        )
    except Exception as e:
        logger.exception("[API] create_periodic_task create error: {}".format(e))
        return {"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code}

    data = info_data_from_period_task(task)
    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
