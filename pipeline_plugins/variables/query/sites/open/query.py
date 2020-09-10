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

from gcloud.conf import settings
from gcloud.utils.cmdb import batch_request
from gcloud.core.models import StaffGroupSet
from pipeline_plugins.variables.query.sites.open import select

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


urlpatterns += [
    url(r"^cc_get_set/(?P<biz_cc_id>\d+)/$", cc_get_set),
    url(r"^cc_get_module/(?P<biz_cc_id>\d+)/(?P<biz_set_id>\d+)/$", cc_get_module),
    url(r"^get_staff_groups/(?P<project_id>\d+)/$", get_staff_groups),
]
