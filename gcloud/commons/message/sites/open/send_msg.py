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

from gcloud.core.utils import get_client_by_user_and_biz_id

logger = logging.getLogger("root")


def send_message(biz_cc_id, executor, notify_type, receivers, title, content):
    client = get_client_by_user_and_biz_id(executor, biz_cc_id)
    if 'weixin' in notify_type:
        kwargs = {
            'receiver__username': receivers,
            'data': {
                'heading': title,
                'message': content,
            }
        }
        result = client.cmsi.send_weixin(kwargs)
        if not result['result']:
            logger.error('taskflow send weixin, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                         json.dumps(result)))
    if 'sms' in notify_type:
        kwargs = {
            'receiver__username': receivers,
            'content': u"%s\n%s" % (title, content),
        }
        result = client.cmsi.send_sms(kwargs)
        if not result['result']:
            logger.error('taskflow send sms, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                      json.dumps(result)))

    if 'email' in notify_type:
        kwargs = {
            'receiver__username': receivers,
            'title': title,
            'content': content,
        }
        result = client.cmsi.send_mail(kwargs)
        if not result['result']:
            logger.error('taskflow send mail, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                       json.dumps(result)))

    if 'voice' in notify_type:
        kwargs = {
            'receiver__username': receivers,
            'auto_read_message': u"%s\n%s" % (title, content),
        }
        result = client.cmsi.send_voice_msg(kwargs)
        if not result['result']:
            logger.error('taskflow send voice, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                        json.dumps(result)))

    return True
