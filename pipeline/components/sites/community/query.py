# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import importlib
import logging

from pipeline.conf import settings
from django.http import JsonResponse

from blueapps.utils.esbclient import get_client_by_request
from pipeline.components.utils import cc_get_inner_ip_by_module_id

atoms_cc = importlib.import_module('pipeline.components.collections.sites.%s.cc' % settings.RUN_VER)

logger = logging.getLogger('root')


def cc_search_object_attribute(request, obj_id, biz_cc_id):
    """
    @summary: 获取对象自定义属性
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    client.set_bk_api_ver('v2')
    kwargs = {
        'bk_obj_id': obj_id,
    }
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result['result']:
        message = atoms_cc.cc_handle_api_error('cc.search_object_attribute', kwargs, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    obj_property = []
    for item in cc_result['data']:
        if item['editable']:
            obj_property.append({
                'value': item['bk_property_id'],
                'text': item['bk_property_name']
            })

    return JsonResponse({'result': True, 'data': obj_property})


def cc_search_create_object_attribute(request, obj_id, biz_cc_id):
    client = get_client_by_request(request)
    client.set_bk_api_ver('v2')
    kwargs = {
        'bk_obj_id': obj_id,
    }
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result['result']:
        message = atoms_cc.cc_handle_api_error('cc.search_object_attribute', kwargs, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    obj_property = []
    for item in cc_result['data']:
        if item['editable']:
            prop_dict = {
                'tag_code': item['bk_property_id'],
                'type': "input",
                'attrs': {
                    'name': item['bk_property_name'],
                    'editable': 'true',
                },
            }
            if item['bk_property_id'] in ['bk_set_name']:
                prop_dict["attrs"]["validation"] = [
                    {
                        "type": "required"
                    }
                ]
            obj_property.append(prop_dict)

    return JsonResponse({'result': True, 'data': obj_property})


def cc_format_topo_data(data, obj_id):
    tree_data = []
    data_flag = False
    for item in data:
        tree_item = {
            'id': item['bk_inst_id'],
            'label': item['bk_inst_name']
        }

        if item['bk_obj_id'] == obj_id:
            tree_data.append(tree_item)
            data_flag = True

        if item['bk_obj_id'] != obj_id and item.get('child'):
            tree_item['children'], data_flag = cc_format_topo_data(item['child'], obj_id)
            if data_flag:
                tree_data.append(tree_item)

    return tree_data, data_flag


def cc_format_picker_topo_data(data, obj_id):
    tree_data = []
    data_flag = False
    for item in data:
        tree_item = {
            'id': '%s_%s' % (item['bk_obj_id'], item['bk_inst_id']),
            'label': item['bk_inst_name']
        }

        if item['bk_obj_id'] == obj_id:
            tree_data.append(tree_item)
            data_flag = True

        if item['bk_obj_id'] != obj_id and item.get('child'):
            tree_item['children'], data_flag = cc_format_picker_topo_data(item['child'], obj_id)
            if data_flag:
                tree_data.append(tree_item)

    return tree_data, data_flag


def cc_format_prev_topo_data(data, obj_id):
    tree_data = []
    for item in data:
        if item['bk_obj_id'] != obj_id:
            tree_item = {
                'id': item['bk_inst_id'],
                'label': item['bk_inst_name']
            }

            if item.get('child'):
                tree_item['children'] = cc_format_prev_topo_data(item['child'], obj_id)

            tree_data.append(tree_item)
    return tree_data


def cc_format_module_hosts(username, biz_cc_id, module_id_list):
    module_host_list = cc_get_inner_ip_by_module_id(username, biz_cc_id, module_id_list)
    module_host_dict = {}
    for item in module_host_list:
        for module in item['module']:
            if module_host_dict.get('module_%s' % module['bk_module_id']):
                module_host_dict['module_%s' % module['bk_module_id']].append({
                    'id': '%s_%s' % (module['bk_module_id'], item['host']['bk_host_innerip']),
                    'label': item['host']['bk_host_innerip']
                })
            else:
                module_host_dict['module_%s' % module['bk_module_id']] = [{
                    'id': '%s_%s' % (module['bk_module_id'], item['host']['bk_host_innerip']),
                    'label': item['host']['bk_host_innerip']
                }]
    return module_host_dict


def cc_search_topo(request, obj_id, category, biz_cc_id):
    """
    @summary: 查询对象拓扑
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    client.set_bk_api_ver('v2')
    kwargs = {
        'bk_biz_id': biz_cc_id
    }
    cc_result = client.cc.search_biz_inst_topo(kwargs)
    if not cc_result['result']:
        message = atoms_cc.cc_handle_api_error('cc.search_biz_inst_topo', kwargs, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    if category == "normal":
        cc_topo, _ = cc_format_topo_data(cc_result['data'], obj_id)
    elif category == "prev":
        cc_topo = cc_format_prev_topo_data(cc_result['data'], obj_id)
    elif category == "picker":
        cc_topo, _ = cc_format_picker_topo_data(cc_result['data'], obj_id)
    else:
        cc_topo = []

    return JsonResponse({'result': True, 'data': cc_topo})


def cc_get_host_by_module_id(request, biz_cc_id):
    """
    查询模块对应主机
    :param request:
    :param biz_cc_id:
    :return:
    """
    select_module_id = request.GET.getlist('query', [])
    # 查询module对应的主机
    module_hosts = cc_format_module_hosts(request.user.username, biz_cc_id, map(lambda x: int(x), select_module_id))

    for del_id in (set(module_hosts.keys()) - set(map(lambda x: 'module_%s' % x, select_module_id))):
        del module_hosts[del_id]

    return JsonResponse({'result': True if module_hosts else False, 'data': module_hosts})
