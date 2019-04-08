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

from django.utils.translation import ugettext_lazy as _

from pipeline_plugins.components.utils import handle_api_error

from gcloud.conf.default_settings import ESB_GET_CLIENT_BY_USER as get_client_by_user


def get_ip_picker_result(username, bk_biz_id, bk_supplier_account, kwargs):
    selector = kwargs['selectors'][0]
    filters = kwargs['filters']
    excludes = kwargs['excludes']

    cc_kwargs = {
        'bk_biz_id': bk_biz_id,
        'bk_supplier_account': bk_supplier_account,
        'condition': [{
            'bk_obj_id': 'module',
            'fields': ['bk_module_id', 'bk_module_name'],
            'condition': []
        }]
    }

    topo_result = get_cmdb_topo_tree(username, bk_biz_id, bk_supplier_account)
    if not topo_result['result']:
        return topo_result
    biz_topo_tree = topo_result['data'][0]

    if selector == 'topo':
        topo = kwargs['topo']
        if not topo:
            return {'result': False, 'data': [], 'message': ''}
        # transfer topo to modules
        topo_dct = {}
        for tp in topo:
            topo_dct.setdefault(tp['bk_obj_id'], []).append(tp['bk_inst_id'])
        topo_objects = get_objects_of_topo_tree(biz_topo_tree, topo_dct)
        topo_modules = []
        for obj in topo_objects:
            topo_modules += get_modules_of_bk_obj(obj)
        topo_modules_id = get_modules_id(topo_modules)

        condition = [{
            'field': 'bk_module_id',
            'operator': '$in',
            'value': topo_modules_id
        }]
        cc_kwargs['condition'][0]['codition'] = condition

    else:
        host_list = kwargs['ip']
        if not host_list:
            return []
        ip_list = ['%s:%s' % (str(host['cloud'][0]['id']), host['bk_host_innerip']) for host in host_list]
        cc_kwargs['condition'].append({
            "bk_obj_id": "host",
            "fields": ["bk_host_id", "bk_host_innerip", "bk_host_outerip", "bk_host_name"],
            "condition": [{
                "field": "bk_host_innerip",
                "operator": "$in",
                "value": [host['bk_host_innerip'] for host in host_list]
            }]
        })

    client = get_client_by_user(username)
    host_result = client.cc.search_host(cc_kwargs)
    if not host_result:
        message = handle_api_error(_(u"配置平台(CMDB)"), 'cc.search_host', cc_kwargs, host_result['message'])
        return {'result': False, 'data': [], 'message': message}
    host_info = host_result['data']['info']
    data = []
    for host in host_info:
        host_modules_id = get_modules_id(host['module'])
        if selector == 'topo' or '%s:%s' % (str(host['host']['bk_cloud_id'][0]['id']),
                                            host['host']['bk_host_innerip']) in ip_list:
            data.append({
                'bk_host_id': host['host']['bk_host_id'],
                'bk_host_innerip': host['host']['bk_host_innerip'],
                'bk_host_outerip': host['host']['bk_host_outerip'],
                'bk_host_name': host['host']['bk_host_name'],
                'bk_cloud_id': host['host']['bk_cloud_id'][0]['id'],
                'host_modules_id': host_modules_id
            })

    if filters:
        filters_dct = {}
        for ft in filters:
            filters_dct.setdefault(ft['field'], [])
            filters_dct[ft['field']] += ft['value']
        filter_modules = get_modules_of_filters(biz_topo_tree, filters_dct)
        filter_modules_id = get_modules_id(filter_modules)
        data = [host for host in data if set(host['host_modules_id']) & set(filter_modules_id)]
        if 'ip' in filters_dct:
            data = [host for host in data if host['bk_host_innerip'] in filters_dct['ip']]

    if excludes:
        excludes_dct = {}
        for ex in filters:
            excludes_dct.setdefault(ex['field'], [])
            excludes_dct[ex['field']] += ex['value']
        exclude_modules = get_modules_of_filters(biz_topo_tree, excludes_dct)
        exclude_modules_id = get_modules_id(exclude_modules)
        data = [host for host in data if not set(host['host_modules_id']) & set(exclude_modules_id)]
        if 'ip' in excludes_dct:
            data = [host for host in data if host['bk_host_innerip'] not in excludes_dct['ip']]

    result = {
        'result': True,
        'code': 0,
        'data': data,
        'message': ''
    }
    return result


def get_modules_id(modules):
    return [mod.get('bk_module_id') or mod.get('bk_inst_id') for mod in modules]


def get_modules_of_filters(bk_obj, filters_dct):
    """
    @summary: 获取拓扑树中满足条件的所有叶子(模块)节点
    @param bk_obj:
    @param filters_dct:
    @return:
    """
    modules = []
    if bk_obj['bk_obj_id'] == 'module':
        if 'module' not in filters_dct or bk_obj['bk_inst_name'] in filters_dct['module']:
            modules.append(bk_obj)
    else:
        if bk_obj['bk_obj_id'] not in filters_dct or bk_obj['bk_inst_name'] in filters_dct[bk_obj['bk_obj_id']]:
            for child in bk_obj.get('child', []):
                modules += get_modules_of_filters(child, filters_dct)
    return modules


def get_objects_of_topo_tree(bk_obj, obj_dct):
    """
    @summary: 获取满足obj_dict条件中的所有节点
    @param bk_obj: 拓扑树
    @param obj_dct: 拓扑节点限制
    @return:
    """
    bk_objects = []
    if bk_obj['bk_inst_id'] in obj_dct.get(bk_obj['bk_obj_id'], []):
        bk_objects.append(bk_obj)
    else:
        for child in bk_obj.get('child', []):
            bk_objects += get_objects_of_topo_tree(child, obj_dct)
    return bk_objects


def get_modules_of_bk_obj(bk_obj):
    """
    @summary: 获取配置平台某个节点下的所有叶子(模块)节点
    @param bk_obj:
    @return:
    """
    modules = []
    if bk_obj['bk_obj_id'] == 'module':
        modules.append(bk_obj)
    for child in bk_obj.get('child', []):
        modules += get_modules_of_bk_obj(child)
    return modules


def get_cmdb_topo_tree(username, bk_biz_id, bk_supplier_account):
    client = get_client_by_user(username)
    kwargs = {
        'bk_biz_id': bk_biz_id,
        'bk_supplier_account': bk_supplier_account,
    }
    topo_result = client.cc.search_biz_inst_topo(kwargs)
    if not topo_result['result']:
        message = handle_api_error(_(u"配置平台(CMDB)"), 'cc.search_biz_inst_topo', kwargs, topo_result['message'])
        result = {'result': False, 'code': 100, 'message': message, 'data': []}
        return result

    inter_result = client.cc.get_biz_internal_module(kwargs)
    if not inter_result['result']:
        message = handle_api_error(_(u"配置平台(CMDB)"), 'cc.get_biz_internal_module', kwargs, inter_result['message'])
        result = {'result': False, 'code': 101, 'message': message, 'data': []}
        return result

    inter_data = inter_result['data']
    data = topo_result['data']
    if 'bk_set_id' in inter_data:
        default_set = {
            'default': 1,
            'bk_obj_id': 'set',
            'bk_obj_name': _(u"集群"),
            'bk_inst_id': inter_data['bk_set_id'],
            'bk_inst_name': inter_data['bk_set_name'],
            'child': [{
                'default': 1,
                'bk_obj_id': 'module',
                'bk_obj_name': _(u"模块"),
                'bk_inst_id': mod['bk_module_id'],
                'bk_inst_name': mod['bk_module_name'],
            } for mod in inter_data['module']]
        }
        data[0]['child'].insert(0, default_set)
    return {'result': True, 'code': 0, 'data': data, 'messsage': ''}
