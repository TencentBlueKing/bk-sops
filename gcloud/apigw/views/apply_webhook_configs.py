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
from django.db import transaction
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from webhook.api import apply_scope_subscriptions, apply_scope_webhooks

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.apigw.decorators import project_inject
from gcloud.constants import WebhookScopeType
from gcloud.iam_auth.view_interceptors.apigw.apply_webhook_configs import ApplyWebhookConfigs
from gcloud.apigw.views.utils import logger
from gcloud.apigw.serializers import WebhookSerializer

from gcloud.iam_auth.intercept import iam_intercept
from apigw_manager.apigw.decorators import apigw_require


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
    template_ids = webhook_configs.pop("template_ids")

    try:
        with transaction.atomic():
            for template_id in template_ids:
                webhooks = copy.deepcopy(webhook_configs)
                webhook_code = f"template_{template_id}_webhook"
                webhook_name = f"template_{template_id}_webhook"
                webhooks.update({"code": webhook_code, "name": webhook_name})

                apply_scope_webhooks(
                    scope_type=WebhookScopeType.TEMPLATE.value, scope_code=str(template_id), webhooks=[webhooks]
                )
                apply_scope_subscriptions(
                    scope_type=WebhookScopeType.TEMPLATE.value,
                    scope_code=str(template_id),
                    subscription_configs={webhook_code: webhooks["events"]},
                )
    except Exception as e:
        logger.exception("apply_webhook_configs error")
        return {"result": False, "message": f"fail: {e}", "code": err_code.UNKNOWN_ERROR.code}

    return {"result": True, "message": "success", "code": err_code.SUCCESS.code}
