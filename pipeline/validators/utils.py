# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from copy import deepcopy

from django.utils.translation import ugettext_lazy as _

from pipeline.utils.graph import Graph
from pipeline.validators.constants import ACTIVITY_RULES
from pipeline import exceptions
from pipeline.engine.utils import Stack


def get_nodes_dict(data):
    """
    get all FlowNodes of a pipeline
    """
    data = deepcopy(data)
    start = data['start_event']['id']
    end = data['end_event']['id']

    nodes = {
        start: data['start_event'],
        end: data['end_event']
    }

    nodes.update(data['activities'])
    nodes.update(data['gateways'])

    for __, node in nodes.iteritems():
        # format to list
        node['incoming'] = format_to_list(node['incoming'])
        node['outgoing'] = format_to_list(node['outgoing'])

        node['source'] = [data['flows'][incoming]['source'] for incoming in node['incoming']]
        node['target'] = [data['flows'][outgoing]['target'] for outgoing in node['outgoing']]

    return nodes


def format_to_list(notype):
    """
    format a data to list
    :return:
    """
    if isinstance(notype, list):
        return notype
    if not notype:
        return []
    return [notype]


def validate_graph_connection(data):
    """
    节点连接合法性校验

    return {
        "result": False,
        "message": {"dfc939e785c4484f884583beb9bb791a": "error message"},
        "failed_nodes": ["dfc939e785c4484f884583beb9bb791a", "8f0bf9a291dd94627997870405eeff4d"]
    }
    """
    nodes = get_nodes_dict(data)

    result = {
        "result": True,
        "message": {},
        "failed_nodes": []
    }

    for i in nodes:
        node_type = nodes[i]['type']
        rule = ACTIVITY_RULES[node_type]
        message = ""
        for j in nodes[i]['target']:
            if nodes[j]['type'] not in rule['allowed_out']:
                message += _("不能连接%s类型节点\n") % nodes[i]['type']
            if rule["min_in"] > len(nodes[i]['source']) or len(nodes[i]['source']) > rule['max_in']:
                message += _("节点的入度最大为%s，最小为%s\n") % (rule['max_in'], rule['min_in'])
            if rule["min_out"] > len(nodes[i]['target']) or len(nodes[i]['target']) > rule['max_out']:
                message += _("节点的出度最大为%s，最小为%s\n") % (rule['max_out'], rule['min_out'])
        if message:
            result['failed_nodes'].append(i)
            result["message"][i] = message

        if result['failed_nodes']:
            result['result'] = False
        return result


def validate_graph_cycle(data):
    """
    validate if a graph has not cycle

    return {
        "result": False,
        "message": "error message",
        "failed_nodes": ["dfc939e785c4484f884583beb9bb791a", "8f0bf9a291dd94627997870405eeff4d"]
    }
    """

    nodes = [data['start_event']['id'], data['end_event']['id']]
    nodes += data['gateways'].keys() + data['activities'].keys()
    flows = [[flow['source'], flow['target']] for __, flow in data['flows'].iteritems()]
    cycle = Graph(nodes, flows).get_cycle()
    if cycle:
        return {
            'result': False,
            'message': 'pipeline graph has cycle',
            'error_data': cycle
        }
    return {'result': True, 'data': []}


def find_closest_converge(converge, gateway, index):
    """
    递归查找的汇聚网关
    """
    if index not in gateway:
        return None
    if gateway[index]['match']:
        return gateway[index]['match']

    target = gateway[index]['target']
    for i in range(len(target)):
        while target[i] in gateway:
            find_closest_converge(converge, gateway, target[i])
            target[i] = converge[gateway[target[i]]['match']]['target'][0]

    converge_id = None
    # 判断各个分支的汇聚网关是否相同
    for i in range(len(target)):
        if target[i] in converge and not converge_id:
            converge_id = target[i]
        elif target[i] in converge and converge_id == target[i]:
            pass
        else:
            raise exceptions.ConvergeMatchError(u"branch of %s doesn't converge to same converge gateway" % index)

    # 判断汇聚网关有没有连接其他的节点产生的分支
    if len(converge[converge_id]['incoming']) != len(target):
        raise exceptions.ConvergeMatchError(u"%s can only converge branches from one gateway" % index)

    gateway[index]['match'] = converge_id

    return converge_id


def not_in_parallel_gateway(gateway_stack):
    for gateway in gateway_stack:
        if gateway['type'] == 'ParallelGateway':
            return False
    return True


def without_parallel_gateway(from_gateway, gateway_stack):
    if not from_gateway:
        return True
    result = True
    for gateway in reversed(gateway_stack):
        if gateway['id'] == from_gateway:
            break
        if gateway['type'] == 'ParallelGateway':
            return False
    return result


def new_find_closest_converge(converge, gateway, index, stack, end_event):
    """
    递归查找的汇聚网关
    """
    if index not in gateway:
        return None, False
    if gateway[index]['match']:
        return gateway[index]['match'], gateway[index]['share_converge']

    target = gateway[index]['target']
    stack.push(gateway[index])
    for i in range(len(target)):
        while target[i] in gateway:
            converge_id, shared = new_find_closest_converge(converge, gateway, target[i], stack, end_event)
            if converge_id:
                target[i] = converge_id
                if not shared:
                    target[i] = converge[converge_id]['target'][0]
            else:
                target[i] = end_event

    stack.pop()

    is_exg = gateway[index]['type'] == 'ExclusiveGateway'
    converge_id = None
    shared = False

    # 判断各个分支的汇聚网关是否相同
    for i in range(len(target)):
        if target[i] in converge and not converge_id:
            converge_id = target[i]
        elif target[i] in converge and converge_id == target[i]:
            pass
        elif is_exg and target[i] == end_event:
            if not_in_parallel_gateway(stack):
                pass
            else:
                raise exceptions.ConvergeMatchError(index, _(u"并行网关中的分支网关必须将所有分支汇聚到一个汇聚网关"))
        else:
            raise exceptions.ConvergeMatchError(index, _(u"该网关的分支并必须汇聚到同一个汇聚网关"))

    # 判断汇聚网关有没有连接其他的节点产生的分支
    if is_exg:
        if converge_id in converge:
            if len(converge[converge_id]['incoming']) > len(target):
                shared = True
    else:
        converge_incoming = len(converge[converge_id]['incoming'])
        gateway_outgoing = len(target)
        if converge_incoming > gateway_outgoing:
            shared = True
        elif converge_incoming < gateway_outgoing:
            raise exceptions.ConvergeMatchError(converge_id, _(u"汇聚网关没有汇聚其对应的并行网关的所有分支"))

    if not is_exg:
        gateway[index]['match'] = converge_id
        gateway[index]['share_converge'] = shared

    return converge_id, shared


def validate_converge_gateway(data):
    """
    检测对应汇聚网关及合法性
    """
    converge_list = {}
    gateway_list = {}

    for i, item in data['gateways'].iteritems():
        node = {
            "incoming": item['incoming'] if isinstance(item['incoming'], list) else [item['incoming']],
            "outgoing": item['outgoing'] if isinstance(item['outgoing'], list) else [item['outgoing']],
            "type": item["type"],
            "target": [],
            "match": None,
            "id": item['id']
        }

        for index in node['outgoing']:
            index = data['flows'][index]['target']
            while index in data['activities']:
                index = data['flows'][data['activities'][index]['outgoing']]['target']
            node['target'].append(index)

        if item['type'] == "ConvergeGateway":
            converge_list[i] = node
        else:
            gateway_list[i] = node

    for i in gateway_list:
        if not gateway_list[i]['match']:
            new_find_closest_converge(converge_list, gateway_list, i, Stack(), data['end_event']['id'])

    for i in gateway_list:
        if gateway_list[i]['match']:
            data['gateways'][i]['converge_gateway_id'] = gateway_list[i]['match']
