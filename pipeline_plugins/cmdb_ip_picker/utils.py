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

import copy

from django.utils.translation import ugettext_lazy as _

from pipeline_plugins.components.utils import handle_api_error
from gcloud.conf import settings

from .constants import NO_ERROR, ERROR_CODES

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def get_ip_picker_result(username, bk_biz_id, bk_supplier_account, kwargs):
    """
    @summary：根据前端表单数据获取合法的IP
    @param username:
    @param bk_biz_id:
    @param bk_supplier_account:
    @param kwargs:
    @return:
    """
    topo_result = get_cmdb_topo_tree(username, bk_biz_id, bk_supplier_account)
    if not topo_result['result']:
        return topo_result
    biz_topo_tree = topo_result['data'][0]

    build_result = build_cmdb_search_host_kwargs(bk_biz_id,
                                                 bk_supplier_account,
                                                 kwargs,
                                                 biz_topo_tree)
    if not build_result['result']:
        return {'result': False, 'code': ERROR_CODES.PARAMETERS_ERROR, 'data': [], 'message': build_result['message']}
    cmdb_kwargs = build_result['data']

    client = get_client_by_user(username)
    host_result = client.cc.search_host(cmdb_kwargs)
    if not host_result:
        message = handle_api_error(_(u"配置平台(CMDB)"), 'cc.search_host', cmdb_kwargs, host_result['message'])
        return {'result': False, 'data': [], 'message': message}
    host_info = host_result['data']['info']

    # IP选择器
    selector = kwargs['selectors'][0]
    if selector == 'ip':
        ip_list = ['%s:%s' % (str(host['cloud'][0]['id']), host['bk_host_innerip']) for host in kwargs['ip']]
    else:
        ip_list = []
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

    # 筛选条件
    filters = kwargs['filters']
    if filters:
        filters_dct = {}
        for ft in filters:
            filters_dct.setdefault(ft['field'], [])
            filters_dct[ft['field']] += format_condition_value(ft['value'])
        new_topo_tree = process_topo_tree_by_condition(biz_topo_tree, filters_dct)
        filter_host = set(filters_dct.pop('host', []))
        # 把拓扑筛选条件转换成 modules 筛选条件
        filter_modules = get_modules_by_condition(new_topo_tree, filters_dct)
        filter_modules_id = get_modules_id(filter_modules)
        data = [host for host in data if set(host['host_modules_id']) & set(filter_modules_id)]
        if filter_host:
            data = [host for host in data if host['bk_host_innerip'] in filter_host]

    # 过滤条件
    excludes = kwargs['excludes']
    if excludes:
        excludes_dct = {}
        for ex in excludes:
            excludes_dct.setdefault(ex['field'], [])
            excludes_dct[ex['field']] += format_condition_value(ex['value'])
        new_topo_tree = process_topo_tree_by_condition(biz_topo_tree, excludes_dct)
        exclude_host = set(excludes_dct.pop('host', []))
        # 把拓扑排除条件转换成 modules 排除条件
        exclude_modules = [] if not excludes_dct else get_modules_by_condition(new_topo_tree, excludes_dct)
        exclude_modules_id = get_modules_id(exclude_modules)
        data = [host for host in data if not (set(host['host_modules_id']) & set(exclude_modules_id))]
        if exclude_host:
            data = [host for host in data if host['bk_host_innerip'] not in exclude_host]

    result = {
        'result': True,
        'code': NO_ERROR,
        'data': data,
        'message': ''
    }
    return result


def format_condition_value(conditions):
    """
    @summary:
        ['111', '222'] -> ['111', '222']
        ['111', '222\n333'] -> ['111', '222', '333']
        ['', '222\n', ' 333  '] -> ['222', '333']
    @param conditions:
    @return:
    """
    formatted = []
    for val in conditions:
        formatted += [item for item in val.strip().split('\n') if item]
    return formatted


def build_cmdb_search_host_kwargs(bk_biz_id, bk_supplier_account, kwargs, biz_topo_tree):
    """
    @summary: 组装配置平台请求参数
    @param bk_biz_id:
    @param bk_supplier_account:
    @param kwargs:
    @param biz_topo_tree:
    @return:
    """
    cmdb_kwargs = {
        'bk_biz_id': bk_biz_id,
        'bk_supplier_account': bk_supplier_account,
        'condition': [{
            'bk_obj_id': 'module',
            'fields': ['bk_module_id', 'bk_module_name'],
            'condition': []
        }]
    }

    selector = kwargs['selectors'][0]
    if selector == 'topo':
        topo = kwargs['topo']
        if not topo:
            return {'result': False, 'data': {}, 'message': 'dynamic topo selector is empty'}
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
        cmdb_kwargs['condition'][0]['condition'] = condition

    else:
        host_list = kwargs['ip']
        if not host_list:
            return {'result': False, 'data': [], 'message': 'static ip is empty'}
        cmdb_kwargs['condition'].append({
            "bk_obj_id": "host",
            "fields": ["bk_host_id", "bk_host_innerip", "bk_host_outerip", "bk_host_name"],
            "condition": [{
                "field": "bk_host_innerip",
                "operator": "$in",
                "value": [host['bk_host_innerip'] for host in host_list]
            }]
        })
    return {'result': True, 'data': cmdb_kwargs, 'message': ''}


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


def get_modules_id(modules):
    """
    @summary: 将模块列表转换成 id 格式
    @param modules:
    @return:
    """
    return [mod.get('bk_module_id') or mod.get('bk_inst_id') for mod in modules]


def process_topo_tree_by_condition(topo_tree, condition):
    """
    @summary: 根据过滤条件保留或者排除空闲机池
    @param topo_tree:
    @param condition:
    @return:
    """
    # 筛选条件只包含set、module，不需要处理 topo_tree
    if not (set(condition.keys()) - {'set', 'module'}):
        return topo_tree
    # 筛选条件包含非set、module，那么一定不包含 topo_tree 中的空闲机池集群
    new_tree = copy.deepcopy(topo_tree)
    new_tree['child'] = [child for child in new_tree['child'] if child['bk_obj_id'] not in ['set', 'module']]
    return new_tree


def get_modules_by_condition(bk_obj, condition):
    """
    @summary: 获取拓扑树中满足条件的所有叶子(模块)节点
    @param bk_obj:
    @param condition:
    @return:
    """
    modules = []
    if bk_obj['bk_obj_id'] == 'module':
        if 'module' not in condition or bk_obj['bk_inst_name'] in condition['module']:
            modules.append(bk_obj)
    else:
        if bk_obj['bk_obj_id'] not in condition or bk_obj['bk_inst_name'] in condition[bk_obj['bk_obj_id']]:
            for child in bk_obj.get('child', []):
                modules += get_modules_by_condition(child, condition)
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


def get_cmdb_topo_tree(username, bk_biz_id, bk_supplier_account):
    """
    @summary: 从 CMDB API 获取业务完整拓扑树，包括空闲机池
    @param username:
    @param bk_biz_id:
    @param bk_supplier_account:
    @return:
    """
    client = get_client_by_user(username)
    kwargs = {
        'bk_biz_id': bk_biz_id,
        'bk_supplier_account': bk_supplier_account,
    }
    topo_result = client.cc.search_biz_inst_topo(kwargs)
    if not topo_result['result']:
        message = handle_api_error(_(u"配置平台(CMDB)"), 'cc.search_biz_inst_topo', kwargs, topo_result['message'])
        result = {'result': False, 'code': ERROR_CODES.API_CMDB_ERROR, 'message': message, 'data': []}
        return result

    inter_result = client.cc.get_biz_internal_module(kwargs)
    if not inter_result['result']:
        message = handle_api_error(_(u"配置平台(CMDB)"), 'cc.get_biz_internal_module', kwargs, inter_result['message'])
        result = {'result': False, 'code': ERROR_CODES.API_CMDB_ERROR, 'message': message, 'data': []}
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
    return {'result': True, 'code': NO_ERROR, 'data': data, 'messsage': ''}
