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

from apigw_manager.apigw.decorators import apigw_require
from bamboo_engine import exceptions as bamboo_exceptions
from blueapps.account.decorators import login_exempt
from pipeline.eri.runtime import BambooDjangoRuntime
from django.views.decorators.http import require_GET

from gcloud.apigw.decorators import mark_request_whether_is_trust, mcp_apigw, project_inject, return_json_response
from gcloud.apigw.log_auth import get_execution_data_for_node, get_taskflow_for_log, validate_task_node
from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from pipeline_plugins.components.collections.sites.open.job.base import get_job_instance_log
from pipeline_plugins.components.utils import has_biz_set

node_logger = logging.getLogger("root")

JOB_INST_ID_MAP = {
    "job_fast_execute_script": "快速执行脚本",
    "job_local_content_upload": "本地文本框内容上传",
    "job_execute_task": "执行作业",
    "all_biz_job_fast_execute_script": "业务集快速执行脚本",
    "all_biz_execute_job_plan": "业务集执行作业",
    "job_cc_execute_script": "CC脚本执行",
}

JOB_INST_ID_IN_LIST_MAP = {
    "job_fast_push_file": "快速分发文件",
    "job_push_local_files": "分发本地文件",
    "all_biz_job_fast_push_file": "业务集快速分发文件",
}

# 业务集(all_biz_*)插件下发的作业实例挂在 biz_set 维度，查询日志须用 biz_set scope
JOB_BIZ_SET_COMPONENT_CODES = {
    "all_biz_job_fast_execute_script",
    "all_biz_execute_job_plan",
    "all_biz_job_fast_push_file",
}


def _get_component_all_biz_cc_id(inputs):
    """从业务集插件节点输入中获取业务集 ID，兼容 all_biz_job_config 嵌套结构"""
    if not inputs:
        return None
    all_biz_cc_id = inputs.get("all_biz_cc_id")
    if all_biz_cc_id:
        return all_biz_cc_id
    job_config = inputs.get("all_biz_job_config") or {}
    return job_config.get("all_biz_cc_id")


def fetch_node_job_executed_log(
    node_id, bk_biz_id, target_ip=None, component_code=None, job_scope_type=None, execution_data=None
):
    """获取节点JOB执行日志的核心逻辑，供内外接口共用"""
    client = settings.ESB_GET_CLIENT_BY_USER(settings.SYSTEM_USE_API_ACCOUNT)
    if execution_data is None:
        runtime = BambooDjangoRuntime()
        try:
            execution_data = runtime.get_execution_data(node_id=node_id)
        except bamboo_exceptions.NotFoundError:
            node_logger.warning("execution data not found for node_id: %s", node_id)
            return {
                "result": False,
                "message": "execution data not found for node_id: {}".format(node_id),
                "logs": "",
            }

    inputs = getattr(execution_data, "inputs", {}) or {}

    if component_code in JOB_BIZ_SET_COMPONENT_CODES:
        # 业务集插件的作业实例挂在节点实际选择的业务集维度下，需用该业务集 ID 及对应 scope 查询
        all_biz_cc_id = _get_component_all_biz_cc_id(inputs)
        if all_biz_cc_id:
            bk_biz_id = all_biz_cc_id
            if job_scope_type is None:
                # 与组件执行逻辑保持一致：是业务集用 biz_set，否则降级为 biz
                job_scope_type = (
                    JobBizScopeType.BIZ_SET.value
                    if has_biz_set(int(all_biz_cc_id))
                    else JobBizScopeType.BIZ.value
                )
    else:
        # 普通 JOB 插件优先使用节点输入中的 biz_cc_id，与组件执行时的取值保持一致
        node_biz_cc_id = inputs.get("biz_cc_id")
        if node_biz_cc_id:
            bk_biz_id = node_biz_cc_id
    if job_scope_type is None:
        job_scope_type = JobBizScopeType.BIZ.value

    if component_code and component_code in JOB_INST_ID_IN_LIST_MAP:
        job_instance_id_list = execution_data.outputs.get("job_instance_id_list") or []
        log_content_list = []
        for job_instance_id in job_instance_id_list:
            log_result = get_job_instance_log(
                client, node_logger, job_instance_id, bk_biz_id, target_ip, job_scope_type
            )
            if not log_result["result"]:
                return {
                    "result": False,
                    "message": log_result["message"],
                    "logs": "",
                }
            log_content_list.append(log_result["data"])
        return {
            "result": True,
            "message": "success",
            "logs": "\n".join(log_content_list),
        }

    if component_code and component_code not in JOB_INST_ID_MAP:
        return {
            "result": False,
            "message": "component code not found: {}".format(component_code),
            "logs": "",
        }

    job_instance_id = execution_data.outputs.get("job_inst_id")
    log_result = get_job_instance_log(client, node_logger, job_instance_id, bk_biz_id, target_ip, job_scope_type)
    if not log_result["result"]:
        return {
            "result": False,
            "message": log_result["message"],
            "logs": "",
        }
    return {
        "result": True,
        "message": "success",
        "logs": log_result["data"],
    }


@login_exempt
@require_GET
@apigw_require
@mcp_apigw()
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
def get_node_job_executed_log(request, task_id, project_id):
    project = request.project
    taskflow, error_response = get_taskflow_for_log("get_node_job_executed_log", task_id, project)
    if error_response is not None:
        return error_response

    node_id = request.GET.get("node_id")
    target_ip = request.GET.get("target_ip")
    component_code = request.GET.get("component_code")
    error_response = validate_task_node("get_node_job_executed_log", taskflow, node_id)
    if error_response is not None:
        return error_response

    execution_data, error_response = get_execution_data_for_node("get_node_job_executed_log", node_id)
    if error_response is not None:
        return error_response

    return fetch_node_job_executed_log(
        node_id, project.bk_biz_id, target_ip, component_code=component_code, execution_data=execution_data
    )
