# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
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

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
logger = logging.getLogger("root")


def send_message(executor, notify_type, receivers, title, content):
    # 兼容旧数据
    if 'email' in notify_type:
        notify_type[notify_type.index('email')] = 'mail'
    client = get_client_by_user(executor)
    kwargs = {
        'receiver__username': receivers,
        'title': title,
        'content': content,
    }
    for msg_type in notify_type:
        kwargs.update({'msg_type': msg_type})
        send_result = client.cmsi.send_msg(kwargs)
        if not send_result['result']:
            logger.error('taskflow send message failed, kwargs={}, result={}'.format(json.dumps(kwargs),
                                                                                     json.dumps(send_result)))
    return True
