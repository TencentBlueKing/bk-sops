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

# 第三方插件节点的只读回答流：把插件后台 ``bk_plugin/plugin_api/answer_stream/{trace_id}/`` 的 SSE
# 转发给节点详情页面。节点运行中为实时回答；节点结束后插件返回会话记录中的思考过程（正文以正式输出为准）。
# 只读：不影响节点执行、轮询和正式输出。

import json
import logging
import os
import re
import time

import requests
from bamboo_engine import api as bamboo_engine_api
from bamboo_engine import states as bamboo_engine_states
from django.http import StreamingHttpResponse
from pipeline.eri.runtime import BambooDjangoRuntime

from gcloud.taskflow3.models import TaskFlowInstance
from plugin_service import env as plugin_service_env
from plugin_service.exceptions import PluginServiceException
from plugin_service.plugin_client import PluginServiceApiClient

logger = logging.getLogger("root")

REMOTE_PLUGIN_CODE = "remote_plugin"
# 运行中返回实时回答，结束后返回历史思考过程
STREAM_STATES = {bamboo_engine_states.RUNNING, bamboo_engine_states.FINISHED, bamboo_engine_states.FAILED}
# BPF trace_id 为 uuid4().hex，这里只做路径安全校验
TRACE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

CONNECT_TIMEOUT = 5
# 节点刚进入 RUNNING 时 invoke 可能尚未返回 trace_id，在此预算内等待
READY_WAIT = 20
READY_RETRY_INTERVAL = 1
# 插件空闲时约 15s 发一次心跳，读取超时需大于该间隔
READ_TIMEOUT = 60
MAX_DURATION = 30 * 60


class AnswerStreamUnavailable(Exception):
    """当前节点无法提供回答流，reason 返回给页面。"""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def sse(event: str, data: dict) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


def _node_component_code(task, node_id: str, subprocess_stack: list) -> str:
    pipeline = task.pipeline_instance.execution_data
    try:
        for subprocess_id in subprocess_stack:
            pipeline = pipeline["activities"][subprocess_id]["pipeline"]
        node = pipeline["activities"][node_id]
    except (KeyError, TypeError):
        raise AnswerStreamUnavailable("node_not_found")
    if node.get("type") != "ServiceActivity":
        return ""
    return (node.get("component") or {}).get("code") or ""


def locate_upstream(task, node_id: str, subprocess_stack: list = None, loop=None) -> str:
    """定位节点当前执行对应的插件回答流地址。调用方需已校验任务查看权限。"""
    subprocess_stack = subprocess_stack or []
    if task.engine_ver != 2:
        raise AnswerStreamUnavailable("engine_not_supported")
    if not task.has_node(node_id):
        raise AnswerStreamUnavailable("node_not_found")
    if _node_component_code(task, node_id, subprocess_stack) != REMOTE_PLUGIN_CODE:
        raise AnswerStreamUnavailable("not_remote_plugin")

    runtime = BambooDjangoRuntime()
    states_result = bamboo_engine_api.get_children_states(runtime=runtime, node_id=node_id)
    node_state = (states_result.data or {}).get(node_id) if states_result.result else None
    if not node_state or node_state.get("state") not in STREAM_STATES:
        raise AnswerStreamUnavailable("not_running")
    # 只有运行中才可能稍后拿到 trace_id；已结束的节点没有就是没有，不必等待
    not_ready = "not_ready" if node_state["state"] == bamboo_engine_states.RUNNING else "no_trace_id"
    if loop is not None and int(loop) < node_state.get("loop", 1):
        raise AnswerStreamUnavailable("not_current_loop")

    data_result = bamboo_engine_api.get_execution_data(runtime=runtime, node_id=node_id)
    if not data_result.result:
        raise AnswerStreamUnavailable(not_ready)
    plugin_code = (data_result.data.get("inputs") or {}).get("plugin_code")
    trace_id = (data_result.data.get("outputs") or {}).get("trace_id")
    if not plugin_code or not trace_id:
        raise AnswerStreamUnavailable(not_ready)
    if not TRACE_ID_PATTERN.match(str(trace_id)):
        raise AnswerStreamUnavailable("invalid_trace_id")

    try:
        client = PluginServiceApiClient(plugin_code)
    except PluginServiceException as e:
        logger.warning("[answer_stream] plugin client init failed plugin=%s: %s", plugin_code, e)
        raise AnswerStreamUnavailable("plugin_service_error")
    return os.path.join(client.plugin_host, "plugin_api", "answer_stream", str(trace_id)) + "/"


def answer_events(task, node_id: str, subprocess_stack: list = None, loop=None, clock=time.monotonic, sleep=time.sleep):
    """定位并转发节点回答流；关联未就绪时有限等待，期间发送心跳。"""
    started = clock()
    while True:
        try:
            url = locate_upstream(task, node_id, subprocess_stack, loop)
            break
        except AnswerStreamUnavailable as e:
            if e.reason != "not_ready" or clock() - started >= READY_WAIT:
                yield sse("unsupported", {"reason": e.reason})
                return
        yield b": waiting\n\n"
        sleep(READY_RETRY_INTERVAL)
    yield from proxy_answer_stream(url, clock=clock)


def proxy_answer_stream(url: str, clock=time.monotonic):
    """转发插件 SSE 字节流。上游不支持或出错时转成 unsupported / end 事件。

    页面关闭时 Django 关闭本生成器，``with`` 退出即关闭上游连接。
    """
    try:
        response = requests.get(
            url,
            stream=True,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            headers={"Accept": "text/event-stream"},
        )
    except requests.RequestException as e:
        logger.warning("[answer_stream] upstream connect failed url=%s: %s", url, e)
        yield sse("unsupported", {"reason": "upstream_unreachable"})
        return

    with response:
        if response.status_code != 200:
            try:
                reason = response.json().get("reason") or ""
            except ValueError:
                reason = ""
            yield sse("unsupported", {"reason": reason or f"upstream_{response.status_code}"})
            return

        started = clock()
        try:
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    yield chunk
                if clock() - started > MAX_DURATION:
                    yield sse("end", {"reason": "timeout"})
                    return
        except requests.RequestException as e:
            logger.warning("[answer_stream] upstream broken url=%s: %s", url, e)
            yield sse("end", {"reason": "upstream_error"})


def answer_stream_response(project_id, query) -> StreamingHttpResponse:
    """节点详情回答流接口：开关关闭时只返回一条 unsupported。调用方需已校验任务查看权限。"""
    if plugin_service_env.ENABLE_NODE_ANSWER_STREAM:
        task = TaskFlowInstance.objects.get(pk=query["instance_id"], project_id=project_id)
        subprocess_stack = json.loads(query.get("subprocess_stack", "[]"))
        events = answer_events(task, query["node_id"], subprocess_stack, query.get("loop"))
    else:
        events = iter([sse("unsupported", {"reason": "disabled"})])

    response = StreamingHttpResponse(events, content_type="text/event-stream; charset=utf-8")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
