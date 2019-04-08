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
from django.utils.translation import ugettext_lazy as _

from gcloud.core.models import Business
from gcloud.conf import settings as gcloud_settings

logger = logging.getLogger('root')


def get_client_by_request(*args, **kwargs):
    client = gcloud_settings.ESB_GET_CLIENT_BY_REQUEST(*args, **kwargs)
    if hasattr(client, 'set_bk_api_ver'):
        client.set_bk_api_ver('')
    return client


def cc_get_set_list(request, biz_cc_id):
    """
    @summary: 获取配置平台的业务所有集群列表
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    kwargs = {
        'app_id': biz_cc_id,
    }
    cc_result = client.cc.get_topo_tree_by_app_id(kwargs)
    if not cc_result['result']:
        message = _(u"查询配置平台(CMDB)的业务[app_id=%s]的集群拓扑接口cc.get_topo_tree_by_app_id返回失败: %s") % (
            biz_cc_id, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    set_list = [{
        'value': '0',
        'text': _(u"所有集群(all)"),
    }]
    set_data = cc_result['data'].get('Children', [])
    for _set in set_data:
        set_list.append({
            'value': _set['SetID'],
            'text': _set['SetName']
        })
    return JsonResponse({'result': True, 'data': set_list})


def cc_get_module_name_list(request, biz_cc_id):
    """
    @summary: 获取配置平台的业务所有模块名称列表
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    kwargs = {
        'app_id': biz_cc_id,
    }
    cc_result = client.cc.get_modules(kwargs)
    if not cc_result['result']:
        message = _(u"查询配置平台(CMDB)的业务[app_id=%s]的所有模块接口cc.get_modules返回失败: %s") % (
            biz_cc_id, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    module_name_list = [_(u"所有模块(all)")]
    for mod in cc_result['data']:
        if mod['ModuleName'] not in module_name_list:
            module_name_list.append(mod['ModuleName'])
    module_name_list = [{'value': mod, 'text': mod} for mod in module_name_list]
    return JsonResponse({'result': True, 'data': module_name_list})


def cc_get_plat_id(request, biz_cc_id):
    client = get_client_by_request(request)
    biz = Business.objects.get(cc_id=biz_cc_id)
    cc_owner = biz.cc_owner
    cc_result = client.cc.get_plat_id({'plat_company': biz.cc_company})
    if not cc_result['result']:
        message = _(u"查询配置平台(CMDB)的云区域列表接口cc.get_plat_id返回失败: %s") % (
            biz_cc_id, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    data = []
    for plat in cc_result['data']:
        if 'plat_id' in plat:
            plat_id = plat['plat_id']
            plat_company = plat['plat_company']
            plat_name = plat['plat_name']
        else:
            plat_id = plat['platId']
            plat_company = plat['platCompany']
            plat_name = plat['platName']
        if plat_company == cc_owner:
            data.append({
                'value': plat_id,
                'text': plat_name,
            })
    return JsonResponse({'result': True, 'data': data})
