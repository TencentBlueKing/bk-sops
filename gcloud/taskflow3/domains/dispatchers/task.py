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
import json
import logging
import traceback
import typing
from typing import Optional

from bamboo_engine import api as bamboo_engine_api
from bamboo_engine import exceptions as bamboo_engine_exceptions
from bamboo_engine import states as bamboo_engine_states
from bamboo_engine.context import Context
from bamboo_engine.eri import ContextValue
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from opentelemetry import trace
from pipeline.core.data.var import Variable
from pipeline.engine import api as pipeline_api
from pipeline.engine import exceptions as pipeline_exceptions
from pipeline.engine.models import PipelineModel
from pipeline.eri.runtime import BambooDjangoRuntime
from pipeline.eri.utils import CONTEXT_TYPE_MAP
from pipeline.exceptions import ConnectionValidateError, ConvergeMatchError, IsolateNodeError, StreamValidateError
from pipeline.models import PipelineInstance
from pipeline.parser.context import get_pipeline_context
from pipeline.service import task_service

from engine_pickle_obj.context import SystemObject
from gcloud import err_code
from gcloud.constants import TaskExtraStatus
from gcloud.project_constants.domains.context import get_project_constants_context
from gcloud.taskflow3.domains.context import TaskContext
from gcloud.taskflow3.signals import pre_taskflow_start, taskflow_started
from gcloud.taskflow3.utils import _format_status_time, find_nodes_from_pipeline_tree, format_pipeline_status
from pipeline_web.parser.format import classify_constants, format_web_data_to_pipeline

from .base import EngineCommandDispatcher, ensure_return_is_dict

logger = logging.getLogger("root")


class TaskCommandDispatcher(EngineCommandDispatcher):

    CREATED_STATUS = {
        "start_time": None,
        "state": "CREATED",
        "retry": 0,
        "skip": 0,
        "finish_time": None,
        "elapsed_time": 0,
        "children": {},
    }

    TASK_COMMANDS = {
        "start",
        "pause",
        "resume",
        "revoke",
    }

    OPERATION_TYPE_COMMANDS = {
        "pause",
        "resume",
        "revoke",
    }

    def __init__(
        self, engine_ver: int, taskflow_id: int, pipeline_instance: PipelineInstance, project_id: int, queue: str = ""
    ):
        self.engine_ver = engine_ver
        self.taskflow_id = taskflow_id
        self.pipeline_instance = pipeline_instance
        self.project_id = project_id
        self.queue = queue

    def dispatch(self, command: str, operator: str) -> dict:
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        if command not in self.TASK_COMMANDS:
            return {"result": False, "message": "task command is invalid", "code": err_code.INVALID_OPERATION.code}

        if command in self.OPERATION_TYPE_COMMANDS and not self.pipeline_instance.is_started:
            return {"result": False, "message": "task not started", "code": err_code.INVALID_OPERATION.code}

        with trace.get_tracer(__name__).start_as_current_span("task_operate") as span:
            span.set_attribute("bk_sops.task_id", self.taskflow_id)
            span.set_attribute("bk_sops.pipeline_id", self.pipeline_instance.instance_id)
            span.set_attribute("bk_sops.engine_ver", self.engine_ver)
            span.set_attribute("bk_sops.task_command", command)

            return getattr(self, "{}_v{}".format(command, self.engine_ver))(operator)

    def start_v1(self, executor: str) -> dict:
        try:
            pre_taskflow_start.send(sender=self.__class__, task_id=self.taskflow_id, executor=executor)
            result = self.pipeline_instance.start(executor=executor, queue=self.queue, check_workers=False)
            if result.result:
                taskflow_started.send(sender=self.__class__, task_id=self.taskflow_id)

            dict_result = {
                "result": result.result,
                "code": err_code.SUCCESS.code if result.result else err_code.UNKNOWN_ERROR.code,
                "message": result.message,
                "data": None,
            }
            return dict_result
        except ConvergeMatchError as e:
            message = "task[id=%s] has invalid converge, message: %s, node_id: %s" % (
                self.taskflow_id,
                str(e),
                e.gateway_id,
            )
            logger.exception(message)
            code = err_code.VALIDATION_ERROR.code

        except StreamValidateError as e:
            message = "task[id=%s] stream is invalid, message: %s, node_id: %s" % (self.taskflow_id, str(e), e.node_id)
            logger.exception(message)
            code = err_code.VALIDATION_ERROR.code

        except IsolateNodeError as e:
            message = "task[id=%s] has isolate structure, message: %s" % (self.taskflow_id, str(e))
            logger.exception(message)
            code = err_code.VALIDATION_ERROR.code

        except ConnectionValidateError as e:
            message = "task[id=%s] connection check failed, message: %s, nodes: %s" % (
                self.taskflow_id,
                e.detail,
                e.failed_nodes,
            )
            logger.exception(message)
            code = err_code.VALIDATION_ERROR.code

        except Exception as e:
            message = "task[id=%s] command failed:%s" % (self.taskflow_id, e)
            logger.exception(traceback.format_exc())
            code = err_code.UNKNOWN_ERROR.code

        return {"result": False, "message": message, "code": code}

    def start_v2(self, executor: str) -> dict:
        # CAS
        pre_taskflow_start.send(sender=self.__class__, task_id=self.taskflow_id, executor=executor)
        update_success = PipelineInstance.objects.filter(
            instance_id=self.pipeline_instance.instance_id, is_started=False
        ).update(start_time=timezone.now(), is_started=True, executor=executor)
        self.pipeline_instance.calculate_tree_info()
        PipelineInstance.objects.filter(instance_id=self.pipeline_instance.instance_id).update(
            tree_info_id=self.pipeline_instance.tree_info.id
        )

        if not update_success:
            message = _("任务操作失败: 已启动的任务不可再次启动 | start_v2")
            logger.error(message)
            return {"result": False, "message": message, "code": err_code.INVALID_OPERATION.code}

        try:
            # convert web pipeline to pipeline
            pipeline = format_web_data_to_pipeline(self.pipeline_instance.execution_data)

            root_pipeline_data = get_pipeline_context(
                self.pipeline_instance, obj_type="instance", data_type="data", username=executor
            )
            system_obj = SystemObject(root_pipeline_data)
            root_pipeline_context = {"${_system}": system_obj}
            root_pipeline_context.update(get_project_constants_context(self.project_id))

            # run pipeline
            result = bamboo_engine_api.run_pipeline(
                runtime=BambooDjangoRuntime(),
                pipeline=pipeline,
                root_pipeline_data=root_pipeline_data,
                root_pipeline_context=root_pipeline_context,
                subprocess_context=root_pipeline_context,
                queue=self.queue,
                cycle_tolerate=True,
            )
        except Exception as e:
            logger.exception("run pipeline failed")
            PipelineInstance.objects.filter(instance_id=self.pipeline_instance.instance_id, is_started=True).update(
                start_time=None,
                is_started=False,
                executor="",
            )
            message = _(f"任务启动失败: 引擎启动失败, 请重试. 如持续失败可联系管理员处理. {e} | start_v2")
            logger.error(message)
            return {
                "result": False,
                "message": message,
                "code": err_code.UNKNOWN_ERROR.code,
            }

        if not result.result:
            PipelineInstance.objects.filter(instance_id=self.pipeline_instance.instance_id, is_started=True).update(
                start_time=None,
                is_started=False,
                executor="",
            )
            logger.error("run_pipeline fail: {}, exception: {}".format(result.message, result.exc_trace))
        else:
            taskflow_started.send(sender=self.__class__, task_id=self.taskflow_id)

        dict_result = {
            "result": result.result,
            "message": result.message,
            "code": err_code.SUCCESS.code if result.result else err_code.UNKNOWN_ERROR.code,
        }

        return dict_result

    @ensure_return_is_dict
    def pause_v1(self, operator: str) -> dict:
        return task_service.pause_pipeline(pipeline_id=self.pipeline_instance.instance_id)

    @ensure_return_is_dict
    def pause_v2(self, operator: str) -> dict:
        return bamboo_engine_api.pause_pipeline(
            runtime=BambooDjangoRuntime(), pipeline_id=self.pipeline_instance.instance_id
        )

    @ensure_return_is_dict
    def resume_v1(self, operator: str) -> dict:
        return task_service.resume_pipeline(pipeline_id=self.pipeline_instance.instance_id)

    @ensure_return_is_dict
    def resume_v2(self, operator: str) -> dict:
        return bamboo_engine_api.resume_pipeline(
            runtime=BambooDjangoRuntime(), pipeline_id=self.pipeline_instance.instance_id
        )

    @ensure_return_is_dict
    def revoke_v1(self, operator: str) -> dict:
        return task_service.revoke_pipeline(pipeline_id=self.pipeline_instance.instance_id)

    @ensure_return_is_dict
    def revoke_v2(self, operator: str) -> dict:
        return bamboo_engine_api.revoke_pipeline(
            runtime=BambooDjangoRuntime(), pipeline_id=self.pipeline_instance.instance_id
        )

    def set_task_constants(
        self, task_is_started: bool, task_is_finished: bool, constants: dict, meta_constants: dict
    ) -> dict:
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        if task_is_finished:
            return {
                "result": False,
                "message": "task is finished",
                "data": None,
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }

        # 产品需要，暂时放开修改，不进行检查
        # taskflow_model = apps.get_model("taskflow3", "TaskFlowInstance")
        # try:
        #     taskflow = taskflow_model.objects.get(id=self.taskflow_id)
        # except taskflow_model.DoesNotExist as e:
        #     logger.exception(f"[set_task_constants] Taskflow does not exist: {e}")
        #     return {
        #         "result": False,
        #         "message": _(f"校验失败: 任务[{self.taskflow_id}]不存在"),
        #         "data": None,
        #         "code": err_code.REQUEST_PARAM_INVALID.code,
        #     }

        # # 检查是否是根任务
        # if taskflow.is_child_taskflow:
        #     return {
        #         "result": False,
        #         "message": _(f"校验失败: 任务[{taskflow.id}]不是根任务"),
        #         "data": None,
        #         "code": err_code.REQUEST_PARAM_INVALID.code,
        #     }

        # # 检查是否有已使用的变量被修改
        # handler = TaskConstantsHandler(taskflow)
        # rendered_keys = handler.get_rendered_constant_keys()
        # modify_keys = set(constants.keys()).union(set(meta_constants.keys()))
        # invalid_keys = modify_keys.intersection(rendered_keys)
        # if invalid_keys:
        #     message = _(f"任务[{self.taskflow_id}]参数设置失败: 以下参数已被使用，不可修改: {','.join(invalid_keys)}")
        #     logger.error(message)
        #     return {
        #         "result": False,
        #         "message": message,
        #         "data": None,
        #         "code": err_code.REQUEST_PARAM_INVALID.code,
        #     }

        exec_data = self.pipeline_instance.execution_data

        pre_render_constants = []
        hide_constants = []
        component_outputs = []
        validate_keys = set()
        validate_keys = validate_keys.union(constants.keys())
        validate_keys = validate_keys.union(meta_constants.keys())
        for key in validate_keys:
            if key not in exec_data["constants"]:
                continue
            if task_is_started and exec_data["constants"][key].get("pre_render_mako", False):
                pre_render_constants.append(key)
            if exec_data["constants"][key].get("show_type", "hide") != "show":
                hide_constants.append(key)
            if exec_data["constants"][key].get("source_type") == "component_outputs":
                component_outputs.append(key)

        if pre_render_constants or hide_constants or component_outputs:
            message = _(
                f"任务参数设置失败: 常量、输出参数 {pre_render_constants}、隐藏变量 {hide_constants}, 不可修改值, "
                f"输出为 {component_outputs}. 请检查变量配置 | set_task_constants"
            )
            logger.error(message)
            return {
                "result": False,
                "message": message,
                "data": None,
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }

        try:
            # set constants
            for key, value in constants.items():
                if key in exec_data["constants"]:
                    exec_data["constants"][key]["value"] = value

            # set meta constants
            for key, value in meta_constants.items():
                if key in exec_data["constants"] and "meta" in exec_data["constants"][key]:
                    exec_data["constants"][key]["meta"]["value"] = value
        except Exception:
            logger.exception(
                "TaskFlow set_task_constants error:id=%s, constants=%s, error=%s"
                % (self.taskflow_id, json.dumps(constants), traceback.format_exc())
            )
            message = _("任务参数设置失败: 非法的任务参数, 请修改后重试 | set_task_constants")
            logger.error(message)
            return {
                "result": False,
                "message": message,
                "data": None,
                "code": err_code.UNKNOWN_ERROR.code,
            }

        context_values = []
        if task_is_started:
            web_constants = {}
            for key in constants:
                if key not in exec_data["constants"]:
                    continue

                web_constants[key] = copy.deepcopy(exec_data["constants"][key])

            # parse web tree constants to bamboo tree data
            data_inputs = classify_constants(constants=web_constants, is_subprocess=False)["data_inputs"]
            for key, data in data_inputs.items():
                context_values.append(
                    ContextValue(
                        key=key,
                        type=CONTEXT_TYPE_MAP[data["type"]],
                        value=data["value"],
                        code=data.get("custom_type", ""),
                    )
                )

        with transaction.atomic():
            if task_is_started:
                # 对修改参数的任务状态进行检查
                status_result = self.get_task_status(subprocess_id=None, with_ex_data=False)
                if status_result is False:
                    logger.error(
                        f"update context values failed: get pipeline states error, "
                        f"error message is {status_result['message']}"
                    )
                    message = _(f"任务参数设置失败: 获取任务状态失败，错误信息为{status_result['message']}。")
                    return {"result": False, "message": message, "data": None, "code": err_code.VALIDATION_ERROR.code}
                if status_result["data"].get("state") not in [
                    bamboo_engine_states.FAILED,
                    bamboo_engine_states.READY,
                    bamboo_engine_states.CREATED,
                    bamboo_engine_states.SUSPENDED,
                    bamboo_engine_states.BLOCKED,
                ]:
                    logger.error(
                        f"update context values failed: pipeline instance state error, "
                        f"tree state is {status_result}"
                    )
                    message = _(f"任务参数设置失败: 任务状态校验失败，" f"任务状态为{status_result['data']['state']}，不支持进行参数修改。")
                    return {"result": False, "data": "", "message": message, "code": err_code.VALIDATION_ERROR.code}

                bamboo_runtime = BambooDjangoRuntime()
                update_res = bamboo_engine_api.update_context_values(
                    runtime=bamboo_runtime,
                    pipeline_id=self.pipeline_instance.instance_id,
                    context_values=context_values,
                )
                if not update_res.result:
                    logger.error("update context values failed: %s" % update_res.exc_trace)
                    message = _(f"任务参数设置失败: 更新引擎上下文发生异常: {update_res.message}. 请重试, 如持续失败可联系管理员处理 | set_task_constants")
                    logger.error(message)
                    return {
                        "result": False,
                        "data": "",
                        "message": message,
                        "code": err_code.UNKNOWN_ERROR.code,
                    }
            self.pipeline_instance.set_execution_data(exec_data)

        return {
            "result": True,
            "data": "success",
            "message": "",
            "code": err_code.SUCCESS.code,
        }

    def get_task_status(self, subprocess_id: Optional[str] = None, with_ex_data: bool = False) -> dict:
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        return getattr(self, "get_task_status_v{}".format(self.engine_ver))(
            subprocess_id=subprocess_id, with_ex_data=with_ex_data
        )

    def _collect_fail_nodes(self, task_status: dict) -> list:
        task_status["ex_data"] = {}
        children_list = [task_status["children"]]
        failed_nodes = []
        while len(children_list) > 0:
            children = children_list.pop(0)
            for node_id, node in children.items():
                if node["state"] == bamboo_engine_states.FAILED:
                    if len(node["children"]) > 0:
                        children_list.append(node["children"])
                        continue
                    failed_nodes.append(node_id)
        return failed_nodes

    def get_task_status_v1(self, subprocess_id: Optional[str], with_ex_data: bool) -> dict:
        if self.pipeline_instance.is_expired:
            return {"result": True, "data": {"state": "EXPIRED"}, "message": "", "code": err_code.SUCCESS.code}
        if not self.pipeline_instance.is_started:
            return {
                "result": True,
                "data": self.CREATED_STATUS,
                "message": "",
                "code": err_code.SUCCESS.code,
            }
        if not subprocess_id:
            try:
                task_status = pipeline_api.get_status_tree(self.pipeline_instance.instance_id, max_depth=99)
                format_pipeline_status(task_status)
                return {
                    "result": True,
                    "data": task_status,
                    "message": "",
                    "code": err_code.SUCCESS.code,
                }
            except pipeline_exceptions.InvalidOperationException as e:
                logger.error(f"node relationship does not exist: {e}")
                task_status = self.CREATED_STATUS
            except Exception:
                message = _("任务数据请求失败: 请重试, 如持续失败可联系管理员处理 | get_task_status_v1")
                logger.exception(message)
                return {
                    "result": False,
                    "message": message,
                    "data": {},
                    "code": err_code.UNKNOWN_ERROR.code,
                }
        else:
            try:
                task_status = pipeline_api.get_status_tree(subprocess_id, max_depth=99)
                format_pipeline_status(task_status)
            except pipeline_exceptions.InvalidOperationException:
                # do not raise error when subprocess not exist or has not been executed
                task_status = self.CREATED_STATUS
            except Exception:
                message = _(f"获取任务状态树数据失败: subprocess[ID: {subprocess_id}]请重试, 如持续失败可联系管理员处理 | get_task_status_v1")
                logger.exception(message)
                return {
                    "result": False,
                    "message": message,
                    "data": {},
                    "code": err_code.UNKNOWN_ERROR.code,
                }

        # 返回失败节点和对应调试信息
        if with_ex_data and task_status["state"] == bamboo_engine_states.FAILED:
            failed_nodes = self._collect_fail_nodes(task_status)
            task_status["ex_data"] = {}
            failed_nodes_outputs = pipeline_api.get_batch_outputs(failed_nodes)
            for node_id in failed_nodes:
                task_status["ex_data"][node_id] = failed_nodes_outputs[node_id]["ex_data"]

        return {"result": True, "data": task_status, "code": err_code.SUCCESS.code, "message": ""}

    def get_task_status_v2(self, subprocess_id: Optional[str], with_ex_data: bool) -> dict:
        if self.pipeline_instance.is_expired:
            return {"result": True, "data": {"state": "EXPIRED"}, "message": "", "code": err_code.SUCCESS.code}
        if not self.pipeline_instance.is_started:
            return {
                "result": True,
                "data": self.CREATED_STATUS,
                "message": "",
                "code": err_code.SUCCESS.code,
            }

        runtime = BambooDjangoRuntime()
        status_result = bamboo_engine_api.get_pipeline_states(
            runtime=runtime, root_id=self.pipeline_instance.instance_id, flat_children=False
        )

        if not status_result:
            logger.exception("bamboo_engine_api.get_pipeline_states fail")
            return {
                "result": False,
                "data": {},
                "message": "{}: {}".format(status_result.message, status_result.exc),
                "code": err_code.UNKNOWN_ERROR.code,
            }
        task_status = status_result.data
        if not task_status:
            return {
                "result": True,
                "data": self.CREATED_STATUS,
                "message": "",
                "code": err_code.SUCCESS.code,
            }
        task_status = task_status[self.pipeline_instance.instance_id]

        def get_subprocess_status(task_status: dict, subprocess_id: str) -> dict:
            for child in task_status["children"].values():
                if child["id"] == subprocess_id:
                    return child
                if child["children"]:
                    status = get_subprocess_status(child, subprocess_id)
                    if status is not None:
                        return status

        if subprocess_id:
            task_status = get_subprocess_status(task_status, subprocess_id)

        # subprocess not been executed
        task_status = task_status or self.CREATED_STATUS

        # 遍历树，获取需要进行状态优化的节点，标记哪些节点具有独立子流程
        # 遍历状态树，hit -> 状态优化，独立子流程 -> 递归
        node_infos_gby_code: typing.Dict[
            str, typing.List[typing.Dict[str, typing.Any]]
        ] = find_nodes_from_pipeline_tree(
            self.pipeline_instance.execution_data, codes=["pause_node", "bk_approve", "subprocess_plugin"]
        )

        node_ids_gby_code: typing.Dict[str, typing.Set[str]] = {}
        for code, node_infos in node_infos_gby_code.items():
            node_ids_gby_code[code] = {node_info["act_id"] for node_info in node_infos}

        code__status_map: typing.Dict[str, str] = {
            "pause_node": TaskExtraStatus.PENDING_CONFIRMATION.value,
            "bk_approve": TaskExtraStatus.PENDING_APPROVAL.value,
        }
        self.format_bamboo_engine_status(task_status, node_ids_gby_code, code__status_map)

        # 返回失败节点和对应调试信息
        if with_ex_data and task_status["state"] == bamboo_engine_states.FAILED:
            failed_nodes = self._collect_fail_nodes(task_status)
            task_status["ex_data"] = {}
            for node_id in failed_nodes:
                data_result = bamboo_engine_api.get_execution_data_outputs(runtime=runtime, node_id=node_id)

                if not data_result:
                    task_status["ex_data"][node_id] = "get ex_data fail: {}".format(data_result.exc)
                else:
                    task_status["ex_data"][node_id] = data_result.data.get("ex_data")

        return {"result": True, "data": task_status, "code": err_code.SUCCESS.code, "message": ""}

    def render_current_constants(self):
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        return getattr(self, "render_current_constants_v{}".format(self.engine_ver))()

    def render_current_constants_v1(self):
        if not (
            self.pipeline_instance.is_started
            and not self.pipeline_instance.is_finished
            and not self.pipeline_instance.is_revoked
        ):
            return {
                "result": False,
                "data": None,
                "code": err_code.INVALID_OPERATION.code,
                "message": "task is not running",
            }

        pipeline_model = PipelineModel.objects.get(id=self.pipeline_instance.instance_id)
        context = pipeline_model.process.root_pipeline.context

        data = []
        for key, var in context.variables.items():
            try:
                if issubclass(var.__class__, Variable):
                    if isinstance(var.value, TaskContext):
                        data.append({"key": key, "value": var.value.__dict__})
                    else:
                        data.append({"key": key, "value": var.get()})
                else:
                    data.append({"key": key, "value": var})
            except Exception:
                logger.exception("[render_current_constants_v1] error occurred at value resolve for %s" % key)
                data.append({"key": key, "value": "[ERROR]value resolve error"})

        return {"result": True, "data": data, "code": err_code.SUCCESS.code, "message": ""}

    def render_current_constants_v2(self):
        runtime = BambooDjangoRuntime()
        context_values = runtime.get_context(self.pipeline_instance.instance_id)
        try:
            root_pipeline_inputs = {
                key: di.value for key, di in runtime.get_data_inputs(self.pipeline_instance.instance_id).items()
            }
        except bamboo_engine_exceptions.NotFoundError:
            return {
                "result": False,
                "data": None,
                "code": err_code.CONTENT_NOT_EXIST.code,
                "message": "data not found, task is not running",
            }
        context = Context(runtime, context_values, root_pipeline_inputs)

        try:
            hydrated_context = context.hydrate()
        except Exception as e:
            logger.exception("[render_current_constants_v2] error occurred at context hydrate")
            return {
                "result": False,
                "data": None,
                "code": err_code.UNKNOWN_ERROR.code,
                "message": "context hydrate error: %s" % str(e),
            }

        data = []
        for key, value in hydrated_context.items():
            if isinstance(value, SystemObject):
                data.append({"key": key, "value": value.__dict__})
            else:
                data.append({"key": key, "value": value})

        return {"result": True, "data": data, "code": err_code.SUCCESS.code, "message": ""}

    def format_bamboo_engine_status(
        self,
        status_tree: typing.Dict[str, typing.Any],
        node_ids_gby_code: typing.Dict[str, typing.Set[str]],
        code__status_map: typing.Dict[str, str],
    ):
        """
        格式化 bamboo 状态树
        :param status_tree: 状态树
        :param node_ids_gby_code: 按组件 Code 聚合节点 ID
        :param code__status_map: 状态映射关系
        :return:
        """

        from gcloud.taskflow3.models import TaskFlowInstance

        _format_status_time(status_tree)

        # 处理状态映射
        if status_tree["state"] in [bamboo_engine_states.SUSPENDED, TaskExtraStatus.NODE_SUSPENDED.value]:
            status_tree["state"] = TaskExtraStatus.PENDING_PROCESSING.value
        elif status_tree["state"] == bamboo_engine_states.RUNNING:
            # 独立子流程下钻
            if status_tree["id"] in node_ids_gby_code.get("subprocess_plugin", set()):
                try:
                    # 尝试从独立子流程组件输出中获取 TaskID
                    task: TaskFlowInstance = TaskFlowInstance.objects.get(
                        pk=self.taskflow_id, project_id=self.project_id
                    )
                    node_outputs: typing.List[typing.Dict[str, typing.Any]] = task.get_node_data(
                        status_tree["id"], "admin", "subprocess_plugin"
                    )["data"]["outputs"]

                    # Raise StopIteration if not found
                    task_id: typing.Optional[int] = next(
                        (node_output["value"] for node_output in node_outputs if node_output["key"] == "task_id")
                    )
                    sub_task: TaskFlowInstance = TaskFlowInstance.objects.get(pk=task_id, project_id=self.project_id)
                except Exception:
                    # 非核心逻辑，记录排查日志并跳过
                    logger.exception(
                        f"[format_bamboo_engine_status] get subprocess_plugin task_id failed, "
                        f"project_id -> {self.project_id}, taskflow_id -> {self.taskflow_id}, "
                        f"node -> {status_tree['id']}"
                    )
                    pass
                else:
                    dispatcher = TaskCommandDispatcher(
                        engine_ver=sub_task.engine_ver,
                        taskflow_id=sub_task.id,
                        pipeline_instance=sub_task.pipeline_instance,
                        project_id=self.project_id,
                    )
                    get_task_status_result: typing.Dict[str, typing.Any] = dispatcher.get_task_status(
                        with_ex_data=False
                    )
                    if get_task_status_result.get("result"):
                        status_tree["state"] = get_task_status_result["data"]["state"]

            else:
                # 状态转换
                for code, node_ids in node_ids_gby_code.items():
                    # 短路原则：code in code__status_map 处理效率高于后者，先行过滤不需要转换的 code
                    if code in code__status_map and status_tree["id"] in node_ids:
                        status_tree["state"] = code__status_map[code]

        child_status: typing.Set[str] = set()
        for identifier_code, child_tree in list(status_tree["children"].items()):
            self.format_bamboo_engine_status(child_tree, node_ids_gby_code, code__status_map)
            child_status.add(child_tree["state"])

        if status_tree["state"] == bamboo_engine_states.RUNNING:
            if bamboo_engine_states.FAILED in child_status:
                # 失败优先级最高
                status_tree["state"] = bamboo_engine_states.FAILED
            elif {
                TaskExtraStatus.PENDING_APPROVAL.value,
                TaskExtraStatus.PENDING_CONFIRMATION.value,
                TaskExtraStatus.PENDING_PROCESSING.value,
            } & child_status:
                # 存在其中一个状态，父级状态扭转为等待处理（PENDING_PROCESSING）
                status_tree["state"] = TaskExtraStatus.PENDING_PROCESSING.value
