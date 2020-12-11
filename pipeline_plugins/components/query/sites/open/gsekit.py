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

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url

from api import BKGseKitClient
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")


def gsekit_get_config_template_list(request, biz_cc_id):
    """
    通过bk_biz_id获取当前业务下所有可用的 gsekit config template
    :param biz_cc_id: 业务ID
    :param request:
    :return:
    """
    client = BKGseKitClient(request.user.username)
    template_raw_info = client.list_config_template(bk_biz_id=int(biz_cc_id))
    if not template_raw_info["result"]:
        message = handle_api_error(_("gsekit"), "config.template_list", {"biz_cc_id": biz_cc_id}, template_raw_info)
        logger.error(message)
        return JsonResponse(
            {"result": template_raw_info["result"], "code": template_raw_info.get("code", "-1"), "message": message})
    template_list = []
    for template in template_raw_info["data"]:
        template_list.append({"text": template["template"], "value": template["id"]})
    return JsonResponse({"result": True, "data": template_list})


gsekit_urlpatterns = [
    url(r"^gsekit_get_config_template_list/(?P<biz_cc_id>\d+)/$", gsekit_get_config_template_list),
]
