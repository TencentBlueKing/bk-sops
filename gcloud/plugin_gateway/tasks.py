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

from celery import task
from django.conf import settings

from gcloud.plugin_gateway.constants import PLUGIN_SOURCE_THIRD_PARTY
from gcloud.plugin_gateway.models import PluginGatewayRun
from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService
from plugin_service.exceptions import PluginServiceException
from plugin_service.plugin_client import PluginServiceApiClient

logger = logging.getLogger("celery")

PLUGIN_STATE_POLL = 2
PLUGIN_STATE_CALLBACK = 3
PLUGIN_STATE_SUCCESS = 4
PLUGIN_STATE_FAIL = 5


@task
def dispatch_plugin_gateway_run(open_plugin_run_id):
    try:
        run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id)
    except PluginGatewayRun.DoesNotExist:
        logger.warning("[plugin_gateway] dispatch task skipped because run(%s) does not exist", open_plugin_run_id)
        return

    if run.run_status in PluginGatewayRun.Status.TERMINAL:
        logger.info("[plugin_gateway] dispatch task skipped for terminal run(%s)", open_plugin_run_id)
        return

    plugin_source = run.trigger_payload.get("plugin_source")
    if plugin_source != PLUGIN_SOURCE_THIRD_PARTY:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="plugin_source({}) is not supported by plugin gateway runtime".format(plugin_source or ""),
        )
        return

    plugin_code = run.trigger_payload.get("plugin_code") or run.plugin_id
    try:
        plugin_client = PluginServiceApiClient(plugin_code)
    except PluginServiceException as e:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="plugin client init failed: {}".format(e),
        )
        return

    detail_result = plugin_client.get_detail(run.plugin_version)
    if not detail_result.get("result"):
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=detail_result.get("message", "query plugin detail failed"),
        )
        return

    ok, result_data = plugin_client.invoke(
        run.plugin_version,
        {
            "inputs": run.trigger_payload.get("inputs", {}),
            "context": _build_context(run, detail_result.get("data", {})),
        },
    )
    if not ok:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=result_data.get("message", "invoke plugin failed"),
        )
        return

    state = result_data.get("state")
    if state == PLUGIN_STATE_SUCCESS:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs=result_data.get("outputs") or {},
        )
        return

    if state == PLUGIN_STATE_FAIL:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=result_data.get("err") or "plugin runtime returned failed state",
        )
        return

    if state in {PLUGIN_STATE_POLL, PLUGIN_STATE_CALLBACK}:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=(
                "plugin gateway runtime does not support asynchronous state({}); "
                "please use a synchronous-completion plugin"
            ).format(state),
        )
        return

    PluginGatewayCallbackService.callback_run(
        open_plugin_run_id=open_plugin_run_id,
        run_status=PluginGatewayRun.Status.FAILED,
        error_message="plugin runtime returned unknown state({})".format(state),
    )


def _build_context(run, detail_data):
    available_context = {
        key: value
        for key, value in run.trigger_payload.items()
        if key not in {"inputs", "plugin_source", "plugin_code"}
    }
    operator = run.trigger_payload.get("operator") or getattr(settings, "SYSTEM_USE_API_ACCOUNT", "admin")
    available_context.update(
        {
            "source_key": run.source_key,
            "caller_app_code": run.caller_app_code,
            "open_plugin_run_id": run.open_plugin_run_id,
            "operator": operator,
            "executor": operator,
        }
    )
    context_keys = (detail_data.get("context_inputs", {}) or {}).get("properties", {}).keys()
    return {key: available_context[key] for key in context_keys if key in available_context}
