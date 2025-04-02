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

from gcloud.conf import settings
from gcloud.constants import BIZ_INTERNAL_SET, Type
from gcloud.core.models import Project
from pipeline_plugins.base.utils.inject import supplier_account_for_project
from pipeline_plugins.components.utils.sites.open.utils import cc_get_ips_info_by_str, cc_get_ips_info_by_str_ipv6
from pipeline_plugins.variables.base import FieldExplain, SelfExplainVariable
from pipeline_plugins.variables.utils import (
    filter_ip,
    find_module_with_relation,
    get_biz_internal_module,
    get_list_by_selected_names,
    get_service_template_list,
    get_service_template_list_by_names,
    get_set_list,
    list_biz_hosts,
)

ALL_SELECTED_STR = "all"

logger = logging.getLogger("root")


class SetModuleIpSelector(LazyVariable, SelfExplainVariable):
    code = "set_module_ip_selector"
    name = _("集群模块IP选择器")
    type = "dynamic"
    tag = "set_module_ip_selector.ip_selector"
    form = "%svariables/cmdb/var_set_module_ip_selector.js" % settings.STATIC_URL
    desc = _(
        "集群模块IP选择器只能拉取使用服务模板创建的模块，不适用于自定义拓扑的场景，自定义拓扑请使用IP选择器，输出为选择IP以 ',' 分隔的字符串"
    )

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description="选择的IP列表，以,分隔")]

    def get_value(self):
        if "executor" not in self.pipeline_data or "project_id" not in self.pipeline_data:
            raise Exception("ERROR: executor and project_id of pipeline is needed")
        var_ip_selector = self.value
        username = self.pipeline_data["executor"]
        project_id = self.pipeline_data["project_id"]
        project = Project.objects.get(id=project_id)
        tenant_id = self.pipeline_data["tenant_id"]
        bk_biz_id = project.bk_biz_id if project.from_cmdb else ""
        bk_supplier_account = supplier_account_for_project(project_id)
        # 筛选集群
        filter_set = var_ip_selector["var_filter_set"]
        # 筛选模块
        filter_service_template = var_ip_selector["var_filter_module"]
        # 输入方式
        produce_method = var_ip_selector["var_ip_method"]

        if produce_method == "custom":
            # 根据输入获取空闲机module id
            service_template_list = get_service_template_list(tenant_id, username, bk_biz_id, bk_supplier_account)
            # 如果勾选的set中有空闲机池，则会将所有空闲机module id添加进去
            service_template_list.extend(
                get_biz_inner_module_list(tenant_id, var_ip_selector, username, bk_biz_id, bk_supplier_account,
                                          produce_method)
            )

            # 通过集群模块筛选的ip
            module_ids = get_module_id_list(
                tenant_id,
                bk_biz_id,
                username,
                get_set_list(tenant_id, username, bk_biz_id, bk_supplier_account),
                service_template_list,
                filter_set,
                filter_service_template,
                bk_supplier_account,
            )
            logger.info("[SetModuleIpSelector.get_value] module_ids: %s" % module_ids)

            # 如果没有过滤到任何模块id，此时返回空
            # 自定义输入ip
            custom_value = var_ip_selector["var_ip_custom_value"]
            if settings.ENABLE_IPV6:
                ip_filter_result = cc_get_ips_info_by_str_ipv6(tenant_id, username, bk_biz_id, custom_value)
                logger.info("[SetModuleIpSelector.get_value] ip_filter_result: %s" % ip_filter_result)

                set_module_filter_host_id_list = get_host_id_list_by_module_id(
                    tenant_id, username, bk_biz_id, bk_supplier_account, module_ids
                )
                data = ",".join(
                    [
                        ip["InnerIP"]
                        for ip in ip_filter_result["ip_result"]
                        if ip["HostID"] in set(set_module_filter_host_id_list)
                    ]
                )
            else:
                ip_filter_result = cc_get_ips_info_by_str(tenant_id, username, bk_biz_id, custom_value)
                # 过滤输入的ip
                ip_filter_result_list = ",".join([ip["InnerIP"] for ip in ip_filter_result["ip_result"]])
                logger.info("[SetModuleIpSelector.get_value] ip_filter_result_list: %s" % ip_filter_result_list)

                set_module_filter_ip_list = get_ip_list_by_module_id(
                    tenant_id, username, bk_biz_id, bk_supplier_account, module_ids
                )
                # 获取在集群模块筛选的ip列表中的自定义输入ip
                data = filter_ip(ip_filter_result_list, set_module_filter_ip_list)
        elif produce_method == "select":
            set_input_method = "var_set"
            module_input_method = "var_module"

            data = get_ip_result_by_input_method(
                tenant_id,
                set_input_method,
                module_input_method,
                var_ip_selector,
                username,
                bk_biz_id,
                bk_supplier_account,
                filter_set,
                filter_service_template,
                produce_method,
                var_module_name=var_ip_selector["var_ip_select_value"]["var_module_name"],
            )
        elif produce_method == "manual":
            set_input_method = "var_manual_set"
            module_input_method = "var_manual_module"
            data = get_ip_result_by_input_method(
                tenant_id,
                set_input_method,
                module_input_method,
                var_ip_selector,
                username,
                bk_biz_id,
                bk_supplier_account,
                filter_set,
                filter_service_template,
                produce_method,
                var_module_name=var_ip_selector["var_ip_manual_value"]["var_module_name"],
            )
        else:
            # 输入ip方式不存在
            logger.error("[SetModuleIpSelector.get_value] input ip method: {} not exist".format(produce_method))
            data = ""
        return data


def get_module_id_list(
    tenant_id,
    bk_biz_id,
    username,
    set_list,
    service_template_list,
    filter_set_names,
    filter_service_template_names,
    bk_supplier_account,
):
    """
    筛选总体流程
        1. set_list中的是选择到的集群，与筛选规则中的filter_set_names取交集得到set_list
        2. service_template_list中是选择到的服务模版module id，会与与筛选规则中的filter_service_template_names取交集得到service_template_ids
        3. 调用find_module_with_relation传入set_list和service_template_ids得到module id

    针对空闲机模块的筛选规则特殊处理
        - 自定义输入ip、选择集群模块、手动输入集群模块后如果用户在筛选的集群中有 "空闲机池"，
          需要添加一个接口去获取相应模块的模块id，与用 find_module_with_relation得到的module_id合并在一起去获取ip
        - 自定义输入ip、选择集群模块、手动输入集群模块后如果用户在筛选的模块中有 "空闲机"、"待回收"、"故障机"等，
          需要添加一个接口去获取相应模块的模块id，与用 find_module_with_relation得到的module_id合并在一起去获取ip
        - 如果用户筛选规则中输入了 空闲机池 + 空闲机 则只取空闲机 模块id，
          与用 find_module_with_relation得到的module_id合并在一起去获取ip
        - 如果用户筛选规则中输入了 空闲机池 取空闲机池下 所有模块id，与用 find_module_with_relation得到的module_id合并在一起去获取ip
        - 空闲机池setid会被去掉，不能传到find_module_with_relation接口中，由于空闲机池下没有使用服务模板创建的模块
    @summary 根据集群模块筛选规则筛选出符合条件的模块id
    @param tenant_id: 租户 ID
    @param username: 执行用户名
    @param bk_biz_id: 业务id
    @param set_list: 集群list
    @param service_template_list: 服务模板list
    @param filter_set_names: 需要筛选的集群名称，多个用英文逗号分隔
    @param filter_service_template_names: 需要筛选的服务模板名称，多个用英文分隔
    @return:
    """

    logger.info("[get_module_id_list] set_list: %s" % set_list)
    logger.info("[get_module_id_list] service_template_list: %s" % service_template_list)
    logger.info("[get_module_id_list] filter_set_names: %s" % filter_set_names)
    logger.info("[get_module_id_list] filter_service_template_names: %s" % filter_service_template_names)
    if not service_template_list:
        logger.info("[get_module_id_list] service_template_list is empty, return empty module list early")
        return []

    # 排除空闲机池set id
    if not filter_set_names:
        set_ids = [set_item["bk_set_id"] for set_item in set_list if set_item["bk_set_name"] != BIZ_INTERNAL_SET]
    else:
        filter_set_names = filter_set_names.split(",")
        set_ids = [
            set_item["bk_set_id"]
            for set_item in set_list
            if set_item["bk_set_name"] in filter_set_names and set_item["bk_set_name"] != BIZ_INTERNAL_SET
        ]

    filter_service_template_names_list = filter_service_template_names.split(",")
    if not filter_service_template_names:
        service_template_ids = [service_template_item["id"] for service_template_item in service_template_list]
    else:
        # 过滤筛选规则中的model id
        service_template_ids = [
            service_template_item["id"]
            for service_template_item in service_template_list
            if service_template_item["name"] in filter_service_template_names_list
        ]

    biz_internal_modules = get_biz_internal_module(tenant_id, username, bk_biz_id, bk_supplier_account)["data"]
    biz_internal_module_names = set([m["name"] for m in biz_internal_modules])
    logger.info("[get_module_id_list] biz_internal_modules: %s" % biz_internal_modules)

    # 筛选规则与空闲机、待回收、故障机模块取交集
    internal_module_in_filter = set(biz_internal_module_names) & set(filter_service_template_names_list)

    selected_inner_module_id_set = set(
        [
            service_template_item["id"]
            for service_template_item in service_template_list
            if service_template_item["name"] in biz_internal_module_names
        ]
    )

    # 所有选择到的集群名
    all_selected_set_names_list = [set_item["bk_set_name"] for set_item in set_list]
    inner_module_id_list = []
    if BIZ_INTERNAL_SET in filter_set_names and BIZ_INTERNAL_SET in all_selected_set_names_list:
        # 判断是否有选择到空闲机模块ID，如果有取选择到的空闲机模块ID，没有则取空闲机池下所有模块ID
        if selected_inner_module_id_set:
            inner_module_id_list = [
                {"default": 0, "bk_module_id": service_template_item["id"]}
                for service_template_item in service_template_list
                if service_template_item["name"] in biz_internal_module_names
            ]
        else:
            inner_module_id_list = [
                {"default": 0, "bk_module_id": biz_internal_module_item["id"]}
                for biz_internal_module_item in biz_internal_modules
            ]
        # 用户输入空闲机，只取空闲机模块ID
        if internal_module_in_filter:
            inner_module_id_list = [
                {"default": 0, "bk_module_id": biz_internal_module_item["id"]}
                for biz_internal_module_item in service_template_list
                if biz_internal_module_item["name"] in internal_module_in_filter
            ]
        # 如果用户筛选规则中有空闲机池，模块ID中不包含空闲机模块，获取到的模块ID为空
        elif filter_service_template_names:
            inner_module_id_list = []
    # 筛选规则没有set name但是有module name，选择筛选规则中的module name
    elif (
        not filter_set_names
        and internal_module_in_filter
        and (BIZ_INTERNAL_SET in all_selected_set_names_list or ALL_SELECTED_STR in all_selected_set_names_list)
    ):
        inner_module_id_list = [
            {"default": 0, "bk_module_id": biz_internal_module_item["id"]}
            for biz_internal_module_item in service_template_list
            if biz_internal_module_item["name"] in internal_module_in_filter
        ]

    # 没有筛选规则时，并且选择到空闲机池，添加选择到的空闲机module id
    if not filter_set_names and not filter_service_template_names and BIZ_INTERNAL_SET in all_selected_set_names_list:
        # 获取service_template_list的空闲模块名
        internal_module_in_filter = [
            service_template_item["name"]
            for service_template_item in service_template_list
            if service_template_item["name"] in biz_internal_module_names
        ]
        inner_module_id_list = [
            {"default": 0, "bk_module_id": biz_internal_module_item["id"]}
            for biz_internal_module_item in service_template_list
            if biz_internal_module_item["name"] in internal_module_in_filter
        ]

    # 当存在服务模板过滤，并一个也过滤不到时
    if filter_service_template_names and not service_template_ids:
        return []

    # 调用find_module_with_relation接口根据set id list, service_template_id_list查询模块id
    module_id_list = find_module_with_relation(
        tenant_id, bk_biz_id, username, set_ids, service_template_ids, ["bk_module_id"])
    # 拼接空闲机、待回收等模块ID
    module_id_list.extend(inner_module_id_list)
    logger.info("[get_module_id_list] inner_module_id_list: %s" % inner_module_id_list)
    logger.info("[get_module_id_list] module_id_list: %s" % module_id_list)
    return module_id_list


def get_ip_list_by_module_id(tenant_id, username, bk_biz_id, bk_supplier_account, module_ids):
    """
    @summary 根据模块id获取模块下主机ip
    @param tenant_id: 租户 ID
    @param username: 执行用户名
    @param bk_biz_id: 业务id
    @param bk_supplier_account: 供应商账号
    @param module_ids: 模块id列表
    @return: 逗号分隔的ip字符串
    """
    if not module_ids:
        return ""
    kwargs = {"bk_module_ids": [module_id["bk_module_id"] for module_id in module_ids], "fields": ["bk_host_innerip"]}
    ip_result = list_biz_hosts(tenant_id, username, bk_biz_id, bk_supplier_account, kwargs)
    return ",".join([ip["bk_host_innerip"] for ip in ip_result])


def get_ip_list_by_module_id_with_ipv6(tenant_id, username, bk_biz_id, bk_supplier_account, module_ids):
    """
    @summary 根据模块id获取模块下主机ip，支持ipv6
    @param tenant_id: 租户 ID
    @param username: 执行用户名
    @param bk_biz_id: 业务id
    @param bk_supplier_account: 供应商账号
    @param module_ids: 模块id列表
    @return: 逗号分隔的ip字符串
    """
    if not module_ids:
        return ""
    kwargs = {
        "bk_module_ids": [module_id["bk_module_id"] for module_id in module_ids],
        "fields": ["bk_host_innerip", "bk_host_innerip_v6"],
    }
    ip_result = list_biz_hosts(tenant_id, username, bk_biz_id, bk_supplier_account, kwargs)
    return ",".join([ip.get("bk_host_innerip") or ip.get("bk_host_innerip_v6") for ip in ip_result])


def get_host_id_list_by_module_id(tenant_id, username, bk_biz_id, bk_supplier_account, module_ids) -> list:
    """
    @summary 根据模块id获取模块下主机id
    @param tenant_id: 租户 ID
    @param username: 执行用户名
    @param bk_biz_id: 业务id
    @param bk_supplier_account: 供应商账号
    @param module_ids: 模块id列表
    @return: 主机id列表
    """
    if not module_ids:
        return ""
    kwargs = {"bk_module_ids": [module_id["bk_module_id"] for module_id in module_ids], "fields": ["bk_host_id"]}
    ip_result = list_biz_hosts(tenant_id, username, bk_biz_id, bk_supplier_account, kwargs)
    return [ip["bk_host_id"] for ip in ip_result]


def get_ip_result_by_input_method(
    tenant_id,
    set_input_method,
    module_input_method,
    var_ip_selector,
    username,
    bk_biz_id,
    bk_supplier_account,
    filter_set,
    filter_service_template,
    produce_method,
    var_module_name="",
):
    """
    @summary 根据输入方式获取ip
    @param tenant_id: 租户 ID
    @param var_module_name: 模块属性名
    @param set_input_method: 集群输入方式对应tag code
    @param module_input_method: 模块输入方式对应tag code
    @param var_ip_selector: 表单数据
    @param username: 用户名
    @param bk_biz_id: 业务id
    @param bk_supplier_account: 供应商账户
    @param filter_set: 筛选集群
    @param filter_service_template: 筛选模块
    @param produce_method: 输入方式
    @return: 逗号分隔ip字符串
    """
    produce_method = "var_ip_{}_value".format(produce_method)
    select_method = var_ip_selector[produce_method]

    # 对填入的集群和服务模版进行预处理
    selected_set_names, selected_service_template_names = (
        select_method[set_input_method],
        select_method[module_input_method],
    )
    if isinstance(selected_set_names, str):
        # 去除两端的空格
        selected_set_names = [selected_set_name.strip() for selected_set_name in selected_set_names.split(",")]
    if isinstance(selected_service_template_names, str):
        selected_service_template_names = selected_service_template_names.split(",")

    # 获取全部集群列表
    set_list = get_set_list(tenant_id, username, bk_biz_id, bk_supplier_account)
    # 集群全选，筛选条件不为空则调接口获取集群id列表
    if ALL_SELECTED_STR not in selected_set_names:
        logger.info(f"[get_ip_result_by_input_method]selected_set_names: {selected_set_names}")
        # 根据选中的集群名称获取选中的集群列表
        set_list = get_list_by_selected_names(selected_set_names, set_list)
    # 获取全部服务模板列表
    service_template_list = get_service_template_list(tenant_id, username, bk_biz_id, bk_supplier_account)
    # 服务模板全选，则调接口获取服务模板列表
    if ALL_SELECTED_STR not in selected_service_template_names:
        logger.info(
            f"[get_ip_result_by_input_method]selected_service_template_names: {selected_service_template_names}"
        )
        # 通过选中的或输入的集群模板获取集群模板列表
        service_template_list = get_service_template_list_by_names(
            selected_service_template_names, service_template_list
        )

    # 根据输入获取空闲机module id
    service_template_list.extend(
        get_biz_inner_module_list(
            tenant_id,
            var_ip_selector,
            username,
            bk_biz_id,
            bk_supplier_account,
            produce_method,
            set_input_method=set_input_method,
            module_input_method=module_input_method,
        )
    )

    # 获取模块id列表
    module_ids = get_module_id_list(
        tenant_id, bk_biz_id, username, set_list, service_template_list, filter_set, filter_service_template,
        bk_supplier_account,
    )

    # 根据模块 id 列表获取 ip 并返回
    if settings.ENABLE_IPV6:
        data = get_ip_list_by_module_id_with_ipv6(tenant_id, username, bk_biz_id, bk_supplier_account, module_ids)
    else:
        data = get_ip_list_by_module_id(tenant_id, username, bk_biz_id, bk_supplier_account, module_ids)
    return data


def get_biz_inner_module_list(
    tenant_id,
    var_ip_selector,
    username,
    bk_biz_id,
    bk_supplier_account,
    produce_method,
    set_input_method=None,
    module_input_method=None,
):
    """
    @summary 根据输入获取空闲机module id
    @param tenant_id: 租户 ID
    @param var_module_name: 模块属性名
    @param set_input_method: 集群输入方式对应tag code
    @param module_input_method: 模块输入方式对应tag code
    @param var_ip_selector: 表单数据
    @param username: 用户名
    @param bk_biz_id: 业务id
    @param bk_supplier_account: 供应商账户
    @param produce_method: 输入方式
    @return:
    """
    # 获取所有空闲机池下的模块ID
    biz_internal_module_list = get_biz_internal_module(tenant_id, username, bk_biz_id, bk_supplier_account)["data"]
    biz_internal_module_names = set([m["name"] for m in biz_internal_module_list])

    if set_input_method is None and module_input_method is None:
        return biz_internal_module_list

    # 勾选的模块与空闲机、待回收、故障机模块取交集
    select_method = var_ip_selector[produce_method]
    select_sets = select_method[set_input_method]
    select_modules = select_method[module_input_method]

    if isinstance(select_sets, str):
        select_sets = select_sets.split(",")
    if isinstance(select_modules, str):
        select_modules = select_modules.split(",")

    if ALL_SELECTED_STR in select_modules:
        select_biz_internal_module = biz_internal_module_names
    else:
        select_biz_internal_module = set(biz_internal_module_names) & set(select_modules)

    # 用户输入空闲机池或all，选择到模块为空或all，取空闲机池下所有模块ID
    if (BIZ_INTERNAL_SET in select_sets or ALL_SELECTED_STR in select_sets) and (
        not select_modules or ALL_SELECTED_STR in select_modules
    ):
        return biz_internal_module_list

    biz_internal_module_option_list = []
    # 用户输入空闲机，只取空闲机模块ID
    if select_biz_internal_module:
        for biz_internal_module_option in biz_internal_module_list:
            if biz_internal_module_option["name"] in select_biz_internal_module:
                biz_internal_module_option_list.append(biz_internal_module_option)

    return biz_internal_module_option_list
