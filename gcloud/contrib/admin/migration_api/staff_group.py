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

from blueapps.account.decorators import login_exempt
from .decorators import require_migrate_token
from gcloud.core.models import ProjectConfig, StaffGroupSet

logger = logging.getLogger("root")


@login_exempt
@csrf_exempt
@require_migrate_token
def staff_group_register(request):
    group_info = json.loads(request.body)

    groups = group_info.get('info')
    project_id = group_info.get("biz_id")

    try:
        project_config = ProjectConfig.objects.get(project_id=project_id)
    except ProjectConfig.DoesNotExist:
        message = "Project({}) config does not exist".format(project_id)
        logger.error(message)
        return JsonResponse({
            "result": False,
            "message": message
        })

    untreated_group = []
    staff_groups = project_config.staff_groups.all()
    group_names = [_group["name"] for _group in groups]
    groups_query = staff_groups.filter(name__in=group_names).values()

    group_dict = defaultdict(list)
    for group_info in groups_query:
        group_dict[group_info["name"]].append(group_info)

    for group in groups:
        group_query_count = len(group_dict[group["name"]])

        # 项目中分组不存在，则创建分组，添加到项目配置中
        if group_query_count == 0:
            group_obj = StaffGroupSet.objects.create(**group)
            project_config.staff_groups.add(group_obj)

        # 项目中人员分组存在则更新
        elif group_query_count == 1:
            group_id = group_dict[group["name"]][0]["id"]
            staff_groups.filter(id=group_id).update(**group)

        else:
            # 未处理的人员分组
            untreated_group.append(group["name"])

    if untreated_group:
        message = "Group({}) register failed, project({})".format(
            ",".join(untreated_group), project_id)
        logger.error(message)
        result = {
            "result": False,
            "message": message,
            "data": untreated_group
        }
    else:
        result = {
            "result": True,
            "message": "register success",
            "data": []
        }

    return JsonResponse(result)
