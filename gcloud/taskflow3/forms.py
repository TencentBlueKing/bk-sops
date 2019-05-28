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

import ujson as json
from django import forms


class PeriodicTaskEnabledSetForm(forms.Form):
    enabled = forms.BooleanField(
        required=False,
        initial=False
    )


class JSONField(forms.CharField):
    def __init__(self, assert_type=None, type_string='', *args, **kwargs):
        self.assert_type = assert_type
        self.type_string = type_string
        super(JSONField, self).__init__(*args, **kwargs)

    def validate(self, value):
        super(JSONField, self).validate(value)
        try:
            json_val = json.loads(value)
        except Exception:
            raise forms.ValidationError('invalid json string', code='invalid')

        if self.assert_type and not isinstance(json_val, self.assert_type):
            raise forms.ValidationError('this json string must a %s' % self.type_string, code='invalid')

    def clean(self, value):
        value = super(JSONField, self).clean(value)
        return json.loads(value)


class PeriodicTaskCronModifyForm(forms.Form):
    cron = JSONField(
        assert_type=dict,
        type_string='object',
        required=True,
    )


class PeriodicTaskConstantsModifyForm(forms.Form):
    constants = JSONField(
        assert_type=dict,
        type_string='object',
        required=True
    )
