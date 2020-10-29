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

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = "1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCBatchUpdateSetService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("填参方式"), key="cc_set_select_method", type="str", schema=StringItemSchema(description=_("填参方式")),
            ),
            self.InputItem(
                name=_("拓扑模块属性修改"),
                key="cc_set_update_data",
                type="array",
                schema=ArrayItemSchema(
                    description=_("拓扑模块属性修改"),
                    item_schema=ObjectItemSchema(description=_("拓扑模块属性修改对象"), property_schemas={}),
                ),
            ),
            self.InputItem(
                name=_("自动扩展分隔符"),
                key="cc_set_template_break_line",
                type="str",
                schema=StringItemSchema(description=_("批量修改模块属性参数")),
            ),
        ]

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("更新成功的set"),
                key="set_update_success",
                type="object",
                schema=ObjectItemSchema(description=_("更新成功的set"), property_schemas={}),
            ),
            self.OutputItem(
                name=_("更新失败的set"),
                key="set_update_failed",
                type="object",
                schema=ObjectItemSchema(description=_("更新失败的set"), property_schemas={}),
            ),
        ]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        cc_set_select_method = data.get_one_of_inputs("cc_set_select_method")
        cc_set_update_data = data.get_one_of_inputs("cc_set_update_data")
        cc_set_template_break_line = data.get_one_of_inputs("cc_set_template_break_line") or ","

        attr_list = []
        # 如果用户选择了单行扩展
        if cc_set_select_method == "template":
            for cc_set_item in cc_set_update_data:
                chunk_result = chunk_table_data(cc_set_item, cc_set_template_break_line)
                if not chunk_result["result"]:
                    data.set_outputs("ex_data", chunk_result["message"])
                    return False
                attr_list.extend(chunk_result["data"])
        else:
            # 非单行扩展的情况无需处理
            attr_list = cc_set_update_data

        success_update = []
        failed_update = []

        for update_item in attr_list:
            # 过滤,去除用户没有填的字段
            update_params = {key: value for key, value in update_item.items() if value}
            bk_set_name = update_params["bk_set_name"]
            if "bk_new_set_name" in update_params:
                update_params["bk_set_name"] = update_params["bk_new_set_name"]
                del update_params["bk_new_set_name"]

            # 检查set name是否存在
            if not bk_set_name:
                failed_update.append(update_item)
                self.logger.info("set 属性更新失败, set name有空值, data={}".format(update_item))
                continue
            # 根据set name查询set  id
            kwargs = {
                "bk_biz_id": biz_cc_id,
                "fields": ["bk_set_id", "bk_set_name"],
                "condition": {"bk_set_name": bk_set_name},
            }
            search_result = client.cc.search_set(kwargs)
            bk_set_id = 0
            for search_set in search_result["data"]["info"]:
                if search_set["bk_set_name"] == bk_set_name:
                    bk_set_id = search_set["bk_set_id"]
                    break
            # 更新set属性
            kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_set_id": bk_set_id,
                "data": update_params,
            }
            update_result = client.cc.update_set(kwargs)
            if update_result["result"]:
                self.logger.info("set 属性更新成功, data={}".format(kwargs))
                success_update.append(update_item)
            else:
                self.logger.info("set 属性更新失败, data={}".format(kwargs))
                failed_update.append(update_item)

        data.set_outputs("set_update_success", success_update)
        data.set_outputs("set_update_failed", failed_update)
        # 如果没有更新失败的行
        if not failed_update:
            return True

        return False


class CCBatchUpdateSetComponent(Component):
    """
    @version log（v1.0）:支持手动输入拓扑路径选择集群，并提供相应输入容错： 冗余回车/换行
    """

    name = _("批量更新集群属性")
    code = "cc_batch_update_set"
    bound_service = CCBatchUpdateSetService
    form = "{static_url}components/atoms/cc/batch_update_set/v{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
