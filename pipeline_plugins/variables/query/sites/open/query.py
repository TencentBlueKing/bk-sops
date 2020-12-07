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

from django.conf.urls import url
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from gcloud.conf import settings
from gcloud.constants import BIZ_INTERNAL_MODULE
from gcloud.utils.cmdb import batch_request
from gcloud.core.models import StaffGroupSet
from pipeline_plugins.base.utils.inject import supplier_account_inject
from pipeline_plugins.variables.query.sites.open import select
from pipeline_plugins.variables.utils import get_service_template_list, get_set_list

logger = logging.getLogger("root")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

urlpatterns = select.select_urlpatterns


def cc_get_set(request, biz_cc_id):
    """
    批量获取业务下所有集群
    @param request: 请求信息
    @param biz_cc_id: 业务ID
    @return:
    """
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_biz_id": int(biz_cc_id), "fields": ["bk_set_name", "bk_set_id"]}
    cc_set_result = batch_request(client.cc.search_set, kwargs)
    logger.info("[cc_get_set] cc_set_result: {cc_set_result}".format(cc_set_result=cc_set_result))
    result = [{"value": set_item["bk_set_id"], "text": set_item["bk_set_name"]} for set_item in cc_set_result]

    return JsonResponse({"result": True, "data": result})


def cc_get_module(request, biz_cc_id, biz_set_id):
    """
    批量获取业务下所有模块
    @param request: 请求信息
    @param biz_cc_id: 业务ID
    @param biz_set_id: 集群ID
    @return:
    """
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_biz_id": int(biz_cc_id), "bk_set_id": int(biz_set_id), "fields": ["bk_module_name", "bk_module_id"]}
    cc_module_result = batch_request(client.cc.search_module, kwargs)
    logger.info("[cc_get_module] cc_module_result: {cc_module_result}".format(cc_module_result=cc_module_result))
    result = [
        {"value": module_item["bk_module_id"], "text": module_item["bk_module_name"]}
        for module_item in cc_module_result
    ]

    return JsonResponse({"result": True, "data": result})


def get_staff_groups(request, project_id):
    """
    获取业务对应的人员分组
    """

    staff_groups = StaffGroupSet.objects.filter(project_id=project_id, is_deleted=False).values("id", "name")
    staff_groups = [{"text": group["name"], "value": group["id"]} for group in staff_groups]

    return JsonResponse({"result": True, "data": staff_groups})


@supplier_account_inject
def cc_get_set_list(request, biz_cc_id, supplier_account):
    """
    @summary: 批量获取业务下所有集群，过滤掉name相同的集群
    @param request:
    @param biz_cc_id:
    @param supplier_account:
    @return:
    """
    cc_set_result = get_set_list(request.user.username, biz_cc_id, supplier_account)
    set_name_list = []
    result = []
    for set_item in cc_set_result:
        if set_item["bk_set_name"] in set_name_list:
            continue
        result.append({"value": set_item["bk_set_name"], "text": set_item["bk_set_name"]})
        set_name_list.append(set_item["bk_set_name"])
    result.insert(0, {"value": "all", "text": _("所有集群(all)")})

    return JsonResponse({"result": True, "data": result})


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
    service_templates_untreated = get_service_template_list(request.user.username, biz_cc_id, supplier_account)
    service_templates = []
    for template_untreated in service_templates_untreated:
        if template_untreated["name"] not in BIZ_INTERNAL_MODULE:
            template = {
                "value": template_untreated["name"],
                "text": template_untreated["name"],
            }
            service_templates.append(template)
    # 为服务模板列表添加一个all选项
    if request.GET.get("all"):
        service_templates.insert(0, {"value": "all", "text": _("所有模块(all)")})

    # 添加空闲机, 故障机和待回收模块选项
    service_templates.extend([
        {"value": _("空闲机"), "text": _("空闲机")},
        {"value": _("待回收"), "text": _("待回收")},
        {"value": _("故障机"), "text": _("故障机")}
    ])
    return JsonResponse({"result": True, "data": service_templates, "message": "success"})


def cc_get_set_group(request, biz_cc_id):
    """
    通过bk_biz_id获取当前业务下所有集群类型的动态分组
    :param biz_cc_id: 业务ID
    :param request:
    :param operator: 操作者
    :return:
    """
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_biz_id": int(biz_cc_id), "condition": {"bk_obj_id": "set"}}
    group_info = batch_request(client.cc.search_dynamic_group, kwargs, limit=200)
    group_data = []
    for group in group_info:
        group_data.append({"text": group["name"], "value": group["id"]})
    return JsonResponse({"result": True, "data": group_data})


urlpatterns += [
    url(r"^cc_get_set/(?P<biz_cc_id>\d+)/$", cc_get_set),
    url(r"^cc_get_module/(?P<biz_cc_id>\d+)/(?P<biz_set_id>\d+)/$", cc_get_module),
    url(r"^cc_get_set_list/(?P<biz_cc_id>\d+)/$", cc_get_set_list),
    url(r"^cc_get_service_template_list/(?P<biz_cc_id>\d+)/$", cc_list_service_template),
    url(r"^cc_get_set_group/(?P<biz_cc_id>\d+)/$", cc_get_set_group),
    url(r"^get_staff_groups/(?P<project_id>\d+)/$", get_staff_groups),
]
