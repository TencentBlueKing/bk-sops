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
import time

import requests
import ujson as json
from django.utils import timezone
from requests import RequestException

from gcloud.plugin_gateway.models import PluginGatewayRun
from gcloud.utils import crypto

logger = logging.getLogger("root")


class PluginGatewayCallbackService:
    MAX_OUTPUT_BYTES = 64 * 1024
    MAX_CALLBACK_RETRIES = 3
    RETRY_BACKOFF_SECONDS = 1

    @classmethod
    def callback_run(cls, open_plugin_run_id, run_status=None, outputs=None, error_message=""):
        """回调通知调用方；支持两种调用语义：

        1. 首次回调：传入 ``run_status``/``outputs``/``error_message``，先落盘再请求。
        2. 补偿重试：只传 ``open_plugin_run_id``（run_status=None），直接按最近一次
           DB 中保存的结果重新投递，不再修改状态。

        只有当下游返回 2xx 时才会将 ``callback_delivered_at`` 置位，之后的同一份
        记录不会被重复投递，也不会因为 run 已处于终态而被短路。
        """

        run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id)

        if run.callback_delivered_at is not None:
            logger.info(
                "[plugin_gateway] skip callback, already delivered run_id=%s delivered_at=%s",
                open_plugin_run_id,
                run.callback_delivered_at,
            )
            return False

        if run_status is not None:
            if run.run_status in PluginGatewayRun.Status.TERMINAL and run.run_status != run_status:
                logger.warning(
                    "[plugin_gateway] callback rejected, run already in terminal run_id=%s current=%s incoming=%s",
                    open_plugin_run_id,
                    run.run_status,
                    run_status,
                )
                return False

            truncated_outputs, truncated, truncated_fields = cls._truncate_outputs(outputs or {})
            run.run_status = run_status
            run.outputs = truncated_outputs
            run.error_message = error_message
            run.save(update_fields=["run_status", "outputs", "error_message", "update_time"])
        else:
            truncated_outputs, truncated, truncated_fields = cls._truncate_outputs(run.outputs or {})

        callback_payload = {
            "open_plugin_run_id": open_plugin_run_id,
            "status": run.run_status,
            "outputs": truncated_outputs,
            "error_message": run.error_message,
            "truncated": truncated,
            "truncated_fields": truncated_fields,
        }
        callback_headers = {"X-Callback-Token": crypto.decrypt(run.callback_token)}

        delivered = cls._post_with_retries(
            open_plugin_run_id=open_plugin_run_id,
            callback_url=run.callback_url,
            payload=callback_payload,
            headers=callback_headers,
        )

        if delivered:
            run.callback_delivered_at = timezone.now()
            run.save(update_fields=["callback_delivered_at", "update_time"])
        return delivered

    @classmethod
    def _post_with_retries(cls, open_plugin_run_id, callback_url, payload, headers):
        for attempt in range(1, cls.MAX_CALLBACK_RETRIES + 1):
            try:
                response = requests.post(callback_url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                return True
            except RequestException as e:
                if attempt == cls.MAX_CALLBACK_RETRIES:
                    logger.exception(
                        "[plugin_gateway] callback request failed after retries, run_id=%s callback_url=%s error=%s",
                        open_plugin_run_id,
                        callback_url,
                        e,
                    )
                    return False

                logger.warning(
                    "[plugin_gateway] callback request failed, retrying "
                    "run_id=%s callback_url=%s attempt=%s/%s error=%s",
                    open_plugin_run_id,
                    callback_url,
                    attempt,
                    cls.MAX_CALLBACK_RETRIES,
                    e,
                )
                time.sleep(cls.RETRY_BACKOFF_SECONDS)

        return False

    @classmethod
    def _truncate_outputs(cls, outputs):
        encoded = json.dumps(outputs)
        encoded_size = len(encoded.encode("utf-8"))
        if encoded_size <= cls.MAX_OUTPUT_BYTES:
            return outputs, False, []
        return (
            {
                "_truncated": True,
                "_summary": {"original_size": encoded_size, "keys": sorted(outputs.keys())[:20]},
            },
            True,
            ["outputs"],
        )
