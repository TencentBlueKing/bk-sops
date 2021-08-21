# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
from abc import ABCMeta
from enum import Enum
from functools import partial
from collections import Counter

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from pipeline.core.flow.io import StringItemSchema
from pipeline.core.flow.activity import Service

from gcloud.utils import cmdb
from gcloud.conf import settings
from gcloud.utils.ip import get_ip_by_regex
from gcloud.utils.handlers import handle_api_error


logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")

cc_handle_api_error = partial(handle_api_error, __group_name__)


class BkObjType(Enum):
    """
    模型层级类型对应的逆序深度，以host为起点，索引从0开始
    LAST_CUSTOM 从业务往下的最后一个自定义层级
    SET         集群
    MODULE      模块
    HOST        主机
    HOST(0) -> MODULE(1) -> SET(2) -> LAST_CUSTOM(3)
    """

    LAST_CUSTOM = 3
    SET = 2
    MODULE = 1
    HOST = 0


class SelectMethod(Enum):
    """
    选择父实例的方法
    TOPO    拓扑树选择节点
    TEXT    手动输入
    """

    TOPO = "topo"
    TEXT = "text"


class ModuleCreateMethod(Enum):
    """
    创建模块的方法
    TEMPLATE    按模板创建
    CATEGORY    直接创建（按服务分类创建）
    """

    TEMPLATE = "template"
    CATEGORY = "category"


def cc_get_host_id_by_innerip(executor, bk_biz_id, ip_list, supplier_account):
    """根据主机内网 IP 获取主机 ID

    :param executor: API 请求用户身份
    :type executor: string
    :param bk_biz_id: 业务 CC ID
    :type bk_biz_id: int
    :param ip_list: 主机内网 IP 列表
    :type ip_list: list
    :param supplier_account: 开发商账号
    :type supplier_account: int
    :return: 主机 id 列表
    :rtype: list
    ["1", "2", "3", ...]
    """

    host_list = cmdb.get_business_host(
        executor, bk_biz_id, supplier_account, ["bk_host_id", "bk_host_innerip"], ip_list,
    )

    if not host_list:
        return {"result": False, "message": "list_biz_hosts query failed, return empty list"}

    if len(host_list) > len(ip_list):
        # find repeat innerip host
        host_counter = Counter([host["bk_host_innerip"] for host in host_list])
        mutiple_innerip_hosts = [innerip for innerip, count in host_counter.items() if count > 1]

        return {
            "result": False,
            "message": "mutiple same innerip host found: {}".format(", ".join(mutiple_innerip_hosts)),
        }

    if len(host_list) < len(ip_list):
        return_innerip_set = {host["bk_host_innerip"] for host in host_list}
        absent_innerip = set(ip_list).difference(return_innerip_set)

        return {"result": False, "message": "ip not found in business: {}".format(", ".join(absent_innerip))}

    return {"result": True, "data": [str(host["bk_host_id"]) for host in host_list]}


def get_module_set_id(topo_data, module_id):
    """
    获取模块属于的集群ID
    :param topo_data:
    :param module_id:
    :return:
    """
    for item in topo_data:
        if item["bk_obj_id"] == "set" and item.get("child"):
            set_id = item["bk_inst_id"]
            for mod in item["child"]:
                if mod["bk_inst_id"] == module_id:
                    return set_id

        if item.get("child"):
            set_id = get_module_set_id(item["child"], module_id)
            if set_id:
                return set_id


def cc_format_prop_data(executor, obj_id, prop_id, language, supplier_account):
    ret = {"result": True, "data": {}}
    client = get_client_by_user(executor)
    if language:
        setattr(client, "language", language)
    cc_kwargs = {"bk_obj_id": obj_id, "bk_supplier_account": supplier_account}

    cc_result = client.cc.search_object_attribute(cc_kwargs)
    if not cc_result["result"]:
        message = cc_handle_api_error("cc.search_object_attribute", cc_kwargs, cc_result)
        ret["result"] = False
        ret["message"] = message
        return ret

    for prop in cc_result["data"]:
        if prop["bk_property_id"] == prop_id:
            for item in prop["option"]:
                ret["data"][item["name"].strip()] = item["id"]
            else:
                break
    return ret


def cc_format_tree_mode_id(front_id_list):
    if front_id_list is None:
        return []
    return [int(str(x).split("_")[1]) if len(str(x).split("_")) == 2 else int(x) for x in front_id_list]


def cc_get_name_id_from_combine_value(combine_value):
    """
    组合value中获取id
    :param combine_value: name_id
    :return name -> str, id -> int
        错误返回 None, None
    """
    try:
        value_name, _, value_id = str(combine_value).rpartition("_")
        return value_name, int(value_id)
    except Exception as e:
        logger.error("cc_get_name_id_from_combine_value error: {}".format(e))
        return None, None


def cc_parse_path_text(path_text):
    """
    将目标主机/模块/自定义层级的文本路径解析为列表形式，支持空格/空行容错解析
    :param path_text: 目标主机/模块/自定义层级的文本路径
    :return:路径列表，每个路径是一个节点列表
    example:
    a > b > c > s
       a>v>c
    a
    解析结果
    [
        [a, b, c, s],
        [a, v, c],
        [a]
    ]
    """
    text_path_list = path_text.split("\n")
    path_list = []
    for text_path in text_path_list:
        text_path = text_path.strip()
        path = []
        if len(text_path) == 0:
            continue
        for text_node in text_path.split(">"):
            text_node = text_node.strip()
            if len(text_path) == 0:
                continue
            path.append(text_node)
        path_list.append(path)
    return path_list


def cc_list_match_node_inst_id(executor, biz_cc_id, supplier_account, path_list):
    """
    路径匹配，对path_list中的所有路径与指定biz_cc_id的拓扑树匹配，返回匹配节点bk_inst_id
    :param executor:
    :param biz_cc_id:
    :param supplier_account:
    :param path_list: 路径列表，example: [[a, b], [a, c]]
    :return:
        True: list -匹配父节点的bk_inst_id
        False: message -错误信息

    业务拓扑树示例
    [
        {
            "bk_inst_id": 2,
            "bk_inst_name": "blueking",
            "bk_obj_id": "biz",
            "bk_obj_name": "business",
            "child": [
                {
                    "bk_inst_id": 3,
                    "bk_inst_name": "job",
                    "bk_obj_id": "set",
                    "bk_obj_name": "set",
                    "child": [
                        {
                            "bk_inst_id": 5,
                            "bk_inst_name": "job",
                            "bk_obj_id": "module",
                            "bk_obj_name": "module",
                            "child": []
                        },
                        {
                            ...
                        }
                    ]
                }
            ]
        }
    ]
    """
    client = get_client_by_user(executor)
    kwargs = {"bk_biz_id": biz_cc_id, "bk_supplier_account": supplier_account}
    search_biz_inst_topo_return = client.cc.search_biz_inst_topo(kwargs)
    if not search_biz_inst_topo_return["result"]:
        message = cc_handle_api_error("cc.search_biz_inst_topo", kwargs, search_biz_inst_topo_return)
        return {"result": False, "message": message}
    topo_tree = search_biz_inst_topo_return["data"]

    inst_id_list = []
    for path in path_list:
        index = 0
        topo_node_list = topo_tree
        while len(path) > index:
            match_node = None
            for topo_node in topo_node_list:
                if path[index] == topo_node["bk_inst_name"]:
                    match_node = topo_node
                    break
            if match_node:
                index = index + 1
                if index == len(path):
                    inst_id_list.append(match_node["bk_inst_id"])
                topo_node_list = match_node["child"]
            else:
                return {"result": False, "message": _("不存在该拓扑路径：{}").format(">".join(path))}
    return {"result": True, "data": inst_id_list}


def cc_list_select_node_inst_id(
    executor: str,
    biz_cc_id: int,
    supplier_account: str,
    bk_obj_type: BkObjType,
    path_text: str,
    auto_complete_biz_name: str = None,
):
    """
    获取选择节点的bk_inst_id
    :param executor:
    :param biz_cc_id:
    :param supplier_account:
    :param bk_obj_type: bk_obj_type: 校验层级类型, enum
    :param path_text: 目标主机/模块/自定义层级的文本路径
    :return:
        True: list -选择节点的bk_inst_id
        False: message -错误信息
    """
    # 文本路径解析
    path_list = cc_parse_path_text(path_text)

    # 对输入的文本路径进行业务层级校验
    if bk_obj_type.name not in BkObjType.__members__:
        return {"result": False, "message": _("该层级类型不存在：{}").format(bk_obj_type)}

    client = get_client_by_user(executor)
    kwargs = {"bk_supplier_account": supplier_account, "bk_biz_id": biz_cc_id}
    # 获取主线模型业务拓扑
    get_mainline_object_topo_return = client.cc.get_mainline_object_topo(kwargs)
    if not get_mainline_object_topo_return["result"]:
        message = cc_handle_api_error("cc.get_mainline_object_topo", kwargs, get_mainline_object_topo_return)
        return {"result": False, "message": message}

    clean_path_list = []
    mainline = get_mainline_object_topo_return["data"]
    obj_depth = len(mainline) - bk_obj_type.value
    for path in path_list:
        if len(path) == obj_depth:
            clean_path_list.append(path)
            continue
        elif (len(path) == obj_depth - 1) and auto_complete_biz_name:
            clean_path_list.append([auto_complete_biz_name, *path])
            continue

        return {"result": False, "message": _("输入文本路径[{}]与业务拓扑层级不匹配").format(">".join(path))}

    # 获取选中节点bk_inst_id列表
    cc_list_match_node_inst_id_return = cc_list_match_node_inst_id(
        executor, biz_cc_id, supplier_account, clean_path_list
    )
    if not cc_list_match_node_inst_id_return["result"]:
        return {"result": False, "message": cc_list_match_node_inst_id_return["message"]}
    return {"result": True, "data": cc_list_match_node_inst_id_return["data"]}


class BaseTransferHostToModuleService(Service, metaclass=ABCMeta):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("主机 IP"),
                key="cc_host_ip",
                type="string",
                schema=StringItemSchema(description=_("转移到故障机的主机内网 IP，多个用英文逗号 `,` 分隔")),
            ),
        ]

    def outputs_format(self):
        return []

    def exec_transfer_host_module(self, data, parent_data, transfer_cmd):
        executor = parent_data.get_one_of_inputs("executor")
        supplier_account = parent_data.get_one_of_inputs("biz_supplier_account")
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        # 查询主机id
        ip_list = get_ip_by_regex(data.get_one_of_inputs("cc_host_ip"))
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list, supplier_account)
        if not host_result["result"]:
            data.set_outputs("ex_data", host_result["message"])
            return False

        transfer_kwargs = {
            "bk_supplier_account": supplier_account,
            "bk_biz_id": biz_cc_id,
            "bk_host_id": [int(host_id) for host_id in host_result["data"]],
        }

        transfer_result = getattr(client.cc, transfer_cmd)(transfer_kwargs)

        if transfer_result["result"]:
            return True
        else:
            message = cc_handle_api_error("cc.{}".format(transfer_cmd), transfer_kwargs, transfer_result)
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False
