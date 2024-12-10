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

from gcloud.utils.validate import ObjectJsonBodyValidator


class CopyTemplateAcrossProjectValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):
        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not json.loads(request.body).get("new_project_id") or not json.loads(request.body).get("template_id"):
            return False, "new_project_id and template_id is required"

        return True, ""
