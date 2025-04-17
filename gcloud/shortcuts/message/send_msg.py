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

import ujson as json

from gcloud.conf import settings
from packages.bkapi.bk_cmsi.shortcuts import get_client_by_username

logger = logging.getLogger("root")


def send_message(executor, tenant_id, notify_type, receivers, title, content, email_content=None):
    # 兼容旧数据
    if not email_content:
        email_content = content

    if "email" in notify_type:
        notify_type[notify_type.index("email")] = "mail"
    client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
    kwargs = {
        "receiver": receivers,
        "title": title,
        "content": content,
    }
    _send_func = {"weixin": "v1_send_weixin", "email": "v1_send_mail", "sms": "v1_send_sms", "voice": "v1_send_voice"}
    for msg_type in notify_type:
        kwargs.update({"msg_type": msg_type})
        if "mail" == msg_type:
            kwargs.update({"content": email_content})
        try:
            getattr(client.api, _send_func[msg_type])(kwargs, headers={"X-Bk-Tenant-Id": tenant_id})
        except Exception as e:
            logger.error("taskflow send message failed, kwargs={}, result={}".format(json.dumps(kwargs), str(e)))
    return True
