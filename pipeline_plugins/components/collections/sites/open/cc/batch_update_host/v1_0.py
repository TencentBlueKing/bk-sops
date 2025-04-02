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
from copy import deepcopy
from functools import partial

from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import ArrayItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import CCPluginIPMixin, cc_format_prop_data
from pipeline_plugins.components.utils import chunk_table_data, convert_num_to_str
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("celery")

__group_name__ = _("配置平台(CMDB)")
VERSION = "1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


def verify_host_property(tenant_id, executor, supplier_account, language, cc_host_property, cc_host_prop_value):
    if cc_host_property == "bk_isp_name":
        bk_isp_name = cc_format_prop_data(
            tenant_id, executor, "host", "bk_isp_name", language, supplier_account)
        if not bk_isp_name["result"]:
            ex_data = bk_isp_name["message"]
            return False, ex_data

        host_prop_value = bk_isp_name["data"].get(cc_host_prop_value)
        if not host_prop_value:
            ex_data = _("所属运营商【{}】校验失败，请重试并修改为正确的所属运营商".format(cc_host_prop_value))
            return False, ex_data

    elif cc_host_property == "bk_state_name":
        bk_state_name = cc_format_prop_data(
            tenant_id, executor, "host", "bk_state_name", language, supplier_account)
        if not bk_state_name["result"]:
            ex_data = bk_state_name["message"]
            return False, ex_data

        host_prop_value = bk_state_name["data"].get(cc_host_prop_value)
        if not host_prop_value:
            ex_data = _("所在国家【{}】校验失败，请重试并修改为正确的所在国家".format(cc_host_prop_value))
            return False, ex_data
    elif cc_host_property == "bk_province_name":
        bk_province_name = cc_format_prop_data(
            tenant_id, executor, "host", "bk_province_name", language, supplier_account)
        if not bk_province_name["result"]:
            ex_data = bk_province_name["message"]
            return False, ex_data
        host_prop_value = bk_province_name["data"].get(cc_host_prop_value)
        if not host_prop_value:
            ex_data = _("所在省份【{}】校验失败，请重试并修改为正确的所在省份".format(cc_host_prop_value))
            return False, ex_data
    return True, ""


class CCBatchUpdateHostService(Service, CCPluginIPMixin):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("填参方式"),
                key="cc_host_update_method",
                type="string",
                schema=StringItemSchema(description=_("填参方式"), enum=["manual", "auto"]),
            ),
            self.InputItem(
                name=_("主机属性修改"),
                key="cc_host_property_custom",
                type="array",
                schema=ArrayItemSchema(
                    item_schema=ObjectItemSchema(description=_("主机属性修改"), property_schemas={}),
                    description="主机属性列表",
                ),
            ),
            self.InputItem(
                name=_("自动扩展分隔符"),
                key="gcs_template_break_line",
                type="string",
                schema=StringItemSchema(description=_("凯丽开区参数")),
            ),
        ]

    def execute(self, data, parent_data):
        biz_cc_id = parent_data.get_one_of_inputs("biz_cc_id")
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")

        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        supplier_account = supplier_account_for_business(biz_cc_id)
        language = parent_data.get_one_of_inputs("language")

        host_update_method = data.get_one_of_inputs("cc_host_update_method")
        host_property_custom = data.get_one_of_inputs("cc_host_property_custom")
        separator = data.get_one_of_inputs("cc_auto_separator")

        host_property_custom = convert_num_to_str(host_property_custom)
        if host_update_method == "auto":
            host_property_data = []
            for column in host_property_custom:
                column_result = chunk_table_data(column, separator)
                if not column_result["result"]:
                    message = _(
                        f"单行扩展失败: 请检查输入参数格式是否合法, 修复后重试. 错误内容: {column_result['message']}"
                    )
                    data.outputs.ex_data = message
                    self.logger.error(message)
                    return False
                host_property_data.extend(column_result["data"])
            host_property_custom = host_property_data

        # do not operate inputs data directly
        host_property_copy = deepcopy(host_property_custom)
        update_host_message = []
        for host_property_dir in host_property_copy:
            ip_str = host_property_dir["bk_host_innerip"]
            host_result = self.get_host_list_with_cloud_id(tenant_id, executor, biz_cc_id, ip_str, supplier_account)
            if not host_result["result"]:
                data.outputs.ex_data = host_result.get("message")
                return False
            host_id = int(host_result["data"][0])
            host_update = {"bk_host_id": host_id}
            host_property_dir.pop("bk_host_innerip")
            properties = {}
            for cc_host_property, cc_host_prop_value in host_property_dir.items():
                if cc_host_prop_value:
                    is_legal, ex_data = verify_host_property(
                        tenant_id, executor, supplier_account, language, cc_host_property, cc_host_prop_value
                    )
                    if not is_legal:
                        data.outputs.ex_data = ex_data
                        self.logger.error(ex_data)
                        return False
                    properties[cc_host_property] = cc_host_prop_value
            host_update["properties"] = properties
            update_host_message.append(host_update)

        cc_kwargs = {"bk_supplier_account": supplier_account, "update": update_host_message}

        cc_result = client.api.batch_update_host(
            cc_kwargs,
            headers={"X-Bk-Tenant-Id": tenant_id},
        )
        if cc_result["result"]:
            return True
        else:
            message = cc_handle_api_error("cc.batch_update_host", cc_kwargs, cc_result)
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("不合法的IP"),
                key="invalid_ip",
                type="string",
                schema=StringItemSchema(description=_("不合法的IP")),
            ),
        ]


class CCBatchUpdateHostComponent(Component):
    name = _("批量修改主机属性")
    code = "cc_batch_update_host"
    bound_service = CCBatchUpdateHostService
    form = "{static_url}components/atoms/cc/batch_update_host/{ver}.js".format(
        static_url=settings.STATIC_URL, ver="v1_0"
    )
    version = VERSION
    desc = _(
        "1. 填参方式支持手动填写和结合模板生成（单行自动扩展）\n"
        "2. 使用单行自动扩展模式时，每一行支持填写多个已自定义分隔符或是英文逗号分隔的数据，"
        '插件后台会自动将其扩展成多行，如 "1,2,3,4" 会被扩展成四行：1 2 3 4\n'
        "3. 结合模板生成（单行自动扩展）当有一列有多条数据时，其他列要么也有相等个数的数据，要么只有一条数据"
    )
