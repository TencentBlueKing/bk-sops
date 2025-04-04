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
import logging
import traceback

from blueapps.account.decorators import login_exempt
from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from pipeline.models import TemplateScheme

from gcloud import err_code
from gcloud.conf import settings
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate

from .decorators import require_migrate_token

logger = logging.getLogger("root")


def do_migrate_app_maker(project: Project, app_makers):
    migrate_result = []
    for app_maker in app_makers:
        # 尝试获取存在的轻应用
        try:
            exist_app = AppMaker.objects.get(project=project, name=app_maker["name"])
        except AppMaker.DoesNotExist:
            app_maker_id = None
        else:
            app_maker_id = exist_app.id

        # 尝试获取存在的模板
        template_qs = TaskTemplate.objects.filter(
            project=project, pipeline_template__name=app_maker["template_name"]
        ).values("id", "pipeline_template__id")
        template_count = template_qs.count()
        if template_count != 1:
            migrate_result.append(
                {
                    "name": app_maker["name"],
                    "success": False,
                    "error": "Found {} template for name: {}".format(template_count, app_maker["template_name"]),
                }
            )
            continue
        else:
            template_id = template_qs[0]["id"]
            pipeline_template_id = template_qs[0]["pipeline_template__id"]

        # 尝试获取存在的执行方案
        scheme_qs = TemplateScheme.objects.filter(
            template_id=pipeline_template_id, name=app_maker["scheme_name"]
        ).values("id")
        scheme_count = scheme_qs.count()
        if scheme_count != 1:
            migrate_result.append(
                {
                    "name": app_maker["name"],
                    "success": False,
                    "error": "Found {} template for scheme: {}".format(scheme_count, app_maker["scheme_name"]),
                }
            )
            continue
        else:
            template_scheme_id = scheme_qs[0]["id"]

        save_app_maker_params = {
            "id": app_maker_id,
            "name": app_maker["name"],
            "desc": app_maker["desc"],
            "username": app_maker["username"],
            "link_prefix": "{}appmaker/".format(settings.APP_HOST),
            "template_id": template_id,
            "template_scheme_id": template_scheme_id,
            "logo_content": None,
        }

        try:
            AppMaker.objects.save_app_maker(
                project_id=project.id, app_params=save_app_maker_params, tenant_id=project.tenant_id
            )
        except Exception:
            migrate_result.append(
                {
                    "name": app_maker["name"],
                    "success": False,
                    "error": "save app maker error: {}".format(traceback.format_exc()),
                }
            )
        else:
            migrate_result.append({"name": app_maker["name"], "success": True, "error": None})

    return migrate_result


@login_exempt
@csrf_exempt
@require_migrate_token
@require_POST
def migrate_app_maker(request):

    try:
        params = json.loads(request.body)
    except Exception as e:
        message = _(f"非法请求: 数据错误, 请求不是合法的Json格式, {e} | migrate_app_maker")
        logger.error(message)
        return JsonResponse(
            {
                "result": False,
                "message": message,
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    bk_biz_id = params.get("bk_biz_id")

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

    migrate_result = do_migrate_app_maker(project, params.get("app_makers", []))

    return JsonResponse({"result": True, "data": migrate_result})
