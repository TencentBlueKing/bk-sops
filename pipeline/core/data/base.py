# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
try:
    import ujson as json
except ImportError:
    import json

from pipeline import exceptions


class DataObject(object):
    def __init__(self, inputs, outputs=None):
        if not isinstance(inputs, dict):
            raise exceptions.DataTypeErrorException('inputs is not dict')
        self.inputs = inputs
        if outputs is None:
            outputs = {}
        if not isinstance(outputs, dict):
            raise exceptions.DataTypeErrorException('outputs is not dict')
        self.outputs = outputs

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

    def get_one_of_inputs(self, key, default=None):
        return self.inputs.get(key, default)

    def get_one_of_outputs(self, key, default=None):
        return self.outputs.get(key, default)

    def set_outputs(self, key, value):
        self.outputs.update({key: value})
        return True

    def reset_outputs(self, outputs):
        if not isinstance(outputs, dict):
            raise exceptions.DataTypeErrorException('outputs is not dict')
        self.outputs = outputs
        return True

    def update_outputs(self, dic):
        self.outputs.update(dic)

    def serializer(self):
        result = {
            'inputs': self.inputs,
            'outputs': self.outputs
        }
        return json.dumps(result)
