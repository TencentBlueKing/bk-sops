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
import requests
import ujson as json

from gcloud.conf import settings

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
logger = logging.getLogger("root")

BK_CHAT_API_ENTRY = settings.BK_CHAT_API_ENTRY


class MessageSender:
    def send(self, executor, notify_type, notify_receivers, receivers, title, content, email_content=None):
        bkchat_receivers = notify_receivers.split(",")
        cmsi_receivers = [notify for notify in notify_type if notify != "bk_chat"]

        if settings.ENABLE_BK_CHAT_CHANNEL and bkchat_receivers:
            logger.info("bkchat send message, receivers: {}".format(bkchat_receivers))
            BkchatSender().send(bkchat_receivers, content)
        logger.info("cmsi send message, receivers: {}".format(cmsi_receivers))
        CmsiSender().send(executor, cmsi_receivers, receivers, title, content, email_content)


class CmsiSender:
    def send(self, executor, notify_type, receivers, title, content, email_content=None):
        # 兼容旧数据
        if not email_content:
            email_content = content

        if "email" in notify_type:
            notify_type[notify_type.index("email")] = "mail"
        client = get_client_by_user(executor)
        base_kwargs = {
            "receiver__username": receivers,
            "title": title,
            "content": content,
        }
        for msg_type in notify_type:
            if msg_type == "voice":
                kwargs = {"receiver__username": receivers, "auto_read_message": content}
                send_result = client.cmsi.send_voice_msg(kwargs)
            else:
                kwargs = {"msg_type": msg_type, **base_kwargs}
                if msg_type == "mail":
                    kwargs["content"] = email_content
                send_result = client.cmsi.send_msg(kwargs)
            if not send_result["result"]:
                logger.error(
                    "taskflow send {}message failed, kwargs={}, result={}".format(
                        "voice " if msg_type == "voice" else "",
                        json.dumps(kwargs),
                        json.dumps(send_result),
                    )
                )


class BkchatSender:
    def _get_bkchat_api(self):
        return "{}/{}".format(BK_CHAT_API_ENTRY, "prod/im/api/v1/send_msg")

    def send(self, notify, content):
        params = {"bk_app_code": settings.BK_CHAT_APP_CODE, "bk_app_secret": settings.BK_CHAT_APP_SECRET_KEY}

        data = {
            "im": "WEWORK",
            "msg_type": "text",
            "msg_param": {"content": content},
            "receiver": {"receiver_type": "group", "receiver_ids": notify},
        }

        result = requests.post(url=self._get_bkchat_api(), params=params, json=data)
        send_result = result.json()
        if send_result.get("code") != 0:
            logger.error(
                "bkchat send message failed, kwargs={}, result={}".format(json.dumps(data), json.dumps(send_result))
            )
