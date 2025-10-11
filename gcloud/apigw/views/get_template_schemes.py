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


from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.http import require_GET
from pipeline.models import TemplateScheme

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import FlowViewInterceptor
from gcloud.tasktmpl3.models import TaskTemplate


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(FlowViewInterceptor())
def get_template_schemes(request, project_id, template_id):
    template = TaskTemplate.objects.get(project_id=request.project.id, id=template_id)

    schemes = TemplateScheme.objects.filter(template__id=template.pipeline_template.id)

    data = []
    for s in schemes:
        data.append({"id": s.unique_id, "name": s.name, "data": s.data})

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
