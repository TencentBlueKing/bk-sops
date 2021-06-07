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

from gcloud.constants import TEMPLATE_EXPORTER_SOURCE_COMMON
from gcloud.utils.validate import RequestValidator
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
            if r["data"]["template_data"]["template_source"] != TEMPLATE_EXPORTER_SOURCE_COMMON:
                return False, "can not import project template"

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
            if r["data"]["template_data"]["template_source"] != TEMPLATE_EXPORTER_SOURCE_COMMON:
                return False, "can not import project template"

        f.seek(0)

        return True, ""
