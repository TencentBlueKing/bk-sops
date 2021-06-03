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

import json
import traceback

from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud.contrib.admin.migration_api.decorators import require_migrate_token
from gcloud.constants import TASK_CATEGORY
from gcloud import err_code
from gcloud.label.models import Label, TemplateLabelRelation
from gcloud.tasktmpl3.models import TaskTemplate


@login_exempt
@csrf_exempt
@require_POST
@require_migrate_token
def migrate_template_category(request):
    try:
        params = json.loads(request.body)
    except Exception as e:
        return JsonResponse(
            {
                "result": False,
                "message": "request body is not a valid json: {}".format(str(e)),
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    project_id = params.get("project_id")
    creator = params.get("creator", "admin")

    MIGRATE_LABEL_COLOR = "#b3eafa"
    category_mappings = {}
    existing_labels = Label.objects.filter(project_id=project_id).values("id", "name")
    label_info = {label["name"]: label["id"] for label in existing_labels}
    for category_code, category_name in TASK_CATEGORY:
        if category_name in label_info:
            category_mappings[category_code] = label_info[category_name]
        elif category_code != "Default":
            label = Label(
                name=category_name,
                description=category_code,
                is_default=False,
                creator=creator,
                color=MIGRATE_LABEL_COLOR,
                project_id=project_id,
            )
            label.save()
            category_mappings[category_code] = label.id

    task_templates = TaskTemplate.objects.filter(project__id=project_id, is_deleted=False).values("id", "category")
    label_relationships = [
        TemplateLabelRelation(template_id=template["id"], label_id=category_mappings[template["category"]])
        for template in task_templates
        if template["category"] in category_mappings
    ]
    try:
        TemplateLabelRelation.objects.bulk_create(label_relationships, ignore_conflicts=True)
    except Exception as e:
        return JsonResponse(
            {
                "result": False,
                "error": "migrate template category to labels error: {} \n {}".format(e, traceback.format_exc()),
            }
        )

    return JsonResponse({"result": True, "data": "migrate template category to labels success"})
