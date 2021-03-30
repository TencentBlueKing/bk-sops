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
from typing import Optional, List

from bamboo_engine import api as bamboo_engine_api
from pipeline.engine import api as pipeline_api
from pipeline.service import task_service
from pipeline.models import PipelineInstance
from pipeline.parser.context import get_pipeline_context
from pipeline.eri.runtime import BambooDjangoRuntime
from pipeline.log.models import LogEntry
from pipeline.component_framework.library import ComponentLibrary
from pipeline import exceptions as pipeline_exceptions

from gcloud import err_code
from gcloud.utils.handlers import handle_plain_log
from pipeline_web.parser import WebPipelineAdapter

from .base import EngineCommandDispatcher, ensure_return_has_code, ensure_return_is_dict

logger = logging.getLogger("root")


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

    def _get_act_web_info(self, act_id: str, pipeline: dict):
        def get_act_of_pipeline(pipeline):
            for node_id, node_info in list(pipeline["activities"].items()):
                if node_id == act_id:
                    return node_info
                elif node_info["type"] == "SubProcess":
                    act = get_act_of_pipeline(node_info["pipeline"])
                    if act:
                        return act

        return get_act_of_pipeline(pipeline)

    def get_node_data(self, username: str, component_code: Optional[str] = None, loop: Optional[int] = None, **kwargs):
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        return getattr(self, "get_node_data_v{}".format(self.engine_ver))(
            username=username, component_code=component_code, loop=loop, **kwargs
        )

    def _prerender_node_data(
        self, pipeline_instance: PipelineInstance, subprocess_stack: List[str], username: str
    ) -> (bool, str, dict, dict):
        try:
            inputs = WebPipelineAdapter(pipeline_instance.execution_data).get_act_inputs(
                act_id=self.node_id,
                subprocess_stack=subprocess_stack,
                root_pipeline_data=get_pipeline_context(
                    pipeline_instance, obj_type="instance", data_type="data", username=username
                ),
                root_pipeline_context=get_pipeline_context(
                    pipeline_instance, obj_type="instance", data_type="context", username=username
                ),
            )
            outputs = {}
        except Exception:
            logger.exception(
                "_prerender_node_data(node_id:{}, subprocess_stack:{}, username: {}) fail".format(
                    self.node_id, subprocess_stack, username
                )
            )
            return False, "_prerender_node_data fail", {}, {}

        if not isinstance(inputs, dict):
            inputs = {}

        return True, "", inputs, outputs

    def _format_outputs(
        self, outputs: dict, component_code: str, pipeline_instance: PipelineInstance
    ) -> (bool, str, list):
        outputs_table = []
        if component_code:
            version = (
                self._get_act_web_info(self.node_id, pipeline_instance.execution_data)
                .get("component", {})
                .get("version", None)
            )
            try:
                component = ComponentLibrary.get_component_class(component_code=component_code, version=version)
                outputs_format = component.outputs_format()
            except Exception:
                logger.exception(
                    "_format_outputs(node_id: {}, outputs: {}, component_code: {}) fail".format(
                        self.node_id, outputs, component_code
                    )
                )
                return False, "_format_outputs fail", []
            else:
                # for some special empty case e.g. ''
                outputs_data = outputs.get("outputs") or {}
                # 在标准插件定义中的预设输出参数
                archived_keys = []
                for outputs_item in outputs_format:
                    value = outputs_data.get(outputs_item["key"], "")
                    outputs_table.append(
                        {"name": outputs_item["name"], "key": outputs_item["key"], "value": value, "preset": True}
                    )
                    archived_keys.append(outputs_item["key"])
                # 其他输出参数
                for out_key, out_value in list(outputs_data.items()):
                    if out_key not in archived_keys:
                        outputs_table.append({"name": out_key, "key": out_key, "value": out_value, "preset": False})
        else:
            try:
                outputs_table = [
                    {"key": key, "value": val, "preset": False} for key, val in list(outputs.get("outputs", {}).items())
                ]
            except Exception:
                logger.exception(
                    "_format_outputs(node_id: {}, outputs: {}, component_code: {}) fail".format(
                        self.node_id, outputs, component_code
                    )
                )
                return False, "_format_outputs fail", []

        return True, "", outputs_table

    def get_node_data_v1(
        self, username: str, component_code: Optional[str] = None, loop: Optional[int] = None, **kwargs
    ):
        act_started = True
        inputs = {}
        outputs = {}
        try:
            detail = pipeline_api.get_status_tree(self.node_id)
        except pipeline_exceptions.InvalidOperationException:
            act_started = False
        else:
            # 最新 loop 执行记录，直接通过接口获取
            if loop is None or int(loop) >= detail["loop"]:
                inputs = pipeline_api.get_inputs(self.node_id)
                outputs = pipeline_api.get_outputs(self.node_id)
            # 历史 loop 记录，需要从 histories 获取，并取最新一次操作数据（如手动重试时重新填参）
            else:
                his_data = pipeline_api.get_activity_histories(self.node_id, loop)
                inputs = his_data[-1]["inputs"]
                outputs = {"outputs": his_data[-1]["outputs"], "ex_data": his_data[-1]["ex_data"]}

        pipeline_instance = kwargs["pipeline_instance"]
        subprocess_stack = kwargs["subprocess_stack"]
        if not act_started:
            success, err, inputs, outputs = self._prerender_node_data(
                pipeline_instance=pipeline_instance, subprocess_stack=subprocess_stack, username=username
            )
            if not success:
                return {
                    "result": False,
                    "data": {},
                    "message": err,
                    "code": err_code.UNKNOWN_ERROR.code,
                }

        # 根据传入的 component_code 对输出进行格式化
        success, err, outputs_table = self._format_outputs(
            outputs=outputs, component_code=component_code, pipeline_instance=pipeline_instance
        )
        if not success:
            return {
                "result": False,
                "data": {},
                "message": err,
                "code": err_code.UNKNOWN_ERROR.code,
            }

        data = {"inputs": inputs, "outputs": outputs_table, "ex_data": outputs.pop("ex_data", "")}
        return {"result": True, "data": data, "message": "", "code": err_code.SUCCESS.code}

    def get_node_data_v2(
        self, username: str, component_code: Optional[str] = None, loop: Optional[int] = None, **kwargs
    ):
        runtime = BambooDjangoRuntime()
        result = bamboo_engine_api.get_children_states(runtime=runtime, node_id=self.node_id)
        if not result.result:
            logger.exception("bamboo_engine_api.get_children_states fail")
            return {
                "result": False,
                "data": {},
                "message": "{}: {}".format(result.message, result.exc),
                "code": err_code.UNKNOWN_ERROR.code,
            }

        state = result.data
        # 已执行的节点直接获取执行数据
        inputs = {}
        outputs = {}
        pipeline_instance = kwargs["pipeline_instance"]
        subprocess_stack = kwargs["subprocess_stack"]

        if state:
            # 获取最新的执行数据
            if loop is None or int(loop) >= state["loop"]:
                result = bamboo_engine_api.get_execution_data(runtime=runtime, node_id=self.node_id)
                if not result.result:
                    logger.exception("bamboo_engine_api.get_execution_data fail")
                    return {
                        "result": False,
                        "data": {},
                        "message": "{}: {}".format(result.message, result.exc),
                        "code": err_code.UNKNOWN_ERROR.code,
                    }

                data = result.data
                inputs = data["inputs"]
                outputs = data["outputs"]
                outputs = {"outputs": outputs, "ex_data": outputs.get("ex_data")}
            # 读取历史记录
            else:
                result = bamboo_engine_api.get_node_histories(runtime=runtime, node_id=self.node_id, loop=loop)
                if not result.result:
                    logger.exception("bamboo_engine_api.get_node_histories fail")
                    return {
                        "result": False,
                        "data": {},
                        "message": "{}: {}".format(result.message, result.exc),
                        "code": err_code.UNKNOWN_ERROR.code,
                    }

                hist = result.data
                if hist:
                    inputs = hist[-1]["inputs"]
                    outputs = hist[-1]["outputs"]
                    outputs = {"outputs": outputs, "ex_data": outputs.get("ex_data")}
        # 未执行节点需要实时渲染
        else:
            success, err, inputs, outputs = self._prerender_node_data(
                pipeline_instance=pipeline_instance, subprocess_stack=subprocess_stack, username=username
            )
            if not success:
                return {
                    "result": False,
                    "data": {},
                    "message": err,
                    "code": err_code.UNKNOWN_ERROR.code,
                }

        # 根据传入的 component_code 对输出进行格式化
        success, err, outputs_table = self._format_outputs(
            outputs=outputs, component_code=component_code, pipeline_instance=pipeline_instance
        )
        if not success:
            return {
                "result": False,
                "data": {},
                "message": err,
                "code": err_code.UNKNOWN_ERROR.code,
            }

        data = {"inputs": inputs, "outputs": outputs_table, "ex_data": outputs.pop("ex_data", "")}
        return {
            "result": True,
            "data": data,
            "message": "",
            "code": err_code.SUCCESS.code,
        }
