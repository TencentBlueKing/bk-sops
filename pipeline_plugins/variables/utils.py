# -*- coding: utf-8 -*-
import logging

from django.http import JsonResponse

from gcloud.conf import settings
from gcloud.utils.cmdb import batch_request
from gcloud.utils.handlers import handle_api_error

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
logger = logging.getLogger("root")


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


def list_biz_hosts(username, bk_biz_id, bk_supplier_account, kwargs=None):
    """
    @summary: 批量获取业务下主机
    @param kwargs:
    @param username: 执行用户
    @param bk_biz_id: 业务id
    @param bk_supplier_account:
    @return: [{'bk_set_id':'', 'bk_set_name':''}, {'bk_set_id':'', 'bk_set_name':''}]
    """
    client = get_client_by_user(username)
    params = {"bk_biz_id": bk_biz_id, "bk_supplier_account": bk_supplier_account}
    if kwargs:
        params.update(kwargs)
    return batch_request(client.cc.list_biz_hosts, params)
