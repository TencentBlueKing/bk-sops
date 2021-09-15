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
import jsonschema

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.core.models import EngineConfig
from gcloud.conf import settings
from gcloud.constants import BUSINESS, COMMON
from gcloud.apigw.views.utils import logger
from gcloud.apigw.schemas import APIGW_CREATE_AND_START_TASK_PARAMS
from gcloud.common_template.models import CommonTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.celery.tasks import prepare_and_start_task
from gcloud.taskflow3.domains.queues import PrepareAndStartTaskQueueResolver
from gcloud.utils.decorators import request_validate
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from packages.bkoauth.decorators import apigw_required
from gcloud.iam_auth.view_interceptors.apigw import CreateTaskInterceptor
from gcloud.apigw.validators import CreateTaskValidator
from gcloud.contrib.operate_record.constants import RecordType, OperateType, OperateSource


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@request_validate(CreateTaskValidator)
@iam_intercept(CreateTaskInterceptor())
@record_operation(RecordType.task.name, OperateType.create.name, OperateSource.api.name)
def create_and_start_task(request, template_id, project_id):
    params = json.loads(request.body)
    project = request.project
    template_source = params.get("template_source", BUSINESS)

    logger.info(
        "[API] create_and_start_task, template_id: {template_id}, project_id: {project_id}, params: {params}.".format(
            template_id=template_id, project_id=project.id, params=params
        )
    )

    # 根据template_id获取template
    if template_source == BUSINESS:
        try:
            tmpl = TaskTemplate.objects.select_related("pipeline_template").get(
                id=template_id, project_id=project.id, is_deleted=False
            )
        except TaskTemplate.DoesNotExist:
            result = {
                "result": False,
                "message": "template[id={template_id}] of project[project_id={project_id},biz_id={biz_id}] "
                "does not exist".format(template_id=template_id, project_id=project.id, biz_id=project.bk_biz_id),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
            return result
    else:
        try:
            tmpl = CommonTemplate.objects.select_related("pipeline_template").get(id=template_id, is_deleted=False)
        except CommonTemplate.DoesNotExist:
            result = {
                "result": False,
                "message": "common template[id={template_id}] does not exist".format(template_id=template_id),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
            return result

    # 检查app_code是否存在
    app_code = getattr(request.jwt.app, settings.APIGW_APP_CODE_KEY)
    if not app_code:
        message = "app_code cannot be empty, make sure api gateway has sent correct params"
        return {"result": False, "message": message, "code": err_code.CONTENT_NOT_EXIST.code}

    # 请求参数校验
    try:
        params.setdefault("flow_type", COMMON)
        params.setdefault("template_source", BUSINESS)
        params.setdefault("constants", {})
        params.setdefault("exclude_task_nodes_id", [])
        jsonschema.validate(params, APIGW_CREATE_AND_START_TASK_PARAMS)
    except jsonschema.ValidationError as e:
        logger.warning("[API] create_and_start_task raise params error: %s" % e)
        message = "task parmas is invalid: %s" % e
        return {"result": False, "message": message, "code": err_code.REQUEST_PARAM_INVALID.code}

    # 创建pipeline_instance
    pipeline_instance_kwargs = {
        "name": params["name"],
        "creator": request.user.username,
        "description": params.get("description", ""),
    }
    try:
        data = TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes(
            tmpl, pipeline_instance_kwargs, params["constants"], params["exclude_task_nodes_id"]
        )
    except Exception as e:
        return {"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code}

    # 创建task
    try:
        task = TaskFlowInstance.objects.create(
            project=project,
            pipeline_instance=data,
            category=tmpl.category,
            template_id=template_id,
            template_source=params["template_source"],
            create_method="api",
            create_info=app_code,
            flow_type=params["flow_type"],
            current_flow="execute_task" if params["flow_type"] == COMMON else "func_claim",
            engine_ver=EngineConfig.objects.get_engine_ver(
                project_id=project.id, template_id=template_id, template_source=template_source
            ),
        )
    except Exception as e:
        return {"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code}
    # 开始执行task
    queue, routing_key = PrepareAndStartTaskQueueResolver(
        settings.API_TASK_QUEUE_NAME_V2
    ).resolve_task_queue_and_routing_key()

    prepare_and_start_task.apply_async(
        kwargs=dict(task_id=task.id, project_id=project.id, username=request.user.username),
        queue=queue,
        routing_key=routing_key,
    )

    return {
        "result": True,
        "code": err_code.SUCCESS.code,
        "data": {"pipeline_tree": task.pipeline_tree, "task_id": task.id, "task_url": task.url},
    }
