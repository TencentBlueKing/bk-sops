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
from collections import defaultdict

from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from .decorators import require_migrate_token
from gcloud.core.models import Project, ProjectConfig, StaffGroupSet
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

    try:
        project_config, res = ProjectConfig.objects.get_or_create(project_id=project.id)
    except Exception as err:
        return JsonResponse(
            {
                "result": False,
                "message": "get project config for bk_biz_id{}: {}".format(bk_biz_id, str(err)),
                "code": err_code.OPERATION_FAIL.code,
            }
        )

    staff_groups = project_config.staff_groups.all()
    group_names = [_group["name"] for _group in groups]
    groups_query = staff_groups.filter(name__in=group_names).values()

    group_dict = defaultdict(list)
    for group_info in groups_query:
        group_dict[group_info["name"]].append(group_info)

    migrate_result = []
    for group in groups:
        group_query_count = len(group_dict[group["name"]])

        # 项目配置中人员分组不存在，则创建分组，添加到项目配置中
        if group_query_count == 0:
            group_obj = StaffGroupSet.objects.create(**group)
            project_config.staff_groups.add(group_obj)

            migrate_result.append({"name": group["name"], "success": True, "error": None})

        # 项目配置中人员分组存在则更新
        elif group_query_count == 1:
            group_id = group_dict[group["name"]][0]["id"]
            staff_groups.filter(id=group_id).update(**group)
            migrate_result.append({"name": group["name"], "success": True, "error": None})
        else:
            # 未处理的人员分组
            migrate_result.append(
                {
                    "name": group["name"],
                    "success": False,
                    "error": "There are multiple groups with the same name in the configuration",
                }
            )

    return JsonResponse({"result": True, "data": migrate_result})
