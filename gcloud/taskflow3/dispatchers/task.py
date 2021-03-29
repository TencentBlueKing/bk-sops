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
import traceback

from django.utils import timezone
from bamboo_engine import api as bamboo_engine_api

from gcloud import err_code
from gcloud.taskflow3.signals import taskflow_started
from pipeline.eri.runtime import BambooDjangoRuntime
from pipeline.service import task_service
from pipeline.models import PipelineInstance
from pipeline.parser.context import get_pipeline_context
from pipeline_web.parser.format import format_web_data_to_pipeline
from pipeline.exceptions import ConvergeMatchError, ConnectionValidateError, IsolateNodeError, StreamValidateError
from .base import EngineCommandDispatcher, ensure_return_is_dict, ensure_return_has_code

logger = logging.getLogger("root")


class TaskCommandDispatcher(EngineCommandDispatcher):
    TASK_COMMANDS = {
        "start",
        "pause",
        "resume",
        "revoke",
    }

    def __init__(self, engine_ver, taskflow, pipeline_instance, queue):
        self.engine_ver = engine_ver
        self.taskflow = taskflow
        self.pipeline_instance = pipeline_instance
        self.queue = queue

    def dispatch(self, command, operator):
        if self.engine_ver not in self.VALID_ENGINE_VER:
            return self._unsupported_engine_ver_result()

        if command not in self.TASK_COMMANDS:
            return {"result": False, "message": "task command is invalid", "code": err_code.INVALID_OPERATION.code}

        return getattr(self, "{}_v{}".format(command, self.engine_ver))(operator)

    def start_v1(self, executor):
        try:
            result = self.pipeline_instance.start(executor=executor, queue=self.queue)
            if result.result:
                taskflow_started.send(sender=self.__class__, task_id=self.taskflow.id)

            result["code"] = err_code.SUCCESS.code if result.result else err_code.UNKNOWN_ERROR
            return result
        except ConvergeMatchError as e:
            message = "task[id=%s] has invalid converge, message: %s, node_id: %s" % (self.id, str(e), e.gateway_id)
            logger.exception(message)
            code = err_code.VALIDATION_ERROR.code

        except StreamValidateError as e:
            message = "task[id=%s] stream is invalid, message: %s, node_id: %s" % (self.id, str(e), e.node_id)
            logger.exception(message)
            code = err_code.VALIDATION_ERROR.code

        except IsolateNodeError as e:
            message = "task[id=%s] has isolate structure, message: %s" % (self.id, str(e))
            logger.exception(message)
            code = err_code.VALIDATION_ERROR.code

        except ConnectionValidateError as e:
            message = "task[id=%s] connection check failed, message: %s, nodes: %s" % (
                self.id,
                e.detail,
                e.failed_nodes,
            )
            logger.exception(message)
            code = err_code.VALIDATION_ERROR.code

        except TypeError:
            message = "redis connection error, please check redis configuration"
            logger.exception(traceback.format_exc())
            code = err_code.ENV_ERROR.code

        except Exception as e:
            message = "task[id=%s] command failed:%s" % (self.id, e)
            logger.exception(traceback.format_exc())
            code = err_code.UNKNOWN_ERROR.code

        return {"result": False, "message": message, "code": code}

    def start_v2(self, executor):
        # CAS
        update_success = PipelineInstance.objects.filter(id=self.pipeline_instance.id, is_started=False).update(
            start_time=timezone.now(), is_started=True, executor=executor,
        )
        self.pipeline_instance.calculate_tree_info()
        PipelineInstance.objects.filter(id=self.pipeline_instance.id).update(
            tree_info__id=self.pipeline_instance.tree_info.id
        )

        if not update_success:
            return {"result": False, "message": "task already started", "code": err_code.INVALID_OPERATION.code}

        # convert web pipeline to pipeline
        pipeline = format_web_data_to_pipeline(self.pipeline_instance.execution_data)

        # run pipeline
        result = bamboo_engine_api.run_pipeline(
            runtime=BambooDjangoRuntime(),
            pipeline=pipeline,
            root_pipeline_data=get_pipeline_context(
                self.pipeline_instance, obj_type="instance", data_type="data", username=executor
            ),
            queue=self.queue,
        )

        if not result.result:
            PipelineInstance.objects.filter(id=self.pipeline_instance.id, is_started=True).update(
                start_time=None, is_started=False, executor="",
            )
            logger.error(
                "run_pipeline fail: {}, exception: {}".format(
                    result.message, traceback.TracebackException.from_exception(result.exc).format()
                )
            )
        else:
            taskflow_started.send(sender=self.__class__, task_id=self.taskflow.id)

        dict_result = {
            "result": result.result,
            "message": result.message,
            "code": err_code.SUCCESS.code if result.result else err_code.UNKNOWN_ERROR,
        }

        return dict_result

    @ensure_return_has_code
    def pause_v1(self, operator):
        return task_service.pause_pipeline(pipeline_id=self.pipeline_instance.id)

    @ensure_return_is_dict
    def pause_v2(self, operator):
        return bamboo_engine_api.pause_pipeline(runtime=BambooDjangoRuntime(), pipeline_id=self.pipeline_instance.id)

    @ensure_return_has_code
    def resume_v1(self, operator):
        return task_service.resume_pipeline(pipeline_id=self.pipeline_instance.id)

    @ensure_return_is_dict
    def resume_v2(self, operator):
        return bamboo_engine_api.resume_pipeline(runtime=BambooDjangoRuntime(), pipeline_id=self.pipeline_instance.id)

    @ensure_return_has_code
    def revoke_v1(self, operator):
        return task_service.revoke_pipeline(pipeline_id=self.pipeline_instance.id)

    @ensure_return_is_dict
    def revoke_v2(self, operator):
        return bamboo_engine_api.revoke_pipeline(runtime=BambooDjangoRuntime(), pipeline_id=self.pipeline_instance.id)
