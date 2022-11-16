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
import traceback
from datetime import datetime

from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud.contrib.admin.migration_api.decorators import require_migrate_token
from gcloud.core.models import Project, ResourceConfig
from gcloud import err_code
from django.utils.translation import ugettext_lazy as _
import logging

logger = logging.getLogger("root")


@login_exempt
@csrf_exempt
@require_POST
@require_migrate_token
def register_resource_config(request):
    try:
        params = json.loads(request.body)
    except Exception as e:
        message = _(f"非法请求: 数据错误, 请求不是合法的Json格式, {e} | register_resource_config")
        logger.error(message)
        return JsonResponse(
            {
                "result": False,
                "message": message,
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    biz_id = params.get("biz_id")
    try:
        project = Project.objects.get(bk_biz_id=biz_id)
        project_id = project.id
    except Project.DoesNotExist:
        return JsonResponse(
            {
                "result": False,
                "message": "biz_id: {} has not corresponding project in v3".format(biz_id),
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )
    config_data = params.get("data", {})

    migrate_result = []
    for name, data in config_data.items():
        try:
            create_time = datetime.strptime(data["create_time"], "%Y-%m-%d %H:%M:%S")
            defaults = {
                "config_type": data["config_type"],
                "data": data["json_data"],
                "creator": data["creator"],
                "create_time": create_time,
            }
            resource_config, create = ResourceConfig.objects.update_or_create(
                project_id=project_id, name=name, defaults=defaults
            )
            # 将时间重置为旧数据的时间
            if create:
                resource_config.create_time = create_time
                resource_config.save()
        except Exception:
            migrate_result.append(
                {
                    "name": name,
                    "success": False,
                    "error": "save resource config error: {}".format(traceback.format_exc()),
                }
            )
        else:
            migrate_result.append({"name": name, "success": True, "error": None})
    return JsonResponse({"result": True, "data": migrate_result})
