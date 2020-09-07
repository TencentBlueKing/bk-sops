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

from django.utils.translation import ugettext_lazy as _

from pipeline.core.data.var import LazyVariable
from pipeline_plugins.base.utils.inject import supplier_account_for_project
from pipeline_plugins.components.utils.sites.open.utils import cc_get_ips_info_by_str
from pipeline_plugins.variables.utils import (
    get_service_template_list_by_names,
    get_list_by_selected_names,
    filter_ip,
    get_module_list,
    get_set_list,
    get_service_template_list,
    list_biz_hosts,
    find_module_with_relation,
)

from gcloud.conf import settings
from gcloud.core.models import Project

ALL_SELECTED_STR = "all"

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


class SetModuleIpSelector(LazyVariable):
    code = "set_module_ip_selector"
    name = _("集群模块IP选择器")
    type = "general"
    tag = "set_module_ip_selector.ip_selector"
    form = "%svariables/cmdb/var_set_module_ip_selector.js" % settings.STATIC_URL

    def get_value(self):
        var_ip_selector = self.value
        username = self.pipeline_data["executor"]
        project_id = self.pipeline_data["project_id"]
        project = Project.objects.get(id=project_id)
        bk_biz_id = project.bk_biz_id if project.from_cmdb else ""
        bk_supplier_account = supplier_account_for_project(project_id)
        # 筛选集群
        filter_set = var_ip_selector["var_filter_set"]
        # 筛选模块
        filter_service_template = var_ip_selector["var_filter_module"]
        # 输入方式
        produce_method = var_ip_selector["var_ip_method"]

        if produce_method == "custom":
            # 自定义输入ip
            custom_value = var_ip_selector["var_ip_custom_value"]
            ip_filter_result = cc_get_ips_info_by_str(username, bk_biz_id, custom_value)
            # 过滤输入的ip
            ip_filter_result_list = ",".join([ip["InnerIP"] for ip in ip_filter_result["ip_result"]])
            # 通过集群模块筛选的ip
            module_ids = get_module_id_list(
                bk_biz_id,
                username,
                get_set_list(username, bk_biz_id, bk_supplier_account),
                get_service_template_list(username, bk_biz_id, bk_supplier_account),
                filter_set,
                filter_service_template,
            )
            set_module_filter_ip_list = get_ip_list_by_module_id(username, bk_biz_id, bk_supplier_account, module_ids)
            # 获取在集群模块筛选的ip列表中的自定义输入ip
            data = filter_ip(ip_filter_result_list, set_module_filter_ip_list)
        elif produce_method == "select":
            set_input_method = "var_set"
            module_input_method = "var_module"

            data = get_ip_result_by_input_method(
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
        elif produce_method == "manual":
            set_input_method = "var_manual_set"
            module_input_method = "var_manual_module"
            data = get_ip_result_by_input_method(
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

        else:
            # 输入ip方式不存在
            logger.warning("input ip method: {} not exit".format(produce_method))
            data = ""
        return data


def get_module_id_list(
    bk_biz_id, username, set_list, service_template_list, filter_set_names, filter_service_template_names
):
    """
    @summary 根据集群模块筛选规则筛选出符合条件的模块id
    @param username: 执行用户名
    @param bk_biz_id: 业务id
    @param set_list: 集群list
    @param service_template_list: 服务模板list
    @param filter_set_names: 需要筛选的集群名称，多个用英文逗号分隔
    @param filter_service_template_names: 需要筛选的服务模板名称，多个用英文分隔
    @return:
    """
    filter_set_name_list = filter_set_names.split(",")
    filter_service_template_name_list = filter_service_template_names.split(",")

    if filter_set_name_list is None or filter_service_template_name_list is None:
        return []
    set_ids = [set_item["bk_set_id"] for set_item in set_list if set_item["bk_set_name"] in filter_set_name_list]
    service_template_ids = [
        service_template_item["id"]
        for service_template_item in service_template_list
        if service_template_item["name"] in filter_service_template_name_list
    ]

    # 调用find_module_with_relation接口根据set id list, service_template_id_list查询模块id
    module_id_list = find_module_with_relation(bk_biz_id, username, set_ids, service_template_ids, ["bk_module_id"])
    return module_id_list


def get_ip_list_by_module_id(username, bk_biz_id, bk_supplier_account, module_ids):
    """
    @summary 根据模块id获取模块下主机ip
    @param username: 执行用户名
    @param bk_biz_id: 业务id
    @param bk_supplier_account: 供应商账号
    @param module_ids: 模块id列表
    @return: 逗号分隔的ip字符串
    """
    kwargs = {"bk_module_ids": module_ids, "fields": ["bk_host_innerip"]}
    ip_result = list_biz_hosts(username, bk_biz_id, bk_supplier_account, kwargs)
    return ",".join([ip["bk_host_innerip"] for ip in ip_result])


def get_ip_result_by_input_method(
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
    # 获取全部集群列表
    set_list = get_set_list(username, bk_biz_id, bk_supplier_account)
    # 集群全选，筛选条件不为空则调接口获取集群id列表
    if ALL_SELECTED_STR not in select_method[set_input_method]:
        selected_set_names = select_method[set_input_method]
        # 根据选中的集群名称获取选中的集群列表
        set_list = get_list_by_selected_names(selected_set_names, set_list)
    # 获取全部服务模板列表
    service_template_list = get_service_template_list(username, bk_biz_id, bk_supplier_account)
    # 服务模板全选，则调接口获取服务模板列表
    if ALL_SELECTED_STR not in select_method[module_input_method]:
        selected_service_template_names = select_method[module_input_method]
        # 通过选中的或输入的集群模板获取集群模板列表
        service_template_list = get_service_template_list_by_names(
            selected_service_template_names, service_template_list
        )
    # 获取模块id列表
    module_ids = get_module_id_list(
        bk_biz_id, username, set_list, service_template_list, filter_set, filter_service_template
    )
    if not var_module_name or var_module_name == "ip":
        # 根据模块id列表获取ip并返回
        data = get_ip_list_by_module_id(username, bk_biz_id, bk_supplier_account, module_ids)
    else:
        # 根据模块属性名获取模块信息
        kwargs = {"bk_ids": module_ids, "fields": var_module_name.split(",")}
        data = [module_attr[var_module_name] for module_attr in get_module_list(username, bk_biz_id, kwargs=kwargs)]
    return data
