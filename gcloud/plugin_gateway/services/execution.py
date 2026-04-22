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
from uuid import uuid4

from gcloud.plugin_gateway.exceptions import PluginGatewayConflictError
from gcloud.plugin_gateway.models import PluginGatewayRun, PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.context import PluginGatewayContextService
from gcloud.utils import crypto

logger = logging.getLogger("root")


class PluginGatewayExecutionService:
    @classmethod
    def create_run(cls, caller_app_code, payload):
        source_config = cls._get_source_config(payload["source_key"])
        PluginGatewayContextService.validate_callback_domain(source_config, payload["callback_url"])
        trigger_payload = PluginGatewayContextService.build_trigger_payload(
            source_config=source_config,
            plugin_id=payload["plugin_id"],
            payload={"inputs": payload.get("inputs", {}), "project_id": payload.get("project_id")},
        )

        run, created = PluginGatewayRun.objects.get_or_create(
            caller_app_code=caller_app_code,
            client_request_id=payload["client_request_id"],
            defaults={
                "source_key": payload["source_key"],
                "plugin_id": payload["plugin_id"],
                "plugin_version": payload["plugin_version"],
                "open_plugin_run_id": cls._generate_run_id(),
                "callback_url": payload["callback_url"],
                "callback_token": crypto.encrypt(payload["callback_token"]),
                "run_status": PluginGatewayRun.Status.WAITING_CALLBACK,
                "trigger_payload": trigger_payload,
            },
        )
        if not created:
            cls._validate_idempotent_conflict(run=run, payload=payload, trigger_payload=trigger_payload)

        logger.info(
            "[plugin_gateway] create run caller_app_code=%s source_key=%s plugin_id=%s run_id=%s created=%s",
            caller_app_code,
            payload["source_key"],
            payload["plugin_id"],
            run.open_plugin_run_id,
            created,
        )
        return run, created

    @classmethod
    def get_run_status(cls, task_tag, caller_app_code):
        run = cls.get_run_detail(task_tag, caller_app_code)
        return PluginGatewayRun.objects.only(
            "open_plugin_run_id",
            "run_status",
            "outputs",
            "error_message",
            "caller_app_code",
        ).get(pk=run.pk)

    @classmethod
    def get_run_detail(cls, open_plugin_run_id, caller_app_code):
        run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id)
        if run.caller_app_code != caller_app_code:
            raise PermissionError("plugin gateway run does not belong to app({})".format(caller_app_code))
        return run

    @classmethod
    def cancel_run(cls, open_plugin_run_id, caller_app_code):
        run = cls.get_run_detail(open_plugin_run_id, caller_app_code)
        if run.run_status in PluginGatewayRun.Status.TERMINAL:
            return run

        run.run_status = PluginGatewayRun.Status.CANCELLED
        run.save(update_fields=["run_status", "update_time"])
        logger.info("[plugin_gateway] cancel run run_id=%s caller_app_code=%s", open_plugin_run_id, caller_app_code)
        return run

    @staticmethod
    def _generate_run_id():
        return uuid4().hex

    @staticmethod
    def _get_source_config(source_key):
        return PluginGatewaySourceConfig.objects.get(source_key=source_key, is_enabled=True)

    @staticmethod
    def _validate_idempotent_conflict(run, payload, trigger_payload):
        existing = {
            "source_key": run.source_key,
            "plugin_id": run.plugin_id,
            "plugin_version": run.plugin_version,
            "callback_url": run.callback_url,
            "callback_token": crypto.decrypt(run.callback_token),
            "trigger_payload": run.trigger_payload,
        }
        current = {
            "source_key": payload["source_key"],
            "plugin_id": payload["plugin_id"],
            "plugin_version": payload["plugin_version"],
            "callback_url": payload["callback_url"],
            "callback_token": payload["callback_token"],
            "trigger_payload": trigger_payload,
        }
        conflicts = sorted([field for field, value in current.items() if existing[field] != value])
        if conflicts:
            raise PluginGatewayConflictError(
                "client_request_id({}) conflicts on fields: {}".format(run.client_request_id, ",".join(conflicts))
            )
