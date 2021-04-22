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
import logging
import traceback

import ujson as json
from cryptography.fernet import Fernet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.utils.translation import ugettext_lazy as _

from blueapps.account.decorators import login_exempt

from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE
from iam.exceptions import RawAuthFailedException

from gcloud import err_code
from gcloud.core.models import EngineConfig
from gcloud.utils.decorators import request_validate
from gcloud.conf import settings
from gcloud.taskflow3.constants import TASK_CREATE_METHOD, PROJECT
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.context import TaskContext
from gcloud.contrib.analysis.analyse_items import task_flow_instance
from gcloud.taskflow3.models import preview_template_tree
from gcloud.taskflow3.validators import (
    StatusValidator,
    DataValidator,
    DetailValidator,
    GetJobInstanceLogValidator,
    TaskActionValidator,
    NodesActionValidator,
    SpecNodesTimerResetValidator,
    TaskCloneValidator,
    TaskModifyInputsValidator,
    TaskFuncClaimValidator,
    PreviewTaskTreeValidator,
    QueryTaskCountValidator,
    GetNodeLogValidator,
)
from gcloud.taskflow3.dispatchers import NodeCommandDispatcher, TaskCommandDispatcher
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.taskflow import (
    DataViewInterceptor,
    DetailViewInterceptor,
    TaskActionInterceptor,
    NodesActionInpterceptor,
    SpecNodesTimerResetInpterceptor,
    TaskCloneInpterceptor,
    TaskModifyInputsInterceptor,
    TaskFuncClaimInterceptor,
    GetNodeLogInterceptor,
    StatusViewInterceptor,
)

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


@require_GET
def context(request):
    """
    @summary: 返回流程中可以引用的任务全局变量
    @param request:
    @return:
    """
    return JsonResponse(
        {"result": True, "data": TaskContext.flat_details(), "code": err_code.SUCCESS.code, "message": ""}
    )


@require_GET
@request_validate(StatusValidator)
@iam_intercept(StatusViewInterceptor())
def status(request, project_id):
    instance_id = request.GET.get("instance_id")
    subprocess_id = request.GET.get("subprocess_id")

    try:
        task = TaskFlowInstance.objects.get(pk=instance_id, project_id=project_id)
    except TaskFlowInstance.DoesNotExist:
        return JsonResponse(
            {
                "result": False,
                "message": "task with instance_id({}) not exist".format(instance_id),
                "data": None,
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
        )

    dispatcher = TaskCommandDispatcher(
        engine_ver=task.engine_ver, taskflow_id=task.id, pipeline_instance=task.pipeline_instance
    )
    result = dispatcher.get_task_status(subprocess_id=subprocess_id)
    return JsonResponse(result)


@require_GET
@request_validate(DataValidator)
@iam_intercept(DataViewInterceptor())
def data(request, project_id):
    task_id = request.GET["instance_id"]
    node_id = request.GET["node_id"]
    loop = request.GET.get("loop")
    component_code = request.GET.get("component_code")

    subprocess_stack = json.loads(request.GET.get("subprocess_stack", "[]"))

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    ctx = task.get_node_data(node_id, request.user.username, component_code, subprocess_stack, loop)

    return JsonResponse(ctx)


@require_GET
@request_validate(DetailValidator)
@iam_intercept(DetailViewInterceptor())
def detail(request, project_id):
    task_id = request.GET["instance_id"]
    node_id = request.GET["node_id"]
    loop = request.GET.get("loop")
    component_code = request.GET.get("component_code")

    subprocess_stack = json.loads(request.GET.get("subprocess_stack", "[]"))

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    ctx = task.get_node_detail(node_id, request.user.username, component_code, subprocess_stack, loop)

    return JsonResponse(ctx)


@require_GET
@request_validate(GetJobInstanceLogValidator)
def get_job_instance_log(request, biz_cc_id):
    job_instance_id = request.GET["job_instance_id"]
    log_kwargs = {"bk_biz_id": biz_cc_id, "job_instance_id": job_instance_id}

    client = get_client_by_user(request.user.username)
    job_result = client.job.get_job_instance_log(log_kwargs)

    if not job_result["result"]:
        message = _("查询作业平台(JOB)的作业模板[app_id=%s]接口job.get_task返回失败: %s") % (biz_cc_id, job_result["message"])

        if job_result.get("code", 0) == HTTP_AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise RawAuthFailedException(permissions=job_result.get("permission", {}))

        logger.error(message)

    return JsonResponse(job_result)


@require_POST
@request_validate(TaskActionValidator)
@iam_intercept(TaskActionInterceptor())
def task_action(request, action, project_id):
    task_id = json.loads(request.body)["instance_id"]
    username = request.user.username

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)

    ctx = task.task_action(action, username)
    return JsonResponse(ctx)


@require_POST
@request_validate(NodesActionValidator)
@iam_intercept(NodesActionInpterceptor())
def nodes_action(request, action, project_id):
    data = json.loads(request.body)

    task_id = data["instance_id"]
    node_id = data["node_id"]
    username = request.user.username
    kwargs = {
        "data": data.get("data", {}),
        "inputs": data.get("inputs", {}),
        "flow_id": data.get("flow_id", ""),
    }
    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    ctx = task.nodes_action(action, node_id, username, **kwargs)
    return JsonResponse(ctx)


@require_POST
@request_validate(SpecNodesTimerResetValidator)
@iam_intercept(SpecNodesTimerResetInpterceptor())
def spec_nodes_timer_reset(request, project_id):
    data = json.loads(request.body)

    task_id = data["instance_id"]
    node_id = data["node_id"]
    inputs = data.get("inputs", {})
    username = request.user.username

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    ctx = task.spec_nodes_timer_reset(node_id, username, inputs)
    return JsonResponse(ctx)


@require_POST
@request_validate(TaskCloneValidator)
@iam_intercept(TaskCloneInpterceptor())
def task_clone(request, project_id):
    data = json.loads(request.body)

    task_id = data["instance_id"]
    username = request.user.username

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    kwargs = {"name": data.get("name")}

    if data.get("create_method"):
        kwargs["create_method"] = data.get("create_method")
        kwargs["create_info"] = data.get("create_info", "")

    new_task_id = task.clone(username, **kwargs)

    ctx = {"result": True, "data": {"new_instance_id": new_task_id}, "message": "", "code": err_code.SUCCESS.code}

    return JsonResponse(ctx)


@require_POST
@request_validate(TaskModifyInputsValidator)
@iam_intercept(TaskModifyInputsInterceptor())
def task_modify_inputs(request, project_id):
    data = json.loads(request.body)

    task_id = data["instance_id"]

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)

    constants = data["constants"]

    return JsonResponse(task.set_task_context(constants))


@require_POST
@request_validate(TaskFuncClaimValidator)
@iam_intercept(TaskFuncClaimInterceptor())
def task_func_claim(request, project_id):
    data = json.loads(request.body)
    task_id = data["instance_id"]
    constants = data["constants"]
    name = data.get("name", "")

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    ctx = task.task_claim(request.user.username, constants, name)

    return JsonResponse(ctx)


@require_POST
@request_validate(PreviewTaskTreeValidator)
def preview_task_tree(request, project_id):
    """
    @summary: 调整可选节点后预览任务流程，这里不创建任何实例，只返回调整后的pipeline_tree
    @param request:
    @param project_id:
    @return:
    """
    params = json.loads(request.body)

    template_source = params.get("template_source", PROJECT)
    template_id = params["template_id"]
    version = params.get("version")
    exclude_task_nodes_id = params.get("exclude_task_nodes_id", [])

    try:
        data = preview_template_tree(project_id, template_source, template_id, version, exclude_task_nodes_id)
    except Exception as e:
        err_msg = "preview_template_tree fail: {}".format(e)
        logger.exception(err_msg)
        return JsonResponse({"result": False, "message": err_msg})

    return JsonResponse({"result": True, "data": data})


@require_POST
@request_validate(QueryTaskCountValidator)
def query_task_count(request, project_id):
    """
    @summary: 按任务分类统计总数
    @param request:
    @param project_id:
    @return:
    """
    data = json.loads(request.body)

    conditions = data.get("conditions", {})
    group_by = data["group_by"]

    filters = {"project_id": project_id, "is_deleted": False}
    filters.update(conditions)
    success, content = task_flow_instance.dispatch(group_by, filters)

    if not success:
        return JsonResponse({"result": False, "message": content, "data": None, "code": err_code.UNKNOWN_ERROR.code})

    return JsonResponse({"result": True, "data": content, "message": "", "code": err_code.SUCCESS.code})


@require_GET
@request_validate(GetNodeLogValidator)
@iam_intercept(GetNodeLogInterceptor())
def get_node_log(request, project_id, node_id):
    """
    @summary: 查看某个节点的日志
    @param request:
    @param project_id:
    @param node_id
    @return:
    """
    task_id = request.GET["instance_id"]
    history_id = request.GET.get("history_id") or -1

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    if not task.has_node(node_id):
        return JsonResponse(
            {
                "result": False,
                "data": None,
                "message": "node[node_id={node_id}] not found in task[task_id={task_id}]".format(
                    node_id=node_id, task_id=task.id
                ),
            }
        )

    dispatcher = NodeCommandDispatcher(engine_ver=task.engine_ver, node_id=node_id)
    return JsonResponse(dispatcher.get_node_log(history_id))


@require_GET
def get_task_create_method(request):
    task_create_method_list = []
    for item in TASK_CREATE_METHOD:
        task_create_method_list.append({"value": item[0], "name": item[1]})
    return JsonResponse({"result": True, "data": task_create_method_list})


@login_exempt
@csrf_exempt
@require_POST
def node_callback(request, token):
    """
    old callback view, handle pipeline callback
    """
    logger.info("[old_node_callback]callback body for token({}): {}".format(token, request.body))

    try:
        f = Fernet(settings.CALLBACK_KEY)
        node_id = f.decrypt(bytes(token, encoding="utf8")).decode()
    except Exception:
        logger.warning("invalid token %s" % token)
        return JsonResponse({"result": False, "message": "invalid token"}, status=400)

    try:
        callback_data = json.loads(request.body)
    except Exception:
        logger.warning("node callback error: %s" % traceback.format_exc())
        return JsonResponse({"result": False, "message": "invalid request body"}, status=400)

    # 老的回调接口，一定是老引擎的接口
    dispatcher = NodeCommandDispatcher(engine_ver=EngineConfig.ENGINE_VER_V1, node_id=node_id)

    # 由于回调方不一定会进行多次回调，这里为了在业务层防止出现不可抗力（网络，DB 问题等）导致失败
    # 增加失败重试机制
    callback_result = None
    for i in range(3):
        callback_result = dispatcher.dispatch(command="callback", operator="", data=callback_data)
        logger.info("result of callback call({}): {}".format(token, callback_result))
        if callback_result["result"]:
            break

    return JsonResponse(callback_result)
