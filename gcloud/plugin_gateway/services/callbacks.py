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
from requests import RequestException

from gcloud.plugin_gateway.models import PluginGatewayRun
from gcloud.utils import crypto

logger = logging.getLogger("root")


class PluginGatewayCallbackService:
    MAX_OUTPUT_BYTES = 64 * 1024
    MAX_CALLBACK_RETRIES = 3
    RETRY_BACKOFF_SECONDS = 1

    @classmethod
    def callback_run(cls, open_plugin_run_id, run_status, outputs=None, error_message=""):
        run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id)
        if run.run_status in PluginGatewayRun.Status.TERMINAL:
            logger.info(
                "[plugin_gateway] skip callback for terminal run, run_id=%s status=%s",
                open_plugin_run_id,
                run.run_status,
            )
            return False

        truncated_outputs, truncated, truncated_fields = cls._truncate_outputs(outputs or {})
        run.run_status = run_status
        run.outputs = truncated_outputs
        run.error_message = error_message
        run.save(update_fields=["run_status", "outputs", "error_message", "update_time"])

        callback_payload = {
            "open_plugin_run_id": open_plugin_run_id,
            "status": run_status,
            "outputs": truncated_outputs,
            "error_message": error_message,
            "truncated": truncated,
            "truncated_fields": truncated_fields,
        }
        callback_headers = {"X-Callback-Token": crypto.decrypt(run.callback_token)}

        for attempt in range(1, cls.MAX_CALLBACK_RETRIES + 1):
            try:
                requests.post(
                    run.callback_url,
                    json=callback_payload,
                    headers=callback_headers,
                    timeout=10,
                )
                return True
            except RequestException as e:
                if attempt == cls.MAX_CALLBACK_RETRIES:
                    logger.exception(
                        "[plugin_gateway] callback request failed after retries, run_id=%s callback_url=%s error=%s",
                        open_plugin_run_id,
                        run.callback_url,
                        e,
                    )
                    return False

                logger.warning(
                    "[plugin_gateway] callback request failed, retrying "
                    "run_id=%s callback_url=%s attempt=%s/%s error=%s",
                    open_plugin_run_id,
                    run.callback_url,
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
