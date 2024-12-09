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

from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.conf import settings

from pipeline_plugins.components.collections.sites.open.wechat_work.wechat_work_send_message import v1_0

__group_name__ = _("企业微信(WechatWork)")


class WechatWorkSendMessageService(v1_0.WechatWorkSendMessageService):
    pass


class WechatWorkSendMessageComponent(Component):
    name = _("发送消息")
    code = "wechat_work_send_message"
    bound_service = WechatWorkSendMessageService
    form = "%scomponents/atoms/wechat_work/wechat_work_send_message/v2_0.js" % settings.STATIC_URL
    version = "2.0"
    desc = _(
        "1.部署环境与企业微信服务器网络必须联通 "
        "2.通过企业微信机器人获取会话 ID，可参考https://open.work.weixin.qq.com/api/doc/90000/90136/91770"
        "3. 支持「会话 ID」脱敏填写"
    )
