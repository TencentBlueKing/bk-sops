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

from django.utils import translation
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import ArrayItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.core.roles import CC_V2_ROLE_MAP
from gcloud.utils.cmdb import get_notify_receivers
from pipeline_plugins.base.utils.inject import supplier_account_for_business

__group_name__ = _("蓝鲸服务(BK)")
logger = logging.getLogger(__name__)
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


class NotifyService(Service):

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("通知人员所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("通知方式"),
                key="bk_notify_type",
                type="array",
                schema=ArrayItemSchema(
                    description=_("需要使用的通知方式"),
                    enum=["weixin", "email", "sms"],
                    item_schema=StringItemSchema(description=_("通知方式")),
                ),
            ),
            self.InputItem(
                name=_("通知分组"),
                key="bk_receiver_group",
                type="array",
                required=False,
                schema=ArrayItemSchema(
                    description=_("需要进行通知的业务人员分组"),
                    enum=["Maintainers", "ProductPm", "Developer", "Tester"],
                    item_schema=StringItemSchema(description=_("通知分组")),
                ),
            ),
            self.InputItem(
                name=_("额外通知人"),
                key="bk_more_receiver",
                type="string",
                schema=StringItemSchema(description=_("除了通知分组外需要额外通知的人员")),
            ),
            self.InputItem(
                name=_("通知标题"),
                key="bk_notify_title",
                type="string",
                schema=StringItemSchema(description=_("通知的标题")),
            ),
            self.InputItem(
                name=_("通知内容"),
                key="bk_notify_content",
                type="string",
                schema=StringItemSchema(description=_("通知的内容")),
            ),
        ]

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("返回码"), key="code", type="string", schema=StringItemSchema(description=_("通知接口的返回码"))
            ),
            self.OutputItem(
                name=_("信息"),
                key="message",
                type="string",
                schema=StringItemSchema(description=_("通知接口返回的信息")),
            ),
        ]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            translation.activate(parent_data.get_one_of_inputs("language"))

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)
        notify_type = data.get_one_of_inputs("bk_notify_type")
        receiver_info = data.get_one_of_inputs("bk_receiver_info")
        # 兼容原有数据格式
        if receiver_info:
            receiver_groups = receiver_info.get("bk_receiver_group")
            more_receiver = receiver_info.get("bk_more_receiver")

            # 转换为cc3.0字段
            receiver_group = [CC_V2_ROLE_MAP[group] for group in receiver_groups]
        else:
            receiver_group = data.get_one_of_inputs("bk_receiver_group")
            more_receiver = data.get_one_of_inputs("bk_more_receiver")
        title = data.get_one_of_inputs("bk_notify_title")
        content = data.get_one_of_inputs("bk_notify_content")

        code = ""
        message = ""
        res = get_notify_receivers(client, biz_cc_id, supplier_account, receiver_group, more_receiver)

        result, msg, receivers = res["result"], res["message"], res["data"]

        if not result:
            data.set_outputs("ex_data", msg)
            return False

        for t in notify_type:
            kwargs = self._args_gen[t](self, receivers, title, content)
            result = getattr(client.cmsi, self._send_func[t])(kwargs)

            if not result["result"]:
                data.set_outputs("ex_data", result["message"])
                return False

            code = result["code"]
            message = result["message"]

        data.set_outputs("code", code)
        data.set_outputs("message", message)
        return True

    def _email_args(self, receivers, title, content):
        return {
            "receiver__username": receivers,
            "title": title,
            # 保留通知内容中的换行和空格
            "content": "<pre>%s</pre>" % content,
        }

    def _weixin_args(self, receivers, title, content):
        return {"receiver__username": receivers, "data": {"heading": title, "message": content}}

    def _sms_args(self, receivers, title, content):
        return {"receiver__username": receivers, "content": "%s\n%s" % (title, content)}

    _send_func = {
        "weixin": "send_weixin",
        "email": "send_mail",
        "sms": "send_sms",
    }

    _args_gen = {"weixin": _weixin_args, "email": _email_args, "sms": _sms_args}


class NotifyComponent(Component):
    name = _("发送通知")
    code = "bk_notify"
    bound_service = NotifyService
    form = "%scomponents/atoms/bk/notify/legacy.js" % settings.STATIC_URL
    desc = _(
        "API 网关定义了这些消息通知组件的接口协议，但是，并没有完全实现组件内容，用户可根据接口协议，重写此部分组件。"
        "API网关为降低实现消息通知组件的难度，提供了在线更新组件配置，不需编写组件代码的方案。详情请查阅PaaS->API网"
        "关->使用指南。"
    )
