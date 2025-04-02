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
from typing import List

from django.utils.translation import gettext_lazy as _
from pipeline.core.data.var import LazyVariable

from api.utils.request import batch_request
from gcloud.conf import settings
from gcloud.constants import Type
from gcloud.exceptions import ApiRequestError
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.variables.base import FieldExplain, SelfExplainVariable
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("root")


def get_set_property(tenant_id, operator):
    """
    @summary: 获取集群所有的属性
    @return:
    """
    client = get_client_by_username(operator, stage=settings.BK_APIGW_STAGE_NAME)
    kwargs = {"bk_obj_id": "set"}
    cc_result = client.api.search_object_attribute(
        kwargs,
        headers={"X-Bk-Tenant-Id": tenant_id},
    )
    if not cc_result["result"]:
        message = handle_api_error("cc", "search_object_attribute", kwargs, cc_result)
        logger.error(message)
        raise ApiRequestError(message)
    obj_property = ["bk_set_id"]
    for item in cc_result["data"]:
        obj_property.append(item["bk_property_id"])
    return obj_property


def cc_execute_dynamic_group(tenant_id, operator, bk_biz_id, bk_group_id, set_field):
    """
    通过集群ID和模块ID查询对应的名字
    :param tenant_id: 租户ID
    :param operator: 操作者
    :param bk_biz_id: 业务ID
    :param bk_group_id: 动态分组id
    :return:
    """
    client = get_client_by_username(operator, stage=settings.BK_APIGW_STAGE_NAME)
    set_data_dir = {}
    kwargs = {"bk_biz_id": bk_biz_id, "id": bk_group_id, "fields": set_field}
    group_info = batch_request(
        client.api.execute_dynamic_group,
        kwargs,
        limit=200,
        path_params={"bk_biz_id": bk_biz_id},
        headers={"X-Bk-Tenant-Id": tenant_id},
    )
    for _field in set_field:
        set_data_dir[_field] = []
    for set_data in group_info:
        for _field in set_field:
            set_data_dir[_field].append(str(set_data.get(_field, "")))
    for _field in set_field:
        flat_field_name = "flat__{}".format(_field)
        set_data_dir[flat_field_name] = ",".join(set_data_dir[_field])
    return set_data_dir


class SetGroupInfo(object):
    """
    设置集群和模块的信息
    """

    def __init__(self, data, set_field):
        for _field in set_field:
            flat_field_name = "flat__{}".format(_field)
            setattr(self, _field, data[_field])
            setattr(self, "flat__{}".format(_field), data[flat_field_name])
        self._pipeline_var_str_value = "set_field_data: {}".format(data)

    def __repr__(self):
        return self._pipeline_var_str_value


class VarSetGroupSelector(LazyVariable, SelfExplainVariable):
    code = "set_group_selector"
    name = _("集群分组选择器")
    type = "dynamic"
    tag = "var_set_group_selector.set_group_selector"
    form = "%svariables/cmdb/var_set_group_selector.js" % settings.STATIC_URL
    desc = _(
        "用于获取集群类型的动态分组的集群信息，输出字典，键为集群的属性名称，值为集群的属性值"
        "引用${KEY.{集群属性编码}}，返回类型为列表，列表值为集群属性值"
        "获取集群的名称列表: ${KEY.bk_set_name}"
        "获取集群环境类型: ${KEY.bk_set_env}"
        "引用${KEY.flat__{集群属性编码}}，返回类型为字符串，值为用英文逗号，连接的集群属性值"
        "获取集群的名称值: ${KEY.flat__bk_set_name}"
        "获取集群环境类型值: ${KEY.flat__bk_set_env}"
        "更多集群属性请查阅 CMDB 集群模型字段页面"
    )

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        fields = [FieldExplain(key="${KEY}", type=Type.STRING, description="选择的IP列表，以,分隔")]

        client = get_client_by_username(settings.SYSTEM_USE_API_ACCOUNT, stage=settings.BK_APIGW_STAGE_NAME)
        params = {"bk_obj_id": "set"}
        resp = client.api.search_object_attribute(
            params,
            headers={"X-Bk-Tenant-Id": kwargs["tenant_id"]},
        )
        resp_data = []
        if not resp["result"]:
            logger.error("[_self_explain] %s search_object_attribute err: %s" % (cls.tag, resp["message"]))
        else:
            resp_data = resp["data"]

        for item in resp_data:
            fields.append(
                FieldExplain(
                    key="${KEY.%s}" % item["bk_property_id"],
                    type=Type.LIST,
                    description="集群属性(%s)列表" % item["bk_property_name"],
                )
            )
            fields.append(
                FieldExplain(
                    key="${KEY.flat__%s}" % item["bk_property_id"],
                    type=Type.STRING,
                    description="集群属性(%s)列表，以,分隔" % item["bk_property_name"],
                )
            )

        return fields

    def get_value(self):
        """
        获取该变量中对应属性值
        """
        if "executor" not in self.pipeline_data or "biz_cc_id" not in self.pipeline_data:
            raise Exception("ERROR: executor and biz_cc_id of pipeline is needed")
        operator = self.pipeline_data.get("executor", "")
        tenant_id = self.pipeline_data.get("tenant_id", "")
        bk_biz_id = int(self.pipeline_data.get("biz_cc_id", 0))
        bk_group_id = self.value
        set_field = get_set_property(tenant_id, operator)
        set_module_info = cc_execute_dynamic_group(tenant_id, operator, bk_biz_id, bk_group_id, set_field)

        return SetGroupInfo(set_module_info, set_field)
