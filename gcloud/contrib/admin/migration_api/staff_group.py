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
import logging
import json

from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from .decorators import require_migrate_token
from gcloud.core.models import Project, StaffGroupSet
from gcloud import err_code

logger = logging.getLogger("root")


@login_exempt
@csrf_exempt
@require_migrate_token
@require_POST
def migrate_staff_group(request):

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

    groups = params.get("info")
    bk_biz_id = params.get("biz_id")

    try:
        project = Project.objects.get(bk_biz_id=bk_biz_id)
    except Project.DoesNotExist:
        return JsonResponse(
            {
                "result": False,
                "message": "can not find project for bk_biz_id: {}".format(bk_biz_id),
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    migrate_result = []
    for group in groups:

        try:
            StaffGroupSet.objects.update_or_create(project_id=project.id, name=group["name"], defaults=group)

            # 记录同步成功人员分组
            migrate_result.append({"name": group["name"], "success": True, "error": None})
        except Exception:

            # 未处理的人员分组
            migrate_result.append(
                {
                    "name": group["name"],
                    "success": False,
                    "error": "There are multiple groups with the same name in the configuration",
                }
            )

    return JsonResponse({"result": True, "data": migrate_result})
