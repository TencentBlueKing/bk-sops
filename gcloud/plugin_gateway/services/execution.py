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

from django.db import IntegrityError, transaction

from gcloud.plugin_gateway.exceptions import (
    PluginGatewayConflictError,
    PluginGatewayPluginNotFoundError,
    PluginGatewayVersionNotFoundError,
)
from gcloud.plugin_gateway.models import PluginGatewayRun, PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService
from gcloud.plugin_gateway.services.catalog import PluginGatewayCatalogService
from gcloud.plugin_gateway.services.context import PluginGatewayContextService
from gcloud.plugin_gateway.tasks import dispatch_plugin_gateway_run
from gcloud.utils import crypto

logger = logging.getLogger("root")


class PluginGatewayExecutionService:
    # 幂等冲突检测按字段优先级排序：前两个字段不涉及解密，可作为快速比对通道；
    # 只有当其它字段都一致时才解密 callback_token 做最终比对。
    _IDEMPOTENT_PLAIN_FIELDS = ("source_key", "plugin_id", "plugin_version", "callback_url", "trigger_payload")

    @classmethod
    def create_run(cls, caller_app_code, payload):
        source_config = cls._get_source_config(payload["source_key"])
        plugin_reference = cls._get_plugin_reference(payload["plugin_id"], payload["plugin_version"])
        PluginGatewayContextService.validate_callback_domain(source_config, payload["callback_url"])
        trigger_payload = PluginGatewayContextService.build_trigger_payload(
            source_config=source_config,
            plugin_id=payload["plugin_id"],
            payload={
                "inputs": payload.get("inputs", {}),
                "project_id": payload.get("project_id"),
                "operator": payload.get("operator"),
                "plugin_source": plugin_reference["plugin_source"],
                "plugin_code": plugin_reference["plugin_code"],
            },
        )

        defaults = {
            "source_key": payload["source_key"],
            "plugin_id": payload["plugin_id"],
            "plugin_version": payload["plugin_version"],
            "open_plugin_run_id": cls._generate_run_id(),
            "callback_url": payload["callback_url"],
            "callback_token": crypto.encrypt(payload["callback_token"]),
            "run_status": PluginGatewayRun.Status.WAITING_CALLBACK,
            "trigger_payload": trigger_payload,
        }

        try:
            with transaction.atomic():
                run, created = PluginGatewayRun.objects.get_or_create(
                    caller_app_code=caller_app_code,
                    client_request_id=payload["client_request_id"],
                    defaults=defaults,
                )
        except IntegrityError:
            # 并发场景下两条请求同时进入 created=True 分支，其中一条会因唯一约束落空。
            # 此时记录一定已经存在，直接读取后走幂等冲突检测。
            run = PluginGatewayRun.objects.get(
                caller_app_code=caller_app_code,
                client_request_id=payload["client_request_id"],
            )
            created = False

        if not created:
            cls._validate_idempotent_conflict(run=run, payload=payload, trigger_payload=trigger_payload)
        else:
            dispatch_plugin_gateway_run.apply_async(kwargs={"open_plugin_run_id": run.open_plugin_run_id})

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
        return cls.get_run_detail(task_tag, caller_app_code)

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
        run.error_message = run.error_message or "run cancelled by caller"
        run.save(update_fields=["run_status", "error_message", "update_time"])
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id=open_plugin_run_id,
            run_status=PluginGatewayRun.Status.CANCELLED,
            outputs=run.outputs or {},
            error_message=run.error_message,
        )
        logger.info("[plugin_gateway] cancel run run_id=%s caller_app_code=%s", open_plugin_run_id, caller_app_code)
        return run

    @staticmethod
    def _generate_run_id():
        return uuid4().hex

    @staticmethod
    def _get_source_config(source_key):
        return PluginGatewaySourceConfig.objects.get(source_key=source_key, is_enabled=True)

    @staticmethod
    def _get_plugin_reference(plugin_id, plugin_version):
        plugin_reference = PluginGatewayCatalogService.get_plugin_reference(plugin_id)
        if plugin_reference is None:
            raise PluginGatewayPluginNotFoundError("plugin gateway plugin({}) does not exist".format(plugin_id))
        if plugin_version not in plugin_reference.get("versions", []):
            raise PluginGatewayVersionNotFoundError(
                "plugin({}) version({}) is not available".format(plugin_id, plugin_version)
            )
        return plugin_reference

    @classmethod
    def _validate_idempotent_conflict(cls, run, payload, trigger_payload):
        existing_plain = {
            "source_key": run.source_key,
            "plugin_id": run.plugin_id,
            "plugin_version": run.plugin_version,
            "callback_url": run.callback_url,
            "trigger_payload": run.trigger_payload,
        }
        current_plain = {
            "source_key": payload["source_key"],
            "plugin_id": payload["plugin_id"],
            "plugin_version": payload["plugin_version"],
            "callback_url": payload["callback_url"],
            "trigger_payload": trigger_payload,
        }
        conflicts = [field for field in cls._IDEMPOTENT_PLAIN_FIELDS if existing_plain[field] != current_plain[field]]

        # 非敏感字段一致时再解密 token 做最终比对，避免每次幂等重放都付出解密成本
        if not conflicts and crypto.decrypt(run.callback_token) != payload["callback_token"]:
            conflicts.append("callback_token")

        if conflicts:
            raise PluginGatewayConflictError(
                "client_request_id({}) conflicts on fields: {}".format(
                    run.client_request_id, ",".join(sorted(conflicts))
                )
            )
