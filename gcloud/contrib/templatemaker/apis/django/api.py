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
import requests
import logging

from rest_framework.response import Response
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse

from gcloud.conf import settings
from gcloud import err_code
from gcloud.contrib.templatemaker.models import TemplateSharedRecord
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.utils.decorators import request_validate
from gcloud.contrib.templatemaker.apis.django.validators import JsonValidator


def _get_market_routing(market_url):
    return "{}/{}".format(settings.FLOW_MARKET_API_URL, market_url)


@require_GET
def get_template_market_details(request, template_id):
    project_id = json.loads(request.body).get("project_id")

    url = _get_market_routing("market/details/")

    kwargs = {
        "project_id": project_id,
    }

    # 根据业务id和模板id从第三方接口获取模板详情
    result = requests.post(url, data=kwargs)

    if not result:
        logging.exception("get market template details from third party fails")
        return Response(
            {
                "result": False,
                "message": "get market template details from third party fails",
                "code": err_code.OPERATION_FAIL.code,
            }
        )

    return True


@require_POST
@request_validate(JsonValidator)
def maker_template(request, template_id):
    if not settings.ENABLE_FLOW_MARKET:
        return False

    params = json.loads(request.body)
    project_id = params.get("project_id")
    try:
        TaskTemplate.objects.filter(id=template_id, project__id=project_id).first()
    except Exception as e:
        logging.exception(e)
        return Response(
            {"result": False, "message": "template_id does not exist", "code": err_code.OPERATION_FAIL.code}
        )

    url = _get_market_routing("prod/api/")

    kwargs = None

    headers = None

    # 调用第三方接口
    result = requests.post(url, headers=headers, data=kwargs)

    if not result:
        logging.exception("Sharing template to SRE store fails")
        return JsonResponse(
            {"result": False, "message": "Sharing template to SRE store fails", "code": err_code.OPERATION_FAIL.code}
        )

    record, created = TemplateSharedRecord.objects.get_or_create(
        project_id=params["project_id"],
        template_id=template_id,
        defaults={"template_source": params["template_source"], "create": request.user.username},
    )
    if not created:
        return JsonResponse({"result": False, "message": "Record already exists", "code": err_code.OPERATION_FAIL.code})

    return JsonResponse({"result": True, "message": "shared success", "code": err_code.SUCCESS.code})
