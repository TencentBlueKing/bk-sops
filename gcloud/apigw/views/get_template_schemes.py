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


from django.http import JsonResponse
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import api_verify_perms
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.permissions import task_template_resource
from pipeline.models import TemplateScheme

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(
    task_template_resource,
    [task_template_resource.actions.view],
    get_kwargs={'template_id': 'id', 'project_id': 'project_id'}
)
def get_template_schemes(request, project_id, template_id):
    template = TaskTemplate.objects.get(project_id=request.project.id, id=template_id)

    schemes = TemplateScheme.objects.filter(template__id=template.pipeline_template.id)

    data = []
    for s in schemes:
        data.append({
            'id': s.unique_id,
            'name': s.name,
            'data': s.data
        })

    return JsonResponse({
        'result': True,
        'data': data,
        'code': err_code.SUCCESS.code
    })
