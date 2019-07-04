# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json
import logging

import jsonschema
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    def apigw_required(func):
        return func

from account.decorators import login_exempt
from gcloud.apigw.decorators import api_check_user_perm_of_business, api_check_user_perm_of_task
from gcloud.apigw.schemas import APIGW_CREATE_TASK_PARAMS
from gcloud.core.models import Business
from gcloud.core.utils import strftime_with_timezone
from gcloud.tasktmpl3.models import (TaskTemplate,
                                     CREATE_TASK_PERM_NAME,
                                     EXECUTE_TASK_PERM_NAME)
from gcloud.taskflow3.models import TaskFlowInstance
from pipeline.exceptions import PipelineException
from pipeline.engine import api as pipeline_api

logger = logging.getLogger("root")


@login_exempt
@require_GET
@apigw_required
@api_check_user_perm_of_business('view_business')
def get_template_list(request, bk_biz_id):
    biz = Business.objects.get(cc_id=bk_biz_id)
    templates = TaskTemplate.objects.select_related('pipeline_template').filter(business=biz, is_deleted=False)
    data = [
        {
            'id': tmpl.id,
            'name': tmpl.pipeline_template.name,
            'creator': tmpl.pipeline_template.creator,
            'create_time': strftime_with_timezone(tmpl.pipeline_template.create_time),
            'editor': tmpl.pipeline_template.editor,
            'edit_time': strftime_with_timezone(tmpl.pipeline_template.edit_time),
            'category': tmpl.category,
            'bk_biz_id': bk_biz_id,
            'bk_biz_name': biz.cc_name
        } for tmpl in templates
    ]
    return JsonResponse({'result': True, 'data': data})


@login_exempt
@require_GET
@apigw_required
@api_check_user_perm_of_business('view_business')
def get_template_info(request, template_id, bk_biz_id):
    try:
        tmpl = TaskTemplate.objects.select_related('pipeline_template', 'business')\
                                   .get(id=template_id, business__cc_id=bk_biz_id, is_deleted=False)
    except TaskTemplate.DoesNotExist:
        result = {
            'result': False,
            'message': 'template: %s of business:%s does not exist' % (template_id, bk_biz_id)
        }
        return JsonResponse(result)
    pipeline_tree = tmpl.pipeline_tree
    pipeline_tree.pop('line')
    pipeline_tree.pop('location')
    data = {
        'id': tmpl.id,
        'name': tmpl.pipeline_template.name,
        'creator': tmpl.pipeline_template.creator,
        'create_time': strftime_with_timezone(tmpl.pipeline_template.create_time),
        'editor': tmpl.pipeline_template.editor,
        'edit_time': strftime_with_timezone(tmpl.pipeline_template.edit_time),
        'category': tmpl.category,
        'bk_biz_id': bk_biz_id,
        'bk_biz_name': tmpl.business.cc_name,
        'pipeline_tree': pipeline_tree
    }
    return JsonResponse({'result': True, 'data': data})


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@api_check_user_perm_of_task(CREATE_TASK_PERM_NAME)
def create_task(request, template_id, bk_biz_id):
    biz = Business.objects.get(cc_id=bk_biz_id)
    tmpl = TaskTemplate.objects.select_related('pipeline_template').get(id=template_id, business=biz)
    params = json.loads(request.body)
    logger.info('apigw create_task info, template_id: %s, bk_biz_id: %s, params: %s' % (template_id,
                                                                                        bk_biz_id,
                                                                                        params))
    try:
        params.setdefault('flow_type', 'common')
        params.setdefault('constants', {})
        params.setdefault('exclude_task_nodes_id', [])
        jsonschema.validate(params, APIGW_CREATE_TASK_PARAMS)
    except jsonschema.ValidationError as e:
        logger.warning(u"apigw create_task raise prams error: %s" % e)
        message = 'task params is invalid: %s' % e
        return JsonResponse({'result': False, 'message': message})

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
        return JsonResponse({'result': False, 'message': e.message})
    if not result:
        return JsonResponse({'result': False, 'message': data})

    task = TaskFlowInstance.objects.create(
        business=biz,
        pipeline_instance=data,
        category=tmpl.category,
        template_id=template_id,
        create_method='api',
        create_info=request.jwt.app.app_code if hasattr(request, 'jwt') else request.META.get('HTTP_BK_APP_CODE'),
        flow_type=params.get('flow_type', 'common'),
        current_flow='execute_task' if params.get('flow_type', 'common') == 'common' else 'func_claim',
    )
    return JsonResponse({'result': True, 'data': {'task_id': task.id}})


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@api_check_user_perm_of_task(EXECUTE_TASK_PERM_NAME)
def start_task(request, task_id, bk_biz_id):
    username = request.user.username
    task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=bk_biz_id)
    ctx = task.task_action('start', username)
    return JsonResponse(ctx)


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@api_check_user_perm_of_task(EXECUTE_TASK_PERM_NAME)
def operate_task(request, task_id, bk_biz_id):
    params = json.loads(request.body)
    action = params.get('action')
    username = request.user.username
    task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=bk_biz_id)
    ctx = task.task_action(action, username)
    return JsonResponse(ctx)


@login_exempt
@require_GET
@apigw_required
@api_check_user_perm_of_business('view_business')
def get_task_status(request, task_id, bk_biz_id):
    try:
        task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=bk_biz_id)
        task_status = task.get_status()
        result = {
            'result': True,
            'data': task_status
        }
        return JsonResponse(result)
    # 请求子流程的状态，直接通过pipeline api查询
    except (ValueError, TaskFlowInstance.DoesNotExist):
        logger.info('task[id=%s] does not exist' % task_id)
    except Exception as e:
        message = 'task[id=%s] get status error: %s' % (task_id, e)
        logger.error(message)
        result = {'result': False, 'message': message}
        return JsonResponse(result)
    try:
        task_status = pipeline_api.get_status_tree(task_id, max_depth=99)
        TaskFlowInstance.format_pipeline_status(task_status)
    except Exception as e:
        message = 'task[id=%s] get status error: %s' % (task_id, e)
        logger.error(message)
        result = {'result': False, 'message': message}
        return JsonResponse(result)
    result = {
        'result': True,
        'data': task_status
    }
    return JsonResponse(result)


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@api_check_user_perm_of_business('view_business')
def query_task_count(request, bk_biz_id):
    """
    @summary: 按照不同纬度统计业务任务总数
    @param request:
    @param bk_biz_id:
    @return:
    """
    params = json.loads(request.body)
    conditions = params.get('conditions', {})
    group_by = params.get('group_by')
    if not isinstance(conditions, dict):
        message = u"query_task_list params conditions[%s] are invalid dict data" % conditions
        logger.error(message)
        return JsonResponse({'result': False, 'message': message})
    if group_by not in ['category', 'create_method', 'flow_type', 'status']:
        message = u"query_task_list params group_by[%s] is invalid" % group_by
        logger.error(message)
        return JsonResponse({'result': False, 'message': message})

    filters = {'business__cc_id': bk_biz_id, 'is_deleted': False}
    filters.update(conditions)
    success, content = TaskFlowInstance.objects.extend_classified_count(group_by, filters)
    if not success:
        return JsonResponse({'result': False, 'message': content})
    return JsonResponse({'result': True, 'data': content})
