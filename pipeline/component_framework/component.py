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

from pipeline.core.data.base import DataObject
from pipeline.core.data.converter import get_variable
from pipeline.exceptions import ComponentDataLackException
from pipeline.component_framework.base import ComponentMeta


class Component(object):
    __metaclass__ = ComponentMeta

    def __init__(self, data_dict):
        self.data_dict = data_dict

    @classmethod
    def outputs_format(cls):
        outputs = cls.bound_service().outputs()
        outputs = map(lambda oi: oi._asdict(), outputs)
        return outputs

    @classmethod
    def inputs_format(cls):
        inputs = cls.bound_service().inputs()
        inputs = map(lambda ii: ii._asdict(), inputs)
        return inputs

    @classmethod
    def form_is_embedded(cls):
        return getattr(cls, 'embedded_form', False)

    def clean_execute_data(self, context):
        """
        @summary: hook for subclass of Component to clean execute data with context
        @param context:
        @return:
        """
        return self.data_dict

    def data_for_execution(self, context, pipeline_data):
        data_dict = self.clean_execute_data(context)
        inputs = {}

        for key, tag_info in data_dict.items():
            if tag_info is None:
                raise ComponentDataLackException('Lack of inputs: %s' % key)

            inputs[key] = get_variable(key, tag_info, context, pipeline_data)

        return DataObject(inputs)

    def service(self):
        return self.bound_service()
