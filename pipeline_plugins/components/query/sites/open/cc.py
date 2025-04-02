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
import traceback

from django.http import JsonResponse
from django.urls import path, re_path
from django.utils.translation import gettext_lazy as _
from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE
from iam.exceptions import RawAuthFailedException

from packages.bkapi.bk_cmdb.shortcuts import get_client_by_request
from api.utils.request import batch_request
from gcloud.conf import settings
from gcloud.core.utils import get_user_business_list
from gcloud.exceptions import APIError, ApiRequestError
from gcloud.iam_auth.utils import check_and_raise_raw_auth_fail_exception
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.base.utils.inject import supplier_account_inject, supplier_id_inject
from pipeline_plugins.cmdb_ip_picker.query import (
    cmdb_get_mainline_object_topo,
    cmdb_search_dynamic_group,
    cmdb_search_host,
    cmdb_search_topo_tree,
)
from pipeline_plugins.components.utils import batch_execute_func

logger = logging.getLogger("root")


@supplier_account_inject
def cc_search_object_attribute(request, obj_id, biz_cc_id, supplier_account):
    """
    @summary: 获取对象自定义属性
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}
    include_not_editable = request.GET.get("all", False)
    kwargs = {"bk_obj_id": obj_id, "bk_supplier_account": supplier_account, "bk_biz_id": int(biz_cc_id)}
    cc_result = client.api.search_object_attribute(kwargs, headers=headers)
    if not cc_result["result"]:
        message = handle_api_error("cc", "cc.search_object_attribute", kwargs, cc_result)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(cc_result, message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

    obj_property = []
    for item in cc_result["data"]:
        if include_not_editable or item["editable"]:
            obj_property.append({"value": item["bk_property_id"], "text": item["bk_property_name"]})

    return JsonResponse({"result": True, "data": obj_property})


@supplier_account_inject
def cc_search_object_attribute_all(request, obj_id, biz_cc_id, supplier_account):
    """
    @summary: 获取对象全部属性
    @param request:
    @return:
    """
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}
    kwargs = {"bk_obj_id": obj_id, "bk_supplier_account": supplier_account, "bk_biz_id": int(biz_cc_id)}
    cc_result = client.api.search_object_attribute(kwargs, headers=headers)
    if not cc_result["result"]:
        message = handle_api_error("cc", "cc.search_object_attribute", kwargs, cc_result)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(cc_result, message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

    obj_property = []
    for item in cc_result["data"]:
        obj_property.append({"value": item["bk_property_id"], "text": item["bk_property_name"]})

    return JsonResponse({"result": True, "data": obj_property})


def cc_attribute_type_to_table_type(attribute):
    result = {
        "tag_code": attribute["bk_property_id"],
        "type": "input",
        "attrs": {"name": attribute["bk_property_name"], "editable": attribute["editable"]},
    }
    if attribute["bk_property_type"] == "int":
        result["type"] = "int"
    elif attribute["bk_property_type"] == "enum":
        result["type"] = "select"
        result["attrs"]["items"] = []
        for item in attribute["option"]:
            # 修改时会通过cc_format_prop_data获取对应的属性id，这里使用name字段方便展示
            item_name = item["name"].strip()
            if item["is_default"] is True:
                result["attrs"]["default"] = item_name
            result["attrs"]["items"].append({"text": item_name, "value": item["id"]})
    return result


@supplier_account_inject
def cc_search_create_object_attribute(request, obj_id, biz_cc_id, supplier_account):
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}
    kwargs = {"bk_obj_id": obj_id, "bk_supplier_account": supplier_account, "bk_biz_id": int(biz_cc_id)}
    cc_result = client.api.search_object_attribute(kwargs, headers=headers)
    if not cc_result["result"]:
        message = handle_api_error("cc", "cc.search_object_attribute", kwargs, cc_result)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(cc_result, message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

    obj_property = []
    for item in cc_result["data"]:
        if item["editable"]:
            prop_dict = cc_attribute_type_to_table_type(item)
            # 集群/模块名称设置为必填项
            if item["bk_property_id"] in ["bk_set_name", "bk_module_name"]:
                prop_dict["attrs"]["validation"] = [{"type": "required"}]
            obj_property.append(prop_dict)

    return JsonResponse({"result": True, "data": obj_property})


@supplier_account_inject
def cc_list_service_category(request, biz_cc_id, bk_parent_id, supplier_account):
    """
    查询指定节点bk_parent_id的所有子服务分类
    url: /pipeline/cc_list_service_category/biz_cc_id/bk_parent_id/
    :param request:
    :param biz_cc_id:
    :param bk_parent_id: 父服务分类id, 根id = 0
    :param supplier_account:
    :return:
        - 请求成功 {"result": True, "data": service_categories, "message": "success"}
            - service_categories: [{"value" : 服务分类id, "label": 服务分类名称}, ...]
        - 请求失败 {"result": False, "data": [], "message": message}
    """
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}
    kwargs = {"bk_biz_id": int(biz_cc_id), "bk_supplier_account": supplier_account}
    list_service_category_return = client.api.list_service_category(kwargs, headers=headers)
    if not list_service_category_return["result"]:
        message = handle_api_error("cc", "cc.list_service_category", kwargs, list_service_category_return)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(list_service_category_return, message)
        return JsonResponse({"result": False, "data": [], "message": message})

    service_categories_untreated = list_service_category_return["data"]["info"]
    service_categories = []
    for category_untreated in service_categories_untreated:
        if category_untreated["bk_parent_id"] != int(bk_parent_id):
            continue
        category = {"value": category_untreated["id"], "label": category_untreated["name"]}
        service_categories.append(category)
    return JsonResponse({"result": True, "data": service_categories, "message": "success"})


@supplier_account_inject
def cc_get_service_category_topo(request, biz_cc_id, supplier_account):
    """
    获取指定biz_cc_id模板类型拓扑
    :param request:
    :param biz_cc_id:
    :param supplier_account:
    :return:
        - 请求成功
        {
            "result": True,
            "message": "success",
            "data": [
                {
                    "value": "1-1",
                    "label": "1-1",
                    children: [{"value": "2-1", "label": "2-1"},]
                },
                ...
            ]
        }
        - 请求失败  {"result": False, "data": [], "message": message}
    """
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}
    kwargs = {"bk_biz_id": int(biz_cc_id), "bk_supplier_account": supplier_account}
    list_service_category_return = client.api.list_service_category(kwargs, headers=headers)
    if not list_service_category_return["result"]:
        message = handle_api_error("cc", "cc.list_service_category", kwargs, list_service_category_return)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(list_service_category_return, message)
        return JsonResponse({"result": False, "data": [], "message": message})
    service_categories = list_service_category_return["data"]["info"]
    topo_merged_by_id = {
        sc["id"]: {"value": sc["id"], "label": sc["name"], "children": []}
        for sc in service_categories
        if sc["bk_parent_id"] == 0
    }
    for sc in service_categories:
        if sc["bk_parent_id"] not in topo_merged_by_id:
            continue
        topo_merged_by_id[sc["bk_parent_id"]]["children"].append({"value": sc["id"], "label": sc["name"]})
    # 筛选两层结构的拓扑
    service_category_topo = [topo for topo in topo_merged_by_id.values() if topo["children"]]
    return JsonResponse({"result": True, "data": service_category_topo, "message": "success"})


@supplier_account_inject
def cc_list_service_template(request, biz_cc_id, supplier_account):
    """
    获取服务模板
    url: /pipeline/cc_list_service_template/biz_cc_id/
    :param request:
    :param biz_cc_id:
    :param supplier_account:
    :return:
        - 请求成功 {"result": True, "data": service_templates, "message": "success"}
            - service_templates： [{"value" : 模板名_模板id, "text": 模板名}, ...]
        - 请求失败 {"result": False, "data": [], "message": message}
    """
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}
    kwargs = {"bk_biz_id": int(biz_cc_id), "bk_supplier_account": supplier_account}
    service_templates = []
    try:
        service_templates_untreated = batch_request(
            client.api.list_service_template,
            kwargs,
            check_iam_auth_fail=True,
            headers=headers,
        )
    except ApiRequestError as e:
        return JsonResponse({"result": False, "data": [], "message": e})
    for template_untreated in service_templates_untreated:
        template = {
            "value": "{name}_{id}".format(name=template_untreated["name"], id=template_untreated["id"]),
            "text": template_untreated["name"],
        }
        service_templates.append(template)
    return JsonResponse({"result": True, "data": service_templates, "message": "success"})


def cc_format_topo_data(data, obj_id, category):
    """
    @summary: 格式化拓扑数据
    @param obj_id set or module
    @param category prev(获取obj_id上一层级拓扑) or normal (获取obj_id层级拓扑) or picker(ip选择器拓扑)
    @return 拓扑数据列表
    """
    tree_data = []
    for item in data:
        tree_item = {
            "id": "%s_%s" % (item["bk_obj_id"], item["bk_inst_id"]),
            "label": item["bk_inst_name"],
        }
        if category == "prev":
            if item["bk_obj_id"] != obj_id:
                tree_data.append(tree_item)
                if "child" in item:
                    tree_item["children"] = cc_format_topo_data(item["child"], obj_id, category)
        else:
            if item["bk_obj_id"] == obj_id:
                tree_data.append(tree_item)
            elif "child" in item:
                tree_item["children"] = cc_format_topo_data(item["child"], obj_id, category)
                tree_data.append(tree_item)

    return tree_data


def insert_inter_result_to_topo_data(inter_result_data, topo_data):
    formatted_inter_result = {
        "bk_inst_id": inter_result_data["bk_set_id"],
        "bk_inst_name": inter_result_data["bk_set_name"],
        "bk_obj_id": "set",
        "bk_obj_name": "set",
        "child": [
            {
                "bk_inst_id": internal_module["bk_module_id"],
                "bk_inst_name": internal_module["bk_module_name"],
                "bk_obj_id": "module",
                "bk_obj_name": "module",
                "child": [],
            }
            for internal_module in inter_result_data["module"]
        ],
    }
    topo_data[0]["child"].insert(0, formatted_inter_result)
    return topo_data


@supplier_account_inject
def cc_search_topo(request, obj_id, category, biz_cc_id, supplier_account):
    """
    @summary: 查询对象拓扑
    @param request:
    @param biz_cc_id:
    @return:
    """
    with_internal_module = request.GET.get("with_internal_module", False)
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}
    kwargs = {"bk_biz_id": biz_cc_id, "bk_supplier_account": supplier_account}
    cc_result = client.api.search_biz_inst_topo(
        kwargs,
        path_params={"bk_biz_id": biz_cc_id},
        headers=headers,
    )
    if not cc_result["result"]:
        message = handle_api_error("cc", "cc.search_biz_inst_topo", kwargs, cc_result)
        logger.error(message)
        check_and_raise_raw_auth_fail_exception(cc_result, message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

    if with_internal_module:
        inter_result = client.api.get_biz_internal_module(
            kwargs,
            path_params={"bk_supplier_account": supplier_account, "bk_biz_id": biz_cc_id},
            headers=headers,
        )
        if not inter_result["result"]:
            message = handle_api_error("cc", "cc.get_biz_internal_module", kwargs, inter_result)
            logger.error(message)
            check_and_raise_raw_auth_fail_exception(inter_result, message)
            result = {"result": False, "data": [], "message": message}
            return JsonResponse(result)
        cc_result["data"] = insert_inter_result_to_topo_data(inter_result["data"], cc_result["data"])

    if category in ["normal", "prev"]:
        cc_topo = cc_format_topo_data(cc_result["data"], obj_id, category)
    else:
        cc_topo = []

    return JsonResponse({"result": True, "data": cc_topo})


@supplier_account_inject
def cc_search_topo_tree(request, biz_cc_id, supplier_account):
    return cmdb_search_topo_tree(request, biz_cc_id, supplier_account)


@supplier_account_inject
@supplier_id_inject
def cc_search_host(request, biz_cc_id, supplier_account, supplier_id):
    return cmdb_search_host(request, biz_cc_id, supplier_account, supplier_id)


@supplier_account_inject
def cc_get_mainline_object_topo(request, biz_cc_id, supplier_account):
    return cmdb_get_mainline_object_topo(request, biz_cc_id, supplier_account)


def cc_get_business(request):
    try:
        business = get_user_business_list(tenant_id=request.user.tenant_id, username=request.user.username)
    except APIError as e:
        message = "an error occurred when fetch user business: %s" % traceback.format_exc()

        if e.result and e.result.get("code", 0) == HTTP_AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise RawAuthFailedException(permissions=e.result.get("permission", {}))

        logger.error(message)
        return JsonResponse({"result": False, "message": "fetch business list failed, please contact administrator"})

    data = []
    for biz in business:
        # archive data filter
        if biz.get("bk_data_status") != "disabled":
            data.append({"text": biz["bk_biz_name"], "value": int(biz["bk_biz_id"])})

    return JsonResponse({"result": True, "data": data})


@supplier_account_inject
def cc_search_dynamic_group(request, biz_cc_id, supplier_account):
    return cmdb_search_dynamic_group(request, biz_cc_id, supplier_account)


@supplier_account_inject
def cc_list_set_template(request, biz_cc_id, supplier_account):
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}
    kwargs = {"bk_biz_id": int(biz_cc_id), "bk_supplier_account": supplier_account}

    set_templates = batch_request(
        client.api.list_set_template,
        kwargs,
        check_iam_auth_fail=True,
        path_params={"bk_biz_id": int(biz_cc_id)},
        headers=headers,
    )
    template_list = [
        {"value": set_template.get("id"), "text": set_template.get("name")} for set_template in set_templates
    ]
    return JsonResponse({"result": True, "data": template_list})


def cc_get_editable_module_attribute(request, biz_cc_id):
    kwargs = {
        "bk_biz_id": int(biz_cc_id),
        "bk_obj_id": "module",
    }
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}
    result = client.api.search_object_attribute(kwargs, headers=headers)
    if not result["result"]:
        check_and_raise_raw_auth_fail_exception(result)
        message = _(
            f"业务配置数据请求失败: 请求[配置平台]接口发生异常: {result['message']} | cc_get_editable_module_attribute"
        )
        logger.error(message)
        return JsonResponse({"result": False, "data": message})
    data = result["data"]
    module_attribute = []
    for module_item in data:
        if module_item["editable"]:
            module_attribute.append(module_item)

    return JsonResponse({"result": True, "data": module_attribute})


def cc_input_host_property(request, biz_cc_id):
    """
    获取CMDB主机对应的属性名称和code
    """
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}

    kwargs = {"bk_obj_id": "host", "bk_biz_id": int(biz_cc_id)}

    cc_result = client.api.search_object_attribute(kwargs, headers=headers)

    if not cc_result["result"]:
        check_and_raise_raw_auth_fail_exception(cc_result)
        return JsonResponse({"result": False, "message": cc_result["message"]})

    obj_property = []
    for item in cc_result["data"]:
        if item["editable"]:
            prop_dict = {"bk_property_id": item["bk_property_id"], "bk_property_name": item["bk_property_name"]}
            obj_property.append(prop_dict)

    return JsonResponse({"result": True, "data": obj_property})


def cc_get_editable_set_attribute(request, biz_cc_id):
    kwargs = {
        "bk_biz_id": int(biz_cc_id),
        "bk_obj_id": "set",
    }
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}

    result = client.api.search_object_attribute(kwargs, headers=headers)
    if not result["result"]:
        check_and_raise_raw_auth_fail_exception(result)
        message = _(
            f"业务配置数据请求失败: 请求[配置平台]接口发生异常: {result['message']} | cc_get_editable_set_attribute"
        )
        logger.error(message)
        return JsonResponse({"result": False, "data": message})
    data = result["data"]
    set_attribute = []
    for set_item in data:
        if set_item["editable"] and set_item["bk_property_id"] != "bk_set_name":
            prop_dict = {"bk_property_id": set_item["bk_property_id"], "bk_property_name": set_item["bk_property_name"]}
            set_attribute.append(prop_dict)

    return JsonResponse({"result": True, "data": set_attribute})


def cc_search_status_options(request, biz_cc_id):
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}
    kwargs = {
        "bk_biz_id": int(biz_cc_id),
        "bk_obj_id": "set",
    }
    result = client.api.search_object_attribute(kwargs, headers=headers)
    options = []
    for data in result["data"]:
        if data["bk_property_id"] == "bk_service_status":
            for option in data["option"]:
                options.append({"text": option["name"], "value": option["id"]})
    if not options:
        message = handle_api_error("cc", "cc.search_object_attribute", kwargs, result)
        logger.error(message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)
    return JsonResponse({"result": True, "data": options})


def cc_find_host_by_topo(request, biz_cc_id):
    """
    批量查询拓扑节点下的主机数量
    @param request:
    @param biz_cc_id: cc id
    @return:
    """
    # 模块ID列表，以 , 分割，例如 123,234,345
    bk_inst_id = request.GET.get("bk_inst_id", "")

    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}

    # 去除split后的空字符串
    bk_inst_id = filter(lambda x: x, bk_inst_id.split(","))
    params_list = [
        {
            "data": {
                "bk_biz_id": int(biz_cc_id),
                "bk_inst_id": int(inst_id),
                "bk_obj_id": "module",
                "fields": ["bk_host_id"],
                "page": {"start": 0, "limit": 1},
            },
            "path_params": {"bk_biz_id": int(biz_cc_id)},
            "headers": headers,
        }
        for inst_id in bk_inst_id
    ]

    result_list = batch_execute_func(client.api.find_host_by_topo, params_list)

    data = []
    failed_request_message = []
    for result in result_list:
        func_result = result["result"]
        if not func_result["result"]:
            message = handle_api_error("cc", "find_host_by_topo", result["params"], func_result)
            failed_request_message.append(message)
        else:
            data.append({"bk_inst_id": result["params"]["bk_inst_id"], "host_count": func_result["data"]["count"]})

    if failed_request_message:
        return JsonResponse({"result": False, "data": [], "message": "\n".join(failed_request_message)})

    return JsonResponse({"result": True, "data": data})


def list_business_set(request):
    """
    查询所有业务集
    @param request:
    @return:
    """
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    headers = {"X-Bk-Tenant-Id": request.user.tenant_id}

    count_resp = client.api.list_business_set({"page": {"enable_count": True}}, headers=headers)

    if not count_resp["result"]:
        return JsonResponse({"result": False, "data": [], "message": "\n".join(count_resp.get("message"))})

    count = count_resp["data"]["count"]
    resp = batch_request(
        client.api.list_business_set,
        {},
        check_iam_auth_fail=True,
        get_count=lambda x: count,
        headers=headers,
    )
    business_set = [
        {"value": item["bk_biz_set_id"], "text": "{}({})".format(item["bk_biz_set_name"], item["bk_biz_set_id"])}
        for item in resp
    ]
    return JsonResponse({"result": True, "data": business_set})


cc_urlpatterns = [
    re_path(r"^cc_get_editable_module_attribute/(?P<biz_cc_id>\d+)/$", cc_get_editable_module_attribute),
    re_path(
        r"^cc_search_object_attribute/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$",
        cc_search_object_attribute,
    ),
    re_path(
        r"^cc_search_object_attribute_all/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$",
        cc_search_object_attribute_all,
    ),
    re_path(
        r"^cc_search_create_object_attribute/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$",
        cc_search_create_object_attribute,
    ),
    re_path(
        r"^cc_search_topo/(?P<obj_id>\w+)/(?P<category>\w+)/(?P<biz_cc_id>\d+)/$",
        cc_search_topo,
    ),
    re_path(
        r"^cc_list_service_category/(?P<biz_cc_id>\w+)/(?P<bk_parent_id>\w+)/$",
        cc_list_service_category,
    ),
    re_path(
        r"^cc_list_service_template/(?P<biz_cc_id>\d+)/$",
        cc_list_service_template,
    ),
    re_path(
        r"^cc_get_service_category_topo/(?P<biz_cc_id>\d+)/$",
        cc_get_service_category_topo,
    ),
    # IP selector
    re_path(r"^cc_search_topo_tree/(?P<biz_cc_id>\d+)/$", cc_search_topo_tree),
    re_path(r"^cc_search_host/(?P<biz_cc_id>\d+)/$", cc_search_host),
    re_path(
        r"^cc_get_mainline_object_topo/(?P<biz_cc_id>\d+)/$",
        cc_get_mainline_object_topo,
    ),
    re_path(r"^cc_get_business_list/$", cc_get_business),
    re_path(r"^cc_search_dynamic_group/(?P<biz_cc_id>\d+)/$", cc_search_dynamic_group),
    # 查询集群模板
    re_path(r"^cc_list_set_template/(?P<biz_cc_id>\d+)/$", cc_list_set_template),
    # 主机自定义属性表格
    re_path(r"^cc_input_host_property/(?P<biz_cc_id>\d+)/$", cc_input_host_property),
    # 查询Set服务状态
    re_path(r"^cc_search_status_options/(?P<biz_cc_id>\d+)/$", cc_search_status_options),
    # 获取可更改的set属性
    re_path(r"^cc_get_set_attribute/(?P<biz_cc_id>\d+)/$", cc_get_editable_set_attribute),
    # 批量查询拓扑节点下的主机
    re_path(r"^cc_find_host_by_topo/(?P<biz_cc_id>\d+)/$", cc_find_host_by_topo),
    path("list_business_set/", list_business_set),
]
