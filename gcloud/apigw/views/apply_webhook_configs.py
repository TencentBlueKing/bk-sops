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

import ujson as json
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.conf import settings
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from webhook.base_models import Webhook
from webhook.models import Scope, Subscription
from webhook.models import Webhook as WebhookModel
from webhook.utils import process_sensitive_info

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.apigw.serializers import WebhookSerializer
from gcloud.apigw.views.utils import logger
from gcloud.constants import WebhookScopeType
from gcloud.contrib.audit.instances import AuditSnapshot
from gcloud.contrib.audit.utils import bk_audit_add_event_on_commit
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw.apply_webhook_configs import ApplyWebhookConfigs
from gcloud.tasktmpl3.models import TaskTemplate


def _get_webhook_audit_context(project_id, template_ids):
    if not settings.ENABLE_BK_AUDIT:
        return {}, {}
    try:
        templates = {
            str(template.id): template
            for template in TaskTemplate.objects.filter(project_id=project_id, id__in=template_ids, is_deleted=False)
        }
        scope_codes = list(templates)
        enabled_by_template = {
            str(item["scope_code"]): item.get("enable_webhook", False)
            for item in WebhookModel.objects.filter(
                scope_type=WebhookScopeType.TEMPLATE.value, scope_code__in=scope_codes
            ).values("scope_code", "enable_webhook")
        }
        events_by_template = {scope_code: set() for scope_code in scope_codes}
        for scope_code, event_code in Subscription.objects.filter(
            scope_type=WebhookScopeType.TEMPLATE.value, scope_code__in=scope_codes
        ).values_list("scope_code", "event_code"):
            events_by_template.setdefault(str(scope_code), set()).add(event_code)
        origins = {
            scope_code: AuditSnapshot(
                {
                    "template_id": template.id,
                    "webhook_enabled": enabled_by_template.get(scope_code, False),
                    "event_types": sorted(events_by_template.get(scope_code, set())),
                }
            )
            for scope_code, template in templates.items()
        }
        return templates, origins
    except Exception:
        logger.exception("bk_audit_webhook_snapshot_failed")
        return {}, {}


def _audit_webhook_changes(username, templates, origins, enabled, events_by_template):
    for scope_code, template in templates.items():
        bk_audit_add_event_on_commit(
            username=username,
            action_id=IAMMeta.FLOW_EDIT_ACTION,
            resource_id=IAMMeta.FLOW_RESOURCE,
            instance=template,
            origin_data=origins[scope_code],
            data=AuditSnapshot(
                {
                    "template_id": template.id,
                    "webhook_enabled": enabled,
                    "event_types": sorted(events_by_template.get(scope_code, [])),
                }
            ),
        )


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(ApplyWebhookConfigs())
def apply_webhook_configs(request, project_id):
    """
    全量应用webhook配置，会覆盖原有配置
    {
       "enable_webhook": true,
       "endpoint": "https://xxx",
       "events": ["*"],
       "extra_info": {},
       "template_ids": ["1"]
    }
    当 enable_webhook 为 false 时，会关闭指定 template_ids 的所有webhook开关
    """
    data = json.loads(request.body)
    ser = WebhookSerializer(data=data)
    if not ser.is_valid():
        return {"result": False, "message": ser.errors, "code": err_code.VALIDATION_ERROR.code}

    webhook_configs = ser.validated_data
    enable_webhook = webhook_configs.pop("enable_webhook", True)
    template_ids = webhook_configs.pop("template_ids")
    templates, audit_origins = _get_webhook_audit_context(request.project.id, template_ids)

    # 关闭webhook：关闭指定模板的所有webhook开关
    if enable_webhook is False:
        scope_codes = [str(template_id) for template_id in template_ids]
        WebhookModel.objects.filter(scope_type="template", scope_code__in=scope_codes).update(enable_webhook=False)
        _audit_webhook_changes(
            request.user.username,
            templates,
            audit_origins,
            False,
            {scope_code: origin["event_types"] for scope_code, origin in audit_origins.items()},
        )
        return {"result": True, "message": "success", "code": err_code.SUCCESS.code}

    events = webhook_configs.pop("events")

    try:
        # 查询已存在的webhook记录
        existing_webhooks = WebhookModel.objects.filter(
            scope_type=WebhookScopeType.TEMPLATE.value, scope_code__in=template_ids
        ).values("scope_code", "id")

        # 构建scope_code到id的映射字典
        existing_webhook_mapping = {webhook["scope_code"]: webhook["id"] for webhook in existing_webhooks}
        with transaction.atomic():
            webhooks_to_create = []
            webhooks_to_update = []
            subscriptions_to_create = []

            # 批量创建Scope记录，使用ignore_conflicts避免重复记录错误
            scopes_to_create = [
                Scope(type=WebhookScopeType.TEMPLATE.value, code=template_id) for template_id in template_ids
            ]
            # 使用ignore_conflicts=True避免唯一约束冲突
            Scope.objects.bulk_create(scopes_to_create, ignore_conflicts=True)

            # 删除现有的webhook关联记录
            Subscription.objects.filter(
                scope_type=WebhookScopeType.TEMPLATE.value, scope_code__in=template_ids
            ).delete()

            # 处理每个模板的webhook配置
            for template_id in template_ids:
                webhook_config = copy.deepcopy(webhook_configs)
                webhook_code = f"template_{template_id}_webhook"
                webhook_name = f"template_{template_id}_webhook"

                # 更新webhook配置
                webhook_config.update(
                    {
                        "code": webhook_code,
                        "name": webhook_name,
                        "scope_type": WebhookScopeType.TEMPLATE.value,
                        "scope_code": template_id,
                        "enable_webhook": True,
                    }
                )
                webhook = Webhook(**webhook_config)
                process_sensitive_info(webhook.extra_info)
                # 根据是否存在决定是更新还是创建
                if str(template_id) in existing_webhook_mapping:
                    webhooks_to_update.append(
                        WebhookModel(id=existing_webhook_mapping[str(template_id)], **webhook.dict())
                    )
                else:
                    webhooks_to_create.append(WebhookModel(**webhook.dict()))

                # 为每个事件创建subscription记录
                for event in events:
                    subscriptions_to_create.append(
                        Subscription(
                            scope_type=WebhookScopeType.TEMPLATE.value,
                            scope_code=template_id,
                            webhook_code=webhook_code,
                            event_code=event,
                        )
                    )

            # 批量执行数据库操作
            if webhooks_to_create:
                WebhookModel.objects.bulk_create(webhooks_to_create)
            if webhooks_to_update:
                WebhookModel.objects.bulk_update(
                    webhooks_to_update, fields=["code", "name", "endpoint", "extra_info", "enable_webhook"]
                )
            Subscription.objects.bulk_create(subscriptions_to_create)

    except Exception as e:
        logger.exception("apply_webhook_configs error")
        return {"result": False, "message": f"fail: {e}", "code": err_code.UNKNOWN_ERROR.code}

    _audit_webhook_changes(
        request.user.username,
        templates,
        audit_origins,
        True,
        {scope_code: events for scope_code in templates},
    )

    return {"result": True, "message": "success", "code": err_code.SUCCESS.code}
