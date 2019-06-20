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

import json
import logging
import sys

import jsonschema
from django.http import JsonResponse
from django.forms.fields import BooleanField
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from auth_backend.plugins.shortcuts import verify_or_raise_auth_failed, batch_verify_or_raise_auth_failed
from blueapps.account.decorators import login_exempt
from pipeline.exceptions import PipelineException
from pipeline.engine import api as pipeline_api

from gcloud.constants import PROJECT
from gcloud.conf import settings
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_existence_check
from gcloud.apigw.schemas import APIGW_CREATE_PERIODIC_TASK_PARAMS, APIGW_CREATE_TASK_PARAMS
from gcloud.core.models import Project
from gcloud.core.utils import format_datetime
from gcloud.core.permissions import project_resource
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.permissions import taskflow_resource
from gcloud.periodictask.models import PeriodicTask
from gcloud.periodictask.permissions import periodic_task_resource
from gcloud.commons.template.models import CommonTemplate, replace_template_id
from gcloud.commons.template.utils import read_template_data_file
from gcloud.commons.template.permissions import common_template_resource
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.permissions import task_template_resource

if not sys.argv[1:2] == ['test'] and settings.USE_BK_OAUTH:
    try:
        from bkoauth.decorators import apigw_required
    except ImportError:
        def apigw_required(func):
            return func
else:
    def apigw_required(func):
        return func

logger = logging.getLogger("root")


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_existence_check
def get_template_list(request, project_id):
    template_source = request.GET.get('template_source', PROJECT)
    project = Project.objects.get(id=project_id)
    if not request.is_trust:
        project = Project.objects.get(id=project_id)
        verify_or_raise_auth_failed(principal_type='user',
                                    principal_id=request.user.username,
                                    resource=project_resource,
                                    action_ids=[project_resource.actions.view.id],
                                    instance=project,
                                    status=200)

    if template_source == PROJECT:
        templates = TaskTemplate.objects.select_related('pipeline_template').filter(project_id=project_id,
                                                                                    is_deleted=False)
    else:
        templates = CommonTemplate.objects.select_related('pipeline_template').filter(is_deleted=False)
    data = [
        {
            'id': tmpl.id,
            'name': tmpl.pipeline_template.name,
            'creator': tmpl.pipeline_template.creator,
            'create_time': format_datetime(tmpl.pipeline_template.create_time),
            'editor': tmpl.pipeline_template.editor,
            'edit_time': format_datetime(tmpl.pipeline_template.edit_time),
            'category': tmpl.category,
            'project_id': project_id,
            'project_name': project.name,
            'bk_biz_id': project.bk_biz_id,
            'bk_biz_name': project.name if project.from_cmdb else None
        } for tmpl in templates
    ]
    return JsonResponse({'result': True, 'data': data})


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_existence_check
def get_template_info(request, template_id, project_id):
    project = Project.objects.get(id=project_id)
    template_source = request.GET.get('template_source', PROJECT)
    if template_source == PROJECT:
        try:
            tmpl = TaskTemplate.objects.select_related('pipeline_template').get(id=template_id,
                                                                                project_id=project_id,
                                                                                is_deleted=False)
            auth_resource = task_template_resource
        except TaskTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'template[id={template_id}] of project[project_id={project_id}] does not exist'.format(
                    template_id=template_id,
                    project_id=project_id)
            }
            return JsonResponse(result)
    else:
        try:
            tmpl = CommonTemplate.objects.select_related('pipeline_template').get(id=template_id, is_deleted=False)
            auth_resource = common_template_resource
        except CommonTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'common template[id={template_id}] does not exist'.format(template_id=template_id)
            }
            return JsonResponse(result)

    if not request.is_trust:
        verify_or_raise_auth_failed(principal_type='user',
                                    principal_id=request.user.username,
                                    resource=auth_resource,
                                    action_ids=[auth_resource.actions.view.id],
                                    instance=tmpl,
                                    status=200)

    pipeline_tree = tmpl.pipeline_tree
    pipeline_tree.pop('line')
    pipeline_tree.pop('location')
    data = {
        'id': tmpl.id,
        'name': tmpl.pipeline_template.name,
        'creator': tmpl.pipeline_template.creator,
        'create_time': format_datetime(tmpl.pipeline_template.create_time),
        'editor': tmpl.pipeline_template.editor,
        'edit_time': format_datetime(tmpl.pipeline_template.edit_time),
        'category': tmpl.category,
        'project_id': project_id,
        'project_name': project.name,
        'bk_biz_id': project.bk_biz_id,
        'bk_biz_name': project.name if project.from_cmdb else None,
        'pipeline_tree': pipeline_tree
    }
    return JsonResponse({'result': True, 'data': data})


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_existence_check
def create_task(request, template_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid param format'
        })
    logger.info('apigw create_task info, template_id: {template_id}, project_id: {project_id}, params: {params}'.format(
        template_id=template_id,
        project_id=project_id,
        params=params))
    project = Project.objects.get(id=project_id)
    template_source = params.get('template_source', PROJECT)
    # 兼容老版本的接口调用
    if template_source == 'business' or template_source == PROJECT:
        try:
            tmpl = TaskTemplate.objects.select_related('pipeline_template').get(id=template_id,
                                                                                project_id=project_id,
                                                                                is_deleted=False)

            if not request.is_trust:
                verify_or_raise_auth_failed(principal_type='user',
                                            principal_id=request.user.username,
                                            resource=task_template_resource,
                                            action_ids=[task_template_resource.actions.create_task.id],
                                            instance=tmpl,
                                            status=200)
        except TaskTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'template[id={template_id}] of project[project_id={project_id}] does not exist'.format(
                    template_id=template_id,
                    project_id=project_id)
            }
            return JsonResponse(result)
    else:
        try:
            tmpl = CommonTemplate.objects.select_related('pipeline_template').get(id=template_id,
                                                                                  is_deleted=False)

            if not request.is_trust:
                perms_tuples = [(project_resource, [project_resource.actions.use_common_template.id], project),
                                (common_template_resource, [common_template_resource.actions.create_task.id], tmpl)]
                batch_verify_or_raise_auth_failed(principal_type='user',
                                                  principal_id=request.user.username,
                                                  perms_tuples=perms_tuples,
                                                  status=200)

        except CommonTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'common template[id={template_id}] does not exist'.format(template_id=template_id)
            }
            return JsonResponse(result)

    try:
        params.setdefault('flow_type', 'common')
        params.setdefault('constants', {})
        params.setdefault('exclude_task_nodes_id', [])
        jsonschema.validate(params, APIGW_CREATE_TASK_PARAMS)
    except jsonschema.ValidationError as e:
        logger.warning(u"apigw create_task raise prams error: %s" % e)
        message = 'task params is invalid: %s' % e
        return JsonResponse({'result': False, 'message': message})

    app_code = request.jwt.app.app_code if hasattr(request, 'jwt') else request.META.get('HTTP_BK_APP_CODE')
    if not app_code:
        message = 'app_code cannot be empty, make sure api gateway has sent correct params'
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
        project=project,
        pipeline_instance=data,
        category=tmpl.category,
        template_id=template_id,
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
        }})


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_existence_check
def start_task(request, task_id, project_id):
    username = request.user.username
    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id)
    if not request.is_trust:
        verify_or_raise_auth_failed(principal_type='user',
                                    principal_id=request.user.username,
                                    resource=taskflow_resource,
                                    action_ids=[taskflow_resource.actions.operate.id],
                                    instance=task,
                                    status=200)
    ctx = task.task_action('start', username)
    return JsonResponse(ctx)


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_existence_check
def operate_task(request, task_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid param format'
        })
    action = params.get('action')
    username = request.user.username
    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id, is_deleted=False)
    if not request.is_trust:
        verify_or_raise_auth_failed(principal_type='user',
                                    principal_id=request.user.username,
                                    resource=taskflow_resource,
                                    action_ids=[taskflow_resource.actions.operate.id],
                                    instance=task,
                                    status=200)
    ctx = task.task_action(action, username)
    return JsonResponse(ctx)


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_existence_check
def get_task_status(request, task_id, project_id):
    try:
        task = TaskFlowInstance.objects.get(pk=task_id, project_id=project_id, is_deleted=False)
        if not request.is_trust:
            verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        resource=taskflow_resource,
                                        action_ids=[taskflow_resource.actions.view.id],
                                        instance=task,
                                        status=200)
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
        message = 'task[id={task_id}] get status error: {error}'.format(task_id=task_id, error=e)
        logger.error(message)
        result = {'result': False, 'message': message}
        return JsonResponse(result)

    try:
        task_status = pipeline_api.get_status_tree(task_id, max_depth=99)
        TaskFlowInstance.format_pipeline_status(task_status)
    except Exception as e:
        message = 'task[id={task_id}] get status error: {error}'.format(task_id=task_id, error=e)
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
@mark_request_whether_is_trust
@project_existence_check
def query_task_count(request, project_id):
    """
    @summary: 按照不同维度统计业务任务总数
    @param request:
    @param project_id:
    @return:
    """
    if not request.is_trust:
        project = Project.objects.get(id=project_id)
        verify_or_raise_auth_failed(principal_type='user',
                                    principal_id=request.user.username,
                                    resource=project_resource,
                                    action_ids=[project_resource.actions.view.id],
                                    instance=project,
                                    status=200)

    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid param format'
        })
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

    filters = {'project_id': project_id, 'is_deleted': False}
    filters.update(conditions)
    success, content = TaskFlowInstance.objects.extend_classified_count(group_by, filters)
    if not success:
        return JsonResponse({'result': False, 'message': content})
    return JsonResponse({'result': True, 'data': content})


def info_data_from_period_task(task, detail=True):
    info = {
        'id': task.id,
        'name': task.name,
        'template_id': task.template_id,
        'creator': task.creator,
        'cron': task.cron,
        'enabled': task.enabled,
        'last_run_at': format_datetime(task.last_run_at),
        'total_run_count': task.total_run_count,
    }

    if detail:
        info['form'] = task.form
        info['pipeline_tree'] = task.pipeline_tree

    return info


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
def get_periodic_task_list(request, project_id):
    if not request.is_trust:
        project = Project.objects.get(id=project_id)
        verify_or_raise_auth_failed(principal_type='user',
                                    principal_id=request.user.username,
                                    resource=project_resource,
                                    action_ids=[project_resource.actions.view.id],
                                    instance=project,
                                    status=200)

    task_list = PeriodicTask.objects.filter(project_id=project_id)
    data = []
    for task in task_list:
        data.append(info_data_from_period_task(task, detail=False))

    return JsonResponse({'result': True, 'data': data})


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
def get_periodic_task_info(request, task_id, project_id):
    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project_id)
        if not request.is_trust:
            verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        resource=periodic_task_resource,
                                        action_ids=[periodic_task_resource.actions.edit.id],
                                        instance=task,
                                        status=200)
    except PeriodicTask.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'task(%s) does not exist' % task_id
        })

    data = info_data_from_period_task(task)
    return JsonResponse({'result': True, 'data': data})


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
def create_periodic_task(request, template_id, project_id):
    try:
        template = TaskTemplate.objects.get(pk=template_id, project_id=project_id, is_deleted=False)
        if not request.is_trust:
            verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        resource=task_template_resource,
                                        action_ids=[task_template_resource.actions.create_periodic_task.id],
                                        instance=template,
                                        status=200)
    except TaskTemplate.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'template(%s) does not exist' % template_id
        })

    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid param format'
        })

    logger.info(
        'apigw create_periodic_task info, '
        'template_id: {template_id}, project_id: {project_id}, params: {params}'.format(template_id=template_id,
                                                                                        project_id=project_id,
                                                                                        params=params))

    try:
        params.setdefault('constants', {})
        params.setdefault('exclude_task_nodes_id', [])
        jsonschema.validate(params, APIGW_CREATE_PERIODIC_TASK_PARAMS)
    except jsonschema.ValidationError as e:
        logger.warning(u"apigw create_periodic_task raise prams error: %s" % e)
        message = 'task params is invalid: %s' % e
        return JsonResponse({'result': False, 'message': message})

    exclude_task_nodes_id = params['exclude_task_nodes_id']
    pipeline_tree = template.pipeline_tree
    try:
        TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'result': False, 'message': e.message})

    for key, val in params['constants'].items():
        if key in pipeline_tree['constants']:
            pipeline_tree['constants'][key]['value'] = val

    project = Project.objects.get(id=project_id)
    name = params['name']
    cron = params['cron']

    try:
        replace_template_id(TaskTemplate, pipeline_tree)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'result': False, 'message': e.message})

    try:
        task = PeriodicTask.objects.create(
            project=project,
            template=template,
            name=name,
            cron=cron,
            pipeline_tree=pipeline_tree,
            creator=request.user.username
        )
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'result': False, 'message': e.message})

    data = info_data_from_period_task(task)
    return JsonResponse({
        'result': True,
        'data': data
    })


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
def set_periodic_task_enabled(request, task_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid param format'
        })

    enabled = params.get('enabled', False)

    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project_id)
        if not request.is_trust:
            verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        resource=periodic_task_resource,
                                        action_ids=[periodic_task_resource.actions.edit.id],
                                        instance=task,
                                        status=200)
    except PeriodicTask.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'task(%s) does not exist' % task_id
        })

    task.set_enabled(enabled)
    return JsonResponse({
        'result': True,
        'data': {
            'enabled': task.enabled
        },
    })


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
def modify_cron_for_periodic_task(request, task_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid param format'
        })

    cron = params.get('cron', {})
    tz = Project.objects.get(id=project_id).time_zone

    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project_id)
        if not request.is_trust:
            verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        resource=periodic_task_resource,
                                        action_ids=[periodic_task_resource.actions.edit.id],
                                        instance=task,
                                        status=200)
    except PeriodicTask.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'task(%s) does not exist' % task_id
        })

    try:
        task.modify_cron(cron, tz)
    except Exception as e:
        return JsonResponse({
            'result': False,
            'message': e.message
        })

    return JsonResponse({
        'result': True,
        'data': {
            'cron': task.cron
        }
    })


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
def modify_constants_for_periodic_task(request, task_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid param format'
        })

    constants = params.get('constants', {})

    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project_id)
        if not request.is_trust:
            verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        resource=periodic_task_resource,
                                        action_ids=[periodic_task_resource.actions.edit.id],
                                        instance=task,
                                        status=200)
    except PeriodicTask.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'task(%s) does not exist' % task_id
        })

    try:
        new_constants = task.modify_constants(constants)
    except Exception as e:
        return JsonResponse({
            'result': False,
            'message': e.message
        })

    return JsonResponse({
        'result': True,
        'data': new_constants
    })


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
def get_task_detail(request, task_id, project_id):
    """
    @summary: 获取任务详细信息
    @param request:
    @param task_id:
    @param project_id:
    @return:
    """
    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project_id)
        if not request.is_trust:
            verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        resource=taskflow_resource,
                                        action_ids=[taskflow_resource.actions.view.id],
                                        instance=task,
                                        status=200)
    except TaskFlowInstance.DoesNotExist:
        message = 'task[id={task_id}] of project[project_id={project_id}] does not exist'.format(
            task_id=task_id,
            project_id=project_id)
        logger.exception(message)
        return JsonResponse({'result': False, 'message': message})

    data = task.get_task_detail()
    return JsonResponse({'result': True, 'data': data})


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
def get_task_node_detail(request, task_id, project_id):
    """
    @summary: 获取节点输入输出
    @param request:
    @param task_id:
    @param project_id:
    @return:
    """
    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project_id)
        if not request.is_trust:
            verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        resource=taskflow_resource,
                                        action_ids=[taskflow_resource.actions.view.id],
                                        instance=task,
                                        status=200)
    except TaskFlowInstance.DoesNotExist:
        message = 'task[id={task_id}] of project[project_id={project_id}] does not exist'.format(
            task_id=task_id,
            project_id=project_id)
        logger.exception(message)
        return JsonResponse({'result': False, 'message': message})

    node_id = request.GET.get('node_id')
    component_code = request.GET.get('component_code')
    try:
        subprocess_stack = json.loads(request.GET.get('subprocess_stack', '[]'))
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'subprocess_stack is not a valid array json'
        })
    result = task.get_node_detail(node_id, component_code, subprocess_stack)
    return JsonResponse(result)


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
def node_callback(request, task_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid param format'
        })

    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project_id)
        if not request.is_trust:
            verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        resource=taskflow_resource,
                                        action_ids=[taskflow_resource.actions.operate.id],
                                        instance=task,
                                        status=200)
    except TaskFlowInstance.DoesNotExist:
        message = 'task[id={task_id}] of project[project_id={project_id}] does not exist'.format(
            task_id=task_id,
            project_id=project_id)
        logger.exception(message)
        return JsonResponse({'result': False, 'message': message})

    node_id = params.get('node_id')
    callback_data = params.get('callback_data')

    return JsonResponse(task.callback(node_id, callback_data))


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
def import_common_template(request):
    if not request.is_trust:
        return JsonResponse({
            'result': False,
            'message': 'you have no permission to call this api.'
        })

    f = request.FILES.get('data_file', None)
    r = read_template_data_file(f)
    if not r['result']:
        return JsonResponse(r)

    override = BooleanField().to_python(request.POST.get('override', False))

    try:
        import_result = CommonTemplate.objects.import_templates(r['data']['template_data'], override)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({
            'result': False,
            'message': 'invalid flow data or error occur, please contact administrator'
        })

    return JsonResponse(import_result)
