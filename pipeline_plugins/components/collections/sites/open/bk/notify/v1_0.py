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
from functools import partial

from django.utils import translation
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import ArrayItemSchema, BooleanItemSchema, IntItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.core.models import StaffGroupSet
from gcloud.core.roles import CC_V2_ROLE_MAP
from gcloud.utils.cmdb import get_notify_receivers
from gcloud.utils.handlers import handle_api_error
from packages.bkapi.bk_cmsi.shortcuts import get_client_by_username
from pipeline_plugins.base.utils.inject import supplier_account_for_business

__group_name__ = _("蓝鲸服务(BK)")
logger_celery = logging.getLogger("celery")
bk_handle_api_error = partial(handle_api_error, __group_name__)


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
                    description=_("需要使用的通知方式，从 API 网关自动获取已实现的通知渠道"),
                    item_schema=StringItemSchema(description=_("通知方式")),
                ),
            ),
            self.InputItem(
                name=_("固定分组"),
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
                name=_("项目人员分组"),
                key="bk_staff_group",
                type="array",
                required=False,
                schema=ArrayItemSchema(
                    description=_("需要进行通知的项目人员分组ID列表"),
                    item_schema=IntItemSchema(description=_("项目人员分组ID")),
                ),
            ),
            self.InputItem(
                name=_("额外通知人"),
                key="bk_more_receiver",
                type="string",
                schema=StringItemSchema(description=_("除了通知分组外需要额外通知的人员，多个用英文逗号 `,` 分隔")),
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
            self.InputItem(
                name=_("通知执行人"),
                key="notify",
                type="boolean",
                schema=BooleanItemSchema(description=_("通知执行人名字")),
            ),
        ]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        if parent_data.get_one_of_inputs("language"):
            translation.activate(parent_data.get_one_of_inputs("language"))

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)
        notify_type = data.get_one_of_inputs("bk_notify_type")
        title = data.get_one_of_inputs("bk_notify_title")
        content = data.get_one_of_inputs("bk_notify_content")

        receiver_info = data.get_one_of_inputs("bk_receiver_info")
        receiver_groups = receiver_info.get("bk_receiver_group")
        staff_groups = receiver_info.get("bk_staff_group")
        more_receiver = receiver_info.get("bk_more_receiver")
        notify = data.get_one_of_inputs("notify")

        # 转换为cc3.0字段
        receiver_group = [CC_V2_ROLE_MAP[group] for group in receiver_groups]

        result = get_notify_receivers(
            tenant_id, executor, biz_cc_id, supplier_account, receiver_group, more_receiver, self.logger
        )

        if not result["result"]:
            data.set_outputs("ex_data", result["message"])
            return False

        # 获取项目的自定义人员分组人员
        staff_names = StaffGroupSet.objects.get_members_with_group_ids(staff_groups) if staff_groups else []

        usernames = result["data"].split(",") + staff_names

        # 当通知接收人包含执行人时，执行人放在列表第一位，且对通知名单进行去重处理
        if notify or executor in usernames:
            usernames.insert(0, executor)
        unique_usernames = sorted(set(usernames), key=usernames.index)

        base_kwargs = {
            "receiver__username": ",".join(unique_usernames).strip(","),
            "title": title,
            "content": content,
        }

        error_flag = False
        error = ""
        for msg_type in notify_type:
            kwargs = {}
            kwargs.update(**base_kwargs)
            kwargs.update({"msg_type": msg_type})

            # 保留通知内容中的换行和空格
            if msg_type == "mail":
                kwargs["content"] = "<pre>%s</pre>" % kwargs["content"]
            result = client.cmsi.send_msg(kwargs, headers={"X-Bk-Tenant-Id": tenant_id})

            if not result["result"]:
                message = bk_handle_api_error("cmsi.send_msg", kwargs, result)
                self.logger.error(message)
                error_flag = True
                error += "%s;" % message

        if error_flag:
            # 这里不需要返回 html 格式到前端，避免导致异常信息展示格式错乱
            data.set_outputs("ex_data", error.replace("<", "|").replace(">", "|"))
            return False

        return True


class NotifyComponent(Component):
    name = _("发送通知")
    code = "bk_notify"
    bound_service = NotifyService
    version = "v1.0"
    form = "%scomponents/atoms/bk/notify/v1_0.js" % settings.STATIC_URL
    desc = _(
        "通知方式从 API 网关自动获取已实现的通知渠道，API网关定义了这些消息通知组件的接口协议，但是并没有完全实现组件内容，"
        "用户可根据接口协议，重写此部分组件。API网关为降低实现消息通知组件的难度，提供了在线更新组件配置，"
        "不需编写组件代码的方案。详情请查阅PaaS->API网关->使用指南。"
    )
