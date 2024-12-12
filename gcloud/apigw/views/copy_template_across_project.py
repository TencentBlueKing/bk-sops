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
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from gcloud import err_code
from gcloud.apigw.decorators import (
    mark_request_whether_is_trust,
    project_inject,
    return_json_response,
)

from gcloud.apigw.views.utils import logger
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.utils import format_import_result_to_response_data
from gcloud.utils.decorators import request_validate
from gcloud.apigw.validators.copy_template_across_project import CopyTemplateAcrossProjectValidator


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@project_inject
@request_validate(CopyTemplateAcrossProjectValidator)
@mark_request_whether_is_trust
def copy_template_across_project(request, project_id):
    if not request.is_trust:
        return {
            "result": False,
            "message": "you have no permission to call this api.",
            "code": err_code.REQUEST_FORBIDDEN_INVALID.code,
        }

    params_data = json.loads(request.body)
    new_project_id = params_data["new_project_id"]
    template_id = params_data["template_id"]

    try:
        export_data = TaskTemplate.objects.export_templates([template_id], is_full=False, project_id=request.project.id)
        import_result = TaskTemplate.objects.import_templates(
            template_data=export_data,
            override=False,
            project_id=new_project_id,
            operator=request.user.username,
        )
    except Exception as e:
        logger.exception("The template fails to be copied across project: {}".format(e))
        return {
            "result": False,
            "message": "invalid flow data or error occur, please contact administrator",
            "code": err_code.UNKNOWN_ERROR.code,
        }

    return format_import_result_to_response_data(import_result)
