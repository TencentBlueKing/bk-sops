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
import re

from django.utils.translation import ugettext_lazy as _

from api.utils.request import batch_request
from gcloud.conf import settings
from gcloud.exceptions import ApiRequestError
from gcloud.utils import cmdb
from gcloud.utils.ip import format_sundry_ip
from gcloud.utils.handlers import handle_api_error
from .constants import NO_ERROR, ERROR_CODES
from ..components.collections.sites.open.cc.base import cc_parse_path_text
from ..components.utils.sites.open.utils import cc_get_ips_info_by_str

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
DEFAULT_BK_CLOUD_ID = "-1"


class IPPickerDataGenerator:
    # IP选择器根据手动输入内容生成对应所需数据，方便后面进行过滤和处理
    def __init__(self, input_type, raw_data, request_kwargs, gen_kwargs):
        """
        :params input_type: 手动输入类型，值为ip(静态IP)/topo(动态IP)/group(动态分组)
        :params raw_data: 手动输入数据字符串
        :params request_kwargs: 包括请求接口所需要的参数信息, 如username,bk_biz_id,bk_supplier_account
        :params gen_kwargs: 包括信息匹配筛选所需要的信息，如biz_topo_tree
        """
        self.input_type = input_type
        self.raw_data = raw_data.strip()
        self.username = request_kwargs.pop("username")
        self.request_kwargs = request_kwargs
        self.gen_kwargs = gen_kwargs

    def generate(self):
        func = getattr(self, f"generate_{self.input_type}_data", None)
        if func is None:
            return {
                "result": False,
                "code": ERROR_CODES.PARAMETERS_ERROR,
                "data": [],
                "message": "input_type should be ip, topo or group.",
            }
        return func()

    def generate_group_data(self):
        """根据字符串生成动态分组数据"""
        client = get_client_by_user(self.username)
        group_names = set(re.split("[,\n]", self.raw_data))
        result = batch_request(client.cc.search_dynamic_group, self.request_kwargs, limit=200)
        dynamic_groups = []
        for dynamic_group in result:
            if dynamic_group["bk_obj_id"] == "host" and dynamic_group["name"] in group_names:
                dynamic_groups.append({"id": dynamic_group["id"], "name": dynamic_group["name"]})

        return {"result": True, "data": dynamic_groups, "message": ""}

    def generate_ip_data(self):
        """根据字符串生成ip数据"""
        result = cc_get_ips_info_by_str(self.username, self.request_kwargs["bk_biz_id"], self.raw_data)
        if result["invalid_ip"]:
            return {"result": False, "data": [], "message": f"ips: {result['invalid_ip']} invalid."}
        ips = [
            {
                "bk_host_innerip": ip["InnerIP"],
                "bk_host_id": ip["HostID"],
                "bk_cloud_id": ip["Source"],
                "cloud": [{"id": str(ip["Source"])}],
            }
            for ip in result["ip_result"]
        ]
        return {"result": True, "data": ips, "message": ""}

    def generate_topo_data(self):
        """根据字符串生成topo数据"""
        path_list = cc_parse_path_text(self.raw_data.replace(",", "\n"))
        processed_path_list = self._remove_included_topo_path(path_list)
        biz_topo_tree = self.gen_kwargs["biz_topo_tree"]
        topo_info = {}
        self._build_topo_info(biz_topo_tree, topo_info)
        generated_topo = []
        for path in processed_path_list:
            cur_info = {"child": topo_info}
            for inst_name in path:
                cur_info = cur_info.get("child", {}).get(inst_name)
                if cur_info is None:
                    raise ApiRequestError(f"path: {'>'.join(path)} not found in topo_tree")
            generated_topo.append({"bk_obj_id": cur_info["bk_obj_id"], "bk_inst_id": cur_info["bk_inst_id"]})
        return {"result": True, "data": generated_topo, "message": ""}

    @staticmethod
    def _remove_included_topo_path(path_list):
        """
        去除包含关系的拓扑路径，只保持最高层级结构
        :prams path_list: 拓扑层级列表
        :type path_list: List[List]
        :return 包含关系去除后的拓扑层级列表
        :rtype List[List]

        e.g.
        1. 不存在包含关系：[[1,2,3], [4,5]] -> [[1,2,3], [4,5]]
        2. 存在包含关系：[[1,2,3], [1,2], [4,5]] -> [[1,2], [4,5]]
        """
        processed_path_list = []
        sorted_path_list = sorted(path_list, key=lambda x: len(x))
        path_record = {}
        for topo in sorted_path_list:
            if any([obj in path_record.get(level, set()) for level, obj in enumerate(topo)]):
                continue
            path_record.setdefault(len(topo) - 1, set()).add(topo[-1])
            processed_path_list.append(topo)
        return processed_path_list

    def _build_topo_info(self, topo_tree, topo_info):
        # 重新提取拓扑树结构，将inst_name作为key，方便索引
        topo_info[topo_tree["bk_inst_name"]] = {
            "bk_inst_id": topo_tree["bk_inst_id"],
            "bk_inst_name": topo_tree["bk_inst_name"],
            "bk_obj_id": topo_tree["bk_obj_id"],
        }
        if "child" in topo_tree:
            topo_child = {}
            for topo_node in topo_tree["child"]:
                self._build_topo_info(topo_node, topo_child)
            topo_info[topo_tree["bk_inst_name"]]["child"] = topo_child


def get_ip_picker_result(username, bk_biz_id, bk_supplier_account, kwargs):
    """
    @summary：根据前端表单数据获取合法的IP
    @param username:
    @param bk_biz_id:
    @param bk_supplier_account:
    @param kwargs:
    @return:
    """
    topo_result = get_cmdb_topo_tree(username, bk_biz_id, bk_supplier_account)
    if not topo_result["result"]:
        return topo_result
    biz_topo_tree = topo_result["data"][0]

    host_info = cmdb.get_business_host_topo(
        username,
        bk_biz_id,
        bk_supplier_account,
        ["bk_host_id", "bk_host_innerip", "bk_host_outerip", "bk_host_name", "bk_cloud_id"],
    )

    logger.info(
        "[get_ip_picker_result(biz_id: {bk_biz_id})] kwargs: {kwargs} cmdb.get_business_host_topo "
        "return: {host_info}".format(
            # noqa
            bk_biz_id=bk_biz_id,
            kwargs=kwargs,
            host_info=host_info,
        )
    )

    if not host_info:
        return {
            "result": False,
            "code": ERROR_CODES.PARAMETERS_ERROR,
            "data": [],
            "message": "get_business_host_topo return empty",
        }

    # IP选择器
    selector = kwargs["selectors"][0]

    # 如果是手动输入，则先按照值构造对应数据后替换到kwargs中
    if selector == "manual":
        input_value = kwargs["manual_input"]["value"]
        input_type = kwargs["manual_input"]["type"]

        gen_kwargs = {"biz_topo_tree": biz_topo_tree}
        request_kwargs = {"username": username, "bk_biz_id": bk_biz_id, "bk_supplier_account": bk_supplier_account}
        gen_result = IPPickerDataGenerator(input_type, input_value, request_kwargs, gen_kwargs).generate()

        if not gen_result["result"]:
            logger.error(
                f"[get_ip_picker_result(biz_id: {bk_biz_id})] kwargs: {kwargs} manual generate data error: {gen_result}"
            )
            raise ApiRequestError(gen_result["message"])
        kwargs[input_type] = gen_result["data"]
        selector = input_type

    if selector == "ip":
        ip_list = [
            "{cloud}:{ip}".format(cloud=get_bk_cloud_id_for_host(host, "cloud"), ip=host["bk_host_innerip"])
            for host in kwargs["ip"]
        ]
    else:
        ip_list = []
    data = []
    host_modules_ids = {}
    for host in host_info:
        host_modules_id = get_modules_id(host["module"])
        host_innerip = format_sundry_ip(host["host"].get("bk_host_innerip", ""))
        host_modules_ids[host_innerip] = host_modules_id
        if (
            selector == "topo"
            or selector == "group"
            or "{cloud}:{ip}".format(cloud=host["host"].get("bk_cloud_id", DEFAULT_BK_CLOUD_ID), ip=host_innerip)
            in ip_list
        ):
            data.append(
                {
                    "bk_host_id": host["host"]["bk_host_id"],
                    "bk_host_innerip": host_innerip,
                    "bk_host_outerip": host["host"].get("bk_host_outerip", ""),
                    "bk_host_name": host["host"].get("bk_host_name", ""),
                    "bk_cloud_id": host["host"].get("bk_cloud_id", DEFAULT_BK_CLOUD_ID),
                    "host_modules_id": host_modules_id,
                }
            )

    logger.info("[get_ip_picker_result] filter data collect: {data}".format(data=data))

    # 先把不在用户选择拓扑中的主机过滤掉
    if selector == "topo":
        user_select_topo_host = {}
        topo_filter = [[{"field": t["bk_obj_id"], "value": [t["bk_inst_id"]]}] for t in kwargs["topo"]]
        # 这里需要单独对每个 filter 进行过滤，因为 filter_hosts 过滤的是同时满足所有条件的主机
        for tf in topo_filter:
            user_select_topo_host.update(
                {host["bk_host_id"]: host for host in filter_hosts(tf, biz_topo_tree, data, "bk_inst_id")}
            )
        data = user_select_topo_host.values()

        logger.info("[get_ip_picker_result] data topo filter: {data}".format(data=data))

    # 动态分组得到的主机ip
    if selector == "group":
        dynamic_group_ids = [dynamic_group["id"] for dynamic_group in kwargs["group"]]
        dynamic_groups_host = {}
        for dynamic_group_id in dynamic_group_ids:
            success, result = cmdb.get_dynamic_group_host_list(
                username, bk_biz_id, bk_supplier_account, dynamic_group_id, host_modules_ids
            )
            if not success:
                return {
                    "result": False,
                    "code": result["code"],
                    "data": [],
                    "message": result["message"],
                }
            dynamic_groups_host.update({host["bk_host_id"]: host for host in result["data"]})
        data = dynamic_groups_host.values()

        logger.info("[get_ip_picker_result] data from dynamic group: {data}".format(data=data))

    # 筛选条件
    filters = kwargs["filters"]
    if filters:
        data = filter_hosts(filters, biz_topo_tree, data, "bk_inst_name")

        logger.info("[get_ip_picker_result] data condition filter: {data}".format(data=data))

    # 过滤条件
    excludes = kwargs["excludes"]
    if excludes:
        # 先把 data 中符合全部排除条件的 hosts 找出来，然后筛除
        exclude_hosts = filter_hosts(excludes, biz_topo_tree, data, "bk_inst_name")
        exclude_host_ip_list = [host["bk_host_innerip"] for host in exclude_hosts]
        new_data = [host for host in data if host["bk_host_innerip"] not in exclude_host_ip_list]
        data = new_data

        logger.info("[get_ip_picker_result] data condition excludes: {data}".format(data=data))

    result = {"result": True, "code": NO_ERROR, "data": data, "message": ""}
    return result


def filter_hosts(filters, biz_topo_tree, hosts, comp_key):
    """筛选出同时满足所有过滤条件的主机

    :param filters: 过滤条件
    :type filters: list
    :param biz_topo_tree: 业务拓扑
    :type biz_topo_tree: dict
    :param hosts: 筛选主机列表
    :type hosts: list
    :param comp_key: 过滤条件值在业务拓扑 biz_topo_tree 中所属的字段
    :type comp_key: str
    :return: 在 hosts 上筛选后的主机列表
    :rtype: list
    """
    filters_dct = format_condition_dict(filters)
    filter_host = set(filters_dct.pop("host", []))

    if filters_dct:
        # 把拓扑筛选条件转换成 modules 筛选条件
        filter_modules = get_modules_by_condition(biz_topo_tree, filters_dct, comp_key)
        filter_modules_id = get_modules_id(filter_modules)
        data = [host for host in hosts if set(host["host_modules_id"]) & set(filter_modules_id)]
    else:
        # 如果没有拓扑筛选条件，则不进行拓扑筛选操作，直接在 hosts 上再次进行 host ip 过滤
        data = hosts

    if filter_host:
        data = [host for host in data if host["bk_host_innerip"] in filter_host]
    return data


def format_condition_dict(conditons):
    """
    @summary: 将 field 相同的聚合成字典中的一条记录
    @param conditons:
    @return:
    """
    con_dct = {}
    for con in conditons:
        con_dct.setdefault(con["field"], [])
        con_dct[con["field"]] += format_condition_value(con["value"])
    return con_dct


def format_condition_value(conditions):
    """
    @summary:
        ['111', '222'] -> ['111', '222']
        ['111', '222\n333'] -> ['111', '222', '333']
        ['111', '222\\n333'] -> ['111', '222', '333']
        ['', '222\n', ' 333  '] -> ['222', '333']
        [111, 222, 333] -> [111, 222, 333]
    @param conditions:
    @return:
    """
    formatted = []
    for val in conditions:
        if isinstance(val, str):
            formatted += [item.strip() for item in re.split(r"\n|\\n", val.strip()) if item.strip()]
        else:
            formatted.append(val)
    return list(set(formatted))


def get_modules_of_bk_obj(bk_obj):
    """获取配置平台某个节点下的所有叶子(模块)节点

    :param bk_obj: cmdb 拓扑实例对象
    :type bk_obj: dict
    {
        "host_count": 0,
        "default": 0,
        "bk_obj_name": "business",
        "bk_obj_id": "biz",
        "service_instance_count": 0,
        "child": [
            {
                "default": 1,
                "bk_obj_id": "set",
                "bk_obj_name": "集群",
                "bk_inst_id": 2,
                "bk_inst_name": "idle pool",
                "child": [
                    {
                        "default": 1,
                        "bk_obj_id": "module",
                        "bk_obj_name": "模块",
                        "bk_inst_id": 3,
                        "bk_inst_name": "idle host"
                    },
                    ...
                ]
            },
            ...
        ]
    }
    :return: [
        {
            "host_count": 0,
            "default": 0,
            "bk_obj_name": "module1",
            "bk_obj_id": "module",
            "bk_inst_id": 3,
            "bk_inst_name": "idle host"
        },
        ...
    ]
    :rtype: list
    """
    modules = []
    if bk_obj["bk_obj_id"] == "module":
        modules.append(bk_obj)
    for child in bk_obj.get("child", []):
        modules += get_modules_of_bk_obj(child)
    return modules


def get_modules_id(modules):
    """将模块列表转换成 id 格式

    :param modules: 模块列表
    :type modules: list
    [
        {
            "host_count": 0,
            "default": 0,
            "bk_obj_name": "module1",
            "bk_obj_id": "module",
            "bk_inst_id": 3,
            "bk_inst_name": "idle host"
        },
        ...
    ]
    :return: [3, ...]
    :rtype: list
    """

    return [mod.get("bk_module_id") or mod.get("bk_inst_id") for mod in modules]


def get_modules_by_condition(bk_obj, condition, comp_key, has_filter_hit=False):
    """
    @summary: 获取拓扑树中满足条件的所有叶子(模块)节点
    @param bk_obj:
    @param condition:
    @return:
    """
    modules = []
    if bk_obj["bk_obj_id"] == "module":
        path_filter_match = "module" not in condition and has_filter_hit
        module_filter_match = bk_obj[comp_key] in condition.get("module", [])
        if path_filter_match or module_filter_match:
            modules.append(bk_obj)
    else:
        continue_dive = bk_obj["bk_obj_id"] not in condition
        current_filter_hit = bk_obj[comp_key] in condition.get(bk_obj["bk_obj_id"], [])
        if continue_dive or current_filter_hit:
            for child in bk_obj.get("child", []):
                modules += get_modules_by_condition(child, condition, comp_key, has_filter_hit or current_filter_hit)
    return modules


def get_objects_of_topo_tree(bk_obj, obj_dct):
    """获取满足obj_dict条件中的所有节点

    :param bk_obj: cmdb 拓扑对象
    :type bk_obj: dict
    {
        "host_count": 0,
        "default": 0,
        "bk_obj_name": "business",
        "bk_obj_id": "biz",
        "service_instance_count": 0,
        "child": [
            {
                "default": 1,
                "bk_obj_id": "set",
                "bk_obj_name": "集群",
                "bk_inst_id": 2,
                "bk_inst_name": "idle pool",
                "child": [
                    {
                        "default": 1,
                        "bk_obj_id": "module",
                        "bk_obj_name": "模块",
                        "bk_inst_id": 3,
                        "bk_inst_name": "idle host"
                    },
                    ...
                ]
            },
            ...
        ]
    }
    :param obj_dct: 拓扑节点限制
    :type obj_dct: dict
    {
        "biz": [1, 2, 3],
        "set": [4, 5, 6],
        ...
    }
    :return:
    [
        {
            "host_count": 0,
            "default": 0,
            "bk_obj_name": "business",
            "bk_obj_id": "biz",
            "service_instance_count": 0,
            "child": [
                ...
            ]
        },
        ...
    ]
    :rtype: list
    """
    bk_objects = []
    if bk_obj["bk_inst_id"] in obj_dct.get(bk_obj["bk_obj_id"], []):
        bk_objects.append(bk_obj)
    else:
        for child in bk_obj.get("child", []):
            bk_objects += get_objects_of_topo_tree(child, obj_dct)
    return bk_objects


def get_cmdb_topo_tree(username, bk_biz_id, bk_supplier_account):
    """从 CMDB API 获取业务完整拓扑树，包括空闲机池

    :param username: 请求 API 使用的用户名
    :type username: string
    :param bk_biz_id: 业务 CC ID
    :type bk_biz_id: int
    :param bk_supplier_account: 开发商账号
    :type bk_supplier_account: int
    :return:
    {
        "result": True or False,
        "code": error code,
        "data": [
            {
                "host_count": 0,
                "default": 0,
                "bk_obj_name": "business",
                "bk_obj_id": "biz",
                "service_instance_count": 0,
                "child": [
                    {
                        "default": 1,
                        "bk_obj_id": "set",
                        "bk_obj_name": "集群",
                        "bk_inst_id": 2,
                        "bk_inst_name": "idle pool",
                        "child": [
                            {
                                "default": 1,
                                "bk_obj_id": "module",
                                "bk_obj_name": "模块",
                                "bk_inst_id": 3,
                                "bk_inst_name": "idle host"
                            },
                            ...
                        ]
                    },
                    ...
                ]
            }
        ]
    }
    :rtype: dict
    """
    client = get_client_by_user(username)
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "bk_supplier_account": bk_supplier_account,
    }
    topo_result = client.cc.search_biz_inst_topo(kwargs)
    if not topo_result["result"]:
        message = handle_api_error(_("配置平台(CMDB)"), "cc.search_biz_inst_topo", kwargs, topo_result)
        result = {"result": False, "code": ERROR_CODES.API_CMDB_ERROR, "message": message, "data": []}
        return result

    inter_result = client.cc.get_biz_internal_module(kwargs)
    if not inter_result["result"]:
        message = handle_api_error(_("配置平台(CMDB)"), "cc.get_biz_internal_module", kwargs, inter_result)
        result = {"result": False, "code": ERROR_CODES.API_CMDB_ERROR, "message": message, "data": []}
        return result

    inter_data = inter_result["data"]
    data = topo_result["data"]
    if "bk_set_id" in inter_data:
        default_set = {
            "default": 1,
            "bk_obj_id": "set",
            "bk_obj_name": _("集群"),
            "bk_inst_id": inter_data["bk_set_id"],
            "bk_inst_name": inter_data["bk_set_name"],
            "child": [],
        }
        if inter_data["module"]:
            default_set["child"] = [
                {
                    "default": 1,
                    "bk_obj_id": "module",
                    "bk_obj_name": _("模块"),
                    "bk_inst_id": mod["bk_module_id"],
                    "bk_inst_name": mod["bk_module_name"],
                }
                for mod in inter_data["module"]
            ]
        data[0]["child"].insert(0, default_set)
    return {"result": True, "code": NO_ERROR, "data": data, "messsage": ""}


def get_bk_cloud_id_for_host(host_info, cloud_key="cloud"):
    """从主机信息中获取 bk_cloud_id，cloud_key 不存在时返回默认值

    :param host_info: host 信息字典
    :type host_info: dict
    {
        {cloud_key}: [
            {
                "id": 0
            },
            ...
        ]
    }
    :param cloud_key: 云区域 ID 键, defaults to 'cloud'
    :type cloud_key: str, optional
    :return: 主机云区域 ID
    :rtype: int
    """

    if not host_info.get(cloud_key, []):
        return DEFAULT_BK_CLOUD_ID
    return host_info[cloud_key][0]["id"]
