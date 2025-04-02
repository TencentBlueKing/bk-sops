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

from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import ArrayItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.utils import chunk_table_data, convert_num_to_str
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("celery")

__group_name__ = _("配置平台(CMDB)")
VERSION = "1.0"

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCBatchUpdateSetService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("填参方式"),
                key="cc_set_select_method",
                type="str",
                schema=StringItemSchema(description=_("填参方式")),
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
        tenant_id = parent_data.get_one_of_inputs("tenant_id")

        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)
        cc_set_select_method = data.get_one_of_inputs("cc_set_select_method")
        cc_set_update_data_list = data.get_one_of_inputs("cc_set_update_data")
        cc_set_template_break_line = data.get_one_of_inputs("cc_set_template_break_line") or ","
        cc_set_update_data = convert_num_to_str(cc_set_update_data_list)
        attr_list = []
        # 如果用户选择了单行扩展
        if cc_set_select_method == "auto":
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

        search_attr_kwargs = {"bk_obj_id": "set", "bk_supplier_account": supplier_account}
        attr_result = client.api.search_object_attribute(
            search_attr_kwargs,
            headers={"X-Bk-Tenant-Id": tenant_id},
        )
        if not attr_result["result"]:
            message = handle_api_error("cc", "cc.search_object_attribute", search_attr_kwargs, attr_result)
            logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        attr_type_mapping = {}
        for item in attr_result["data"]:
            attr_type_transformer = None
            if item["bk_property_type"] == "bool":
                attr_type_transformer = bool
            elif item["bk_property_type"] == "int":
                attr_type_transformer = int
            if attr_type_transformer:
                attr_type_mapping[item["bk_property_id"]] = attr_type_transformer

        for update_item in attr_list:
            # 过滤,去除用户没有填的字段
            update_params = {key: value for key, value in update_item.items() if value}
            # 对字段类型进行转换
            transform_success = True
            for attr, value in update_params.items():
                if attr in attr_type_mapping:
                    try:
                        update_params[attr] = attr_type_mapping[attr](value)
                    except Exception as e:
                        transform_success = False
                        message = _(
                            f"模块属性更新失败: 插件配置的属性不合法, 请修复后重试. item: {update_item}, "
                            f"转换属性: {attr}为{attr_type_mapping[attr]}类型时出错, 错误内容: {e}"
                        )
                        logger.error(message)
                        failed_update.append(message)
                        break
            if not transform_success:
                continue

            if "bk_set_name" not in update_params:
                message = _(f"集群属性更新失败: item: {update_item}, 目前Set名称未填写")
                logger.error(message)
                failed_update.append(message)
                continue
            bk_set_name = update_params["bk_set_name"]
            if "bk_new_set_name" in update_params:
                update_params["bk_set_name"] = update_params["bk_new_set_name"]
                del update_params["bk_new_set_name"]

            # 检查set name是否存在
            if not bk_set_name:
                message = _(f"集群属性更新失败: set 属性更新失败, set name有空值, item={update_item} | execute")
                self.logger.info(message)
                continue
            # 根据set name查询set  id
            kwargs = {
                "bk_biz_id": biz_cc_id,
                "fields": ["bk_set_id", "bk_set_name"],
                "condition": {"bk_set_name": bk_set_name},
            }
            search_result = client.api.search_set(
                kwargs,
                path_params={"bk_supplier_account": supplier_account, "bk_biz_id": biz_cc_id},
                headers={"X-Bk-Tenant-Id": tenant_id},
            )
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
            update_result = client.api.update_set(
                kwargs,
                path_params={"bk_biz_id": biz_cc_id, "bk_set_id": bk_set_id},
                headers={"X-Bk-Tenant-Id": tenant_id},
            )
            if update_result["result"]:
                self.logger.info("set 属性更新成功, item={}, data={}".format(update_item, kwargs))
                success_update.append(update_item)
            else:
                message = "set 属性更新失败, item={}, data={}, message: {}".format(
                    update_item, kwargs, update_result["message"]
                )
                self.logger.info(message)
                failed_update.append(message)

        data.set_outputs("set_update_success", success_update)
        data.set_outputs("set_update_failed", failed_update)
        # 如果没有更新失败的行
        if not failed_update:
            return True
        data.set_outputs("ex_data", failed_update)
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
    desc = _(
        "1. 填参方式支持手动填写和结合模板生成（单行自动扩展）\n"
        "2. 使用单行自动扩展模式时，每一行支持填写多个已自定义分隔符或是英文逗号分隔的数据，"
        '插件后台会自动将其扩展成多行，如 "1,2,3,4" 会被扩展成四行：1 2 3 4\n'
        "3. 结合模板生成（单行自动扩展）当有一列有多条数据时，其他列要么也有相等个数的数据，要么只有一条数据"
    )
