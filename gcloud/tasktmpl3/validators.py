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

import ujson as json

from gcloud.utils.validate import RequestValidator
from gcloud.utils.strings import check_and_rename_params
from gcloud.commons.template.utils import read_template_data_file


class FormValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        template_id = request.GET.get("template_id")

        if not template_id:
            return False, "template_id can not be empty"

        return True, ""


class ExportValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except Exception:
            return False, "request body is not a valid json"

        template_id_list = data.get("template_id_list")

        if not isinstance(template_id_list, list):
            return False, "invalid template_id_list"

        if not template_id_list:
            return False, "template_id_list can not be empty"

        return True, ""


class ImportValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        f = request.FILES.get("data_file", None)

        if not f:
            return False, "data_file can not be empty"

        override = request.POST.get("override")
        if override is None:
            return False, "override can not be empty"

        r = read_template_data_file(f)
        if not r["result"]:
            return False, r["message"]

        return True, ""


class CheckBeforeImportValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):

        f = request.FILES.get("data_file", None)

        if not f:
            return False, "data_file can not be empty"

        r = read_template_data_file(f)
        if not r["result"]:
            return False, r["message"]

        return True, ""


class GetTemplateCountValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        group_by = request.GET.get("group_by", "category")

        check_result = check_and_rename_params({}, group_by)

        if not check_result["success"]:
            return False, check_result["content"]

        return True, ""


class DrawPipelineValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except Exception:
            return False, "request body is not a valid json"

        pipeline_tree = data.get("pipeline_tree")

        if not pipeline_tree:
            return False, "pipeline_tree can not be empty"

        return True, ""
