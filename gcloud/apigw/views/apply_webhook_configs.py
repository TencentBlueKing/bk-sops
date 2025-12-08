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
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from webhook.models import Subscription, Scope
from webhook.models import Webhook as WebhookModel
from webhook.utils import process_sensitive_info
from webhook.base_models import Webhook

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.apigw.serializers import WebhookSerializer
from gcloud.apigw.views.utils import logger
from gcloud.constants import WebhookScopeType
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw.apply_webhook_configs import ApplyWebhookConfigs


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
       "endpoint": "https://xxx",
       "events": ["*"],
       "extra_info": {},
       "template_ids": ["1"]
    }
    """
    data = json.loads(request.body)
    ser = WebhookSerializer(data=data)
    ser.is_valid(raise_exception=True)

    webhook_configs = ser.validated_data
    events = webhook_configs.pop("events")
    template_ids = webhook_configs.pop("template_ids")

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
                WebhookModel.objects.bulk_update(webhooks_to_update, fields=["code", "name", "endpoint", "extra_info"])
            Subscription.objects.bulk_create(subscriptions_to_create)

    except Exception as e:
        logger.exception("apply_webhook_configs error")
        return {"result": False, "message": f"fail: {e}", "code": err_code.UNKNOWN_ERROR.code}

    return {"result": True, "message": "success", "code": err_code.SUCCESS.code}
