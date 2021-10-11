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
        if data.get("override_mappings") and isinstance(data["override_mappings"], str):
            try:
                request.data.update({"override_mappings": json.loads(data["override_mappings"])})
            except Exception as e:
                return False, e
        if data.get("template_kwargs") and isinstance(data["template_kwargs"], str):
            try:
                request.data.update({"template_kwargs": json.loads(data["template_kwargs"])})
            except Exception as e:
                return False, e
        return True, ""


class YamlTemplateExportValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        data = request.data
        if not data.get("template_id_list") or not isinstance(data["template_id_list"], list):
            return False, "template_id_list can not be empty and must be a list"
        if not data.get("template_type"):
            return False, "template_type can not be empty"
        if data["template_type"] == "project" and not data.get("project_id"):
            return False, "project_id can not be empty when template_type=project"


class TemplateParentsValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        if not request.GET.get("template_id"):
            return False, "template_id can not be empty"

        return True, ""
