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
    if email_content:
        content = email_content

    client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
    _send_func = {"weixin": "v1_send_weixin", "mail": "v1_send_mail", "sms": "v1_send_sms", "voice": "v1_send_voice"}
    _args_gen = {"mail": _email_args, "weixin": _weixin_args, "voice": _voice_args, "sms": _sms_args}
    for msg_type in notify_type:
        kwargs = _args_gen[msg_type](receivers, title, content)
        try:
            getattr(client.api, _send_func[msg_type])(kwargs, headers={"X-Bk-Tenant-Id": tenant_id})
        except Exception as e:
            logger.error("taskflow send message failed, kwargs={}, result={}".format(json.dumps(kwargs), str(e)))
    return True


def _email_args(receivers, title, content):
    return {
        "receiver__username": receivers,
        "title": title,
        # 保留通知内容中的换行和空格
        "content": "<pre>%s</pre>" % content,
    }


def _weixin_args(receivers, title, content):
    return {"receiver__username": receivers, "message_data": {"heading": title, "message": content}}


def _voice_args(receivers, title, content):
    return {
        "auto_read_message": "蓝鲸通知 {}".format("%s: %s" % (title, content)),
        "receiver__username": receivers,
    }


def _sms_args(receivers, title, content):
    return {
        "receiver__username": receivers,
        "content": "《蓝鲸作业平台》通知 {} 该信息如非本人订阅，请忽略本短信。".format("%s: %s" % (title, content)),
        "is_content_base64": False,
    }
