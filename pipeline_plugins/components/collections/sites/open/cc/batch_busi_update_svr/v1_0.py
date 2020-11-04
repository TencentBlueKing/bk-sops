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

from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.components.utils import chunk_table_data

from pipeline_plugins.components.collections.sites.open.cc.base import (
cc_parse_path_text
)

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = "1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCBatchBusiUpdateSvrService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("填参方式"), key="cc_busi_select_method", type="str", schema=StringItemSchema(description=_("填参方式")),
            ),
            self.InputItem(
                name=_("更新主机所属业务模块详情"),
                key="cc_busi_update_svr",
                type="array",
                schema=ArrayItemSchema(
                    description=_("更新主机所属业务模块详情"),
                    item_schema=ObjectItemSchema(description=_("业务模块属性修改对象"), property_schemas={}),
                ),
            ),
            self.InputItem(
                name=_("自动扩展分隔符"),
                key="cc_busi_template_break_line",
                type="str",
                schema=StringItemSchema(description=_("在自动填参时使用的扩展分割符")),
            ),
        ]

    def outputs_format(self):
        self.OutputItem(
            name=_("更新成功的主机"),
            key="set_update_success",
            type="object",
            schema=ObjectItemSchema(description=_("更新成功的主机"), property_schemas={}),
        ),
        self.OutputItem(
            name=_("更新失败的主机"),
            key="set_update_failed",
            type="object",
            schema=ObjectItemSchema(description=_("更新失败的主机"), property_schemas={}),
        ),

        return []

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        operator = data.get_one_of_inputs("operator", parent_data.inputs.operator)

        cc_busi_select_method = data.get_one_of_inputs("cc_busi_select_method")
        cc_busi_update_svr_data = data.get_one_of_inputs("cc_busi_update_svr")
        cc_busi_template_break_line = data.get_one_of_inputs("cc_busi_template_break_line") or ","

        attr_list = []
        # 对 单行扩展 填参方式
        if cc_busi_select_method == "template":
            for cc_srv_busi_item in cc_busi_update_svr_data:
                chunk_result = chunk_table_data(cc_srv_busi_item, cc_busi_template_break_line)
                if not chunk_result["result"]:
                    data.set_outputs("ex_data", chunk_result["message"])
                    return False
                attr_list.extend(chunk_result["data"])
        else:
            # 非单行扩展的情况无需处理
            attr_list = cc_busi_update_svr_data
        success_update = []
        failed_update = []
        for attr in attr_list:
            cc_path_list = cc_parse_path_text(attr["cc_busi_update_svr_business"])
            set_name, busi_name, module_name = cc_path_list[0]
            condition = {
                "host_ip": attr["cc_busi_update_svr_IP"],
                "busi1_name": set_name,
                "busi2_name": busi_name,
                "busi3_name": module_name
            }
            kwargs = {
                "bk_biz_id": biz_cc_id,
                "operator": operator,
                "condition": [condition]
            }
            update_result = client.cmdb.svr_busi_update_svr(kwargs)
            if update_result["result"]:
                self.logger.info("主机所属业务模块更新成功, data={}".format(kwargs))
                success_update.append(attr)
            else:
                self.logger.info("主机所属业务模块更新失败, data={}".format(kwargs))
                failed_update.append(attr)

        data.set_outputs("busi_svr_update_success", success_update)
        data.set_outputs("busi_svr_update_failed", failed_update)
        # 如果没有更新失败的行
        if not failed_update:
            return True
        data.set_outputs("ex_data", failed_update)
        return False


class CCBatchBusiUpdateSvrComponent(Component):
    """
    @version log（v1.0）:支持 单行扩展输入配置方式
    """

    name = _("批量更新主机所属业务模块")
    code = "cc_batch_busi_update_svr"
    bound_service = CCBatchBusiUpdateSvrService
    form = "{static_url}components/atoms/cc/batch_busi_update_svr/v{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
