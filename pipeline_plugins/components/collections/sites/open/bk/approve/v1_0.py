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
import traceback

from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema

from gcloud.conf import settings
from gcloud.shortcuts.message import PENDING_PROCESSING
from gcloud.taskflow3.celery.tasks import send_taskflow_message
from gcloud.utils.handlers import handle_api_error
from packages.bkapi.bk_itsm.shortcuts import get_client_by_username
from pipeline_plugins.components.utils import get_node_callback_url

__group_name__ = _("蓝鲸服务(BK)")
logger = logging.getLogger(__name__)


class ApproveService(Service):
    __need_schedule__ = True

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("审核人"),
                key="bk_verifier",
                type="string",
                schema=StringItemSchema(description=_("审核人,多个用英文逗号`,`分隔")),
            ),
            self.InputItem(
                name=_("审核标题"),
                key="bk_approve_title",
                type="string",
                schema=StringItemSchema(description=_("审核标题")),
            ),
            self.InputItem(
                name=_("审核内容"),
                key="bk_approve_message",
                type="string",
                schema=StringItemSchema(description=_("通知的标题")),
            ),
        ]

    def outputs_format(self):
        return [
            self.OutputItem(name=_("单据sn"), key="sn", type="string", schema=StringItemSchema(description=_("单据sn"))),
            self.OutputItem(
                name=_("审核结果"),
                key="approve_result",
                type="string",
                schema=StringItemSchema(description=_("审核结果")),
            ),
        ]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_username(username=executor, stage=settings.BK_APIGW_STAGE_NAME)

        verifier = data.get_one_of_inputs("bk_verifier")
        title = data.get_one_of_inputs("bk_approve_title")
        approve_content = data.get_one_of_inputs("bk_approve_content")

        verifier = verifier.replace(" ", "")

        kwargs = {
            "creator": executor,
            "fields": [
                {"key": "title", "value": title},
                {"key": "APPROVER", "value": verifier},
                {"key": "APPROVAL_CONTENT", "value": approve_content},
            ],
            "fast_approval": True,
            "meta": {
                "callback_url": get_node_callback_url(self.root_pipeline_id, self.id, getattr(self, "version", ""))
            },
        }
        result = client.api.create_ticket(kwargs)
        if not result["result"]:
            message = handle_api_error(__group_name__, "itsm.create_ticket", kwargs, result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

        data.outputs.sn = result["data"]["sn"]
        data.outputs.id = result["data"]["id"]
        task_id: int = parent_data.get_one_of_inputs("task_id")
        send_taskflow_message.delay(
            task_id=task_id,
            msg_type=PENDING_PROCESSING,
            use_root=True,
        )

        return True

    def schedule(self, data, parent_data, callback_data=None):
        try:
            rejected_block = data.get_one_of_inputs("rejected_block", True)
            approve_result = callback_data["approve_result"]
            data.outputs.approve_result = "通过" if approve_result else "拒绝"
            # 审核拒绝不阻塞
            if not approve_result and not rejected_block:
                return True
            return approve_result
        except Exception as e:
            err_msg = "get Approve Component result failed: {}, err: {}"
            self.logger.error(err_msg.format(callback_data, traceback.format_exc()))
            data.outputs.ex_data = err_msg.format(callback_data, e)
            return False


class ApproveComponent(Component):
    name = _("审批(已废弃,请切换新版审批组件)")
    code = "bk_approve"
    bound_service = ApproveService
    form = "%scomponents/atoms/bk/approve/v1_0.js" % settings.STATIC_URL
    version = "v1.0"
