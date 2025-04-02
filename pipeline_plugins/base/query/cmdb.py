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

import ujson as json
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from gcloud.conf import settings
from pipeline_plugins.base.utils.adapter import cc_format_module_hosts
from pipeline_plugins.base.utils.inject import supplier_account_inject
from packages.bkapi.bk_cmdb.shortcuts import get_client_by_request

logger = logging.getLogger("root")


@supplier_account_inject
def cc_get_host_by_module_id(request, biz_cc_id, supplier_account):
    """
    查询模块对应主机
    :param request:
    :param biz_cc_id:
    :return:
    """
    select_module_id = json.loads(request.GET.get("query", "[]"))
    host_fields = json.loads(request.GET.get("host_fields", "[]")) or [
        "bk_host_id",
        "bk_host_name",
        "bk_cloud_id",
        "bk_host_innerip",
    ]
    select_modules = [int(x) for x in select_module_id if x.isdigit()]
    data_format = request.GET.get("format", "tree")
    # 查询 module 对应的主机
    module_hosts = cc_format_module_hosts(
        request.user.tenant_id, request.user.username, biz_cc_id, select_modules, supplier_account, data_format,
        host_fields,
    )

    return JsonResponse({"result": True, "data": module_hosts, "message": ""})


@supplier_account_inject
def cc_search_module(request, biz_cc_id, supplier_account):
    """
    查询集群下的模块
    :param request:
    :param biz_cc_id:
    :return:
    """
    try:
        bk_set_id = int(request.GET.get("bk_set_id"))
        module_fields = json.loads(request.GET.get("module_fields", "[]"))
    except ValueError as e:
        message = _(f"保存失败: 请求参数格式校验失败. 错误信息: {e} | cc_search_module")
        logger.error(message)
        return JsonResponse({"result": False, "data": {}, "message": message})
    client = get_client_by_request(request, stage=settings.BK_APIGW_STAGE_NAME)
    cc_kwargs = {
        "bk_biz_id": biz_cc_id,
        "bk_supplier_account": supplier_account,
        "bk_set_id": bk_set_id,
        "fields": module_fields,
    }
    cc_result = client.api.search_module(
        cc_kwargs,
        path_params={"bk_supplier_account": supplier_account, "bk_biz_id": biz_cc_id, "bk_set_id": bk_set_id},
        headers={"X-Bk-Tenant-Id": request.user.tenant_id},
    )
    if not cc_result["result"]:
        logger.warning(
            "client.cc.search_module ERROR###biz_cc_id=%s" "###cc_result=%s" % (biz_cc_id, json.dumps(cc_result))
        )
        return JsonResponse({"result": False, "data": {}, "message": cc_result["message"]})
    return JsonResponse({"result": True, "data": cc_result["data"], "message": ""})
