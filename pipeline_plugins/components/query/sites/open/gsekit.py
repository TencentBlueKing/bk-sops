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
from django.conf.urls import url

from api import BKGseKitClient

logger = logging.getLogger("root")


def gsekit_get_config_template_list(request, biz_cc_id):
    """
    通过bk_biz_id获取当前业务下所有可用的 gsekit config template
    :param biz_cc_id: 业务ID
    :param request:
    :return:
    """
    client = BKGseKitClient(request.user.username)
    template_raw_list = client.list_config_template(bk_biz_id=int(biz_cc_id))
    template_list = [
        {"text": template["template_name"], "value": template["config_template_id"]} for template in template_raw_list
    ]
    return JsonResponse({"result": True, "data": template_list})


gsekit_urlpatterns = [
    url(r"^gsekit_get_config_template_list/(?P<biz_cc_id>\d+)/$", gsekit_get_config_template_list),
]
