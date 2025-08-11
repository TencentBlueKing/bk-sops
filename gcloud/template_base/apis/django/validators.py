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
import json

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


class FeatPipelineValidator(FormValidator):
    pass


class ExportTemplateApiViewValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):

        template_id_list = request.data.get("template_id_list", [])
        is_full = request.data.get("is_full", None)

        if is_full is None:
            return False, "is_full is required"

        if not isinstance(template_id_list, list):
            return False, "invalid template_id_list"

        if not (template_id_list or is_full):
            return False, "template_id_list can not be empty when is_full is false"

        return True, ""


class FileValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        if not request.data.get("data_file"):
            return False, "data_file can not be empty"
        return True, ""


class YamlTemplateImportValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        data = request.data
        if not data.get("data_file"):
            return False, "data_file can not be empty"
        if not data.get("template_type"):
            return False, "template_type can not be empty"
        if data["template_type"] == "project" and not data.get("project_id"):
            return False, "project_id can not be empty when template_type=project"

        str_to_dict_fields = ("override_mappings", "refer_mappings", "template_kwargs")
        for field in str_to_dict_fields:
            if data.get(field, None) and isinstance(data[field], str):
                try:
                    request.data.update({field: json.loads(data[field])})
                except Exception as e:
                    return False, e
        if set(request.data.get("override_mappings", {}).keys()).intersection(
            set(request.data.get("refer_mappings", {}).keys())
        ):
            return False, "an imported template can not override and refer another template at the same time"
        return True, ""


class YamlTemplateExportValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        data = request.data
        if not (data.get("is_full") or (data.get("template_id_list") and isinstance(data["template_id_list"], list))):
            return False, "is_full and template_id_list can not be empty at the same time"
        if not data.get("template_type"):
            return False, "template_type can not be empty"
        if data["template_type"] == "project" and not data.get("project_id"):
            return False, "project_id can not be empty when template_type=project"
        return True, ""


class TemplateParentsValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        if not request.GET.get("template_id"):
            return False, "template_id can not be empty"

        return True, ""
