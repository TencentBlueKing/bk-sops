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

from blueapps.account.conf import ConfFixture
from blueapps.utils import client
from blueapps.utils.esbclient import CustomComponentAPI


"""
发送短信工具文件，开发者可以直接调用此处的send_sms函数，屏蔽环境之间的差异
"""


def send_sms(user_list, content):
    """
    发送短信给指定的用户，
    :param user_list: 用户列表，list
    :param content: 消息内容
    :return: True | raise Exception
    """

    # 1. 获取发送短信的函数实际句柄
    sms_module = client.__getattr__(ConfFixture.SMS_CLIENT_MODULE)
    sms_func = sms_module.__getattr__(ConfFixture.SMS_CLIENT_FUNC)

    # 2. 拼接发送函数的内容
    request_args = {
        ConfFixture.SMS_CLIENT_USER_ARGS_NAME: ",".join(user_list),
        ConfFixture.SMS_CLIENT_CONTENT_ARGS_NAME: content,
    }

    # 3. 发送短信
    if type(sms_func) == CustomComponentAPI:
        result = sms_func.post(request_args)

    else:
        result = sms_func(request_args)

    return result
