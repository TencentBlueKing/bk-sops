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

# unified_api_utils.py：项目流程和公共流程api接口的统一实现，减少重复代码
from django.http import JsonResponse

from gcloud import err_code


def base_batch_form(request, template_model_cls, filters):
    """批量获取表单数据统一接口"""
    templates_data = request.data.get("templates")
    template_ids = [int(template["id"]) for template in templates_data]
    versions = [template["version"] for template in templates_data]

    if len(template_ids) != len(versions):
        return JsonResponse({"result": False, "data": "", "message": "", "code": err_code.REQUEST_PARAM_INVALID.code})

    filters["id__in"] = template_ids
    filters["is_deleted"] = False
    templates = template_model_cls.objects.filter(**filters)

    data = {
        template.id: [
            {
                "form": template.get_form(),
                "outputs": template.get_outputs(),
                "version": template.version,
                "is_current": True,
            }
        ]
        for template in templates
    }
    for template, version in zip(templates, versions):
        data[template.id].append(
            {
                "form": template.get_form(version),
                "outputs": template.get_outputs(version),
                "version": version,
                "is_current": False,
            }
        )

    return JsonResponse({"result": True, "data": data, "message": "", "code": err_code.SUCCESS.code})
