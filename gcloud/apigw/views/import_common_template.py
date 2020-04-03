# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


import ujson as json
from django.forms.fields import BooleanField
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.commons.template.models import CommonTemplate
from gcloud.commons.template.utils import read_encoded_template_data
from gcloud.apigw.views.utils import logger

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
def import_common_template(request):
    if not request.is_trust:
        return JsonResponse(
            {
                "result": False,
                "message": "you have no permission to call this api.",
                "code": err_code.REQUEST_FORBIDDEN_INVALID.code,
            }
        )

    try:
        req_data = json.loads(request.body)
    except Exception:
        return JsonResponse(
            {
                "result": False,
                "message": "invalid json format",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    template_data = req_data.get("template_data", None)
    if not template_data:
        return JsonResponse(
            {
                "result": False,
                "message": "template data can not be none",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )
    r = read_encoded_template_data(template_data)
    if not r["result"]:
        return JsonResponse(r)

    override = BooleanField().to_python(req_data.get("override", False))

    try:
        import_result = CommonTemplate.objects.import_templates(
            r["data"]["template_data"], override
        )
    except Exception as e:
        logger.exception("[API] import common tempalte error: {}".format(e))
        return JsonResponse(
            {
                "result": False,
                "message": "invalid flow data or error occur, please contact administrator",
                "code": err_code.UNKNOW_ERROR.code,
            }
        )

    return JsonResponse(import_result)
