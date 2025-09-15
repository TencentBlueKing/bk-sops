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

from django.db import transaction
from webhook.api import apply_scope_subscriptions, apply_scope_webhooks
from gcloud.constants import WebhookScopeType, WebhookEventType
from webhook.models import Webhook as WebhookModel
from webhook.models import Scope as ScopeModel
from webhook.models import Subscription, Event
from webhook.contrib.drf.serializers import WebhookSerializer
from django.conf import settings
from webhook.utils import process_sensitive_info
from webhook.models import History
from gcloud.utils.dates import format_datetime

logger = logging.getLogger("root")


def get_webhook_configs(scope_code):
    """
    get webhook retry policy of scope
    """
    try:
        webhooks = WebhookModel.objects.filter(scope_type=WebhookScopeType.TEMPLATE.value, scope_code=scope_code)
        result = {}
        for webhook in webhooks:
            result[webhook.scope_code] = {
                "method": webhook.method,
                "endpoint": webhook.endpoint,
                "extra_info": process_sensitive_info(webhook.extra_info, is_decrypt=True),
            }
    except Exception as e:
        logger.exception(f"get_scope_webhooks error: {e}")
        return {"result": False, "message": f"Failed to get webhook configs: {e}", "data": {}, "code": "500"}

    return result


def get_webhook_delivery_history_by_delivery_ids(delivery_id):
    histories = History.objects.filter(delivery_id=delivery_id)
    result = {delivery_id: []}

    events = Event.objects.all()
    event_name_mapping = {event.code: event.name for event in events}

    for history in histories:
        response = history.extra_info.get("response", {})
        result[delivery_id].append(
            {
                "created_at": format_datetime(history.created_at),
                "event_code": history.event_code,
                "event_code_name": event_name_mapping.get(history.event_code, history.event_code),
                "is_success": history.success,
                "status_code": history.status_code,
                "response": response.get("message", None) if isinstance(response, dict) else None,
            }
        )

    return result


def clear_scope_webhooks(scope_code: list):
    try:
        with transaction.atomic():
            WebhookModel.objects.filter(scope_type=WebhookScopeType.TEMPLATE.value, scope_code__in=scope_code).delete()
            ScopeModel.objects.filter(type=WebhookScopeType.TEMPLATE.value, code__in=scope_code).delete()
            Subscription.objects.filter(scope_type=WebhookScopeType.TEMPLATE.value, scope_code__in=scope_code).delete()
    except Exception as e:
        logger.exception(f"clear_webhooks error: {e}")
        return {"result": False, "message": f"Failed to clear webhooks: {e}", "data": {}, "code": "500"}

    return {"result": True, "message": "success", "data": {}, "code": "0"}


def apply_webhook_configs(webhook_configs, scope_code):
    webhook_code = f"template_{scope_code}_webhook"
    webhook_name = f"template_{scope_code}_webhook"
    webhook_configs.update({"code": webhook_code, "name": webhook_name})
    serializer = WebhookSerializer(data=webhook_configs)
    serializer.is_valid(raise_exception=True)
    retry_times = webhook_configs.get("extra_info", {}).get("retry_times", 2)
    if retry_times > settings.MAX_WEBHOOK_RETRY_TIMES:
        return {
            "result": False,
            "message": "重试次数不能超过{}次".format(settings.MAX_WEBHOOK_RETRY_TIMES),
            "data": {},
            "code": "500",
        }
    scope_type = WebhookScopeType.TEMPLATE.value
    subscription_configs = {webhook_code: [WebhookEventType.TASK_FAILED.value, WebhookEventType.TASK_FINISHED.value]}
    try:
        apply_scope_webhooks(scope_type=scope_type, scope_code=scope_code, webhooks=[webhook_configs])
        apply_scope_subscriptions(
            scope_type=scope_type, scope_code=scope_code, subscription_configs=subscription_configs
        )
    except Exception as e:
        logger.exception(f"apply_webhook_configs error: {e}")
        return {"result": False, "message": f"Failed to apply webhook configs: {e}", "data": {}, "code": "500"}

    return {"result": True, "message": "success", "data": {}, "code": "0"}
