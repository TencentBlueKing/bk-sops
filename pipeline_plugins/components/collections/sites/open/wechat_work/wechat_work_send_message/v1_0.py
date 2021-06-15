# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import traceback

import requests
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from pipeline.conf import settings
from pipeline.core.flow.io import StringItemSchema
from gcloud.core.models import EnvironmentVariables

__group_name__ = _("企业微信(WechatWork)")


class WechatWorkSendMessageService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("会话 ID"),
                key="wechat_work_chat_id",
                type="string",
                schema=StringItemSchema(description=_("通过在群里@企业微信机器人获取，多个用换行分隔")),
            ),
            self.InputItem(
                name=_("消息内容"), key="message_content", type="string", schema=StringItemSchema(description=_("消息内容")),
            ),
            self.InputItem(
                name=_("提醒人"),
                key="wechat_work_mentioned_members",
                type="string",
                schema=StringItemSchema(description=_("提醒群指定成员(@某个成员)，多个成员用 `,` 分隔，@all表示提醒所有人")),
            ),
            self.InputItem(
                name=_("消息格式"),
                key="msgtype",
                type="string",
                schema=StringItemSchema(description=_("文本(text)或Markdown")),
            ),
        ]

    def execute(self, data, parent_data):
        chat_id = data.inputs.wechat_work_chat_id
        content = data.inputs.message_content
        mentioned_members = data.inputs.wechat_work_mentioned_members
        msgtype = data.get_one_of_inputs("msgtype", "text")

        chat_id_list = chat_id.split("\n")

        url = EnvironmentVariables.objects.get_var("BKAPP_SOPS_WECHAT_WORK_WEB_HOOK")
        if not url:
            data.outputs.ex_data = "WechatWork send message URL is not config, contact admin please"
            return False

        if not chat_id:
            data.outputs.ex_data = _("会话 ID 不能为空")
            return False

        for c in chat_id_list:
            if len(c) != 32:
                data.outputs.ex_data = _("无效的会话 ID: {}".format(c))
                return False

        mentioned_list = []
        if mentioned_members:
            mentioned_list = str(mentioned_members).split(",")

        try:
            if msgtype == "text":
                resp = requests.post(
                    url=url,
                    json={
                        "chatid": "|".join(chat_id_list),
                        "msgtype": msgtype,
                        "text": {"content": str(content), "mentioned_list": mentioned_list},
                    },
                    timeout=5,
                )
            elif msgtype == "markdown":
                mentioned_str = " ".join(["<@{}>".format(mentioned) for mentioned in mentioned_list])
                content = "{}\n{}\n".format(str(content), mentioned_str)
                resp = requests.post(
                    url=url,
                    json={
                        "chatid": "|".join(chat_id_list),
                        "msgtype": msgtype,
                        "markdown": {"content": content},
                        "at_short_name": True,
                    },
                    timeout=5,
                )

            else:
                err = _("msgtype 不存在")
                self.logger.error(err)
                data.outputs.ex_data = err.format(err)
                return False
        except Exception as e:
            err = _("企业微信发送消息请求失败，详细信息: {}")
            self.logger.error(err.format(traceback.format_exc()))
            data.outputs.ex_data = err.format(e)
            return False

        if not resp.ok:
            err = _("企业微信发送消息请求失败，状态码: {}, 响应: {}").format(resp.status_code, resp.content)
            data.outputs.ex_data = err
            return False

        self.logger.info(resp.content)
        return True


class WechatWorkSendMessageComponent(Component):
    name = _("发送消息")
    code = "wechat_work_send_message"
    bound_service = WechatWorkSendMessageService
    form = "%scomponents/atoms/wechat_work/wechat_work_send_message/v1_0.js" % settings.STATIC_URL
    version = "1.0"
    desc = _("1.部署环境与企业微信服务器网络必须联通 " "2.通过企业微信机器人获取会话 ID，可参考https://open.work.weixin.qq.com/api/doc/90000/90136/91770")
