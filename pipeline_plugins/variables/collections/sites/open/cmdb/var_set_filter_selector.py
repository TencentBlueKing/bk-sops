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
from functools import reduce
from typing import List

from django.utils.translation import gettext_lazy as _
from pipeline.core.data.var import LazyVariable

from gcloud.conf import settings
from gcloud.constants import Type
from gcloud.exceptions import ApiRequestError
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.variables.base import FieldExplain, SelfExplainVariable
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username

logger = logging.getLogger("root")


def cc_filter_set_variables(tenant_id, operator, bk_biz_id, bk_obj_id, bk_obj_value):
    """
    通过集群ID、过滤属性ID、过滤属性值，过滤集群
    :param tenant_id: 租户ID
    :param operator: 操作者
    :param bk_biz_id: 业务ID
    :param bk_obj_id: 过滤属性ID
    :param bk_obj_value: 过滤属性值
    :return:
    """
    client = get_client_by_username(operator, stage=settings.BK_APIGW_STAGE_NAME)
    obj_value_list = bk_obj_value.split(",")
    results = []
    # 多个过滤属性值时循环请求接口
    for obj_value in obj_value_list:
        kwargs = {
            "bk_biz_id": int(bk_biz_id),
            "condition": {bk_obj_id: obj_value},
        }

        result = client.api.search_set(
            kwargs,
            path_params={"bk_supplier_account": supplier_account_for_business(bk_biz_id), "bk_biz_id": bk_biz_id},
            headers={"X-Bk-Tenant-Id": tenant_id},
        )
        if not result["result"]:
            err_msg = _(
                "[cc_filter_set_variables] 调用 cc.search_set 接口获取集群失败, " "kwargs={kwargs}, result={result}"
            ).format(kwargs=kwargs, result=result)
            logger.error(err_msg)
            raise ApiRequestError(err_msg)
        results += result["data"]["info"]
    if not results:
        return [], set()
    bk_attributes = reduce(set.intersection, [set(result.keys()) for result in results])
    return results, bk_attributes


class SetInfo(object):
    """
    设置集群的信息
    """

    def __init__(self, data, attributes):
        self.bk_sets = data
        for attribute in attributes:
            for bk_set in data:
                if not hasattr(self, attribute):
                    setattr(self, attribute, [])
                getattr(self, attribute).append(bk_set[attribute])
            setattr(self, f"flat__{attribute}", ",".join(map(str, getattr(self, attribute))))
        self._pipeline_var_str_value = f"sets: {self.bk_sets}"

    def __repr__(self):
        return self._pipeline_var_str_value


class VarSetFilterSelector(LazyVariable, SelfExplainVariable):
    code = "set_filter_selector"
    name = _("集群选择器")
    type = "general"
    tag = "var_set_filter_selector.set_filter_selector"
    form = "%svariables/cmdb/var_set_filter_selector.js" % settings.STATIC_URL
    desc = _(
        "该变量返回对象类型，可通过${KEY.bk_sets}获得筛选的所有集群信息，对于所有集群都有的属性(如attr)，"
        "可以通过${KEY.attr}获得所有集群该属性的值列表，可以通过${KEY.flat__attr}获得所有集群该属性的值拼接结果字符串"
    )

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        fields = [
            FieldExplain(key="${KEY}", type=Type.OBJECT, description="选择的集群信息"),
        ]

        client = get_client_by_username(settings.SYSTEM_USE_API_ACCOUNT, stage=settings.BK_APIGW_STAGE_NAME)
        params = {"bk_obj_id": "set"}
        if "bk_biz_id" in kwargs:
            params["bk_biz_id"] = kwargs["bk_biz_id"]
        resp = client.api.search_object_attribute(params, headers={"X-Bk-Tenant-Id": kwargs["tenant_id"]})
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
        example:
            bk_sets: ${var.bk_sets}
            set_name: ${var.bk_set_name}
            set_id: ${var.bk_set_id}
        """
        tenant_id = self.pipeline_data.get("tenant_id", "")
        operator = self.pipeline_data.get("executor", "")
        bk_biz_id = int(self.pipeline_data.get("biz_cc_id", 0))
        bk_obj_id = self.value.get("bk_obj_id", "")
        bk_obj_value = self.value.get("bk_obj_value", "")

        set_infos, bk_attributes = cc_filter_set_variables(tenant_id, operator, bk_biz_id, bk_obj_id, bk_obj_value)
        return SetInfo(set_infos, bk_attributes)
