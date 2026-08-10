# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
import logging
import re
from functools import partial

import six
from bk_audit.contrib.bk_audit.client import bk_audit_client
from bk_audit.log.models import AuditContext
from django.conf import settings
from django.db import transaction
from iam import Action
from iam.auth.models import BaseObject

from gcloud.contrib.audit.instances import AuditSnapshot, build_instance, build_instance_data

logger = logging.getLogger("root")

REMOVED_AUDIT_FIELDS = {
    "constants",
    "extra_info",
    "form",
    "headers",
    "inputs",
    "outputs",
    "pipeline_tree",
    "task_parameters",
    "task_params",
}
SENSITIVE_AUDIT_KEYWORDS = ("authorization", "credential", "password", "secret", "token")
DELEGATED_AUDIT_OPERATOR_META_KEY = "HTTP_X_BKSOPS_AUDIT_OPERATOR"
DELEGATED_AUDIT_OPERATOR_PATTERN = re.compile(r"^[A-Za-z0-9_.@-]{1,64}$")


class ResourceType(BaseObject):
    __slots__ = ("id",)

    def __init__(self, id):
        self.id = id

    def validate(self):
        # Type Check
        if not isinstance(self.id, six.string_types):
            raise TypeError("ResourceType.id should be a string")

        # Value Check
        if not self.id:
            raise ValueError("ResourceType.id should not be empty")

    def to_dict(self):
        return {"id": self.id}


def get_audit_username(request):
    proxy_username = getattr(getattr(request, "user", None), "username", "")
    operator = getattr(request, "META", {}).get(DELEGATED_AUDIT_OPERATOR_META_KEY)
    if not operator:
        return proxy_username

    app = getattr(request, "app", None)
    app_code = getattr(app, settings.APIGW_MANAGER_APP_CODE_KEY, "")
    trusted_apps = getattr(settings, "BK_AUDIT_DELEGATED_OPERATOR_APPS", set())
    trace_id = getattr(request, "trace_id", "")
    if (
        app_code not in trusted_apps
        or getattr(app, "verified", False) is not True
        or getattr(request, "_apigw_jwt_user_verified", False) is not True
    ):
        logger.warning(
            "bk_audit delegated_operator_ignored app_code=%s proxy_username=%s trace_id=%s",
            app_code,
            proxy_username,
            trace_id,
        )
        return proxy_username

    if not DELEGATED_AUDIT_OPERATOR_PATTERN.fullmatch(operator):
        logger.warning(
            "bk_audit delegated_operator_invalid app_code=%s proxy_username=%s trace_id=%s",
            app_code,
            proxy_username,
            trace_id,
        )
        return proxy_username

    logger.info(
        "bk_audit delegated_operator_resolved audit_username=%s proxy_username=%s app_code=%s trace_id=%s",
        operator,
        proxy_username,
        app_code,
        trace_id,
    )
    return operator


def sanitize_audit_data(data):
    """Remove large payloads and redact secret-like values from audit snapshots."""
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            normalized_key = str(key).lower()
            if normalized_key in REMOVED_AUDIT_FIELDS:
                continue
            if any(keyword in normalized_key for keyword in SENSITIVE_AUDIT_KEYWORDS):
                sanitized[key] = "******"
            else:
                sanitized[key] = sanitize_audit_data(value)
        return AuditSnapshot(sanitized) if isinstance(data, AuditSnapshot) else sanitized
    if isinstance(data, (list, tuple)):
        return [sanitize_audit_data(item) for item in data]
    if isinstance(data, six.string_types):
        stripped_data = data.strip()
        if stripped_data.startswith(("{", "[")):
            try:
                decoded_data = json.loads(stripped_data)
            except (TypeError, ValueError):
                return data
            return json.dumps(sanitize_audit_data(decoded_data), ensure_ascii=False, sort_keys=True)
    return data


def get_audit_snapshot(resource_id, instance, data=None):
    """Build a safe before-change snapshot without affecting the business path."""
    if not settings.ENABLE_BK_AUDIT or not resource_id or not instance:
        return None
    try:
        snapshot = data() if callable(data) else data
        if snapshot is None:
            snapshot = build_instance_data(resource_id, instance)
        return AuditSnapshot(sanitize_audit_data(snapshot or {}))
    except Exception:
        logger.exception(
            "bk_audit_snapshot_failed resource_id=%s instance_id=%s",
            resource_id,
            getattr(instance, "id", None),
        )
        return None


def get_periodic_task_audit_snapshot(instance):
    return get_audit_snapshot(
        "periodic_task",
        instance,
        data=lambda: {
            "id": instance.id,
            "name": instance.name,
            "cron": instance.cron,
            "enabled": instance.enabled,
            "template_id": instance.template_id,
            "template_source": instance.template_source,
            "template_version": instance.template_version,
            "creator": instance.creator,
            "editor": instance.editor,
        },
    )


def bk_audit_add_event_on_commit(
    username, action_id, resource_id=None, instance=None, origin_data=None, *args, data=None, **kwargs
):
    """Register a success event only after the surrounding transaction commits."""
    if not settings.ENABLE_BK_AUDIT:
        return
    transaction.on_commit(
        partial(
            bk_audit_add_event,
            username=username,
            action_id=action_id,
            resource_id=resource_id,
            instance=instance,
            origin_data=origin_data,
            data=data,
        )
    )


def bk_audit_add_event(
    username, action_id, resource_id=None, instance=None, origin_data=None, *args, data=None, **kwargs
):
    if not settings.ENABLE_BK_AUDIT:
        return
    instance_id = None
    try:
        instance_id = getattr(instance, "id", None)
        if instance_id is None and isinstance(data, dict):
            instance_id = data.get("id")
        logger.info(
            "bk_audit add_event: username: %s, action_id: %s, resource_id: %s, instance_id: %s",
            username,
            action_id,
            resource_id,
            instance_id,
        )
        if instance is not None and data is None:
            data = build_instance_data(resource_id, instance)
        safe_origin_data = sanitize_audit_data(origin_data)
        safe_data = sanitize_audit_data(data)
        instance = build_instance(resource_id, instance, safe_origin_data, safe_data)
        context = AuditContext(username=username)
        bk_audit_client.add_event(
            action=Action(action_id),
            resource_type=ResourceType(resource_id) if resource_id else None,
            audit_context=context,
            instance=instance,
        )
        logger.info("bk_audit add_event: success")
    except Exception:
        logger.exception(
            "bk_audit_add_event_failed action_id=%s resource_id=%s instance_id=%s",
            action_id,
            resource_id,
            instance_id,
        )
