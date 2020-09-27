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

from gcloud.conf import settings
from django.utils.translation import ugettext_lazy as _

from gcloud.utils.cmdb import batch_request
from pipeline.core.data.var import LazyVariable

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def get_set_property(operator):
    """
    @summary: 获取集群所有的属性
    @return:
    """
    client = get_client_by_user(operator)
    kwargs = {"bk_obj_id": "set"}
    cc_result = client.cc.search_object_attribute(**kwargs)
    if not cc_result["result"]:
        return []
    obj_property = ["bk_set_id"]
    for item in cc_result["data"]:
        obj_property.append(item["bk_property_id"])
    return obj_property


def cc_execute_dynamic_group(operator, bk_biz_id, bk_group_id, set_field):
    """
    通过集群ID和模块ID查询对应的名字
    :param operator: 操作者
    :param bk_biz_id: 业务ID
    :param bk_group_id: 动态分组id
    :return:
    """
    client = get_client_by_user(operator)
    set_data_dir = {}
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "id": bk_group_id,
        "fields": set_field
    }
    group_info = batch_request(client.cc.execute_dynamic_group, kwargs, limit=200)
    for _field in set_field:
        set_data_dir[_field] = []
    for set_data in group_info:
        for _field in set_field:
            if set_data.get(_field) is not None:
                set_data_dir[_field].append(str(set_data[_field]))
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


class VarSetGroupSelector(LazyVariable):
    code = "set_group_selector"
    name = _("集群分组选择器")
    type = "general"
    tag = "var_set_group_selector.set_group_selector"
    form = "%svariables/cmdb/var_set_group_selector.js" % settings.STATIC_URL

    def get_value(self):
        """
        获取该变量中对应属性值
        """
        operator = self.pipeline_data.get("executor", "")
        bk_biz_id = int(self.pipeline_data.get("biz_cc_id", 0))
        bk_group_id = self.value
        set_field = get_set_property(operator)
        set_module_info = cc_execute_dynamic_group(operator, bk_biz_id, bk_group_id, set_field)

        return SetGroupInfo(set_module_info, set_field)
