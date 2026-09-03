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
import copy
import re

import jsonschema
import ujson as json
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from pipeline.exceptions import PipelineException

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, mcp_apigw, project_inject, return_json_response
from gcloud.apigw.schemas import APIGW_CREATE_TASK_PARAMS
from gcloud.apigw.validators import CreateTaskValidator
from gcloud.apigw.views.task_node_selector import (
    TaskNodeSelectionValidationError,
    normalize_template_scheme_params,
    resolve_exclude_task_nodes_id,
)
from gcloud.apigw.views.utils import logger
from gcloud.common_template.models import CommonTemplate
from gcloud.conf import settings
from gcloud.constants import NON_COMMON_TEMPLATE_TYPES, PROJECT, TaskCreateMethod
from gcloud.contrib.audit.mappings import get_task_create_action
from gcloud.contrib.audit.utils import bk_audit_add_event_on_commit, get_audit_event_kwargs
from gcloud.contrib.operate_record.constants import OperateSource, OperateType, RecordType
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.core.models import EngineConfig
from gcloud.core.trace import CallFrom, trace_view
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import CreateTaskInterceptor
from gcloud.taskflow3.domains.auto_retry import AutoRetryNodeStrategyCreator
from gcloud.taskflow3.models import TaskCallBackRecord, TaskFlowInstance, TimeoutNodeConfig
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.utils.decorators import request_validate
from gcloud.utils.strings import standardize_pipeline_node_name
from pipeline_web.parser.validator import validate_web_pipeline_tree


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@mcp_apigw(exclude_responses=["data.pipeline_tree"])
@return_json_response
@mark_request_whether_is_trust
@project_inject
@request_validate(CreateTaskValidator)
@trace_view(attr_keys=["project_id"], call_from=CallFrom.APIGW.value)
@iam_intercept(CreateTaskInterceptor())
@record_operation(RecordType.task.name, OperateType.create.name, OperateSource.api.name)
def create_task(request, template_id, project_id):
    params = json.loads(request.body)
    project = request.project
    template_source = params.get("template_source", PROJECT)

    logger.info(
        "[API] create_task info, template_id: {template_id}, project_id: {project_id}, params: {params}".format(
            template_id=template_id, project_id=project.id, params=params
        )
    )

    callback_url = params.pop("callback_url", None)
    CALLBACK_URL_PATTERN = r"^https?://\w.+$"
    if callback_url and not (isinstance(callback_url, str) and re.match(CALLBACK_URL_PATTERN, callback_url)):
        return {
            "result": False,
            "code": err_code.REQUEST_PARAM_INVALID.code,
            "message": f"callback_url format error, must match {CALLBACK_URL_PATTERN}",
        }
    callback_version = params.get("callback_version", None)

    # 兼容老版本的接口调用
    if template_source in NON_COMMON_TEMPLATE_TYPES:
        template_source = PROJECT
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

    app_code = getattr(request.app, settings.APIGW_MANAGER_APP_CODE_KEY)
    if not app_code:
        message = "app_code cannot be empty, make sure api gateway has sent correct params"
        return {"result": False, "message": message, "code": err_code.CONTENT_NOT_EXIST.code}

    try:
        params.setdefault("flow_type", "common")
        params.setdefault("constants", {})
        params.setdefault("exclude_task_nodes_id", [])
        params.setdefault("simplify_vars", [])
        params.setdefault("execute_task_nodes_id", [])
        params.setdefault("template_schemes_id", [])
        jsonschema.validate(params, APIGW_CREATE_TASK_PARAMS)
        normalize_template_scheme_params(params)
    except jsonschema.ValidationError as e:
        logger.exception("[API] create_task raise prams error: %s" % e)
        message = "task params is invalid: %s" % e
        return {"result": False, "message": message, "code": err_code.REQUEST_PARAM_INVALID.code}
    except TaskNodeSelectionValidationError as e:
        return {"result": False, "message": str(e), "code": err_code.REQUEST_PARAM_INVALID.code}

    create_with_tree = "pipeline_tree" in params
    if create_with_tree and params["template_schemes_id"]:
        return {
            "result": False,
            "message": "template_schemes_id can not be used with pipeline_tree",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    pipeline_instance_kwargs = {
        "name": params["name"],
        "creator": request.user.username,
        "description": params.get("description", ""),
    }

    if create_with_tree:
        try:
            pipeline_tree = params["pipeline_tree"]
            params_constants = params["constants"]
            for key, constant in pipeline_tree["constants"].items():
                if not constant.get("is_meta", False):
                    if key in params_constants:
                        constant["value"] = params_constants[key]
                    continue
                # 补全 meta
                if "meta" not in constant:
                    constant["meta"] = copy.deepcopy(constant)
                # 调用方传了参：以传入值为准
                if key in params_constants:
                    constant["value"] = params_constants[key]
                else:
                    # 未传参：回退到默认值；constant["value"] 可能是下拉框元数据 dict，也可能是字符串/列表等已合法值
                    if isinstance(constant.get("value"), dict):
                        default_val = constant["value"].get("default")
                        if default_val is None:
                            default_val = constant["value"].get("default_text", "")
                        constant["value"] = default_val
            standardize_pipeline_node_name(pipeline_tree)
            validate_web_pipeline_tree(pipeline_tree)
        except Exception as e:
            message = "[API] create_task get invalid pipeline_tree: %s" % str(e)
            logger.exception(message)
            return {"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code}

        pipeline_instance_kwargs["pipeline_tree"] = pipeline_tree

        try:
            data = TaskFlowInstance.objects.create_pipeline_instance(template=tmpl, **pipeline_instance_kwargs)
        except PipelineException as e:
            message = "[API] create_task create pipeline error: %s" % str(e)
            logger.exception(message)
            return {"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code}
    else:
        # tmpl.pipeline_tree不能重复执行
        pipeline_tree = tmpl.pipeline_tree
        validate_web_pipeline_tree(pipeline_tree)

        try:
            exclude_task_nodes_id = resolve_exclude_task_nodes_id(
                tmpl, pipeline_tree, params, support_execute_task_nodes=True
            )
        except TaskNodeSelectionValidationError as e:
            return {
                "result": False,
                "message": str(e),
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }

        try:
            data = TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes(
                tmpl,
                pipeline_instance_kwargs,
                params["constants"],
                exclude_task_nodes_id,
                params["simplify_vars"],
                pipeline_tree,
            )
        except Exception as e:
            message = f"[API] create_task create pipeline without tree error: {e}"
            logger.exception(message)
            return {"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code}

    # 判断是否是 MCP 请求，设置对应的 create_method
    # request.is_mcp_request 由 @mcp_apigw 装饰器注入
    create_method = (
        TaskCreateMethod.MCP.value if getattr(request, "is_mcp_request", False) else TaskCreateMethod.API.value
    )

    task = TaskFlowInstance.objects.create(
        project=project,
        pipeline_instance=data,
        category=tmpl.category,
        template_id=template_id,
        template_source=template_source,
        create_method=create_method,
        create_info=app_code,
        flow_type=params.get("flow_type", "common"),
        current_flow="execute_task" if params.get("flow_type", "common") == "common" else "func_claim",
        engine_ver=EngineConfig.objects.get_engine_ver(
            project_id=project.id, template_id=template_id, template_source=template_source
        ),
        extra_info=json.dumps({"keys_in_constants_parameter": list(params["constants"].keys())}),
    )

    # create callback url record
    if callback_url:
        record_kwargs = {
            "task_id": task.id,
            "url": callback_url,
        }
        if callback_version:
            record_kwargs["extra_info"] = json.dumps({"callback_version": callback_version})
        TaskCallBackRecord.objects.create(**record_kwargs)

    # crete auto retry strategy
    arn_creator = AutoRetryNodeStrategyCreator(taskflow_id=task.id, root_pipeline_id=task.pipeline_instance.instance_id)
    arn_creator.batch_create_strategy(task.pipeline_instance.execution_data)

    # create timeout config
    TimeoutNodeConfig.objects.batch_create_node_timeout_config(
        taskflow_id=task.id,
        root_pipeline_id=task.pipeline_instance.instance_id,
        pipeline_tree=task.pipeline_instance.execution_data,
    )
    action_id = get_task_create_action(template_source, create_method)
    if action_id:
        bk_audit_add_event_on_commit(
            action_id=action_id, resource_id=IAMMeta.TASK_RESOURCE, instance=task, **get_audit_event_kwargs(request)
        )
    result_data = {"task_id": task.id, "task_url": task.url, "pipeline_tree": task.pipeline_tree}
    if task.flow_type == "common_func":
        result_data["function_task_claim_url"] = task.get_function_task_claim_url()
    return {
        "result": True,
        "data": result_data,
        "code": err_code.SUCCESS.code,
    }
