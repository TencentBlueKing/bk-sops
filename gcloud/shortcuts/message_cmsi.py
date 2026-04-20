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

from bkapi_client_core.apigateway import Operation

MSG_TYPE_ALIAS_MAP = {
    "email": "mail",
}


def normalize_msg_type(msg_type):
    return MSG_TYPE_ALIAS_MAP.get(msg_type, msg_type)


def build_cmsi_message_payload(msg_type, receivers, title, content, email_content=None):
    normalized_msg_type = normalize_msg_type(msg_type)

    if normalized_msg_type == "mail":
        mail_content = email_content if email_content is not None else content
        return normalized_msg_type, {
            "receiver__username": receivers,
            "title": title,
            "content": "<pre>%s</pre>" % mail_content,
        }

    if normalized_msg_type == "weixin":
        return normalized_msg_type, {
            "receiver__username": receivers,
            "message_data": {"heading": title, "message": content},
        }

    if normalized_msg_type == "voice":
        return normalized_msg_type, {
            "auto_read_message": "蓝鲸通知 {}".format("%s: %s" % (title, content)),
            "receiver__username": receivers,
        }

    if normalized_msg_type == "sms":
        return normalized_msg_type, {
            "receiver__username": receivers,
            "content": "《蓝鲸作业平台》通知 {} 该信息如非本人订阅，请忽略本短信。".format("%s: %s" % (title, content)),
            "is_content_base64": False,
        }

    return normalized_msg_type, {
        "receiver__username": receivers,
        "title": title,
        "content": content,
    }


def get_cmsi_send_operation(client, msg_type):
    normalized_msg_type = normalize_msg_type(msg_type)
    operation_name = "v1_send_%s" % normalized_msg_type

    try:
        operation = getattr(client.api, operation_name)
    except AttributeError:
        client.api.register(
            operation_name,
            Operation(name=operation_name, method="POST", path="/v1/send_{}/".format(normalized_msg_type)),
        )
        operation = getattr(client.api, operation_name)

    return normalized_msg_type, operation_name, operation


def send_cmsi_message(client, tenant_id, msg_type, receivers, title, content, email_content=None):
    normalized_msg_type, operation_name, operation = get_cmsi_send_operation(client, msg_type)
    _, payload = build_cmsi_message_payload(
        normalized_msg_type,
        receivers=receivers,
        title=title,
        content=content,
        email_content=email_content,
    )
    result = operation(payload, headers={"X-Bk-Tenant-Id": tenant_id})

    return operation_name, payload, result
