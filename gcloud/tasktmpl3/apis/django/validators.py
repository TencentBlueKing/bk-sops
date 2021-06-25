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

import ujson as json

from gcloud.constants import TEMPLATE_EXPORTER_SOURCE_PROJECT
from gcloud.utils.validate import RequestValidator, ObjectJsonBodyValidator
from gcloud.utils.strings import check_and_rename_params
from gcloud.template_base.utils import read_template_data_file


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

        if "template_source" in r["data"]["template_data"]:
            if r["data"]["template_data"]["template_source"] != TEMPLATE_EXPORTER_SOURCE_PROJECT:
                return False, "can not import common template"

        f.seek(0)

        return True, ""


class CheckBeforeImportValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):

        f = request.FILES.get("data_file", None)

        if not f:
            return False, "data_file can not be empty"

        r = read_template_data_file(f)
        if not r["result"]:
            return False, r["message"]

        if "template_source" in r["data"]["template_data"]:
            if r["data"]["template_data"]["template_source"] != TEMPLATE_EXPORTER_SOURCE_PROJECT:
                return False, "can not import common template"

        f.seek(0)

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


class AnalysisConstantsRefValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):
        result, message = super().validate(request, *args, **kwargs)
        if not result:
            return result, message

        obj_valid_list = ["constants", "activities", "gateways"]
        for obj_key in obj_valid_list:
            if not isinstance(self.data.get(obj_key, {}), dict):
                return False, "{} in tree is not a object".format(obj_key)

        return True, ""
