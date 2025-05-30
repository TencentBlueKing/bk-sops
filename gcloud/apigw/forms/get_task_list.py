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


class GetTaskListForm(forms.Form):
    is_started = forms.BooleanField(required=False)
    is_finished = forms.BooleanField(required=False)
    keyword = forms.CharField(required=False)
    executor = forms.CharField(required=False)
    create_method = forms.CharField(required=False)
    template_id = forms.CharField(required=False)
    without_count = forms.BooleanField(required=False)
    template_ids = forms.CharField(required=False)
    is_child_taskflow = forms.BooleanField(required=False)

    def clean_template_ids(self):
        template_ids = self.cleaned_data["template_ids"]
        if not template_ids:
            return []
        return [id.strip() for id in template_ids.split(",") if id.strip()]
