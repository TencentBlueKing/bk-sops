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


def send_message(executor, notify_type, receivers, title, content, email_content=None):
    # 兼容旧数据
    if not email_content:
        email_content = content

    if "email" in notify_type:
        notify_type[notify_type.index("email")] = "mail"
    client = get_client_by_user(executor)
    kwargs = {
        "receiver__username": receivers,
        "title": title,
        "content": content,
    }
    for msg_type in notify_type:
        kwargs.update({"msg_type": msg_type})
        if "mail" == msg_type:
            kwargs.update({"content": email_content})
        send_result = client.cmsi.send_msg(kwargs)
        if not send_result["result"]:
            logger.error(
                "taskflow send message failed, kwargs={}, result={}".format(json.dumps(kwargs), json.dumps(send_result))
            )
    return True


class MessageHandler:
    def _get_bkchat_api(self):
        return "{}/{}".format(BK_CHAT_API_ENTRY, "prod/im/api/v1/send_msg")

    def send(self, executor, notify_type, notify_info, receivers, title, content, email_content=None):
        notify_cmsi = []
        notify_bkchat = []
        for notify in notify_type:
            if notify == "bk_chat":
                notify_bkchat.append(notify_info.get("bkchat_groupid"))
            else:
                notify_cmsi.append(notify)
        if settings.ENABLE_BK_CHAT_CHANNEL and notify_bkchat:
            self.send_bkchat(notify_bkchat, content)
        send_message(executor, notify_cmsi, receivers, title, content, email_content)

        return True

    def send_bkchat(self, notify, content):
        params = {"bk_app_code": settings.APP_CODE, "bk_app_secret": settings.SECRET_KEY}

        data = {
            "im": "WEWORK",
            "msg_type": "text",
            "msg_param": {"content": content},
            "receiver": {"receiver_type": "group", "receiver_ids": notify},
        }

        result = requests.post(url=self._get_bkchat_api(), params=params, json=data)
        send_result = result.json()
        if send_result.get("code") == 0:
            return True
        else:
            logger.error(
                "bkchat send message failed, kwargs={}, result={}".format(json.dumps(data), json.dumps(send_result))
            )
            return False
