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
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, mcp_apigw, project_inject
from gcloud.apigw.views.utils import logger
from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from gcloud.taskflow3.models import TaskFlowInstance
from pipeline_plugins.components.collections.sites.open.job.base import get_job_instance_log

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


def fetch_node_job_executed_log(node_id, bk_biz_id, target_ip=None, component_code=None, job_scope_type=None):
    """获取节点JOB执行日志的核心逻辑，供内外接口共用"""
    if job_scope_type is None:
        job_scope_type = JobBizScopeType.BIZ.value
    client = settings.ESB_GET_CLIENT_BY_USER(settings.SYSTEM_USE_API_ACCOUNT)
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

    if component_code and component_code in JOB_INST_ID_IN_LIST_MAP:
        job_instance_id_list = execution_data.outputs.get("job_inst_id_list") or []
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
@api_view(["GET"])
@apigw_require
@mcp_apigw()
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
def get_node_job_executed_log(request, task_id, project_id):
    project = request.project
    try:
        TaskFlowInstance.objects.get(id=task_id, project_id=project.id)
    except TaskFlowInstance.DoesNotExist:
        message = (
            "[API] get_node_job_executed_log task[id={task_id}] "
            "of project[project_id={project_id}, biz_id={biz_id}] does not exist".format(
                task_id=task_id, project_id=project.id, biz_id=project.bk_biz_id
            )
        )
        logger.exception(message)
        return Response({"result": False, "message": message, "code": err_code.CONTENT_NOT_EXIST.code})

    node_id = request.GET.get("node_id")
    target_ip = request.GET.get("target_ip")

    return Response(fetch_node_job_executed_log(node_id, project.bk_biz_id, target_ip))
