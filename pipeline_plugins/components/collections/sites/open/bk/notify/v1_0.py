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
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from gcloud.core.roles import CC_V2_ROLE_MAP
from gcloud.utils.handlers import handle_api_error

from pipeline_plugins.base.utils.inject import supplier_account_for_business

__group_name__ = _("蓝鲸服务(BK)")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
bk_handle_api_error = partial(handle_api_error, __group_name__)


def get_notify_receivers(client, biz_cc_id, supplier_account, receiver_group, more_receiver):
    """
    @summary: 根据通知分组和附加通知人获取最终通知人
    @param client: API 客户端
    @param biz_cc_id: 业务CC ID
    @param supplier_account: 租户 ID
    @param receiver_group: 通知分组
    @param more_receiver: 附加通知人
    @return:
    """
    kwargs = {
        "bk_supplier_account": supplier_account,
        "condition": {
            "bk_biz_id": int(biz_cc_id)
        }
    }
    cc_result = client.cc.search_business(kwargs)
    if not cc_result["result"]:
        result = {
            "result": False,
            "message": cc_result["message"],
            "data": None
        }
        return result

    biz_count = cc_result["data"]["count"]
    if biz_count != 1:
        result = {
            "result": False,
            "message": _("从 CMDB 查询到业务不唯一，业务ID:{}, 返回数量: {}".format(biz_cc_id, biz_count)),
            "data": None
        }
        return result

    biz_data = cc_result["data"]["info"][0]
    receivers = []

    if not isinstance(receiver_group, list):
        receiver_group = receiver_group.split(",")

    for group in receiver_group:
        receivers.extend(biz_data[CC_V2_ROLE_MAP[group]].split(","))

    if more_receiver:
        receivers.extend([name.strip() for name in more_receiver.split(",")])

    result = {
        "result": True,
        "message": "success",
        "data": ",".join(set(receivers))
    }
    return result


class NotifyService(Service):

    def inputs_format(self):
        return [
            self.InputItem(name=_("业务 ID"),
                           key="biz_cc_id",
                           type="string",
                           schema=StringItemSchema(description=_("通知人员所属的 CMDB 业务 ID"))),
            self.InputItem(name=_("通知方式"),
                           key="bk_notify_type",
                           type="array",
                           schema=ArrayItemSchema(description=_("需要使用的通知方式，从 API 网关自动获取已实现的通知渠道"),
                                                  enum=["weixin", "mail", "sms"],
                                                  item_schema=StringItemSchema(description=_("通知方式")))),
            self.InputItem(name=_("通知分组"),
                           key="bk_receiver_group",
                           type="array",
                           required=False,
                           schema=ArrayItemSchema(description=_("需要进行通知的业务人员分组"),
                                                  enum=["Maintainers", "ProductPm", "Developer", "Tester"],
                                                  item_schema=StringItemSchema(description=_("通知分组")))),
            self.InputItem(name=_("额外通知人"),
                           key="bk_more_receiver",
                           type="string",
                           schema=StringItemSchema(
                               description=_("除了通知分组外需要额外通知的人员，多个用英文逗号 `,` 分隔"))
                           ),
            self.InputItem(name=_("通知标题"),
                           key="bk_notify_title",
                           type="string",
                           schema=StringItemSchema(description=_("通知的标题"))),
            self.InputItem(name=_("通知内容"),
                           key="bk_notify_content",
                           type="string",
                           schema=StringItemSchema(description=_("通知的内容")))]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            translation.activate(parent_data.get_one_of_inputs("language"))

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)
        notify_type = data.get_one_of_inputs("bk_notify_type")
        title = data.get_one_of_inputs("bk_notify_title")
        content = data.get_one_of_inputs("bk_notify_content")

        receiver_info = data.get_one_of_inputs("bk_receiver_info")
        receiver_group = receiver_info.get("bk_receiver_group")
        more_receiver = receiver_info.get("bk_more_receiver")

        result = get_notify_receivers(client,
                                      biz_cc_id,
                                      supplier_account,
                                      receiver_group,
                                      more_receiver)

        if not result["result"]:
            data.set_outputs("ex_data", result["message"])
            return False

        base_kwargs = {
            "receiver__username": result["data"],
            "title": title,
            "content": content,
        }
        for msg_type in notify_type:
            kwargs = {}
            kwargs.update(**base_kwargs)
            kwargs.update({"msg_type": msg_type})
            result = client.cmsi.send_msg(kwargs)

            if not result["result"]:
                message = bk_handle_api_error("cmsi.send_msg", kwargs, result)
                self.logger.error(message)
                data.set_outputs("ex_data", message)
                return False

        return True


class NotifyComponent(Component):
    name = _("发送通知")
    code = "bk_notify"
    bound_service = NotifyService
    version = "v1.0"
    form = "%scomponents/atoms/bk/notify/v1_0.js" % settings.STATIC_URL
    desc = _("通知方式从 API 网关自动获取已实现的通知渠道，API网关定义了这些消息通知组件的接口协议，但是并没有完全实现组件内容，"
             "用户可根据接口协议，重写此部分组件。API网关为降低实现消息通知组件的难度，提供了在线更新组件配置，"
             "不需编写组件代码的方案。详情请查阅PaaS->API网关->使用指南。")
