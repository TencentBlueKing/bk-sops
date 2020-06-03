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
from enum import Enum
from functools import partial

from django.utils.translation import ugettext_lazy as _

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger('celery')
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
    """
    获取主机ID
    :param executor:
    :param bk_biz_id:
    :param ip_list:
    :return: [1, 2, 3] id列表
    """
    cc_kwargs = {
        'bk_biz_id': bk_biz_id,
        'bk_supplier_account': supplier_account,
        'ip': {
            'data': ip_list,
            'exact': 1,
            'flag': 'bk_host_innerip'
        },
        'condition': [
            {
                'bk_obj_id': 'host',
                'fields': ['bk_host_id', 'bk_host_innerip']
            }
        ],
    }

    client = get_client_by_user(executor)
    cc_result = client.cc.search_host(cc_kwargs)

    if not cc_result['result']:
        message = cc_handle_api_error('cc.search_host', cc_kwargs, cc_result)
        return {'result': False, 'message': message}

    # change bk_host_id to str to use str.join() function
    ip_to_id = {item['host']['bk_host_innerip']: str(item['host']['bk_host_id']) for item in cc_result['data']['info']}
    host_id_list = []
    invalid_ip_list = []
    for ip in ip_list:
        if ip in ip_to_id:
            host_id_list.append(ip_to_id[ip])
        else:
            invalid_ip_list.append(ip)

    if invalid_ip_list:
        result = {
            'result': False,
            'message': _("查询配置平台(CMDB)接口cc.search_host表明，存在不属于当前业务的IP: {ip}").format(
                ip=','.join(invalid_ip_list)
            )
        }
        return result
    return {'result': True, 'data': host_id_list}


def get_module_set_id(topo_data, module_id):
    """
    获取模块属于的集群ID
    :param topo_data:
    :param module_id:
    :return:
    """
    for item in topo_data:
        if item['bk_obj_id'] == "set" and item.get('child'):
            set_id = item['bk_inst_id']
            for mod in item['child']:
                if mod['bk_inst_id'] == module_id:
                    return set_id

        if item.get('child'):
            set_id = get_module_set_id(item['child'], module_id)
            if set_id:
                return set_id


def cc_format_prop_data(executor, obj_id, prop_id, language, supplier_account):
    ret = {
        "result": True,
        "data": {}
    }
    client = get_client_by_user(executor)
    if language:
        setattr(client, 'language', language)
    cc_kwargs = {
        "bk_obj_id": obj_id,
        "bk_supplier_account": supplier_account
    }

    cc_result = client.cc.search_object_attribute(cc_kwargs)
    if not cc_result['result']:
        message = cc_handle_api_error('cc.search_object_attribute', cc_kwargs, cc_result)
        ret['result'] = False
        ret['message'] = message
        return ret

    for prop in cc_result['data']:
        if prop['bk_property_id'] == prop_id:
            for item in prop['option']:
                ret['data'][item['name'].strip()] = item['id']
            else:
                break
    return ret


def cc_format_tree_mode_id(front_id_list):
    if front_id_list is None:
        return []
    return [int(str(x).split('_')[1]) if len(str(x).split('_')) == 2 else int(x) for x in front_id_list]


def cc_get_name_id_from_combine_value(combine_value):
    """
    组合value中获取id
    :param combine_value: name_id
    :return name -> str, id -> int
        错误返回 None, None
    """
    name_id_combine = str(combine_value).split("_")
    if len(name_id_combine) != 2:
        return None, None
    try:
        return name_id_combine[0], int(name_id_combine[1])
    except KeyError as error:
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


def cc_batch_validated_business_level(executor, supplier_account, bk_obj_type, path_list):
    """
    业务层级校验
    :param executor:
    :param supplier_account:
    :param bk_obj_type: 校验层级类型, enum
    :param path_list: 路径列表
        - example: [[a, b], [a, c]]
    :return:
        - 执行成功：{'result': True, 'message': 'success'}
        - 执行失败：{'result': False, 'message': '错误信息'}
    """

    if bk_obj_type.name not in BkObjType.__members__:
        return {"result": False, "message": _("该层级类型不存在：{}").format(bk_obj_type)}

    client = get_client_by_user(executor)
    kwargs = {"bk_supplier_account": supplier_account}
    # 获取主线模型业务拓扑
    get_mainline_object_topo_return = client.cc.get_mainline_object_topo(kwargs)
    if not get_mainline_object_topo_return["result"]:
        message = cc_handle_api_error("cc.get_mainline_object_topo", kwargs, get_mainline_object_topo_return)
        return {"result": False, "message": message}
    mainline = get_mainline_object_topo_return["data"]
    obj_depth = len(mainline) - bk_obj_type.value
    for path in path_list:
        if len(path) == obj_depth:
            continue
        return {"result": False, "message": _("输入文本路径[{}]与业务拓扑层级不匹配").format(">".join(path))}
    return {"result": True, "message": "success"}


def cc_list_select_node_inst_id(executor, biz_cc_id, supplier_account, bk_obj_type, path_text):
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
    cc_batch_validated_business_level_return = cc_batch_validated_business_level(
        executor, supplier_account, bk_obj_type, path_list
    )
    if not cc_batch_validated_business_level_return["result"]:
        return {"result": False, "message": cc_batch_validated_business_level_return["message"]}

    # 获取选中节点bk_inst_id列表
    cc_list_match_node_inst_id_return = cc_list_match_node_inst_id(
        executor, biz_cc_id, supplier_account, path_list
    )
    if not cc_list_match_node_inst_id_return["result"]:
        return {"result": False, "message": cc_list_match_node_inst_id_return["message"]}
    return {"result": True, "data": cc_list_match_node_inst_id_return["data"]}
