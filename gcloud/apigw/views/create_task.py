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


import jsonschema
import ujson as json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from pipeline.exceptions import PipelineException

from auth_backend.plugins.shortcuts import batch_verify_or_raise_auth_failed
from auth_backend.plugins.shortcuts import verify_or_raise_auth_failed
from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.apigw.schemas import APIGW_CREATE_TASK_PARAMS
from gcloud.commons.template.models import CommonTemplate
from gcloud.commons.template.permissions import common_template_resource
from gcloud.conf import settings
from gcloud.constants import PROJECT
from gcloud.core.permissions import project_resource
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.constants import NON_COMMON_TEMPLATE_TYPES
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.permissions import task_template_resource
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
@project_inject
def create_task(request, template_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid json format',
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    project = request.project
    template_source = params.get('template_source', PROJECT)

    logger.info('apigw create_task info, template_id: {template_id}, project_id: {project_id}, params: {params}'.format(
        template_id=template_id,
        project_id=project.id,
        params=params))

    # 兼容老版本的接口调用
    if template_source in NON_COMMON_TEMPLATE_TYPES:
        template_source = PROJECT
        try:
            tmpl = TaskTemplate.objects.select_related('pipeline_template').get(id=template_id,
                                                                                project_id=project.id,
                                                                                is_deleted=False)
        except TaskTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'template[id={template_id}] of project[project_id={project_id} , biz_id{biz_id}] '
                           'does not exist'.format(template_id=template_id,
                                                   project_id=project.id,
                                                   biz_id=project.bk_biz_id),
                'code': err_code.CONTENT_NOT_EXIST.code
            }
            return JsonResponse(result)

        if not request.is_trust:
            verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        resource=task_template_resource,
                                        action_ids=[task_template_resource.actions.create_task.id],
                                        instance=tmpl,
                                        status=200)
    else:
        try:
            tmpl = CommonTemplate.objects.select_related('pipeline_template').get(id=template_id,
                                                                                  is_deleted=False)
        except CommonTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'common template[id={template_id}] does not exist'.format(template_id=template_id),
                'code': err_code.CONTENT_NOT_EXIST.code
            }
            return JsonResponse(result)

        if not request.is_trust:
            perms_tuples = [(project_resource, [project_resource.actions.use_common_template.id], project),
                            (common_template_resource, [common_template_resource.actions.create_task.id], tmpl)]
            batch_verify_or_raise_auth_failed(principal_type='user',
                                              principal_id=request.user.username,
                                              perms_tuples=perms_tuples,
                                              status=200)

    try:
        params.setdefault('flow_type', 'common')
        params.setdefault('constants', {})
        params.setdefault('exclude_task_nodes_id', [])
        jsonschema.validate(params, APIGW_CREATE_TASK_PARAMS)
    except jsonschema.ValidationError as e:
        logger.warning("apigw create_task raise prams error: %s" % e)
        message = 'task params is invalid: %s' % e
        return JsonResponse({
            'result': False,
            'message': message,
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    app_code = getattr(request.jwt.app, settings.APIGW_APP_CODE_KEY)
    if not app_code:
        message = 'app_code cannot be empty, make sure api gateway has sent correct params'
        return JsonResponse({
            'result': False,
            'message': message,
            'code': err_code.CONTENT_NOT_EXIST.code
        })

    pipeline_instance_kwargs = {
        'name': params['name'],
        'creator': request.user.username,
    }
    if 'description' in params:
        pipeline_instance_kwargs['description'] = params['description']
    try:
        result, data = TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes(
            tmpl, pipeline_instance_kwargs, params['constants'], params['exclude_task_nodes_id'])
    except PipelineException as e:
        return JsonResponse({
            'result': False,
            'message': str(e),
            'code': err_code.UNKNOW_ERROR.code
        })
    if not result:
        return JsonResponse({
            'result': False,
            'message': data,
            'code': err_code.UNKNOW_ERROR.code
        })

    task = TaskFlowInstance.objects.create(
        project=project,
        pipeline_instance=data,
        category=tmpl.category,
        template_id=template_id,
        template_source=template_source,
        create_method='api',
        create_info=app_code,
        flow_type=params.get('flow_type', 'common'),
        current_flow='execute_task' if params.get('flow_type', 'common') == 'common' else 'func_claim',
    )
    return JsonResponse({
        'result': True,
        'data': {
            'task_id': task.id,
            'task_url': task.url,
            'pipeline_tree': task.pipeline_tree
        },
        'code': err_code.SUCCESS.code
    })
