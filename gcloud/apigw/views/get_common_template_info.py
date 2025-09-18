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


from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.common_template.models import CommonTemplate
from gcloud.apigw.views.utils import format_template_data, process_pipeline_constants
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import CommonFlowViewInterceptor
from apigw_manager.apigw.decorators import apigw_require


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@iam_intercept(CommonFlowViewInterceptor())
def get_common_template_info(request, template_id):
    include_subprocess = request.GET.get("include_subprocess", None)
    include_constants = request.GET.get("include_constants", None)
    include_notify = request.GET.get("include_notify", None)
    try:
        tmpl = CommonTemplate.objects.select_related("pipeline_template").get(id=template_id, is_deleted=False)
    except CommonTemplate.DoesNotExist:
        result = {
            "result": False,
            "message": "common template[id={template_id}] does not exist".format(template_id=template_id),
            "code": err_code.CONTENT_NOT_EXIST.code,
        }
        return result
    data = format_template_data(template=tmpl, include_subprocess=include_subprocess, include_notify=include_notify)
    if include_constants:
        data["template_constants"] = process_pipeline_constants(data["pipeline_tree"])

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
