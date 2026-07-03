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

from pipeline.component_framework.library import ComponentLibrary
from pipeline.core.data.base import DataObject
from pipeline.utils.collections import FancyDict

from gcloud.plugin_gateway.constants import PLUGIN_SOURCE_BUILTIN, decode_plugin_id

logger = logging.getLogger("root")

THIRD_PARTY_COMPONENT_CODE = "remote_plugin"
THIRD_PARTY_COMPONENT_VERSION = "1.0.0"


class PluginGatewayRunner:
    """组件运行壳：直接驱动组件 Service，不创建引擎实例。"""

    @classmethod
    def build_service(cls, run):
        source, code = decode_plugin_id(run.plugin_id)
        if source == PLUGIN_SOURCE_BUILTIN:
            version = None if run.plugin_version in ("", "legacy") else run.plugin_version
            component_cls = ComponentLibrary.get_component_class(code, version)
        else:
            component_cls = ComponentLibrary.get_component_class(
                THIRD_PARTY_COMPONENT_CODE, THIRD_PARTY_COMPONENT_VERSION
            )

        service = component_cls.bound_service()
        service.id = run.open_plugin_run_id
        service.root_pipeline_id = run.open_plugin_run_id
        setattr(service, "version", run.plugin_version)
        return source, code, service

    @classmethod
    def build_data(cls, run, run_context, source, code):
        trigger_payload = run.trigger_payload or {}
        inputs = dict(trigger_payload.get("inputs", {}))
        if source != PLUGIN_SOURCE_BUILTIN:
            inputs.setdefault("plugin_code", code)
            inputs.setdefault("plugin_version", run.plugin_version)

        data = DataObject(inputs=FancyDict(inputs), outputs=FancyDict(dict(run.runtime_outputs or {})))
        parent_data = DataObject(inputs=FancyDict(cls._parent_inputs(run, run_context)))
        return data, parent_data

    @classmethod
    def run_execute(cls, run, run_context):
        source, code, service = cls.build_service(run)
        data, parent_data = cls.build_data(run, run_context, source, code)
        try:
            ok = bool(service.execute(data, parent_data))
        except Exception as e:
            logger.exception("[plugin_gateway] runner execute error run=%s", run.open_plugin_run_id)
            return cls._result(False, cls._outputs(data), str(e), False)

        try:
            need_schedule = bool(service.need_schedule())
        except Exception:
            need_schedule = False

        if not ok:
            mode = "sync"
        elif not need_schedule:
            mode = "sync"
        elif getattr(service, "interval", None) is None:
            mode = "callback"
        else:
            mode = "poll"
        return cls._result(ok, cls._outputs(data), cls._ex_data(data), need_schedule, mode)

    @classmethod
    def run_schedule(cls, run, run_context, callback_data=None):
        source, code, service = cls.build_service(run)
        data, parent_data = cls.build_data(run, run_context, source, code)
        setattr(service, "__need_schedule__", True)
        try:
            ok = bool(service.schedule(data, parent_data, callback_data=callback_data))
        except Exception as e:
            logger.exception("[plugin_gateway] runner schedule error run=%s", run.open_plugin_run_id)
            return cls._result(False, cls._outputs(data), str(e), False, "poll", finished=False)

        try:
            finished = bool(service.is_schedule_finished())
        except Exception:
            finished = False

        return cls._result(ok, cls._outputs(data), cls._ex_data(data), not finished, "poll", finished=finished)

    @staticmethod
    def _parent_inputs(run, run_context):
        run_context = run_context or {}
        operator = run_context.get("operator") or ""
        return {
            "operator": operator,
            "executor": operator,
            "project_id": run_context.get("project_id"),
            "bk_biz_id": run_context.get("bk_biz_id"),
            "task_id": run_context.get("task_id"),
            "task_name": run_context.get("task_name"),
            "task_start_time": None,
            "source_key": run.source_key,
            "caller_app_code": run.caller_app_code,
            "open_plugin_run_id": run.open_plugin_run_id,
        }

    @staticmethod
    def _outputs(data):
        try:
            return dict(data.get_outputs())
        except Exception:
            return {}

    @staticmethod
    def _ex_data(data):
        try:
            return str(data.get_one_of_outputs("ex_data") or "")
        except Exception:
            return ""

    @staticmethod
    def _result(ok, outputs, error_message, need_schedule, mode="sync", finished=False):
        return {
            "ok": ok,
            "outputs": outputs,
            "error_message": error_message,
            "need_schedule": need_schedule,
            "mode": mode,
            "finished": finished,
        }
