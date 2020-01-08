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

from pipeline import exceptions
from pipeline.core.data import library, var
from pipeline.component_framework.constant import ConstantPool
from pipeline.core.data.expression import ConstantTemplate, format_constant_key


def format_web_data_to_pipeline(web_pipeline, is_subprocess=False):
    """
    @summary:
    @param web_pipeline: pipeline 前端数据
    @param is_subprocess: 是否子流程
    @return:
    """
    pipeline_tree = copy.deepcopy(web_pipeline)
    constants = pipeline_tree.pop('constants')
    classification = classify_constants(constants, is_subprocess)
    # 解析隐藏全局变量互引用
    pool_obj = ConstantPool(classification['constant_pool'])
    pre_resolved_constants = pool_obj.pool
    classification['data_inputs'] = calculate_constants_type(pre_resolved_constants,
                                                             classification['data_inputs'])
    classification['data_inputs'] = calculate_constants_type(classification['params'],
                                                             classification['data_inputs'])
    pipeline_tree['data'] = {
        'inputs': classification['data_inputs'],
        'outputs': [key for key in pipeline_tree.pop('outputs')],
    }

    for act_id, act in pipeline_tree['activities'].items():
        if act['type'] == 'ServiceActivity':
            act_data = act['component'].pop('data')
            # for key, info in act_data.items():
            #     info['value'] = pool_obj.resolve_value(info['value'])

            all_inputs = calculate_constants_type(act_data,
                                                  classification['data_inputs'])
            act['component']['inputs'] = {key: value for key, value in all_inputs.items() if key in act_data}
            act['component']['global_outputs'] = classification['acts_outputs'].get(act_id, {})
        elif act['type'] == 'SubProcess':
            parent_params = {}
            act_constants = {}
            for key, info in act['pipeline']['constants'].items():
                act_constants[key] = info
                if info['show_type'] == 'show':
                    references = ConstantTemplate(info['value']).get_reference()
                    for ref_key in references:
                        formatted_key = format_constant_key(ref_key)
                        if formatted_key in classification['data_inputs']:
                            parent_params[formatted_key] = classification['data_inputs'][formatted_key]
            act['params'] = parent_params
            act['pipeline'] = format_web_data_to_pipeline(act['pipeline'], is_subprocess=True)
        else:
            raise exceptions.FlowTypeError(u"Unknown Activity type: %s" %
                                           act['type'])

    for act in pipeline_tree['activities'].values():
        format_node_io_to_list(act, o=False)

    for gateway in pipeline_tree['gateways'].values():
        format_node_io_to_list(gateway, o=False)

    format_node_io_to_list(pipeline_tree['end_event'], o=False)

    return pipeline_tree


def classify_constants(constants, is_subprocess):
    # 可以预解析的变量
    constant_pool = {}
    # 不能预解析的变量
    data_inputs = {}
    # 节点输出的变量
    acts_outputs = {}
    # 需要在父流程中解析的变量
    params = {}
    for key, info in constants.items():
        # 显示的变量可以引用父流程 context，通过 param 传参
        if info['show_type'] == 'show':
            info['is_param'] = True
        else:
            info['is_param'] = False

        if info['custom_type']:
            var_cls = library.VariableLibrary.get_var_class(info['custom_type'])

        # 输出参数
        if info['source_type'] == 'component_outputs':
            source_key = info['source_info'].values()[0][0]
            source_step = info['source_info'].keys()[0]
            data_inputs[key] = {
                'type': 'splice',
                'source_act': source_step,
                'source_key': source_key,
                'value': info['value'],
                'is_param': info['is_param']
            }
            acts_outputs.setdefault(source_step, {}).update({source_key: key})
        # 自定义的Lazy类型变量
        elif info['custom_type'] and var_cls and issubclass(var_cls, var.LazyVariable):
            data_inputs[key] = {
                'type': 'lazy',
                'source_tag': info['source_tag'],
                'custom_type': info['custom_type'],
                'value': info['value'],
                'is_param': info['is_param']
            }
        else:
            if info['show_type'] == 'show' and is_subprocess:
                params[key] = info
            # 只有隐藏的变量才需要预先解析
            else:
                constant_pool[key] = info
    result = {'constant_pool': constant_pool,
              'data_inputs': data_inputs,
              'acts_outputs': acts_outputs,
              'params': params}
    return result


def calculate_constants_type(to_calculate, calculated):
    """
    @summary:
    @param to_calculate: 待计算的变量
    @param calculated: 变量类型确定的，直接放入结果
    @return:
    """
    data = copy.deepcopy(calculated)
    for key, info in to_calculate.items():
        ref = ConstantTemplate(info['value']).get_reference()
        if ref:
            constant_type = 'splice'
        elif info.get('type', 'plain') != 'plain':
            constant_type = info['type']
        else:
            constant_type = 'plain'
        data.setdefault(key, {
            'type': constant_type,
            'value': info['value'],
            'is_param': info.get('is_param', False)
        })

    return data


def format_node_io_to_list(node, i=True, o=True):
    if i:
        node['incoming'] = node['incoming'] if isinstance(node['incoming'], list) else [node['incoming']]

    if o:
        node['outgoing'] = node['outgoing'] if isinstance(node['outgoing'], list) else [node['outgoing']]
