# # -*- coding: utf-8 -*-
import logging

from django.http import JsonResponse

from gcloud.conf import settings
from gcloud.utils.cmdb import batch_request
from gcloud.utils.handlers import handle_api_error

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
logger = logging.getLogger("root")


def filter_ip(origin_ip_str, filter_ip_str):
    """
    @summary 过滤ip
    @param origin_ip_str: 用逗号分隔的ip字符串
    @param filter_ip_str: 用逗号分隔的ip字符串
    @return: 返回在filter_ip_str中的origin_ip_str中的ip
    """
    origin_ip_list = origin_ip_str.split(",")
    filter_ip_list = filter_ip_str.split(",")
    return ",".join([ip for ip in origin_ip_list if ip in filter_ip_list])


def get_list_by_selected_names(set_names, set_list):
    """
    @summary 通过集群名称(列表)获取集群{bk_set_id, bk_set_name}对象列表
    @param set_names: aa,bb or ['aa', 'bb']
    @param set_list: [{"bk_set_id":1, "bk_set_name":"bb"}]
    @return: [{"bk_set_id":1, "bk_set_name":"bb"}]
    """
    set_name_list = set_names
    if not isinstance(set_names, list):
        set_name_list = set_names.split(",")
    return [set_item for set_item in set_list if set_item["bk_set_name"] in set_name_list]


def get_service_template_list_by_names(service_template_names, service_template_list):
    """
    @summary 通过服务模板名称获取服务模板{id, name}对象列表
    @param service_template_names: aa,bb
    @param service_template_list: [{"id":1, "name":"bb"}]
    @return: [{"id":1, "name":"bb"}]
    """
    service_template_name_list = service_template_names
    if not isinstance(service_template_names, list):
        service_template_name_list = service_template_names.split(",")
    return [
        service_template_item
        for service_template_item in service_template_list
        if service_template_item["name"] in service_template_name_list
    ]


def get_module_list(username, bk_biz_id, kwargs=None):
    """
    @summary: 查询模块
    @param kwargs:
    @param username: 执行用户名
    @param bk_biz_id: 业务id
    @return: [{'bk_module_id':'', 'bk_module_name':''}...]
    """
    client = get_client_by_user(username)
    params = {
        "bk_biz_id": bk_biz_id,
    }
    if kwargs:
        params.update(kwargs)
    module_list_result = client.cc.find_module_batch(params)
    if not module_list_result["result"]:
        message = handle_api_error("cc", "cc.find_module_batch", kwargs, module_list_result)
        logger.error(message)
        return JsonResponse({"result": False, "data": [], "message": message})
    return module_list_result["data"]


def get_set_list(username, bk_biz_id, bk_supplier_account, kwargs=None):
    """
    @summary: 批量获取业务下所有集群
    @param kwargs:
    @param username: 执行用户名
    @param bk_biz_id: 业务id
    @param bk_supplier_account: 供应商账号
    @return: [{'bk_set_id':'', 'bk_set_name':''}, {'bk_set_id':'', 'bk_set_name':''}]
    """
    client = get_client_by_user(username)
    params = {
        "bk_biz_id": bk_biz_id,
        "bk_supplier_account": bk_supplier_account,
        "fields": ["bk_set_name", "bk_set_id"],
    }
    if kwargs:
        params.update(kwargs)
    return batch_request(client.cc.search_set, params)


def get_service_template_list(username, bk_biz_id, bk_supplier_account):
    """
    @summary: 批量获取服务模板列表
    @param username: 执行接口用户名
    @param bk_biz_id: 业务id
    @param bk_supplier_account:
    @return: [{'id':'', 'name':''}, {'id':'', 'name':''}]
    """
    client = get_client_by_user(username)
    kwargs = {"bk_biz_id": int(bk_biz_id), "bk_supplier_account": bk_supplier_account}
    list_service_template_return = client.cc.list_service_template(kwargs)
    if not list_service_template_return["result"]:
        message = handle_api_error("cc", "cc.list_service_template", kwargs, list_service_template_return)
        logger.error(message)
        return JsonResponse({"result": False, "data": [], "message": message})
    return list_service_template_return["data"]["info"]


def find_module_with_relation(bk_biz_id, username, set_ids, service_template_ids, fields):
    """
    @summary
    @param bk_biz_id: 业务id
    @param username: 用户名
    @param set_ids: 集群id列表
    @param service_template_ids: 服务模板id列表
    @param fields: 查询的字段
    @return: 查询结果
    """
    result = []

    client = get_client_by_user(username)
    params = {"bk_biz_id": bk_biz_id, "bk_service_template_ids": service_template_ids, "fields": fields}
    start = 0
    step = 200

    while start < len(set_ids):
        params["bk_set_ids"] = set_ids[start : start + step]
        module_list_result = batch_request(client.cc.find_module_with_relation, params)
        result.extend(module_list_result)
        start += step
    return result


def list_biz_hosts(username, bk_biz_id, bk_supplier_account, kwargs=None):
    """
    @summary: 批量获取业务下主机
    @param kwargs:
    @param username: 执行用户
    @param bk_biz_id: 业务id
    @param bk_supplier_account:
    @return: [{'bk_host_innerip':''}, {'bk_host_innerip':''}]
    """
    client = get_client_by_user(username)
    params = {"bk_biz_id": bk_biz_id, "bk_supplier_account": bk_supplier_account}
    if kwargs:
        params.update(kwargs)
    return batch_request(client.cc.list_biz_hosts, params)
