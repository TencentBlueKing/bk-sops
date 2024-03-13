# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django import forms


class GetFunctionalizationTaskListForm(forms.Form):
    status = forms.CharField(required=False)
    task_id_in = forms.CharField(required=False)
    id_in = forms.CharField(required=False)
    project_id = forms.IntegerField(required=False)
    create_time_lte = forms.DateTimeField(required=False)
    create_time_gte = forms.DateTimeField(required=False)

    def _list_field_validate(self, field_name):
        field_value = self.cleaned_data.get(field_name)
        if field_value:
            try:
                field_value = field_value.split(",")
            except Exception:
                raise forms.ValidationError("{} 参数格式错误，需要以逗号分隔的字符串".format(field_name))
        return field_value

    def clean_id_in(self):
        return self._list_field_validate("id_in")

    def clean_task_id_in(self):
        return self._list_field_validate("task_id_in")
