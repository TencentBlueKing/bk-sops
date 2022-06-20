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


import ujson as json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import project_inject
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.template_base.utils import read_encoded_template_data
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.apigw.views.utils import logger
from apigw_manager.apigw.decorators import apigw_require


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@project_inject
@mark_request_whether_is_trust
def import_project_template(request, project_id):
    if not request.is_trust:
        return {
            "result": False,
            "message": "you have no permission to call this api.",
            "code": err_code.REQUEST_FORBIDDEN_INVALID.code,
        }

    try:
        req_data = json.loads(request.body)
    except Exception:
        return {"result": False, "message": "invalid json format", "code": err_code.REQUEST_PARAM_INVALID.code}

    template_data = req_data.get("template_data", None)
    if not template_data:
        return {
            "result": False,
            "message": "template data can not be none",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }
    r = read_encoded_template_data(template_data)
    if not r["result"]:
        return r

    try:
        import_result = TaskTemplate.objects.import_templates(
            template_data=r["data"]["template_data"],
            override=False,
            project_id=request.project.id,
            operator=request.user.username,
        )
    except Exception as e:
        logger.exception("[API] import common tempalte error: {}".format(e))
        return {
            "result": False,
            "message": "invalid flow data or error occur, please contact administrator",
            "code": err_code.UNKNOWN_ERROR.code,
        }

    return import_result
