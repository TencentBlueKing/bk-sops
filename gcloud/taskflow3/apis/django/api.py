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
import logging
import time
import traceback

import ujson as json
from blueapps.account.decorators import login_exempt
from cryptography.fernet import Fernet
from django.db import transaction
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from drf_yasg.utils import swagger_auto_schema
from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE
from iam.exceptions import RawAuthFailedException
from rest_framework.decorators import api_view

import env
from gcloud import err_code
from gcloud.conf import settings
from gcloud.constants import PROJECT, TASK_CREATE_METHOD, JobBizScopeType
from gcloud.contrib.analysis.analyse_items import task_flow_instance
from gcloud.contrib.operate_record.constants import OperateType, RecordType
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.core.models import EngineConfig
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.taskflow import (
    BatchStatusViewInterceptor,
    DataViewInterceptor,
    DetailViewInterceptor,
    GetNodeLogInterceptor,
    NodesActionInterceptor,
    SpecNodesTimerResetInpterceptor,
    StatusViewInterceptor,
    TaskActionInterceptor,
    TaskCloneInpterceptor,
    TaskFuncClaimInterceptor,
)
from gcloud.openapi.schema import AnnotationAutoSchema
from gcloud.taskflow3.apis.django.validators import (
    BatchStatusValidator,
    DataValidator,
    DetailValidator,
    GetJobInstanceLogValidator,
    GetNodeLogValidator,
    NodesActionValidator,
    PreviewTaskTreeValidator,
    QueryTaskCountValidator,
    SpecNodesTimerResetValidator,
    StatusValidator,
    TaskActionValidator,
    TaskCloneValidator,
    TaskFuncClaimValidator,
)
from gcloud.taskflow3.domains.auto_retry import AutoRetryNodeStrategyCreator
from gcloud.taskflow3.domains.context import TaskContext
from gcloud.taskflow3.domains.dispatchers import NodeCommandDispatcher, TaskCommandDispatcher
from gcloud.taskflow3.models import TaskFlowInstance, TimeoutNodeConfig
from gcloud.taskflow3.utils import extract_nodes_by_statuses, fetch_node_id__auto_retry_info_map
from gcloud.utils.decorators import request_validate
from gcloud.utils.throttle import check_task_operation_throttle, get_task_operation_frequence
from pipeline_web.preview import preview_template_tree

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
        message = _(f"任务查询失败: 任务[ID: {instance_id}]不存在, 请检查 | status")
        logger.error(message)
        return JsonResponse(
            {"result": False, "message": message, "data": None, "code": err_code.CONTENT_NOT_EXIST.code}
        )

    dispatcher = TaskCommandDispatcher(
        engine_ver=task.engine_ver, taskflow_id=task.id, pipeline_instance=task.pipeline_instance, project_id=project_id
    )
    result = dispatcher.get_task_status(subprocess_id=subprocess_id, with_new_status=True)

    # 解析状态树失败或者任务尚未被调度，此时直接返回解析结果
    if not result["result"] or not result["data"].get("id"):
        return JsonResponse(result)

    try:
        status_tree, root_pipeline_id = result["data"], result["data"]["id"]
        all_node_ids = extract_nodes_by_statuses(status_tree)
        status_tree["auto_retry_infos"] = fetch_node_id__auto_retry_info_map(root_pipeline_id, all_node_ids)
    except Exception as e:
        message = "task[id={task_id}] extract failed node info error: {error}".format(task_id=task.id, error=e)
        logger.exception(message)
        return JsonResponse({"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code})

    return JsonResponse(result)


@require_POST
@request_validate(BatchStatusValidator)
@iam_intercept(BatchStatusViewInterceptor())
def batch_status(request, project_id):
    """用于批量获取独立子流程状态"""
    body = json.loads(request.body)
    task_ids = body.get("task_ids") or []
    tasks = TaskFlowInstance.objects.filter(id__in=task_ids, project_id=project_id)
    total_result = {"result": True, "data": {}, "code": err_code.SUCCESS.code, "message": ""}
    for task in set(tasks):
        dispatcher = TaskCommandDispatcher(
            engine_ver=task.engine_ver,
            taskflow_id=task.id,
            pipeline_instance=task.pipeline_instance,
            project_id=project_id,
        )

        get_task_status_result = dispatcher.get_task_status(with_new_status=True)

        # 解析状态树失败或者任务尚未被调度，提前返回，不解析节点自动重试逻辑
        if not get_task_status_result["result"] or not get_task_status_result["data"].get("id"):
            total_result["data"][task.id] = get_task_status_result
            continue

        try:
            status_tree, root_pipeline_id = get_task_status_result["data"], get_task_status_result["data"]["id"]
            all_node_ids = extract_nodes_by_statuses(status_tree)
            status_tree["auto_retry_infos"] = fetch_node_id__auto_retry_info_map(root_pipeline_id, all_node_ids)
        except Exception as e:
            message = "task[id={task_id}] extract failed node info error: {error}".format(task_id=task.id, error=e)
            logger.exception(message)

        total_result["data"][task.id] = get_task_status_result

    return JsonResponse(total_result)


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


@swagger_auto_schema(methods=["GET"], auto_schema=AnnotationAutoSchema)
@request_validate(DetailValidator)
@iam_intercept(DetailViewInterceptor())
@api_view(["GET"])
def detail(request, project_id):
    """
    获取节点详情
    param: instance_id: 任务实例 ID, string, query, required
    param: node_id: 节点 ID, string, query, required
    param: loop: 节点重入次数, int, query
    param: component_code: ServiceActivity 节点组件代号，节点类型为 ServiceActivity 时必传, string, query
    param: include_data: 是否返回节点执行数据(1:返回 0:不返回), int, query

    return: dict 根据 result 字段判断是否请求成功
    {
        "result": "是否请求成功(boolean)",
        "data": {
            "id": "节点 ID(string)",
            "state": "节点状态(string)",
            "loop": "重入次数(int)",
            "retry": "重试次数(int)",
            "skip": "是否跳过(boolean)",
            "error_ignorable": "是否失败后跳过(boolean)",
            "elapsed_time": "执行耗时(int)",
            "start_time": "开始时间(string)",
            "finish_time": "结束时间(string)",
            "history_id": "历史 ID，仅 V1 引擎任务节点会返回该字段(int)",
            "histories": [
                {
                    "loop": "重入次数(int)",
                    "skip": "是否跳过(boolean)",
                    "inputs": "节点输入数据(object or null)",
                    "outputs": "节点输出数据(object or null)",
                    "history_id": "历史 ID(int)",
                    "state": "节点历史状态(string)",
                    "elapsed_time": "执行耗时(int)",
                    "start_time": "开始时间(string)",
                    "finish_time": "结束时间(string)",
                    "ex_data": "节点错误信息(string)"
                }
            ],
            "auto_retry_info": "自动重试信息, node_id auto_retry_times max_auto_retry_times 三个 key (dict)",
            "inputs": "节点输入数据, include_data 为 1 时返回(object or null)",
            "outputs": "节点输出数据, include_data 为 1 时返回(list)",
            "ex_data": "节点错误信息, include_data 为 1 时返回(string)"
        },
        "message": "错误时提示(string)"
    }
    """
    task_id = request.query_params["instance_id"]
    node_id = request.query_params["node_id"]
    loop = request.query_params.get("loop")
    subprocess_simple_inputs = request.query_params.get("subprocess_simple_inputs") == "true"
    component_code = request.query_params.get("component_code")
    include_data = int(request.query_params.get("include_data", 1))

    subprocess_stack = json.loads(request.query_params.get("subprocess_stack", "[]"))

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    ctx = task.get_node_detail(
        node_id,
        request.user.username,
        component_code,
        subprocess_stack,
        loop,
        include_data,
        project_id=project_id,
        subprocess_simple_inputs=subprocess_simple_inputs,
    )

    return JsonResponse(ctx)


@require_GET
@request_validate(GetJobInstanceLogValidator)
def get_job_instance_log(request, biz_cc_id):
    job_instance_id = request.GET["job_instance_id"]
    bk_scope_type = request.GET.get("bk_scope_type", JobBizScopeType.BIZ.value)
    log_kwargs = {
        "bk_scope_type": bk_scope_type,
        "bk_scope_id": str(biz_cc_id),
        "bk_biz_id": biz_cc_id,
        "job_instance_id": job_instance_id,
    }

    client = get_client_by_user(request.user.username)
    job_result = client.job.get_job_instance_log(log_kwargs)

    if not job_result["result"]:
        message = _(f"执行历史请求失败: 请求[作业平台ID: {biz_cc_id}] 异常信息: {job_result['message']} | get_job_instance_log")

        if job_result.get("code", 0) == HTTP_AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise RawAuthFailedException(permissions=job_result.get("permission", {}))

        logger.error(message)

    return JsonResponse(job_result)


@require_POST
@request_validate(TaskActionValidator)
@iam_intercept(TaskActionInterceptor())
@record_operation(RecordType.task.name, OperateType.task_action.name)
def task_action(request, action, project_id):
    task_id = json.loads(request.body)["instance_id"]
    username = request.user.username

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    if env.TASK_OPERATION_THROTTLE and not check_task_operation_throttle(project_id, action):
        message = _(f"任务操作失败: 项目[ID: {project_id}]达到启动任务的极限")
        frequence_result, frequence_data = get_task_operation_frequence(project_id, action)
        if frequence_result:
            allowed_times, scope_seconds = frequence_data
            message = _(f"任务操作失败: 项目[ID: {project_id}]启动任务的极限: {allowed_times}/{scope_seconds}(单位:秒)")
        logger.error(message)
        return JsonResponse({"result": False, "message": message, "code": err_code.INVALID_OPERATION.code})

    ctx = task.task_action(action, username)
    return JsonResponse(ctx)


@swagger_auto_schema(methods=["POST"], auto_schema=AnnotationAutoSchema)
@request_validate(NodesActionValidator)
@iam_intercept(NodesActionInterceptor())
@api_view(["POST"])
@record_operation(RecordType.task.name, OperateType.nodes_action.name)
def nodes_action(request, action, project_id):
    """
    节点操作
    param: project_id: 项目 ID, string, query, required
    param: action: 节点动作[可选值有：callback, skip_exg, retry, skip, pause_subproc, resume_subproc, retry_subprocess], string, query, required  # noqa

    body: data
    {
        "instance_id(required)": "任务 ID",
        "node_id(required)": "节点 ID",
        "data": "action 为 callback 时传入的数据",
        "inputs": "action 为 retry 时重试节点时节点的输入数据",
        "flow_id": "action 为 skip_exg 时选择执行的分支 id"
    }

    return: dict 根据 result 字段判断是否请求成功
    {
        "result": "是否请求成功(boolean)",
        "data": {},
        "message": "错误时提示(string)"
    }
    """

    task_id = request.data["instance_id"]
    node_id = request.data["node_id"]
    username = request.user.username
    kwargs = {
        "data": request.data.get("data", {}),
        "inputs": request.data.get("inputs", {}),
        "flow_id": request.data.get("flow_id", ""),
        "flow_ids": request.data.get("flow_ids", []),
        "converge_gateway_id": request.data.get("converge_gateway_id", ""),
    }
    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    ctx = task.nodes_action(action, node_id, username, **kwargs)
    return JsonResponse(ctx)


@require_POST
@request_validate(SpecNodesTimerResetValidator)
@iam_intercept(SpecNodesTimerResetInpterceptor())
@record_operation(RecordType.task.name, OperateType.spec_nodes_timer_reset.name)
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
@record_operation(RecordType.task.name, OperateType.task_clone.name)
def task_clone(request, project_id):
    data = json.loads(request.body)

    task_id = data["instance_id"]
    username = request.user.username

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    kwargs = {"name": data.get("name")}

    if data.get("create_method"):
        kwargs["create_method"] = data.get("create_method")
        kwargs["create_info"] = data.get("create_info", "")

    with transaction.atomic():
        new_task = task.clone(username, **kwargs)

        arn_creator = AutoRetryNodeStrategyCreator(
            taskflow_id=new_task.id, root_pipeline_id=new_task.pipeline_instance.instance_id
        )
        arn_creator.batch_create_strategy(pipeline_tree=task.pipeline_instance.execution_data)

        # create timeout config
        TimeoutNodeConfig.objects.batch_create_node_timeout_config(
            taskflow_id=task.id,
            root_pipeline_id=task.pipeline_instance.instance_id,
            pipeline_tree=task.pipeline_instance.execution_data,
        )

    ctx = {"result": True, "data": {"new_instance_id": new_task.id}, "message": "", "code": err_code.SUCCESS.code}

    return JsonResponse(ctx)


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
        message = _(f"任务数据请求失败: 请求任务数据发生异常: {e}. 请重试, 如多次失败可联系管理员处理 | preview_task_tree")
        logger.exception(message)
        return JsonResponse({"result": False, "message": message})

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


@swagger_auto_schema(methods=["GET"], auto_schema=AnnotationAutoSchema)
@request_validate(GetNodeLogValidator)
@iam_intercept(GetNodeLogInterceptor())
@api_view(["GET"])
def get_node_log(request, project_id, node_id):
    """
    获取节点详情
    param: instance_id: 任务实例 ID, string, query, required
    param: history_id: 历史 ID, int, query

    return: dict 根据 result 字段判断是否请求成功
    {
        "result": "是否请求成功(boolean)",
        "data": "节点日志文本(string)",
        "message": "错误时提示(string)"
    }
    """
    task_id = request.GET["instance_id"]
    history_id = request.GET.get("history_id") or -1

    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    if not task.has_node(node_id):
        message = _(f"节点状态请求失败: 任务[ID: {task.id}]中未找到节点[ID: {node_id}]. 请重试. 如持续失败可联系管理员处理 | get_node_log")
        logger.error(message)
        return JsonResponse({"result": False, "data": None, "message": message})

    dispatcher = NodeCommandDispatcher(engine_ver=task.engine_ver, node_id=node_id, taskflow_id=task_id)
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
    old callback view, handle pipeline callback, will not longer use after 3.6.X+ version
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
        message = _(f"节点回调失败: 无效的请求, 请重试. 如持续失败可联系管理员处理. {traceback.format_exc()} | api node_callback")
        logger.error(message)
        return JsonResponse({"result": False, "message": message}, status=400)

    # 老的回调接口，一定是老引擎的接口
    dispatcher = NodeCommandDispatcher(engine_ver=EngineConfig.ENGINE_VER_V1, node_id=node_id)

    # 由于回调方不一定会进行多次回调，这里为了在业务层防止出现不可抗力（网络，DB 问题等）导致失败
    # 增加失败重试机制
    callback_result = None
    for __ in range(env.NODE_CALLBACK_RETRY_TIMES):
        callback_result = dispatcher.dispatch(command="callback", operator="", data=callback_data)
        logger.info("result of callback call({}): {}".format(token, callback_result))
        if callback_result["result"]:
            break
        # 考虑callback时Process状态还没及时修改为sleep的情况
        time.sleep(0.5)

    return JsonResponse(callback_result)
