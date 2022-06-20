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

import traceback
import ujson as json

from django.db import transaction
from django.views.decorators.http import require_POST
from django.http.response import JsonResponse

from gcloud.core.decorators import check_is_superuser
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.common_template.models import CommonTemplate
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.admin import AdminEditViewInterceptor


@require_POST
@iam_intercept(AdminEditViewInterceptor())
def restore_template(request):

    data = json.loads(request.body)
    template_id = data["template_id"]

    res = TaskTemplate.objects.filter(id=template_id, is_deleted=True).update(is_deleted=False)

    return JsonResponse({"result": True, "data": {"affect": res}})


def _refresh_template_notify_type(template, notify_trans_map):
    err = None
    before = None
    after = None

    try:
        before = json.loads(template.notify_type)
        after = []

        for notify_type in before:
            if notify_type in notify_trans_map:
                after.append(notify_trans_map[notify_type])
            else:
                after.append(notify_type)

        if before == after:
            return {
                "type": "task template",
                "id": template.id,
                "name": template.name,
                "before": before,
                "after": after,
                "err": err,
            }

        template.notify_type = json.dumps(after)
        template.save()
    except Exception:
        err = traceback.format_exc()

    return {
        "type": "task template",
        "id": template.id,
        "name": template.name,
        "before": before,
        "after": after,
        "err": err,
    }


@check_is_superuser()
def refresh_template_notify_type(request):

    try:
        notify_trans_map = json.loads(request.GET["notify_trans_map"])
    except Exception:
        return JsonResponse({"result": False, "message": "notify_trans_map is not a valid JSON"})

    replace_results = []

    task_templates = TaskTemplate.objects.filter(is_deleted=False)
    common_templates = CommonTemplate.objects.filter(is_deleted=False)
    with transaction.atomic():
        for template in task_templates:
            replace_results.append(_refresh_template_notify_type(template, notify_trans_map))

        for template in common_templates:
            replace_results.append(_refresh_template_notify_type(template, notify_trans_map))

    return JsonResponse({"result": True, "data": replace_results})


@iam_intercept(AdminEditViewInterceptor())
def make_template_notify_type_loadable(request):
    task_templates = TaskTemplate.objects.filter(is_deleted=False)
    common_templates = CommonTemplate.objects.filter(is_deleted=False)
    modified_project_templates = []
    modified_common_templates = []
    with transaction.atomic():
        for template in task_templates:
            tid = _modify_notify_type_loadable(template)
            if tid:
                modified_project_templates.append(tid)

        for template in common_templates:
            tid = _modify_notify_type_loadable(template)
            if tid:
                modified_common_templates.append(tid)

    return JsonResponse(
        {
            "result": True,
            "data": {
                "modified_project_templates": modified_project_templates,
                "modified_common_templates": modified_common_templates,
            },
        }
    )


def _modify_notify_type_loadable(template):
    try:
        json.loads(template.notify_type)
    except ValueError:
        template.notify_type = template.notify_type.replace("'", '"')
        template.save()
        return template.id
    except Exception:
        return f"{template.id}:{traceback.format_exc()}"
    return None
