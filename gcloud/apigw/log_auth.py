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

from rest_framework.response import Response

from gcloud import err_code

logger = logging.getLogger("root")


def _build_error_response(message, code):
    return Response({"result": False, "message": message, "code": code})


def get_taskflow_for_log(api_name, task_id, project):
    from gcloud.taskflow3.models import TaskFlowInstance

    try:
        return TaskFlowInstance.objects.get(id=task_id, project_id=project.id), None
    except TaskFlowInstance.DoesNotExist:
        message = (
            "[API] {api_name} task[id={task_id}] " "of project[project_id={project_id}, biz_id={biz_id}] does not exist"
        ).format(api_name=api_name, task_id=task_id, project_id=project.id, biz_id=project.bk_biz_id)
        logger.exception(message)
        return None, _build_error_response(message, err_code.CONTENT_NOT_EXIST.code)


def validate_task_node(api_name, taskflow, node_id):
    if not node_id:
        message = "[API] {api_name} node_id is required".format(api_name=api_name)
        logger.warning(message)
        return _build_error_response(message, err_code.REQUEST_PARAM_INVALID.code)

    if not taskflow.has_node(node_id):
        message = "[API] {api_name} task[id={task_id}] does not have node[{node_id}]".format(
            api_name=api_name, task_id=taskflow.id, node_id=node_id
        )
        logger.warning(message)
        return _build_error_response(message, err_code.CONTENT_NOT_EXIST.code)

    return None


def get_execution_data_for_node(api_name, node_id):
    from bamboo_engine import exceptions as bamboo_exceptions
    from pipeline.eri.runtime import BambooDjangoRuntime

    try:
        return BambooDjangoRuntime().get_execution_data(node_id=node_id), None
    except bamboo_exceptions.NotFoundError:
        message = "[API] {api_name} execution data not found for node_id: {node_id}".format(
            api_name=api_name, node_id=node_id
        )
        logger.warning(message)
        return None, _build_error_response(message, err_code.CONTENT_NOT_EXIST.code)


def validate_node_plugin_trace(api_name, node_id, trace_id, plugin_code):
    if not trace_id:
        message = "[API] {api_name} trace_id is required".format(api_name=api_name)
        logger.warning(message)
        return _build_error_response(message, err_code.REQUEST_PARAM_INVALID.code)

    if not plugin_code:
        message = "[API] {api_name} plugin_code is required".format(api_name=api_name)
        logger.warning(message)
        return _build_error_response(message, err_code.REQUEST_PARAM_INVALID.code)

    execution_data, error_response = get_execution_data_for_node(api_name, node_id)
    if error_response is not None:
        return error_response

    outputs = getattr(execution_data, "outputs", {}) or {}
    node_trace_id = outputs.get("trace_id")
    if trace_id != node_trace_id:
        message = "[API] {api_name} trace_id does not belong to node[{node_id}]".format(
            api_name=api_name, node_id=node_id
        )
        logger.warning(message)
        return _build_error_response(message, err_code.CONTENT_NOT_EXIST.code)

    inputs = getattr(execution_data, "inputs", {}) or {}
    node_plugin_code = inputs.get("plugin_code")
    if node_plugin_code and plugin_code != node_plugin_code:
        message = "[API] {api_name} plugin_code does not belong to node[{node_id}]".format(
            api_name=api_name, node_id=node_id
        )
        logger.warning(message)
        return _build_error_response(message, err_code.CONTENT_NOT_EXIST.code)

    return None
