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
from django.utils import timezone

from gcloud.plugin_gateway.constants import MAX_SCHEDULE_TIMES, poll_countdown
from gcloud.plugin_gateway.exceptions import PluginGatewayContextResolveError
from gcloud.plugin_gateway.models import PluginGatewayRun, PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService
from gcloud.plugin_gateway.services.context import PluginGatewayContextService
from gcloud.plugin_gateway.services.runner import PluginGatewayRunner

logger = logging.getLogger("celery")


@task(queue="open_plugin_polling")
def sweep_expired_plugin_gateway_runs():
    expired_runs = PluginGatewayRun.objects.filter(execution_expire_at__lt=timezone.now()).exclude(
        run_status__in=list(PluginGatewayRun.Status.TERMINAL)
    )
    for run in expired_runs.iterator():
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=run.open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="execution timeout",
        )


@task(queue="open_plugin_dispatch")
def dispatch_plugin_gateway_run(open_plugin_run_id):
    try:
        run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id)
    except PluginGatewayRun.DoesNotExist:
        logger.warning("[plugin_gateway] dispatch task skipped because run(%s) does not exist", open_plugin_run_id)
        return

    if run.run_status in PluginGatewayRun.Status.TERMINAL:
        logger.info("[plugin_gateway] dispatch task skipped for terminal run(%s)", open_plugin_run_id)
        return

    try:
        source_config = PluginGatewaySourceConfig.objects.get(source_key=run.source_key, is_enabled=True)
    except PluginGatewaySourceConfig.DoesNotExist:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="plugin gateway source({}) is not available".format(run.source_key),
        )
        return

    try:
        run_context = PluginGatewayContextService.resolve_run_context(
            source_config=source_config,
            context=(run.trigger_payload or {}).get("context"),
        )
    except PluginGatewayContextResolveError as e:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=str(e),
        )
        return

    run.run_status = PluginGatewayRun.Status.RUNNING
    run.save(update_fields=["run_status", "update_time"])

    try:
        result = PluginGatewayRunner.run_execute(run, run_context)
    except Exception as e:
        logger.exception("[plugin_gateway] dispatch runner error run=%s", open_plugin_run_id)
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=str(e),
        )
        return

    if not result["ok"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=result["error_message"] or "plugin execute failed",
        )
        return

    if not result["need_schedule"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs=result["outputs"],
        )
        return

    run.runtime_outputs = result["outputs"]
    run.schedule_times = 0

    if result["mode"] == "callback":
        run.run_status = PluginGatewayRun.Status.WAITING_CALLBACK
        run.save(update_fields=["run_status", "runtime_outputs", "schedule_times", "update_time"])
        return

    run.save(update_fields=["runtime_outputs", "schedule_times", "update_time"])
    poll_plugin_gateway_run.apply_async(
        kwargs={"open_plugin_run_id": open_plugin_run_id},
        countdown=poll_countdown(run.schedule_times),
        queue="open_plugin_polling",
    )


@task(queue="open_plugin_polling")
def poll_plugin_gateway_run(open_plugin_run_id):
    try:
        run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id)
    except PluginGatewayRun.DoesNotExist:
        logger.warning("[plugin_gateway] polling task skipped because run(%s) does not exist", open_plugin_run_id)
        return

    if run.run_status in PluginGatewayRun.Status.TERMINAL:
        logger.info("[plugin_gateway] polling task skipped for terminal run(%s)", open_plugin_run_id)
        return

    if run.execution_expire_at and timezone.now() >= run.execution_expire_at:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="execution timeout",
        )
        return

    if run.schedule_times >= MAX_SCHEDULE_TIMES:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="exceed max schedule times",
        )
        return

    try:
        source_config = PluginGatewaySourceConfig.objects.get(source_key=run.source_key, is_enabled=True)
    except PluginGatewaySourceConfig.DoesNotExist:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="plugin gateway source({}) is not available".format(run.source_key),
        )
        return

    try:
        run_context = PluginGatewayContextService.resolve_run_context(
            source_config=source_config,
            context=(run.trigger_payload or {}).get("context"),
        )
    except PluginGatewayContextResolveError as e:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=str(e),
        )
        return

    try:
        result = PluginGatewayRunner.run_schedule(run, run_context)
    except Exception as e:
        logger.exception("[plugin_gateway] polling runner error run=%s", open_plugin_run_id)
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=str(e),
        )
        return

    run.schedule_times += 1
    run.runtime_outputs = result["outputs"]
    run.save(update_fields=["schedule_times", "runtime_outputs", "update_time"])

    if not result["ok"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=result["error_message"] or "plugin schedule failed",
        )
        return

    if result["finished"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs=result["outputs"],
        )
        return

    poll_plugin_gateway_run.apply_async(
        kwargs={"open_plugin_run_id": open_plugin_run_id},
        countdown=poll_countdown(run.schedule_times),
        queue="open_plugin_polling",
    )


@task(queue="open_plugin_callback")
def callback_plugin_gateway_run(open_plugin_run_id, callback_data=None):
    try:
        run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id)
    except PluginGatewayRun.DoesNotExist:
        logger.warning("[plugin_gateway] callback task skipped because run(%s) does not exist", open_plugin_run_id)
        return

    if run.run_status in PluginGatewayRun.Status.TERMINAL:
        logger.info("[plugin_gateway] callback task skipped for terminal run(%s)", open_plugin_run_id)
        return

    try:
        source_config = PluginGatewaySourceConfig.objects.get(source_key=run.source_key, is_enabled=True)
    except PluginGatewaySourceConfig.DoesNotExist:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message="plugin gateway source({}) is not available".format(run.source_key),
        )
        return

    try:
        run_context = PluginGatewayContextService.resolve_run_context(
            source_config=source_config,
            context=(run.trigger_payload or {}).get("context"),
        )
    except PluginGatewayContextResolveError as e:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=str(e),
        )
        return

    try:
        result = PluginGatewayRunner.run_schedule(run, run_context, callback_data=callback_data)
    except Exception as e:
        logger.exception("[plugin_gateway] callback runner error run=%s", open_plugin_run_id)
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=str(e),
        )
        return

    run.runtime_outputs = result["outputs"]
    run.save(update_fields=["runtime_outputs", "update_time"])

    if not result["ok"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.FAILED,
            error_message=result["error_message"] or "plugin callback schedule failed",
        )
        return

    if result["finished"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.SUCCEEDED,
            outputs=result["outputs"],
        )
