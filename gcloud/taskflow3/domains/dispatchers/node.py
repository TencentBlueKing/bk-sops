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
from bamboo_engine import states as bamboo_engine_states
from engine_pickle_obj.context import SystemObject
from gcloud.project_constants.domains.context import get_project_constants_context
from pipeline.engine import states as pipeline_states
from pipeline.engine import api as pipeline_api
from pipeline.service import task_service
from pipeline.models import PipelineInstance
from pipeline.parser.context import get_pipeline_context
from pipeline.eri.runtime import BambooDjangoRuntime
from pipeline.eri.models import ExecutionData
from pipeline.log.models import LogEntry
from pipeline.component_framework.library import ComponentLibrary
from pipeline.engine import exceptions as pipeline_exceptions

from gcloud import err_code
from gcloud.utils.handlers import handle_plain_log
from gcloud.taskflow3.utils import format_pipeline_status
from pipeline_web.parser import WebPipelineAdapter
from pipeline_web.parser.format import format_web_data_to_pipeline

from .base import EngineCommandDispatcher, ensure_return_is_dict

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

    @ensure_return_is_dict
    def retry_v1(self, operator: str, **kwargs) -> dict:
        return task_service.retry_activity(act_id=self.node_id, inputs=kwargs["inputs"])

    @ensure_return_is_dict
    def retry_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.retry_node(runtime=BambooDjangoRuntime(), node_id=self.node_id, data=kwargs["inputs"])

    @ensure_return_is_dict
    def skip_v1(self, operator: str, **kwargs) -> dict:
        return task_service.skip_activity(self.node_id)

    @ensure_return_is_dict
    def skip_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.skip_node(runtime=BambooDjangoRuntime(), node_id=self.node_id)

    @ensure_return_is_dict
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

    @ensure_return_is_dict
    def skip_exg_v1(self, operator: str, **kwargs) -> dict:
        return task_service.skip_exclusive_gateway(gateway_id=self.node_id, flow_id=kwargs["flow_id"])

    @ensure_return_is_dict
    def skip_exg_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.skip_exclusive_gateway(
            runtime=BambooDjangoRuntime(), node_id=self.node_id, flow_id=kwargs["flow_id"]
        )

    @ensure_return_is_dict
    def pause_v1(self, operator: str, **kwargs) -> dict:
        return task_service.pause_activity(self.node_id)

    @ensure_return_is_dict
    def pause_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.pause_node_appoint(runtime=BambooDjangoRuntime(), node_id=self.node_id)

    @ensure_return_is_dict
    def resume_v1(self, operator: str, **kwargs) -> dict:
        return task_service.resume_activity(self.node_id)

    @ensure_return_is_dict
    def resume_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.resume_node_appoint(runtime=BambooDjangoRuntime(), node_id=self.node_id)

    @ensure_return_is_dict
    def pause_subproc_v1(self, operator: str, **kwargs) -> dict:
        return task_service.pause_pipeline(self.node_id)

    @ensure_return_is_dict
    def pause_subproc_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.pause_pipeline(runtime=BambooDjangoRuntime(), pipeline_id=self.node_id)

    @ensure_return_is_dict
    def resume_subproc_v1(self, operator: str, **kwargs) -> dict:
        return task_service.resume_activity(self.node_id)

    @ensure_return_is_dict
    def resume_subproc_v2(self, operator: str, **kwargs) -> dict:
        return bamboo_engine_api.resume_pipeline(runtime=BambooDjangoRuntime(), pipeline_id=self.node_id)

    @ensure_return_is_dict
    def forced_fail_v1(self, operator: str, **kwargs) -> dict:
        return task_service.forced_fail(act_id=self.node_id, ex_data="forced fail by {}".format(operator))

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

    def _get_node_info(self, node_id: str, pipeline: dict, subprocess_stack: Optional[list] = None) -> dict:
        subprocess_stack = subprocess_stack or []

        def get_node_info(pipeline: dict, subprocess_stack: list) -> dict:
            # go deeper
            if subprocess_stack:
                return get_node_info(pipeline["activities"][subprocess_stack[0]]["pipeline"], subprocess_stack[1:])

            nodes = {
                pipeline["start_event"]["id"]: pipeline["start_event"],
                pipeline["end_event"]["id"]: pipeline["end_event"],
            }
            nodes.update(pipeline["activities"])
            nodes.update(pipeline["gateways"])
            return nodes[node_id]

        return get_node_info(pipeline, subprocess_stack)

    def get_node_data(
        self,
        username: str,
        subprocess_stack: List[str],
        component_code: Optional[str] = None,
        loop: Optional[int] = None,
        **kwargs,
    ) -> dict:
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        data = getattr(self, "get_node_data_v{}".format(self.engine_ver))(
            username=username, component_code=component_code, loop=loop, subprocess_stack=subprocess_stack, **kwargs
        )
        if data["result"] and isinstance(data["data"]["ex_data"], str):
            data["data"]["ex_data"] = handle_plain_log(data["data"]["ex_data"])

        return data

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
        self,
        outputs: dict,
        component_code: str,
        pipeline_instance: PipelineInstance,
        subprocess_stack: Optional[list] = None,
    ) -> (bool, str, list):
        outputs_table = []
        if component_code:
            version = (
                self._get_node_info(self.node_id, pipeline_instance.execution_data, subprocess_stack)
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
                    {"key": key, "value": val, "preset": False}
                    for key, val in list((outputs.get("outputs") or {}).items())
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
        self,
        username: str,
        subprocess_stack: List[str],
        component_code: Optional[str] = None,
        loop: Optional[int] = None,
        **kwargs,
    ) -> dict:
        node_started = True
        inputs = {}
        outputs = {}
        try:
            detail = pipeline_api.get_status_tree(self.node_id)
        except pipeline_exceptions.InvalidOperationException:
            node_started = False
        else:
            # 最新 loop 执行记录，直接通过接口获取
            if loop is None or int(loop) >= detail["loop"]:
                inputs = pipeline_api.get_inputs(self.node_id)
                outputs = pipeline_api.get_outputs(self.node_id)
            # 历史 loop 记录，需要从 histories 获取，并取最新一次操作数据（如手动重试时重新填参）
            else:
                his_data = pipeline_api.get_activity_histories(node_id=self.node_id, loop=loop)
                inputs = his_data[-1]["inputs"]
                outputs = {"outputs": his_data[-1]["outputs"], "ex_data": his_data[-1]["ex_data"]}

        pipeline_instance = kwargs["pipeline_instance"]
        if not node_started:
            node_info = self._get_node_info(
                node_id=self.node_id, pipeline=pipeline_instance.execution_data, subprocess_stack=subprocess_stack
            )
            if node_info["type"] != "ServiceActivity":
                return {
                    "result": True,
                    "data": {"inputs": {}, "outputs": [], "ex_data": ""},
                    "message": "",
                    "code": err_code.SUCCESS.code,
                }

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
            outputs=outputs,
            component_code=component_code,
            pipeline_instance=pipeline_instance,
            subprocess_stack=subprocess_stack,
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
        self,
        username: str,
        subprocess_stack: List[str],
        component_code: Optional[str] = None,
        loop: Optional[int] = None,
        **kwargs,
    ) -> dict:
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

        if state:
            # 获取最新的执行数据
            if loop is None or int(loop) >= state["loop"]:
                result = bamboo_engine_api.get_execution_data(runtime=runtime, node_id=self.node_id)
                if not result.result:
                    logger.exception("bamboo_engine_api.get_execution_data fail")

                    # 对上层屏蔽执行数据不存在的场景
                    if isinstance(result.exc, ExecutionData.DoesNotExist):
                        return {
                            "result": True,
                            "data": {"inputs": {}, "outputs": [], "ex_data": ""},
                            "message": "",
                            "code": err_code.SUCCESS.code,
                        }
                    else:
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
            node_info = self._get_node_info(
                node_id=self.node_id, pipeline=pipeline_instance.execution_data, subprocess_stack=subprocess_stack
            )
            if node_info["type"] != "ServiceActivity":
                return {
                    "result": True,
                    "data": {"inputs": {}, "outputs": [], "ex_data": ""},
                    "message": "",
                    "code": err_code.SUCCESS.code,
                }
            try:
                root_pipeline_data = get_pipeline_context(
                    pipeline_instance, obj_type="instance", data_type="data", username=username
                )
                system_obj = SystemObject(root_pipeline_data)
                root_pipeline_context = {"${_system}": system_obj}
                root_pipeline_context.update(get_project_constants_context(kwargs["project_id"]))

                formatted_pipeline = format_web_data_to_pipeline(pipeline_instance.execution_data)
                preview_result = bamboo_engine_api.preview_node_inputs(
                    runtime=runtime,
                    pipeline=formatted_pipeline,
                    node_id=self.node_id,
                    subprocess_stack=subprocess_stack,
                    root_pipeline_data=root_pipeline_data,
                    current_constants=root_pipeline_context,
                )

                if not preview_result.result:
                    return {
                        "result": False,
                        "data": {},
                        "message": preview_result.message,
                        "code": err_code.UNKNOWN_ERROR.code,
                    }
                inputs = preview_result.data

            except Exception as err:
                return {
                    "result": False,
                    "data": {},
                    "message": err,
                    "code": err_code.UNKNOWN_ERROR.code,
                }

        # 根据传入的 component_code 对输出进行格式化
        success, err, outputs_table = self._format_outputs(
            outputs=outputs,
            component_code=component_code,
            pipeline_instance=pipeline_instance,
            subprocess_stack=subprocess_stack,
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

    def get_node_detail(
        self,
        username: str,
        subprocess_stack: List[str],
        component_code: Optional[str] = None,
        loop: Optional[int] = None,
        **kwargs,
    ) -> dict:
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        detail = getattr(self, "get_node_detail_v{}".format(self.engine_ver))(
            username=username, component_code=component_code, loop=loop, subprocess_stack=subprocess_stack, **kwargs
        )
        if detail["result"]:
            for hist in detail["data"].get("histories", []):
                if isinstance(hist.get("ex_data"), str):
                    hist["ex_data"] = handle_plain_log(hist["ex_data"])

        return detail

    def _assemble_histroy_detail(self, detail: dict, histories: list):
        # index 为 -1 表示当前 loop 的最新一次重试执行，历史 loop 最终状态一定是 FINISHED
        current_loop = histories[-1]
        current_loop["state"] = bamboo_engine_states.FINISHED
        format_pipeline_status(current_loop)
        detail.update(
            {
                "start_time": current_loop["start_time"],
                "finish_time": current_loop["finish_time"],
                "elapsed_time": current_loop["elapsed_time"],
                "loop": current_loop["loop"],
                "skip": current_loop["skip"],
                "state": current_loop["state"],
            }
        )
        # index 非 -1 表示当前 loop 的重试记录
        detail["histories"] = histories[1:]

    def get_node_detail_v1(
        self,
        username: str,
        subprocess_stack: List[str],
        component_code: Optional[str] = None,
        loop: Optional[int] = None,
        **kwargs,
    ) -> dict:
        act_start = True
        detail = {}
        # 首先获取最新一次执行详情
        try:
            detail = pipeline_api.get_status_tree(self.node_id)
        except pipeline_exceptions.InvalidOperationException:
            act_start = False

        if not act_start:
            pipeline_instance = kwargs["pipeline_instance"]
            node = self._get_node_info(
                node_id=self.node_id, pipeline=pipeline_instance.execution_data, subprocess_stack=subprocess_stack
            )
            detail.update(
                {
                    "name": node["name"],
                    "error_ignorable": node.get("error_ignorable", False),
                    "state": pipeline_states.READY,
                }
            )
        else:
            format_pipeline_status(detail)
            # 默认只请求最后一次循环结果
            if loop is None or int(loop) >= detail["loop"]:
                loop = detail["loop"]
                detail["histories"] = pipeline_api.get_activity_histories(node_id=self.node_id, loop=loop)
            # 如果用户传了 loop 参数，并且 loop 小于当前节点已循环次数 detail['loop']，则从历史数据获取结果
            else:
                self._assemble_histroy_detail(
                    detail=detail, histories=pipeline_api.get_activity_histories(node_id=self.node_id, loop=loop)
                )

            for hist in detail["histories"]:
                # 重试记录必然是因为失败才重试
                hist.setdefault("state", pipeline_states.FAILED)
                format_pipeline_status(hist)

        if "error_ignorable" in detail:
            detail["error_ignored"] = detail["error_ignorable"]
        return {"result": True, "data": detail, "message": "", "code": err_code.SUCCESS.code}

    def get_node_detail_v2(
        self,
        username: str,
        subprocess_stack: List[str],
        component_code: Optional[str] = None,
        loop: Optional[int] = None,
        **kwargs,
    ) -> dict:
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

        detail = result.data
        # 节点已经执行
        if detail:
            detail = detail[self.node_id]
            # 默认只请求最后一次循环结果
            format_pipeline_status(detail)
            if loop is None or int(loop) >= detail["loop"]:
                loop = detail["loop"]
                hist_result = bamboo_engine_api.get_node_histories(runtime=runtime, node_id=self.node_id, loop=loop)
                if not hist_result:
                    logger.exception("bamboo_engine_api.get_node_histories fail")
                    return {
                        "result": False,
                        "data": {},
                        "message": "{}: {}".format(hist_result.message, hist_result.exc),
                        "code": err_code.UNKNOWN_ERROR.code,
                    }
                for hist in hist_result.data:
                    hist["ex_data"] = hist.get("outputs", {}).get("ex_data", "")
                detail["histories"] = hist_result.data
            # 如果用户传了 loop 参数，并且 loop 小于当前节点已循环次数，则从历史数据获取结果
            else:
                hist_result = bamboo_engine_api.get_node_histories(runtime=runtime, node_id=self.node_id, loop=loop)
                if not hist_result:
                    logger.exception("bamboo_engine_api.get_node_histories fail")
                    return {
                        "result": False,
                        "data": {},
                        "message": "{}: {}".format(hist_result.message, hist_result.exc),
                        "code": err_code.UNKNOWN_ERROR.code,
                    }
                self._assemble_histroy_detail(detail=detail, histories=hist_result.data)

            for hist in detail["histories"]:
                # 重试记录必然是因为失败才重试
                hist.setdefault("state", bamboo_engine_states.FAILED)
                hist["history_id"] = hist["id"]
                format_pipeline_status(hist)
        # 节点未执行
        else:
            pipeline_instance = kwargs["pipeline_instance"]
            node = self._get_node_info(
                node_id=self.node_id, pipeline=pipeline_instance.execution_data, subprocess_stack=subprocess_stack
            )
            detail.update(
                {
                    "name": node["name"],
                    "error_ignorable": node.get("error_ignorable", False),
                    "state": bamboo_engine_states.READY,
                }
            )

        return {"result": True, "data": detail, "message": "", "code": err_code.SUCCESS.code}

    def get_outputs(self):
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        return getattr(self, "get_outputs_v{}".format(self.engine_ver))()

    def get_outputs_v1(self):
        try:
            outputs = pipeline_api.get_outputs(self.node_id)
        except Exception:
            logger.exception("pipeline_api.get_outputs(node_id={}) fail".format(self.node_id))
            outputs = {}

        return {"result": True, "data": outputs, "message": "", "code": err_code.SUCCESS.code}

    def get_outputs_v2(self):
        runtime = BambooDjangoRuntime()
        outputs_result = bamboo_engine_api.get_execution_data_outputs(runtime=runtime, node_id=self.node_id)

        if not outputs_result.result:
            logger.exception("bamboo_engine_api.get_execution_data_outputs fail")
            return {
                "result": False,
                "data": {},
                "message": "{}: {}".format(outputs_result.message, outputs_result.exc),
                "code": err_code.UNKNOWN_ERROR.code,
            }

        return {"result": True, "data": outputs_result.data, "message": "", "code": err_code.SUCCESS.code}
