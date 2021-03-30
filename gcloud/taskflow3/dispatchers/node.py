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

from bamboo_engine import api as bamboo_engine_api
from pipeline.service import task_service
from pipeline.eri.runtime import BambooDjangoRuntime
from pipeline.log.models import LogEntry

from gcloud import err_code
from gcloud.utils.handlers import handle_plain_log

from .base import EngineCommandDispatcher, ensure_return_has_code, ensure_return_is_dict


class NodeCommandDispatcher(EngineCommandDispatcher):
    NODE_COMMANDS = {
        "retry",
        "skip",
        "callback",
        "skip_exg",
        "pause",
        "resume",
        "pause_subproc",
        "resume_subproc",
        "forced_fail",
    }

    def __init__(self, engine_ver: int, node_id: str):
        self.engine_ver = engine_ver
        self.node_id = node_id

    def dispatch(self, command: str, operator: str, **kwargs) -> dict:
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        if command not in self.NODE_COMMANDS:
            return {"result": False, "message": "task command is invalid", "code": err_code.INVALID_OPERATION.code}

        return getattr(self, "{}_v{}".format(command, self.engine_ver))(operator=operator, **kwargs)

    @ensure_return_has_code
    def retry_v1(self, operator: str, **kwargs) -> dict:
        return task_service.retry_activity(act_id=self.node_id, inputs=kwargs["inputs"])

    @ensure_return_is_dict
    def retry_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.retry_node(runtime=BambooDjangoRuntime(), node_id=self.node_id, data=kwargs["inputs"])

    @ensure_return_has_code
    def skip_v1(self, operator: str, **kwargs) -> dict:
        return task_service.skip_activity(self.node_id)

    @ensure_return_is_dict
    def skip_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.skip_node(runtime=BambooDjangoRuntime(), node_id=self.node_id)

    @ensure_return_has_code
    def callback_v1(self, operator: str, **kwargs) -> dict:
        return task_service.callback(act_id=self.node_id, data=kwargs["data"])

    @ensure_return_is_dict
    def callback_v2(self, operator: str, **kwargs) -> dict:
        # 兼容 pipeline 引擎时期 callback 可以不传 version 的请求
        runtime = BambooDjangoRuntime()
        version = kwargs.get("version")
        if not version:
            version = runtime.get_state(self.node_id).version

        return bamboo_engine_api.callback(runtime=runtime, node_id=self.node_id, version=version, data=kwargs["data"])

    @ensure_return_has_code
    def skip_exg_v1(self, operator: str, **kwargs) -> dict:
        return task_service.skip_exclusive_gateway(gateway_id=self.node_id, flow_id=kwargs["flow_id"])

    @ensure_return_is_dict
    def skip_exg_v2(self, operator: str, **kwargs) -> dict:
        result = bamboo_engine_api.skip_exclusive_gateway(
            runtime=BambooDjangoRuntime(), node_id=self.node_id, flow_id=kwargs["flow_id"]
        )
        return self._bamboo_api_result_to_dict(result)

    @ensure_return_has_code
    def pause_v1(self, operator: str, **kwargs) -> dict:
        return task_service.pause_activity(self.node_id)

    @ensure_return_is_dict
    def pause_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.pause_node_appoint(runtime=BambooDjangoRuntime(), node_id=self.node_id)

    @ensure_return_has_code
    def resume_v1(self, operator: str, **kwargs) -> dict:
        return task_service.resume_activity(self.node_id)

    @ensure_return_is_dict
    def resume_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.resume_node_appoint(runtime=BambooDjangoRuntime(), node_id=self.node_id)

    @ensure_return_has_code
    def pause_subproc_v1(self, operator: str, **kwargs) -> dict:
        return task_service.pause_pipeline(self.node_id)

    @ensure_return_is_dict
    def pause_subproc_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.pause_pipeline(runtime=BambooDjangoRuntime(), pipeline_id=self.node_id)

    @ensure_return_has_code
    def resume_subproc_v1(self, operator: str, **kwargs) -> dict:
        return task_service.resume_pipeline(self.node_id)

    @ensure_return_is_dict
    def resume_subproc_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.resume_pipeline(runtime=BambooDjangoRuntime(), pipeline_id=self.node_id)

    @ensure_return_has_code
    def forced_fail_v1(self, operator: str, **kwargs) -> dict:
        return task_service.forced_fail(at_id=self.node_id, ex_data="forced fail by {}".format(operator))

    @ensure_return_is_dict
    def forced_fail_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.forced_fail_activity(
            runtime=BambooDjangoRuntime(), node_id=self.node_id, ex_data="forced fail by {}".format(operator)
        )

    def get_node_log(self, history_id: int) -> dict:
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        return getattr(self, "get_node_log_v{}".format(self.engine_ver))(history_id)

    def get_node_log_v1(self, history_id: int) -> dict:
        return {
            "result": True,
            "data": handle_plain_log(LogEntry.objects.plain_log_for_node(node_id=self.node_id, history_id=history_id)),
            "message": "",
        }

    def get_node_log_v2(self, history_id: int) -> dict:
        runtime = BambooDjangoRuntime()
        return {
            "result": True,
            "data": handle_plain_log(runtime.get_plain_log_for_node(node_id=self.node_id, history_id=history_id)),
            "message": "",
        }
