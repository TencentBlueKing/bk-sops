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

from ..base import ComponentAPI


class CollectionsCMSI(object):
    """Collections of CMSI APIS"""

    def __init__(self, client):
        self.client = client

        self.send_mail = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_mail/',
            description='发送邮件'
        )
        self.send_mp_weixin = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_mp_weixin/',
            description='发送公众号微信消息'
        )
        self.send_qy_weixin = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_qy_weixin/',
            description='发送企业微信'
        )
        self.send_sms = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_sms/',
            description='发送短信'
        )
        self.send_voice_msg = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_voice_msg/',
            description='公共语音通知'
        )
        self.send_weixin = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_weixin/',
            description='发送微信消息'
        )
        self.get_msg_type = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cmsi/get_msg_type/',
            description='查询 send_msg 组件支持发送消息的类型'
        )
        self.send_msg = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_msg/',
            description='通用消息发送接口'
        )
