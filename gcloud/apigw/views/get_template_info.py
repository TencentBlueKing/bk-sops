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

from auth_backend.plugins.shortcuts import verify_or_raise_auth_failed
from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.commons.template.models import CommonTemplate
from gcloud.commons.template.permissions import common_template_resource
from gcloud.constants import PROJECT
from gcloud.tasktmpl3.constants import NON_COMMON_TEMPLATE_TYPES
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.permissions import task_template_resource
from gcloud.apigw.views.utils import format_template_data

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
def get_template_info(request, template_id, project_id):
    project = request.project
    template_source = request.GET.get('template_source', PROJECT)
    if template_source in NON_COMMON_TEMPLATE_TYPES:
        try:
            tmpl = TaskTemplate.objects.select_related('pipeline_template').get(id=template_id,
                                                                                project_id=project.id,
                                                                                is_deleted=False)
        except TaskTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'template[id={template_id}] of project[project_id={project_id}, biz_id={biz_id}] '
                           'does not exist'.format(template_id=template_id,
                                                   project_id=project.id,
                                                   biz_id=project.bk_biz_id),
                'code': err_code.CONTENT_NOT_EXIST.code
            }
            return JsonResponse(result)
        auth_resource = task_template_resource
    else:
        try:
            tmpl = CommonTemplate.objects.select_related('pipeline_template').get(id=template_id, is_deleted=False)
        except CommonTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'common template[id={template_id}] does not exist'.format(template_id=template_id),
                'code': err_code.CONTENT_NOT_EXIST.code
            }
            return JsonResponse(result)
        auth_resource = common_template_resource

    if not request.is_trust:
        verify_or_raise_auth_failed(principal_type='user',
                                    principal_id=request.user.username,
                                    resource=auth_resource,
                                    action_ids=[auth_resource.actions.view.id],
                                    instance=tmpl,
                                    status=200)

    return JsonResponse({
        'result': True,
        'data': format_template_data(tmpl, project),
        'code': err_code.SUCCESS.code
    })
