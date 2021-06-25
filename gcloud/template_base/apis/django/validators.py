# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from gcloud.utils.validate import RequestValidator


class BatchFormValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        data = request.data

        template_list = data.get("templates")

        if not isinstance(template_list, list):
            return False, "invalid template_list"

        if not template_list:
            return False, "template_id_list can not be empty"

        return True, ""


class FormValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        if not request.GET.get("template_id"):
            return False, "template_id can not be empty"

        return True, ""


class ExportTemplateApiViewValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):

        template_id_list = request.data.get("template_id_list")

        if not isinstance(template_id_list, list):
            return False, "invalid template_id_list"

        if not template_id_list:
            return False, "template_id_list can not be empty"

        return True, ""
