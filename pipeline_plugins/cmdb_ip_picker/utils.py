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
import re

import requests
from django.utils.translation import gettext_lazy as _

from packages.bkapi.bk_cmdb.shortcuts import get_client_by_username
from api.utils.request import batch_request
from gcloud.conf import settings
from gcloud.exceptions import ApiRequestError
from gcloud.utils import cmdb
from gcloud.utils.cmdb import get_dynamic_group_list
from gcloud.utils.handlers import handle_api_error
from gcloud.utils.ip import extract_ip_from_ip_str, format_sundry_ip

from ..components.collections.sites.open.cc.base import cc_parse_path_text
from ..components.utils.sites.open.utils import cc_get_ips_info_by_str, cc_get_ips_info_by_str_ipv6
from .constants import ERROR_CODES, NO_ERROR

logger = logging.getLogger("root")
DEFAULT_BK_CLOUD_ID = "-1"


class IPPickerDataGenerator:
    # IP选择器根据手动输入内容生成对应所需数据，方便后面进行过滤和处理
    def __init__(self, tenant_id, input_type, raw_data, request_kwargs, gen_kwargs, bk_biz_id: int):
        """
        :params tenant_id: 租户ID
        :params input_type: 手动输入类型，值为ip(静态IP)/topo(动态IP)/group(动态分组)
        :params raw_data: 手动输入数据字符串
        :params request_kwargs: 包括请求接口所需要的参数信息, 如username,bk_biz_id,bk_supplier_account
        :params gen_kwargs: 包括信息匹配筛选所需要的信息，如biz_topo_tree
        :params bk_biz_id: 业务ID
        """
        self.tenant_id = tenant_id
        self.input_type = input_type
        self.raw_data = raw_data.strip()
        self.username = request_kwargs.pop("username")
        self.request_kwargs = request_kwargs
        self.gen_kwargs = gen_kwargs
        self.bk_biz_id = bk_biz_id

    def generate(self):
        func = getattr(self, f"generate_{self.input_type}_data", None)
        if func is None:
            error_mapping = {
                "ip": _(f"IP[{self.raw_data}]在本业务下不存在 | generate"),
                "topo": _(f"拓扑路径[{self.raw_data}]在本业务下不存在 | generate"),
                "group": _(f"动态分组[{self.raw_data}]在本业务下不存在 | generate"),
            }
            message = error_mapping.get(self.input_type)
            logger.error(message)
            return {
                "result": False,
                "code": ERROR_CODES.PARAMETERS_ERROR,
                "data": [],
                "message": message,
            }
        return func()

    def generate_group_data(self):
        """根据字符串生成动态分组数据"""
        client = get_client_by_username(self.username, stage=settings.BK_APIGW_STAGE_NAME)
        group_names = set(re.split("[,\n]", self.raw_data))
        result = batch_request(
            client.api.search_dynamic_group,
            self.request_kwargs,
            path_params={"bk_biz_id": self.bk_biz_id},
            headers={"X-Bk-Tenant-Id": self.tenant_id},
            limit=200,
        )
        dynamic_groups = []
        for dynamic_group in result:
            if dynamic_group["bk_obj_id"] == "host" and dynamic_group["name"] in group_names:
                dynamic_groups.append({"id": dynamic_group["id"], "name": dynamic_group["name"]})

        return {"result": True, "data": dynamic_groups, "message": ""}

    def generate_ip_data(self):
        """根据字符串生成ip数据"""
        if settings.ENABLE_IPV6:
            result = cc_get_ips_info_by_str_ipv6(
                self.tenant_id, self.username, self.request_kwargs["bk_biz_id"], self.raw_data)
        else:
            result = cc_get_ips_info_by_str(
                self.tenant_id, self.username, self.request_kwargs["bk_biz_id"], self.raw_data)
        if result["invalid_ip"]:
            message = _(
                f"IP [{result['invalid_ip']}] 在本业务下不存在: 请检查配置, 修复后重新执行任务 | generate_ip_data"
            )
            logger.error(message)
            return {"result": False, "data": [], "message": message}
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


class IPPickerHandler:
    PROPERTY_FILTER_TYPES = ("set", "module", "host")

    def __init__(
        self, tenant_id, selector, username, bk_biz_id, bk_supplier_account, is_manual=False, filters=None,
            excludes=None
    ):
        self.tenant_id = tenant_id
        self.selector = selector
        self.username = username
        self.bk_biz_id = bk_biz_id
        self.bk_supplier_account = bk_supplier_account
        self.filters = format_condition_dict(filters or [])
        self.excludes = format_condition_dict(excludes or [])
        self.biz_topo_tree: dict = None
        self.host_info: list = None
        self.property_filters: dict = {}
        self.error = None

        # 数据准备
        for property_filter_type in self.PROPERTY_FILTER_TYPES:
            key = f"{property_filter_type}_property_filter"
            self.property_filters[key] = {"condition": "AND", "rules": []}

        # 获取业务下的topo树
        if self.selector == "topo" or is_manual or self.filters or self.excludes:
            topo_result = get_cmdb_topo_tree(username, bk_biz_id, bk_supplier_account)
            if not topo_result["result"]:
                self.error = topo_result
                return
            self.biz_topo_tree = topo_result["data"][0]

        # 预处理过滤筛选条件
        if self.filters:
            self._inject_condition_params("filter", self.filters)
        if self.excludes:
            self._inject_condition_params("exclude", self.excludes)

    def _inject_condition_params(self, condition_type: str, condition_data: dict):
        """
        根据过滤条件注入对应的主机过滤参数
        """
        operator = "in" if condition_type == "filter" else "not_in"
        hosts = condition_data.get("host", [])
        if hosts:
            # 这里需要区分ipv4和ipv6的查询条件
            if settings.ENABLE_IPV6:
                ip_str = ",".join(hosts)
                ipv6_list, ipv4_list, host_id_list, _, _ = extract_ip_from_ip_str(ip_str)
                condition_map = {"in": "OR", "not_in": "AND"}
                conditions = {"condition": condition_map.get(operator, "OR"), "rules": []}
                if ipv4_list:
                    # 添加ipv4主机的条件
                    conditions["rules"].append({"field": "bk_host_innerip", "operator": operator, "value": ipv4_list})
                if ipv6_list:
                    # 添加ipv6主机的构造条件
                    conditions["rules"].append(
                        {"field": "bk_host_innerip_v6", "operator": operator, "value": ipv6_list}
                    )
                if host_id_list:
                    # 添加host_id_list主机的构造条件
                    conditions["rules"].append({"field": "bk_host_id", "operator": operator, "value": host_id_list})
                self.property_filters["host_property_filter"]["rules"].append(conditions)
            else:
                self.property_filters["host_property_filter"]["rules"].append(
                    {"field": "bk_host_innerip", "operator": operator, "value": hosts}
                )
        if set(condition_data.keys()) - {"host"}:
            # 把拓扑筛选条件转换成 modules 筛选条件
            filter_modules = get_modules_by_condition(self.biz_topo_tree, condition_data, "bk_inst_name")
            filter_modules_ids = get_modules_id(filter_modules)
            self.property_filters["module_property_filter"]["rules"].append(
                {"field": "bk_module_id", "operator": operator, "value": filter_modules_ids}
            )

    def _inject_host_params(self, host_list):
        """
        根据主机数据注入主机过滤参数
        """
        input_host_ids = [host["bk_host_id"] for host in host_list]
        self.property_filters["host_property_filter"]["rules"].append(
            {"field": "bk_host_id", "operator": "in", "value": input_host_ids}
        )

    def _inject_topo_params(self, topo_list):
        """
        根据拓扑数据注入拓扑过滤参数
        """
        # 因为set_property_filter和module_property_filter的条件是与关系，所以这里统一转换成module来进行过滤
        topo_filter = [[{"field": topo["bk_obj_id"], "value": [topo["bk_inst_id"]]}] for topo in topo_list]
        module_ids = set()
        for tf in topo_filter:
            filters_dct = format_condition_dict(tf)
            filter_modules = get_modules_by_condition(self.biz_topo_tree, filters_dct, "bk_inst_id")
            filter_modules_ids = get_modules_id(filter_modules)
            module_ids.update(set(filter_modules_ids))
        if module_ids:
            self.property_filters["module_property_filter"]["rules"].append(
                {"field": "bk_module_id", "operator": "in", "value": list(module_ids)}
            )
        return module_ids

    def dispatch(self, params):
        handle_func = getattr(self, f"{self.selector}_picker_handler")
        return handle_func(params[self.selector])

    def ip_picker_handler(self, inputted_ips):
        """
        静态IP选择情况
        :params inputted_ips: ip主机信息列表, list
        """
        self._inject_host_params(inputted_ips)
        host_info_result = self.fetch_host_ip_with_property_filter()
        if not host_info_result["result"]:
            return host_info_result
        return {"result": True, "data": host_info_result["data"], "message": ""}

    def topo_picker_handler(self, inputted_topo):
        """
        topo选择情况
        :params inputted_topo: 拓扑结构信息列表, list
        """
        module_ids = self._inject_topo_params(inputted_topo)
        if not module_ids:
            logger.warning(f"[topo_picker_handler] no module_ids, inputted_topo: {inputted_topo}")
            return {"result": True, "data": [], "message": ""}
        host_info_result = self.fetch_host_ip_with_property_filter()
        if not host_info_result["result"]:
            return host_info_result
        return {"result": True, "data": host_info_result["data"], "message": ""}

    def group_picker_handler(self, inputted_group):
        """
        动态分组选择情况
        :params inputted_group: 动态分组信息列表, list
        """
        dynamic_group_ids = [dynamic_group["id"] for dynamic_group in inputted_group]
        try:
            existing_dynamic_groups = get_dynamic_group_list(self.tenant_id, self.username, self.bk_biz_id,
                                                             self.bk_supplier_account)
            existing_dynamic_group_ids = set([dynamic_group["id"] for dynamic_group in existing_dynamic_groups])
            dynamic_group_ids = set(dynamic_group_ids) & existing_dynamic_group_ids
        except Exception as e:
            # 如果获取动态分组失败，则不做过滤
            logger.info(f"[group_picker_handler]: get_dynamic_group_list error {e}")
        dynamic_groups_host = {}
        for dynamic_group_id in dynamic_group_ids:
            success, result = cmdb.get_dynamic_group_host_list(
                self.tenant_id, self.username, self.bk_biz_id, self.bk_supplier_account, dynamic_group_id
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
        data = self.format_host_info(data)

        # 如果带有过滤条件，则需要拉取主机后进行过滤
        if self.filters or self.excludes:
            host_info_result = self.fetch_host_ip_with_property_filter()
            if not host_info_result["result"]:
                return host_info_result
            match_host_id = set([host["bk_host_id"] for host in host_info_result["data"]])
            data = [host for host in data if host["bk_host_id"] in match_host_id]

        logger.info("[group_picker_handler] data from dynamic group: {data}".format(data=data))
        return {"result": True, "data": data, "message": ""}

    def fetch_host_ip_with_property_filter(self):
        """
        获取业务下过滤后的主机IP列表
        """
        for property_filter_type in self.PROPERTY_FILTER_TYPES:
            key = f"{property_filter_type}_property_filter"
            if not self.property_filters[key]["rules"]:
                self.property_filters.pop(key)

        fields = ["bk_host_id", "bk_host_innerip", "bk_host_outerip", "bk_host_name", "bk_cloud_id"]
        if settings.ENABLE_IPV6:
            fields.append("bk_host_innerip_v6")

        host_info = cmdb.get_business_host_topo(
            self.tenant_id,
            self.username,
            self.bk_biz_id,
            self.bk_supplier_account,
            fields,
            property_filters=self.property_filters,
        )
        logger.info("[fetch_host_info] cmdb.get_business_host_topo return: {host_info}".format(host_info=host_info))

        host_info = self.format_host_info([host["host"] for host in host_info])
        return {"result": True, "code": NO_ERROR, "data": host_info, "message": ""}

    @staticmethod
    def format_host_info(host_info: list):
        """对返回的主机数据进行一些自定义格式化调整"""
        formatted_host_info = []
        for host in host_info:
            ip = format_sundry_ip(host.get("bk_host_innerip", ""))
            # 如果ipv4地址为空并开启了ipv6,则尝试去拿ip_v6地址，否则默认使用该主机的ip_v4地址
            if not ip and settings.ENABLE_IPV6:
                ip = format_sundry_ip(host.get("bk_host_innerip_v6", ""))
            formatted_host_info.append({**host, "bk_host_innerip": ip})
        return formatted_host_info


def get_ip_picker_result(tenant_id, username, bk_biz_id, bk_supplier_account, kwargs):
    """
    @summary：根据前端表单数据获取合法的IP，IP选择器调用
    @param tenant_id: 租户ID
    @param username:
    @param bk_biz_id:
    @param bk_supplier_account:
    @param kwargs:
    @return:
    """
    # IP选择器
    selector = kwargs["selectors"][0]
    # 手动输入情况需要特殊处理
    is_manual = selector == "manual"
    selector = kwargs["manual_input"]["type"] if is_manual else selector

    # 筛选条件
    filters = kwargs["filters"]
    # 过滤条件
    excludes = kwargs["excludes"]

    ip_picker_handler = IPPickerHandler(
        selector, username, bk_biz_id, bk_supplier_account, is_manual, filters, excludes
    )
    if ip_picker_handler.error:
        logger.error(f"[get_ip_picker_result] error: {ip_picker_handler.error}")
        return ip_picker_handler.error

    # 如果是手动输入，则先按照值构造对应数据后替换到kwargs中
    if is_manual:
        input_value = kwargs["manual_input"]["value"]
        input_type = kwargs["manual_input"]["type"]

        gen_kwargs = {"biz_topo_tree": ip_picker_handler.biz_topo_tree}
        request_kwargs = {"username": username, "bk_biz_id": bk_biz_id, "bk_supplier_account": bk_supplier_account}
        gen_result = IPPickerDataGenerator(
            tenant_id, input_type, input_value, request_kwargs, gen_kwargs, bk_biz_id=bk_biz_id).generate()

        if not gen_result["result"]:
            logger.error(
                f"[get_ip_picker_result(biz_id: {bk_biz_id})] kwargs: {kwargs} manual generate data error: {gen_result}"
            )
            return gen_result
        kwargs[input_type] = gen_result["data"]

    host_data_result = ip_picker_handler.dispatch(kwargs)
    return host_data_result


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
        ['', '222\n', ' 333  '] -> ['', '222', '333']
        [111, 222, 333] -> [111, 222, 333]
    @param conditions:
    @return:
    """
    formatted = []
    for val in conditions:
        if isinstance(val, str):
            formatted += [item.strip() for item in re.split(r"\n|\\n", val.strip())]
        else:
            formatted.append(val)
    return sorted(set(formatted), key=formatted.index)


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


def get_cmdb_topo_tree(tenant_id, username, bk_biz_id, bk_supplier_account):
    """从 CMDB API 获取业务完整拓扑树，包括空闲机池

    :param tenant_id: 租户 ID
    :type tenant_id: string
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
    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    kwargs = {
        "bk_biz_id": bk_biz_id,
        "bk_supplier_account": bk_supplier_account,
    }
    headers = {"X-Bk-Tenant-Id": tenant_id}
    topo_result = client.api.search_biz_inst_topo(
        kwargs,
        path_params={"bk_biz_id": bk_biz_id},
        headers=headers,
    )
    if not topo_result["result"]:
        message = handle_api_error(_("配置平台(CMDB)"), "cc.search_biz_inst_topo", kwargs, topo_result)
        result = {"result": False, "code": ERROR_CODES.API_CMDB_ERROR, "message": message, "data": []}
        return result

    inter_result = client.api.get_biz_internal_module(
        kwargs,
        path_params={"bk_supplier_account": bk_supplier_account, "bk_biz_id": bk_biz_id},
        headers=headers,
    )
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
    :param cloud_key: 管控区域 ID 键, defaults to 'cloud'
    :type cloud_key: str, optional
    :return: 主机管控区域 ID
    :rtype: int
    """

    if not host_info.get(cloud_key, []):
        return DEFAULT_BK_CLOUD_ID
    return host_info[cloud_key][0]["id"]


def get_gse_agent_status_ipv6(bk_agent_id_list):
    if not bk_agent_id_list:
        return {}
    ENV_MAP = {"PRODUCT": "prod", "STAGING": "stage"}

    gse_url = settings.BK_API_URL_TMPL.format(api_name="bk-gse")
    get_agent_status_url = "{}/{}/api/v2/cluster/list_agent_state".format(
        gse_url, ENV_MAP.get(settings.RUN_MODE, "stage")
    )

    def send_request(agent_ids):
        params = {
            "bk_app_code": settings.APP_CODE,
            "bk_app_secret": settings.SECRET_KEY,
            "agent_id_list": agent_ids,
        }

        resp = requests.post(url=get_agent_status_url, json=params)

        if resp.status_code != 200:
            raise Exception(
                "[get_gse_agent_status_ipv6] 查询agent状态错误，返回值非200, content = {}".format(resp.content)
            )
        try:
            resp_data = resp.json()
        except Exception as e:
            raise Exception("[get_gse_agent_status_ipv6] 查询agent状态错误，返回值非Json, err={}".format(e))
        if resp_data["code"] != 0:
            raise Exception("[get_gse_agent_status_ipv6] 查询agent状态错误，返回值非code非0, {}".format(data))

        return resp_data.get("data", [])

    # gse 请求最大支持1000个agent_id的同时查询，所以需要把agent_id分成1000份的单元
    multi_agent_id_list = [bk_agent_id_list[i : i + 1000] for i in range(0, len(bk_agent_id_list), 1000)]

    data = []
    for agent_id_list in multi_agent_id_list:
        data.extend(send_request(agent_id_list))

    agent_id_status_map = {}
    for item in data:
        # esb agent 状态规则 : agent在线状态，0为不在线，1为在线
        # apigw agent 状态规则： Agent当前运行状态码, -1:未知 0:初始安装 1:启动中 2:运行中 3:有损状态 4:繁忙状态 5:升级中 6:停止中 7:解除安装
        # 为了前端的显示/与过滤保持一致，所有需要对状态进行转换
        if item["status_code"] == 2:
            status_code = 1
        elif item["status_code"] == -1:
            status_code = -1
        else:
            status_code = 0
        agent_id_status_map[item["bk_agent_id"]] = status_code

    return agent_id_status_map


def format_agent_data(agents):
    agent_data = {}
    for agent in agents:
        key = f"{agent['cloud_area']['id']}:{agent['ip']}"
        val = {"ip": agent["ip"], "bk_cloud_id": agent["cloud_area"]["id"], "bk_agent_alive": agent["alive"]}
        agent_data[key] = val
    return agent_data
