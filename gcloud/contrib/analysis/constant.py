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


# 数据分析相关内容
class AnalysisElement(object):
    # 常量池
    category = 'category'
    business__cc_name = 'business__cc_name'
    business__cc_id = 'business__cc_id'
    state = 'status'
    atom_cite = 'atom_cite'
    atom_template = 'atom_template'
    atom_execute = 'atom_execute'
    atom_instance = 'atom_instance'
    template_node = 'template_node'
    template_cite = 'template_cite'
    instance_node = 'instance_node'
    instance_details = 'instance_details'
    appmaker_instance = 'appmaker_instance'
    create_method = 'create_method'
    flow_type = 'flow_type'
    app_maker = 'app_maker'
    biz_cc_id = 'biz_cc_id'
    order_by = 'order_by'
    instance_time = 'instance_time'
    type = 'type'
    group_list = ['category',
                  'biz_cc_id',
                  'atom_template',
                  'atom_execute',
                  'atom_instance',
                  'template_node',
                  'template_cite',
                  'instance_node',
                  'instance_details',
                  'instance_time',
                  'appmaker_instance',
                  'atom_cite']


AE = AnalysisElement()
