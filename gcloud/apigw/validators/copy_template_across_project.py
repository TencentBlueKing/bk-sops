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

        data = json.loads(request.body)
        if not data.get("new_project_id") or not data.get("template_ids"):
            return False, "new_project_id and template_ids are required"

        if data.get("new_project_id") == request.project.id:
            return False, "无法导入流程到到同一个项目"

        return True, ""
