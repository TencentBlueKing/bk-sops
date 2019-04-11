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

from copy import deepcopy
from pprint import pformat
from pipeline.exceptions import ReferenceNotExistError, InvalidOperationException


class Context(object):
    def __init__(self, act_outputs, output_key=None, scope=None):
        self.variables = scope or {}
        self.act_outputs = act_outputs
        self._output_key = set(output_key or [])
        self._change_keys = set()
        self._raw_variables = None

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
                self.change_keys.add(global_outputs[key])

    def get(self, key):
        try:
            return self.variables[key]
        except KeyError:
            raise ReferenceNotExistError('reference "%s" does not exist.' % key)

    def set_global_var(self, key, val):
        self.variables[key] = val
        self.change_keys.add(key)

    def update_global_var(self, var_dict):
        self.variables.update(var_dict)
        self.change_keys.update(var_dict.keys())

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

    def duplicate_variables(self):
        self._raw_variables = deepcopy(self.variables)

    def clear(self):
        self.variables.clear()
        if self.raw_variables:
            self.raw_variables.clear()

    def recover_variable(self):
        if self.raw_variables is None:
            raise InvalidOperationException('make sure duplicate_variables() is called before do recover')

        # collect all act output key
        act_outputs_keys = set()
        for global_outputs in self.act_outputs.values():
            for output_key in global_outputs.values():
                act_outputs_keys.add(output_key)

        # recover to Variable for which key not in act output
        for key, var in self.raw_variables.items():
            if key not in act_outputs_keys:
                self.variables[key] = deepcopy(var)

    def clear_change_keys(self):
        if hasattr(self, '_change_keys'):
            self.change_keys.clear()

    def sync_change(self, context):
        for k in context.change_keys:
            self.set_global_var(k, context.get(k))

    def __repr__(self):
        return 'variables:{}\nact_outputs:{}\n_output_key:{}'.format(
            pformat(self.variables),
            pformat(self.act_outputs),
            pformat(self._output_key)
        )

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()

    @property
    def change_keys(self):
        if not hasattr(self, '_change_keys'):
            self._change_keys = set()

        return self._change_keys

    @property
    def raw_variables(self):
        if not hasattr(self, '_raw_variables'):
            self._raw_variables = None

        return self._raw_variables


class OutputRef(object):
    def __init__(self, key, context):
        self.key = key
        self.context = context

    @property
    def value(self):
        return self.context.get(self.key)

    def __deepcopy__(self, memodict={}):
        return self
