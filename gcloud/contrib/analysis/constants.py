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


class AnalysisElement:
    # 常量池
    def __init__(self):
        self.category = 'category'
        self.business__cc_name = 'business__cc_name'
        self.business__cc_id = 'business__cc_id'
        self.state = 'status'
        self.atom_cite = 'atom_cite'
        self.atom_template = 'atom_template'
        self.atom_execute = 'atom_execute'
        self.atom_instance = 'atom_instance'
        self.template_node = 'template_node'
        self.template_cite = 'template_cite'
        self.instance_node = 'instance_node'
        self.instance_details = 'instance_details'
        self.appmaker_instance = 'appmaker_instance'
        self.create_method = 'create_method'
        self.flow_type = 'flow_type'
        self.app_maker = 'app_maker'
        self.biz_cc_id = 'biz_cc_id'

    def dict_element(self):
        # 返回常量的dict形式 key : value
        return vars(self)


AE = AnalysisElement()
