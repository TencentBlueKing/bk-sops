# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from pipeline.exceptions import ReferenceNotExistError


class Context(object):
    def __init__(self, act_outputs, output_key=None, scope=None):
        self.variables = scope or {}
        self.act_outputs = act_outputs
        self._output_key = set(output_key or [])

    def extract_output(self, activity):
        self.extract_output_from_data(activity.id, activity.data)

    def extract_output_from_data(self, activity_id, data):
        if activity_id in self.act_outputs:
            global_outputs = self.act_outputs[activity_id]
            output = data.get_outputs()
            for key in global_outputs:
                # set value to key if can not find
                # e.g. key: result
                # e.g. global_outputs[key]: result_5hoi2
                self.variables[global_outputs[key]] = output.get(key, global_outputs[key])

    def get(self, key):
        try:
            return self.variables[key]
        except KeyError:
            raise ReferenceNotExistError('reference "%s" does not exist.' % key)

    def set_global_var(self, key, val):
        self.variables[key] = val

    def update_global_var(self, var_dict):
        self.variables.update(var_dict)

    def mark_as_output(self, key):
        self._output_key.add(key)

    def write_output(self, pipeline):
        data = pipeline.data
        for key in self._output_key:
            value = self.get(key)
            from pipeline.core.data import var
            if issubclass(value.__class__, var.Variable):
                value = value.get()
                # break circle
            data.set_outputs(key, value)

    def clear(self):
        self.variables.clear()


class OutputRef(object):
    def __init__(self, key, context):
        self.key = key
        self.context = context

    @property
    def value(self):
        return self.context.get(self.key)
