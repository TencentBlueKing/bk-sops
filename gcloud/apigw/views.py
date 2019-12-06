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

import logging

import ujson as json
import jsonschema
from django.http import JsonResponse
from django.forms.fields import BooleanField
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from blueapps.account.decorators import login_exempt
from auth_backend.plugins.shortcuts import verify_or_raise_auth_failed, batch_verify_or_raise_auth_failed
from pipeline.exceptions import PipelineException
from pipeline.engine import api as pipeline_api
from pipeline_web.parser.validator import validate_web_pipeline_tree
from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.models import ComponentModel
from pipeline_web.drawing import draw_pipeline

from gcloud import err_code
from gcloud.conf import settings
from gcloud.constants import PROJECT, BUSINESS, ONETIME
from gcloud.apigw.decorators import (
    mark_request_whether_is_trust,
    api_verify_perms,
    api_verify_proj_perms,
    project_inject
)
from gcloud.apigw.schemas import APIGW_CREATE_PERIODIC_TASK_PARAMS, APIGW_CREATE_TASK_PARAMS
from gcloud.core.constant import TASK_CATEGORY, TASK_NAME_MAX_LENGTH
from gcloud.core.utils import format_datetime, name_handler, pipeline_node_name_handle
from gcloud.core.permissions import project_resource
from gcloud.periodictask.models import PeriodicTask
from gcloud.periodictask.permissions import periodic_task_resource
from gcloud.commons.template.models import CommonTemplate, replace_template_id
from gcloud.commons.template.utils import read_encoded_template_data
from gcloud.commons.template.permissions import common_template_resource
from gcloud.tasktmpl3 import varschema
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.contrib.analysis.analyse_items import task_flow_instance
from gcloud.tasktmpl3.permissions import task_template_resource
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.permissions import taskflow_resource

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required

logger = logging.getLogger("root")


def format_template_list_data(templates, project=None):
    data = []
    for tmpl in templates:
        item = {
            'id': tmpl.id,
            'name': tmpl.pipeline_template.name,
            'creator': tmpl.pipeline_template.creator,
            'create_time': format_datetime(tmpl.pipeline_template.create_time),
            'editor': tmpl.pipeline_template.editor,
            'edit_time': format_datetime(tmpl.pipeline_template.edit_time),
            'category': tmpl.category,
        }

        if project:
            item.update({
                'project_id': project.id,
                'project_name': project.name,
                'bk_biz_id': project.bk_biz_id,
                'bk_biz_name': project.name if project.from_cmdb else None
            })

        data.append(item)

    return data


def format_template_data(template, project=None):
    pipeline_tree = template.pipeline_tree
    pipeline_tree.pop('line')
    pipeline_tree.pop('location')
    varschema.add_schema_for_input_vars(pipeline_tree)

    data = {
        'id': template.id,
        'name': template.pipeline_template.name,
        'creator': template.pipeline_template.creator,
        'create_time': format_datetime(template.pipeline_template.create_time),
        'editor': template.pipeline_template.editor,
        'edit_time': format_datetime(template.pipeline_template.edit_time),
        'category': template.category,
        'pipeline_tree': pipeline_tree
    }
    if project:
        data.update({
            'project_id': project.id,
            'project_name': project.name,
            'bk_biz_id': project.bk_biz_id,
            'bk_biz_name': project.name if project.from_cmdb else None
        })

    return data


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_proj_perms([project_resource.actions.view])
def get_template_list(request, project_id):
    template_source = request.GET.get('template_source', PROJECT)
    project = request.project
    if template_source in {BUSINESS, PROJECT}:
        templates = TaskTemplate.objects.select_related('pipeline_template').filter(project_id=project.id,
                                                                                    is_deleted=False)
    else:
        templates = CommonTemplate.objects.select_related('pipeline_template').filter(is_deleted=False)
    return JsonResponse({
        'result': True,
        'data': format_template_list_data(templates, project),
        'code': err_code.SUCCESS.code
    })


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
def get_template_info(request, template_id, project_id):
    project = request.project
    template_source = request.GET.get('template_source', PROJECT)
    if template_source in {BUSINESS, PROJECT}:
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


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
def get_common_template_list(request):
    templates = CommonTemplate.objects.select_related('pipeline_template').filter(is_deleted=False)

    return JsonResponse({
        'result': True,
        'data': format_template_list_data(templates),
        'code': err_code.SUCCESS.code
    })


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
def get_common_template_info(request, template_id):
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
        'data': format_template_data(template=tmpl),
        'code': err_code.SUCCESS.code
    })


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
    if template_source in {BUSINESS, PROJECT}:
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


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(taskflow_resource,
                  [taskflow_resource.actions.operate],
                  get_kwargs={'task_id': 'id', 'project_id': 'project_id'})
def start_task(request, task_id, project_id):
    username = request.user.username
    project = request.project
    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project.id)
    ctx = task.task_action('start', username)
    return JsonResponse(ctx)


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(taskflow_resource,
                  [taskflow_resource.actions.operate],
                  get_kwargs={'task_id': 'id', 'project_id': 'project_id'})
def operate_task(request, task_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid json format',
            'code': err_code.REQUEST_PARAM_INVALID.code
        })
    action = params.get('action')
    username = request.user.username
    project = request.project
    task = TaskFlowInstance.objects.get(pk=task_id, project_id=project.id, is_deleted=False)
    ctx = task.task_action(action, username)
    return JsonResponse(ctx)


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(taskflow_resource,
                  [taskflow_resource.actions.view],
                  get_kwargs={'task_id': 'id', 'project_id': 'project_id'})
def get_task_status(request, task_id, project_id):
    project = request.project
    try:
        task = TaskFlowInstance.objects.get(pk=task_id, project_id=project.id, is_deleted=False)
        task_status = task.get_status()
        result = {
            'result': True,
            'data': task_status,
            'code': err_code.SUCCESS.code
        }
        return JsonResponse(result)
    # 请求子流程的状态，直接通过pipeline api查询
    except (ValueError, TaskFlowInstance.DoesNotExist):
        logger.info('task[id=%s] does not exist' % task_id)
    except Exception as e:
        message = 'task[id={task_id}] get status error: {error}'.format(task_id=task_id, error=e)
        logger.error(message)
        result = {
            'result': False,
            'message': message,
            'code': err_code.UNKNOW_ERROR.code
        }
        return JsonResponse(result)

    try:
        task_status = pipeline_api.get_status_tree(task_id, max_depth=99)
        TaskFlowInstance.format_pipeline_status(task_status)
    except Exception as e:
        message = 'task[id={task_id}] get status error: {error}'.format(task_id=task_id, error=e)
        logger.error(message)
        result = {
            'result': False,
            'message': message,
            'code': err_code.UNKNOW_ERROR.code
        }
        return JsonResponse(result)
    result = {
        'result': True,
        'data': task_status,
        'code': err_code.SUCCESS.code
    }
    return JsonResponse(result)


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_proj_perms([project_resource.actions.view])
def query_task_count(request, project_id):
    """
    @summary: 按照不同维度统计业务任务总数
    @param request:
    @param project_id:
    @return:
    """
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid json format',
            'code': err_code.REQUEST_PARAM_INVALID.code
        })
    project = request.project
    conditions = params.get('conditions', {})
    group_by = params.get('group_by')
    if not isinstance(conditions, dict):
        message = "query_task_list params conditions[%s] are invalid dict data" % conditions
        logger.error(message)
        return JsonResponse({
            'result': False,
            'message': message,
            'code': err_code.REQUEST_PARAM_INVALID.code
        })
    if group_by not in ['category', 'create_method', 'flow_type', 'status']:
        message = "query_task_list params group_by[%s] is invalid" % group_by
        logger.error(message)
        return JsonResponse({
            'result': False,
            'message': message,
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    filters = {'project_id': project.id, 'is_deleted': False}
    filters.update(conditions)
    success, content = task_flow_instance.dispatch(group_by, filters)
    if not success:
        return JsonResponse({
            'result': False,
            'message': content,
            'code': err_code.UNKNOW_ERROR.code
        })
    return JsonResponse({
        'result': True,
        'data': content,
        'code': err_code.SUCCESS.code
    })


def info_data_from_period_task(task, detail=True):
    info = {
        'id': task.id,
        'name': task.name,
        'template_id': task.template_id,
        'template_source': task.template_source,
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
@project_inject
@api_verify_proj_perms([project_resource.actions.view])
def get_periodic_task_list(request, project_id):
    project = request.project
    task_list = PeriodicTask.objects.filter(project_id=project.id)
    data = []
    for task in task_list:
        data.append(info_data_from_period_task(task, detail=False))

    return JsonResponse({
        'result': True,
        'data': data,
        'code': err_code.SUCCESS.code
    })


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_proj_perms([project_resource.actions.view])
def get_periodic_task_info(request, task_id, project_id):
    project = request.project
    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project.id)
    except PeriodicTask.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'task(%s) does not exist' % task_id,
            'code': err_code.CONTENT_NOT_EXIST.code
        })

    data = info_data_from_period_task(task)
    return JsonResponse({
        'result': True,
        'data': data,
        'code': err_code.SUCCESS.code
    })


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
def create_periodic_task(request, template_id, project_id):
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
    logger.info(
        'apigw create_periodic_task info, '
        'template_id: {template_id}, project_id: {project_id}, params: {params}'.format(template_id=template_id,
                                                                                        project_id=project.id,
                                                                                        params=params))

    if template_source in {BUSINESS, PROJECT}:
        template_source = PROJECT
        try:
            template = TaskTemplate.objects.get(pk=template_id, project_id=project.id, is_deleted=False)
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
                                        action_ids=[task_template_resource.actions.create_periodic_task.id],
                                        instance=template,
                                        status=200)
    else:
        try:
            template = CommonTemplate.objects.get(id=template_id, is_deleted=False)
        except CommonTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'common template[id={template_id}] does not exist'.format(template_id=template_id),
                'code': err_code.CONTENT_NOT_EXIST.code
            }
            return JsonResponse(result)

        if not request.is_trust:
            perms_tuples = [(project_resource,
                             [project_resource.actions.use_common_template.id],
                             project),
                            (common_template_resource,
                             [common_template_resource.actions.create_periodic_task.id],
                             template)
                            ]
            batch_verify_or_raise_auth_failed(principal_type='user',
                                              principal_id=request.user.username,
                                              perms_tuples=perms_tuples,
                                              status=200)

    try:
        params.setdefault('constants', {})
        params.setdefault('exclude_task_nodes_id', [])
        jsonschema.validate(params, APIGW_CREATE_PERIODIC_TASK_PARAMS)
    except jsonschema.ValidationError as e:
        logger.warning("apigw create_periodic_task raise prams error: %s" % e)
        message = 'task params is invalid: %s' % e
        return JsonResponse({
            'result': False,
            'message': message,
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    exclude_task_nodes_id = params['exclude_task_nodes_id']
    pipeline_tree = template.pipeline_tree
    try:
        TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({
            'result': False,
            'message': str(e),
            'code': err_code.UNKNOW_ERROR.code
        })

    for key, val in list(params['constants'].items()):
        if key in pipeline_tree['constants']:
            pipeline_tree['constants'][key]['value'] = val

    name = params['name']
    cron = params['cron']

    try:
        replace_template_id(TaskTemplate, pipeline_tree)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({
            'result': False,
            'message': str(e),
            'code': err_code.UNKNOW_ERROR.code
        })

    try:
        task = PeriodicTask.objects.create(
            project=project,
            template=template,
            template_source=template_source,
            name=name,
            cron=cron,
            pipeline_tree=pipeline_tree,
            creator=request.user.username
        )
    except Exception as e:
        logger.exception(e)
        return JsonResponse({
            'result': False,
            'message': str(e),
            'code': err_code.UNKNOW_ERROR.code
        })

    data = info_data_from_period_task(task)
    return JsonResponse({
        'result': True,
        'data': data,
        'code': err_code.SUCCESS.code
    })


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(periodic_task_resource,
                  [periodic_task_resource.actions.edit],
                  get_kwargs={'task_id': 'id', 'project_id': 'project_id'})
def set_periodic_task_enabled(request, task_id, project_id):
    project = request.project
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid json format',
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    enabled = params.get('enabled', False)

    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project.id)
    except PeriodicTask.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'task(%s) does not exist' % task_id,
            'code': err_code.CONTENT_NOT_EXIST.code
        })

    task.set_enabled(enabled)
    return JsonResponse({
        'result': True,
        'data': {
            'enabled': task.enabled
        },
        'code': err_code.SUCCESS.code
    })


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(periodic_task_resource,
                  [periodic_task_resource.actions.edit],
                  get_kwargs={'task_id': 'id', 'project_id': 'project_id'})
def modify_cron_for_periodic_task(request, task_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid json format',
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    project = request.project
    cron = params.get('cron', {})
    tz = project.time_zone

    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project.id)
    except PeriodicTask.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'task(%s) does not exist' % task_id,
            'code': err_code.CONTENT_NOT_EXIST.code
        })

    try:
        task.modify_cron(cron, tz)
    except Exception as e:
        return JsonResponse({
            'result': False,
            'message': str(e),
            'code': err_code.UNKNOW_ERROR.code
        })

    return JsonResponse({
        'result': True,
        'data': {
            'cron': task.cron
        },
        'code': err_code.SUCCESS.code
    })


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(periodic_task_resource,
                  [periodic_task_resource.actions.edit],
                  get_kwargs={'task_id': 'id', 'project_id': 'project_id'})
def modify_constants_for_periodic_task(request, task_id, project_id):
    project = request.project
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid json format',
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    constants = params.get('constants', {})

    try:
        task = PeriodicTask.objects.get(id=task_id, project_id=project.id)
    except PeriodicTask.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'task(%s) does not exist' % task_id,
            'code': err_code.CONTENT_NOT_EXIST.code
        })

    try:
        new_constants = task.modify_constants(constants)
    except Exception as e:
        return JsonResponse({
            'result': False,
            'message': str(e),
            'code': err_code.UNKNOW_ERROR.code
        })

    return JsonResponse({
        'result': True,
        'data': new_constants,
        'code': err_code.SUCCESS.code
    })


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(taskflow_resource,
                  [taskflow_resource.actions.view],
                  get_kwargs={'task_id': 'id', 'project_id': 'project_id'})
def get_task_detail(request, task_id, project_id):
    """
    @summary: 获取任务详细信息
    @param request:
    @param task_id:
    @param project_id:
    @return:
    """
    project = request.project
    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project.id)
    except TaskFlowInstance.DoesNotExist:
        message = 'task[id={task_id}] of project[project_id={project_id, biz_id{biz_id}}] does not exist'.format(
            task_id=task_id,
            project_id=project.id,
            biz_id=project.bk_biz_id)
        logger.exception(message)
        return JsonResponse({
            'result': False,
            'message': message,
            'code': err_code.CONTENT_NOT_EXIST.code
        })

    data = task.get_task_detail()
    return JsonResponse({
        'result': True,
        'data': data,
        'code': err_code.SUCCESS.code
    })


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(taskflow_resource,
                  [taskflow_resource.actions.view],
                  get_kwargs={'task_id': 'id', 'project_id': 'project_id'})
def get_task_node_detail(request, task_id, project_id):
    """
    @summary: 获取节点输入输出
    @param request:
    @param task_id:
    @param project_id:
    @return:
    """
    project = request.project
    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project.id)
    except TaskFlowInstance.DoesNotExist:
        message = 'task[id={task_id}] of project[project_id={project_id, biz_id{biz_id}}] does not exist'.format(
            task_id=task_id,
            project_id=project.id,
            biz_id=project.bk_biz_id)
        logger.exception(message)
        return JsonResponse({
            'result': False,
            'message': message,
            'code': err_code.CONTENT_NOT_EXIST.code
        })

    node_id = request.GET.get('node_id')
    component_code = request.GET.get('component_code')

    try:
        subprocess_stack = json.loads(request.GET.get('subprocess_stack', '[]'))
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'subprocess_stack is not a valid array json',
            'code': err_code.UNKNOW_ERROR.code
        })
    result = task.get_node_detail(node_id, request.user.username, component_code, subprocess_stack)
    return JsonResponse(result)


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
@api_verify_perms(taskflow_resource,
                  [taskflow_resource.actions.operate],
                  get_kwargs={'task_id': 'id', 'project_id': 'project_id'})
def node_callback(request, task_id, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid json format',
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    project = request.project

    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project.id)
    except TaskFlowInstance.DoesNotExist:
        message = 'task[id={task_id}] of project[project_id={project_id, biz_id{biz_id}}] does not exist'.format(
            task_id=task_id,
            project_id=project.id,
            biz_id=project.bk_biz_id)
        logger.exception(message)
        return JsonResponse({
            'result': False,
            'message': message,
            'code': err_code.CONTENT_NOT_EXIST.code
        })

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
            'message': 'you have no permission to call this api.',
            'code': err_code.REQUEST_FORBIDDEN_INVALID.code
        })

    try:
        req_data = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid json format',
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    template_data = req_data.get('template_data', None)
    if not template_data:
        return JsonResponse({
            'result': False,
            'message': 'template data can not be none',
            'code': err_code.REQUEST_PARAM_INVALID.code
        })
    r = read_encoded_template_data(template_data)
    if not r['result']:
        return JsonResponse(r)

    override = BooleanField().to_python(req_data.get('override', False))

    try:
        import_result = CommonTemplate.objects.import_templates(r['data']['template_data'], override)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({
            'result': False,
            'message': 'invalid flow data or error occur, please contact administrator',
            'code': err_code.UNKNOW_ERROR.code
        })

    return JsonResponse(import_result)


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
@project_inject
def fast_create_task(request, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid json format',
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    project = request.project
    logger.info('apigw fast_create_task info, project_id: {project_id}, params: {params}'.format(
        project_id=project.id,
        params=params))

    if not request.is_trust:
        perms_tuples = [(project_resource, [project_resource.actions.fast_create_task.id], project)]
        batch_verify_or_raise_auth_failed(principal_type='user',
                                          principal_id=request.user.username,
                                          perms_tuples=perms_tuples,
                                          status=200)

    try:
        pipeline_tree = params['pipeline_tree']
        pipeline_node_name_handle(pipeline_tree)
        pipeline_tree.setdefault('gateways', {})
        pipeline_tree.setdefault('constants', {})
        pipeline_tree.setdefault('outputs', [])
        draw_pipeline(pipeline_tree)
        validate_web_pipeline_tree(pipeline_tree)
    except Exception as e:
        message = 'invalid param pipeline_tree: %s' % str(e)
        logger.exception(message)
        return JsonResponse({
            'result': False,
            'message': message,
            'code': err_code.UNKNOW_ERROR.code
        })

    try:
        pipeline_instance_kwargs = {
            'name': name_handler(params['name'], TASK_NAME_MAX_LENGTH),
            'creator': request.user.username,
            'pipeline_tree': pipeline_tree,
            'description': params.get('description', '')
        }
    except (KeyError, ValueError) as e:
        return JsonResponse({
            'result': False,
            'message': 'invalid params: %s' % str(e),
            'code': err_code.REQUEST_PARAM_INVALID.code
        })

    try:
        pipeline_instance = TaskFlowInstance.objects.create_pipeline_instance(
            template=None,
            **pipeline_instance_kwargs
        )
    except PipelineException as e:
        message = 'create pipeline instance error: %s' % str(e)
        logger.exception(message)
        return JsonResponse({
            'result': False,
            'message': message,
            'code': err_code.UNKNOW_ERROR.code
        })

    taskflow_kwargs = {
        'project': project,
        'pipeline_instance': pipeline_instance,
        'template_source': ONETIME,
        'create_method': 'api',
    }
    if params.get('category') in [cate[0] for cate in TASK_CATEGORY]:
        taskflow_kwargs['category'] = params['category']
    # 职能化任务，新建后进入职能化认领阶段
    if params.get('flow_type', 'common') == 'common_func':
        taskflow_kwargs['flow_type'] = 'common_func'
        taskflow_kwargs['current_flow'] = 'func_claim'
    # 常规流程，新建后即可执行
    else:
        taskflow_kwargs['flow_type'] = 'common'
        taskflow_kwargs['current_flow'] = 'execute_task'
    task = TaskFlowInstance.objects.create(**taskflow_kwargs)
    return JsonResponse({
        'result': True,
        'data': {
            'task_id': task.id,
            'task_url': task.url,
            'pipeline_tree': task.pipeline_tree
        },
        'code': err_code.SUCCESS.code
    })


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
def get_plugin_list(request, project_id):
    components = ComponentModel.objects.filter(status=True)

    data = []
    for comp_model in components:
        comp = ComponentLibrary.get_component_class(comp_model.code)
        data.append({
            'inputs': comp.inputs_format(),
            'outputs': comp.outputs_format(),
            'desc': comp.desc,
            'code': comp.code,
            'name': comp.name,
            'group_name': comp.group_name
        })

    return JsonResponse({
        'result': True,
        'data': data,
        'code': err_code.SUCCESS.code
    })
