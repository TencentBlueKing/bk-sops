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

import ujson as json
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from pipeline_plugins.components.utils import handle_api_error
from gcloud.conf import settings

from .utils import get_cmdb_topo_tree
from .constants import NO_ERROR, ERROR_CODES

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def cmdb_search_topo_tree(request, bk_biz_id, bk_supplier_account=''):
    """
    @summary: 获取 CMDB 上业务的拓扑树，包含空闲机和故障机模块，根节点是业务
    @param request:
    @param bk_biz_id: 业务 CMDB ID
    @param bk_supplier_account: 业务开发商账号
    @return:
    """
    result = get_cmdb_topo_tree(request.user.username, bk_biz_id, bk_supplier_account)
    return JsonResponse(result)


def cmdb_search_host(request, bk_biz_id, bk_supplier_account='', bk_supplier_id=0):
    """
    @summary: 获取 CMDB 上业务的 IP 列表，以及 agent 状态等信息
    @param request:
    @param bk_biz_id: 业务 CMDB ID
    @param bk_supplier_account: 业务开发商账号
    @param bk_supplier_id: 业务开发商ID
    @params fields: list 查询字段，默认只返回 bk_host_innerip、bk_host_name、bk_host_id, 可以查询主机的任意字段，也可以查询
                set、module、cloud、agent等信息
    @return:
    """
    fields = json.loads(request.GET.get('fields', '[]'))
    client = get_client_by_user(request.user.username)
    condition = [{
        'bk_obj_id': 'host',
        'fields': [],
    }]
    if 'set' in fields:
        condition.append({
            'bk_obj_id': 'set',
            'fields': [],
        })
    if 'module' in fields:
        condition.append({
            'bk_obj_id': 'module',
            'fields': [],
        })
    kwargs = {
        'bk_biz_id': bk_biz_id,
        'bk_supplier_account': bk_supplier_account,
        'condition': condition
    }
    host_result = client.cc.search_host(kwargs)
    if not host_result['result']:
        message = handle_api_error(_(u"配置平台(CMDB)"), 'cc.search_host', kwargs, host_result['message'])
        result = {'result': False, 'code': ERROR_CODES.API_CMDB_ERROR, 'message': message}
        return JsonResponse(result)

    host_info = host_result['data']['info']
    data = []
    default_fields = ['bk_host_innerip', 'bk_host_name', 'bk_host_id']
    fields = list(set(default_fields + fields))
    for host in host_info:
        host_detail = {field: host['host'][field] for field in fields if field in host['host']}
        if 'set' in fields:
            host_detail['set'] = host['set']
        if 'module' in fields:
            host_detail['module'] = host['module']
        if 'cloud' in fields or 'agent' in fields:
            host_detail['cloud'] = host['host']['bk_cloud_id']
        data.append(host_detail)

    if 'agent' in fields:
        agent_kwargs = {
            'bk_biz_id': bk_biz_id,
            'bk_supplier_id': bk_supplier_id,
            'hosts': [{'bk_cloud_id': host['cloud'][0]['id'], 'ip': host['bk_host_innerip']} for host in data]
        }
        agent_result = client.gse.get_agent_status(agent_kwargs)
        if not agent_result['result']:
            message = handle_api_error(_(u"管控平台(GSE)"),
                                       'gse.get_agent_status',
                                       agent_kwargs,
                                       agent_result['message'])
            result = {'result': False, 'code': ERROR_CODES.API_GSE_ERROR, 'message': message}
            return JsonResponse(result)

        agent_data = agent_result['data']
        for host in data:
            # agent在线状态，0为不在线，1为在线，-1为未知
            agent_info = agent_data.get('%s:%s' % (host['cloud'][0]['id'], host['bk_host_innerip']), {})
            host['agent'] = agent_info.get('bk_agent_alive', -1)

    result = {'result': True, 'code': NO_ERROR, 'data': data}
    return JsonResponse(result)


def cmdb_get_mainline_object_topo(request, bk_biz_id, bk_supplier_account=''):
    """
    @summary: 获取配置平台业务拓扑模型
    @param request:
    @param bk_biz_id:
    @param bk_supplier_account:
    @return:
    """
    kwargs = {
        'bk_biz_id': bk_biz_id,
        'bk_supplier_account': bk_supplier_account,
    }
    client = get_client_by_user(request.user.username)
    cc_result = client.cc.get_mainline_object_topo(kwargs)
    if not cc_result['result']:
        message = handle_api_error(_(u"配置平台(CMDB)"),
                                   'cc.get_mainline_object_topo',
                                   kwargs,
                                   cc_result['message'])
        return {'result': cc_result['result'], 'code': cc_result['code'], 'message': message}
    data = cc_result['data']
    for bk_obj in data:
        if bk_obj['bk_obj_id'] == 'host':
            bk_obj['bk_obj_name'] = 'IP'
    result = {'result': cc_result['result'], 'code': cc_result['code'], 'data': cc_result['data']}
    return JsonResponse(result)
