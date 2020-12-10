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
import traceback

from django.http import JsonResponse
from django.conf.urls import url

from gcloud.utils.cmdb import batch_request
from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE
from iam.exceptions import RawAuthFailedException

from pipeline_plugins.base.utils.inject import (
    supplier_account_inject,
    supplier_id_inject,
)
from pipeline_plugins.cmdb_ip_picker.query import (
    cmdb_search_host,
    cmdb_search_topo_tree,
    cmdb_get_mainline_object_topo,
    cmdb_search_dynamic_group,
)

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from gcloud.exceptions import APIError
from gcloud.core.utils import get_user_business_list

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


@supplier_account_inject
def cc_search_object_attribute(request, obj_id, biz_cc_id, supplier_account):
    """
    @summary: 获取对象自定义属性
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_user(request.user.username)
    include_not_editable = request.GET.get("all", False)
    kwargs = {"bk_obj_id": obj_id, "bk_supplier_account": supplier_account}
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result["result"]:
        message = handle_api_error("cc", "cc.search_object_attribute", kwargs, cc_result)
        logger.error(message)
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
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_obj_id": obj_id, "bk_supplier_account": supplier_account, "bk_biz_id": int(biz_cc_id)}
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result["result"]:
        message = handle_api_error("cc", "cc.search_object_attribute", kwargs, cc_result)
        logger.error(message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

    obj_property = []
    for item in cc_result["data"]:
        obj_property.append({"value": item["bk_property_id"], "text": item["bk_property_name"]})

    return JsonResponse({"result": True, "data": obj_property})


@supplier_account_inject
def cc_search_create_object_attribute(request, obj_id, biz_cc_id, supplier_account):
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_obj_id": obj_id, "bk_supplier_account": supplier_account}
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result["result"]:
        message = handle_api_error("cc", "cc.search_object_attribute", kwargs, cc_result)
        logger.error(message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

    obj_property = []
    for item in cc_result["data"]:
        if item["editable"]:
            prop_dict = {
                "tag_code": item["bk_property_id"],
                "type": "input",
                "attrs": {"name": item["bk_property_name"], "editable": "true"},
            }
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
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_biz_id": int(biz_cc_id), "bk_supplier_account": supplier_account}
    list_service_category_return = client.cc.list_service_category(kwargs)
    if not list_service_category_return["result"]:
        message = handle_api_error("cc", "cc.list_service_category", kwargs, list_service_category_return)
        logger.error(message)
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
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_biz_id": int(biz_cc_id), "bk_supplier_account": supplier_account}
    list_service_category_return = client.cc.list_service_category(kwargs)
    if not list_service_category_return["result"]:
        message = handle_api_error("cc", "cc.list_service_category", kwargs, list_service_category_return)
        logger.error(message)
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
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_biz_id": int(biz_cc_id), "bk_supplier_account": supplier_account}
    list_service_template_return = client.cc.list_service_template(kwargs)
    if not list_service_template_return["result"]:
        message = handle_api_error("cc", "cc.list_service_template", kwargs, list_service_template_return)
        logger.error(message)
        return JsonResponse({"result": False, "data": [], "message": message})
    service_templates = []
    service_templates_untreated = list_service_template_return["data"]["info"]
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


@supplier_account_inject
def cc_search_topo(request, obj_id, category, biz_cc_id, supplier_account):
    """
    @summary: 查询对象拓扑
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_biz_id": biz_cc_id, "bk_supplier_account": supplier_account}
    cc_result = client.cc.search_biz_inst_topo(kwargs)
    if not cc_result["result"]:
        message = handle_api_error("cc", "cc.search_biz_inst_topo", kwargs, cc_result)
        logger.error(message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

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
        business = get_user_business_list(username=request.user.username)
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
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_biz_id": int(biz_cc_id), "bk_supplier_account": supplier_account}

    set_template_result = client.cc.list_set_template(kwargs)

    if not set_template_result["result"]:
        message = handle_api_error("cc", "cc.list_set_template", kwargs, set_template_result)
        logger.error(message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

    template_list = []
    for template_info in set_template_result["data"]["info"]:
        template_list.append({"value": template_info.get("id"), "text": template_info.get("name")})
    return JsonResponse({"result": True, "data": template_list})


def cc_get_editable_module_attribute(request, biz_cc_id):
    kwargs = {
        "bk_biz_id": int(biz_cc_id),
        "bk_obj_id": "module",
    }
    client = get_client_by_user(request.user.username)
    result = client.cc.search_object_attribute(kwargs)
    if not result["result"]:
        return JsonResponse({"result": False, "data": "调用cc接口失败，message={}".format(result["message"])})
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
    client = get_client_by_user(request.user.username)

    kwargs = {"bk_obj_id": "host", "bk_biz_id": int(biz_cc_id)}

    cc_result = client.cc.search_object_attribute(kwargs)

    if not cc_result["result"]:
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
    client = get_client_by_user(request.user.username)
    result = client.cc.search_object_attribute(kwargs)
    if not result["result"]:
        return JsonResponse({"result": False, "data": "调用cc接口失败，message={}".format(result["message"])})
    data = result["data"]
    set_attribute = []
    for set_item in data:
        if set_item["editable"] and set_item["bk_property_id"] != "bk_set_name":
            prop_dict = {"bk_property_id": set_item["bk_property_id"], "bk_property_name": set_item["bk_property_name"]}
            set_attribute.append(prop_dict)

    return JsonResponse({"result": True, "data": set_attribute})


def cc_search_status_options(request, biz_cc_id):
    client = get_client_by_user(request.user.username)
    kwargs = {
        "bk_biz_id": int(biz_cc_id),
        "bk_obj_id": "set",
    }
    result = client.cc.search_object_attribute(kwargs)
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


def cc_find_host_by_topo(request, biz_cc_id, bk_inst_id):
    """
    批量查询拓扑节点下的主机
    @param request:
    @param biz_cc_id: cc id
    @param bk_inst_id: 模块ID列表，以 , 分割，例如 123,234,345
    @return:
    """
    client = get_client_by_user(request.user.username)

    # 去除split后的空字符串
    bk_inst_id = filter(lambda x: x, bk_inst_id.split(","))
    params = {
        "bk_biz_id": int(biz_cc_id),
        "bk_obj_id": "module",
        "fields": ["bk_host_id", "bk_cloud_id"],
    }

    data = []
    for inst_id in bk_inst_id:
        request_params = {"bk_inst_id": int(inst_id)}
        request_params.update(params)
        data.extend(batch_request(client.cc.find_host_by_topo, request_params))

    return {"result": True, "data": data}



cc_urlpatterns = [
    url(r"^cc_get_editable_module_attribute/(?P<biz_cc_id>\d+)/$", cc_get_editable_module_attribute),
    url(r"^cc_search_object_attribute/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$", cc_search_object_attribute,),
    url(r"^cc_search_object_attribute_all/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$", cc_search_object_attribute_all,),
    url(r"^cc_search_create_object_attribute/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$", cc_search_create_object_attribute,),
    url(r"^cc_search_topo/(?P<obj_id>\w+)/(?P<category>\w+)/(?P<biz_cc_id>\d+)/$", cc_search_topo,),
    url(r"^cc_list_service_category/(?P<biz_cc_id>\w+)/(?P<bk_parent_id>\w+)/$", cc_list_service_category,),
    url(r"^cc_list_service_template/(?P<biz_cc_id>\d+)/$", cc_list_service_template,),
    url(r"^cc_get_service_category_topo/(?P<biz_cc_id>\d+)/$", cc_get_service_category_topo,),
    # IP selector
    url(r"^cc_search_topo_tree/(?P<biz_cc_id>\d+)/$", cc_search_topo_tree),
    url(r"^cc_search_host/(?P<biz_cc_id>\d+)/$", cc_search_host),
    url(r"^cc_get_mainline_object_topo/(?P<biz_cc_id>\d+)/$", cc_get_mainline_object_topo,),
    url(r"^cc_get_business_list/$", cc_get_business),
    url(r"^cc_search_dynamic_group/(?P<biz_cc_id>\d+)/$", cc_search_dynamic_group),
    # 查询集群模板
    url(r"^cc_list_set_template/(?P<biz_cc_id>\d+)/$", cc_list_set_template),
    # 主机自定义属性表格
    url(r"^cc_input_host_property/(?P<biz_cc_id>\d+)/$", cc_input_host_property),
    # 查询Set服务状态
    url(r"^cc_search_status_options/(?P<biz_cc_id>\d+)/$", cc_search_status_options),
    # 获取可更改的set属性
    url(r"^cc_get_set_attribute/(?P<biz_cc_id>\d+)/$", cc_get_editable_set_attribute),
    # 批量查询拓扑节点下的主机
    url(r"^cc_find_host_by_topo/(?P<biz_cc_id>\d+)/(?P<bk_inst_id>\d+)/$", cc_find_host_by_topo),
]
