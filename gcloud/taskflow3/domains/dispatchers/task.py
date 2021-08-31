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

import json
import logging
import traceback
from typing import Optional

from django.utils import timezone
from bamboo_engine import api as bamboo_engine_api
from bamboo_engine import states as bamboo_engine_states
from bamboo_engine.context import Context
from pipeline.eri.runtime import BambooDjangoRuntime
from pipeline import exceptions as pipeline_exceptions
from pipeline.service import task_service
from pipeline.models import PipelineInstance
from pipeline.parser.context import get_pipeline_context
from pipeline.engine import api as pipeline_api
from pipeline.engine.models import PipelineModel
from pipeline_web.parser.format import format_web_data_to_pipeline
from pipeline.exceptions import (
    ConvergeMatchError,
    ConnectionValidateError,
    IsolateNodeError,
    StreamValidateError,
)

from gcloud import err_code
from gcloud.taskflow3.signals import taskflow_started
from gcloud.taskflow3.domains.context import TaskContext
from gcloud.taskflow3.utils import format_pipeline_status, format_bamboo_engine_status
from gcloud.project_constants.domains.context import get_project_constants_context
from engine_pickle_obj.context import SystemObject
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

        return getattr(self, "{}_v{}".format(command, self.engine_ver))(operator)

    def start_v1(self, executor: str) -> dict:
        try:
            result = self.pipeline_instance.start(executor=executor, queue=self.queue)
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
        update_success = PipelineInstance.objects.filter(
            instance_id=self.pipeline_instance.instance_id, is_started=False
        ).update(start_time=timezone.now(), is_started=True, executor=executor)
        self.pipeline_instance.calculate_tree_info()
        PipelineInstance.objects.filter(instance_id=self.pipeline_instance.instance_id).update(
            tree_info_id=self.pipeline_instance.tree_info.id
        )

        if not update_success:
            return {"result": False, "message": "task already started", "code": err_code.INVALID_OPERATION.code}

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
                start_time=None, is_started=False, executor="",
            )
            return {
                "result": False,
                "message": "run pipeline failed: {}".format(e),
                "code": err_code.UNKNOWN_ERROR.code,
            }

        if not result.result:
            PipelineInstance.objects.filter(instance_id=self.pipeline_instance.instance_id, is_started=True).update(
                start_time=None, is_started=False, executor="",
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

    def set_task_context(self, task_is_started: bool, task_is_finished: bool, context: dict) -> dict:
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        if task_is_started:
            return {
                "result": False,
                "message": "task is started",
                "data": None,
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }

        elif task_is_finished:
            return {
                "result": False,
                "message": "task is finished",
                "data": None,
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }

        exec_data = self.pipeline_instance.execution_data
        try:
            for key, value in list(context.items()):
                if key in exec_data["constants"]:
                    exec_data["constants"][key]["value"] = value
            self.pipeline_instance.set_execution_data(exec_data)
        except Exception:
            logger.exception(
                "TaskFlow set_task_context error:id=%s, constants=%s, error=%s"
                % (self.taskflow_id, json.dumps(context), traceback.format_exc())
            )
            return {
                "result": False,
                "message": "constants is not valid",
                "data": None,
                "code": err_code.UNKNOWN_ERROR.code,
            }

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
            except Exception:
                logger.exception("task.get_status fail")
                return {
                    "result": False,
                    "message": "task.get_status fail",
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
                logger.exception("pipeline_api.get_status_tree(subprocess_id:{}) fail".format(subprocess_id))
                return {
                    "result": False,
                    "message": "pipeline_api.get_status_tree(subprocess_id:{}) fail",
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

        format_bamboo_engine_status(task_status)

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
                if isinstance(var.value, TaskContext):
                    data.append({"key": key, "value": var.value.__dict__})
                elif hasattr(var, "get"):
                    data.append({"key": key, "value": var.get()})
                else:
                    data.append({"key": key, "value": var.value})
            except Exception:
                logger.exception("[render_current_constants_v1] error occurred at value resolve for %s" % key)
                data.append({"key": key, "value": "[ERROR]value resolve error"})

        return {"result": True, "data": data, "code": err_code.SUCCESS.code, "message": ""}

    def render_current_constants_v2(self):
        runtime = BambooDjangoRuntime()
        context_values = runtime.get_context(self.pipeline_instance.instance_id)
        root_pipeline_inputs = {
            key: di.value for key, di in runtime.get_data_inputs(self.pipeline_instance.instance_id).items()
        }
        context = Context(runtime, context_values, root_pipeline_inputs)
        hydrated_context = context.hydrate()

        data = []
        for key, value in hydrated_context.items():
            if isinstance(value, SystemObject):
                data.append({"key": key, "value": value.__dict__})
            else:
                data.append({"key": key, "value": value})

        return {"result": True, "data": data, "code": err_code.SUCCESS.code, "message": ""}
