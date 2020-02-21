# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from django.http import JsonResponse
import ujson as json

from gcloud.conf import settings

from pipeline_plugins.base.utils.adapter import cc_format_module_hosts
from pipeline_plugins.base.utils.inject import supplier_account_inject

logger = logging.getLogger('root')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


@supplier_account_inject
def cc_get_host_by_module_id(request, biz_cc_id, supplier_account):
    """
    查询模块对应主机
    :param request:
    :param biz_cc_id:
    :return:
    """
    select_module_id = json.loads(request.GET.get('query', '[]'))
    host_fields = json.loads(request.GET.get('host_fields', '[]'))
    select_modules = [int(x) for x in select_module_id]
    data_format = request.GET.get('format', 'tree')
    # 查询module对应的主机
    module_hosts = cc_format_module_hosts(request.user.username,
                                          biz_cc_id,
                                          select_modules,
                                          supplier_account,
                                          data_format,
                                          host_fields)

    return JsonResponse({'result': True, 'data': module_hosts, 'message': ''})
