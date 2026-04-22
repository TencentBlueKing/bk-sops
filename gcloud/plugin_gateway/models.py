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

from django.db import models


class PluginGatewaySourceConfig(models.Model):
    source_key = models.CharField(max_length=64, unique=True)
    display_name = models.CharField(max_length=128)
    default_project_id = models.BigIntegerField(null=True, blank=True)
    callback_domain_allow_list = models.JSONField(default=list)
    plugin_allow_list = models.JSONField(default=list)
    is_enabled = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "插件网关来源配置"
        verbose_name_plural = "插件网关来源配置"
        ordering = ["source_key"]


class PluginGatewayRun(models.Model):
    class Status:
        RUNNING = "RUNNING"
        WAITING_CALLBACK = "WAITING_CALLBACK"
        SUCCEEDED = "SUCCEEDED"
        FAILED = "FAILED"
        CANCELLED = "CANCELLED"

        TERMINAL = {SUCCEEDED, FAILED, CANCELLED}

    source_key = models.CharField(max_length=64, db_index=True)
    plugin_id = models.CharField(max_length=128, db_index=True)
    plugin_version = models.CharField(max_length=64)
    client_request_id = models.CharField(max_length=128)
    open_plugin_run_id = models.CharField(max_length=64, unique=True, db_index=True)
    callback_url = models.URLField(max_length=512)
    callback_token = models.CharField(max_length=512)
    run_status = models.CharField(max_length=32, db_index=True)
    caller_app_code = models.CharField(max_length=64, db_index=True)
    trigger_payload = models.JSONField(default=dict)
    outputs = models.JSONField(default=dict)
    error_message = models.TextField(blank=True, default="")
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "插件网关执行记录"
        verbose_name_plural = "插件网关执行记录"
        ordering = ["-create_time", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["caller_app_code", "client_request_id"],
                name="uniq_plugin_gateway_app_request",
            )
        ]
