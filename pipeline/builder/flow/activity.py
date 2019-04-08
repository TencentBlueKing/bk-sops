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

from pipeline.builder.flow.base import *  # noqa
from pipeline.utils.collections import FancyDict

__all__ = [
    'ServiceActivity',
    'SubProcess'
]


class ServiceActivity(Element):
    def __init__(self, component_code=None, *args, **kwargs):
        self.component = FancyDict({
            'code': component_code,
            'inputs': FancyDict({})
        })
        super(ServiceActivity, self).__init__(*args, **kwargs)

    def type(self):
        return PE.ServiceActivity

    def component_dict(self):
        return {
            'code': self.component.code,
            'inputs': {key: var.to_dict() for key, var in self.component.inputs.items()}
        }


class SubProcess(Element):

    def __init__(self, start, data=None, params=None, global_outputs=None, *args, **kwargs):
        self.start = start
        self.data = data
        self.params = params or {}
        self.global_outputs = FancyDict(global_outputs or {})
        super(SubProcess, self).__init__(*args, **kwargs)

    def type(self):
        return PE.SubProcess
