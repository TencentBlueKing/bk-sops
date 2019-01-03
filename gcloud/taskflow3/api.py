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

from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_GET, require_POST

from blueapps.utils.esbclient import get_client_by_user
from gcloud.taskflow3.decorators import check_user_perm_of_task
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import (TaskTemplate,
                                     CREATE_TASK_PERM_NAME,
                                     FILL_PARAMS_PERM_NAME,
                                     EXECUTE_TASK_PERM_NAME)
from pipeline.engine import api as pipeline_api
from pipeline.engine import exceptions, states


logger = logging.getLogger("root")


@require_GET
def status(request, biz_cc_id):
    instance_id = request.GET.get('instance_id')
    try:
        task = TaskFlowInstance.objects.get(pk=instance_id, business__cc_id=biz_cc_id)
        task_status = task.get_status()
        ctx = {'result': True, 'data': task_status}
        return JsonResponse(ctx)
    # 请求子流程的状态，直接通过pipeline api查询
    except (ValueError, TaskFlowInstance.DoesNotExist):
        logger.info('taskflow[id=%s] does not exist' % instance_id)
    except Exception as e:
        message = 'taskflow[id=%s] get status error: %s' % (instance_id, e)
        logger.error(message)
        ctx = {'result': False, 'message': message}
        return JsonResponse(ctx)
    try:
        task_status = pipeline_api.get_status_tree(instance_id, max_depth=99)
        TaskFlowInstance.format_pipeline_status(task_status)
        ctx = {'result': True, 'data': task_status}
    # subprocess pipeline has not executed
    except exceptions.InvalidOperationException:
        ctx = {'result': True, 'data': {'state': states.CREATED}}
    except Exception as e:
        message = 'taskflow[id=%s] get status error: %s' % (instance_id, e)
        logger.error(message)
        ctx = {'result': False, 'message': message}
    return JsonResponse(ctx)


@require_GET
def data(request, biz_cc_id):
    task_id = request.GET.get('instance_id')
    node_id = request.GET.get('node_id')
    component_code = request.GET.get('component_code')
    subprocess_stack = json.loads(request.GET.get('subprocess_stack', '[]'))
    task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=biz_cc_id)
    ctx = task.get_node_data(node_id, component_code, subprocess_stack)
    return JsonResponse(ctx)


@require_GET
def detail(request, biz_cc_id):
    task_id = request.GET.get('instance_id')
    node_id = request.GET.get('node_id')
    component_code = request.GET.get('component_code')
    subprocess_stack = json.loads(request.GET.get('subprocess_stack', '[]'))
    task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=biz_cc_id)
    ctx = task.get_node_detail(node_id, component_code, subprocess_stack)
    return JsonResponse(ctx)


@require_GET
def get_job_instance_log(request, biz_cc_id):
    client = get_client_by_user(request.user.username)
    client.set_bk_api_ver('v2')
    job_instance_id = request.GET.get('job_instance_id')
    log_kwargs = {
        "bk_biz_id": biz_cc_id,
        "job_instance_id": job_instance_id
    }
    log_result = client.job.get_job_instance_log(log_kwargs)
    return JsonResponse(log_result)


@require_POST
@check_user_perm_of_task([EXECUTE_TASK_PERM_NAME])
def task_action(request, action, biz_cc_id):
    task_id = request.POST.get('instance_id')
    username = request.user.username
    task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=biz_cc_id)
    ctx = task.task_action(action, username)
    return JsonResponse(ctx)


@require_POST
@check_user_perm_of_task([EXECUTE_TASK_PERM_NAME])
def nodes_action(request, action, biz_cc_id):
    task_id = request.POST.get('instance_id')
    node_id = request.POST.get('node_id')
    username = request.user.username
    kwargs = {
        'data': json.loads(request.POST.get('data', '{}')),
        'inputs': json.loads(request.POST.get('inputs', '{}')),
        'flow_id': request.POST.get('flow_id', ''),
    }
    task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=biz_cc_id)
    ctx = task.nodes_action(action, node_id, username, **kwargs)
    return JsonResponse(ctx)


@require_POST
@check_user_perm_of_task([EXECUTE_TASK_PERM_NAME])
def spec_nodes_timer_reset(request, biz_cc_id):
    task_id = request.POST.get('instance_id')
    node_id = request.POST.get('node_id')
    username = request.user.username
    inputs = json.loads(request.POST.get('inputs', '{}'))
    task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=biz_cc_id)
    ctx = task.spec_nodes_timer_reset(node_id, username, inputs)
    return JsonResponse(ctx)


@require_POST
@check_user_perm_of_task([CREATE_TASK_PERM_NAME])
def task_clone(request, biz_cc_id):
    task_id = request.POST.get('instance_id')
    username = request.user.username
    task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=biz_cc_id)
    kwargs = {}
    if request.POST.get('create_method'):
        kwargs['create_method'] = request.POST.get('create_method')
        kwargs['create_info'] = request.POST.get('create_info', '')
    new_task_id = task.clone(username, **kwargs)
    ctx = {
        'result': True,
        'data': {
            'new_instance_id': new_task_id
        }
    }
    return JsonResponse(ctx)


@require_POST
@check_user_perm_of_task([FILL_PARAMS_PERM_NAME])
def task_modify_inputs(request, biz_cc_id):
    task_id = request.POST.get('instance_id')
    task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=biz_cc_id)
    if task.is_started:
        ctx = {
            'result': False,
            'message': 'task is started'
        }
    elif task.is_finished:
        ctx = {
            'result': False,
            'message': 'task is finished'
        }
    else:
        constants = json.loads(request.POST.get('constants'))
        name = request.POST.get('name', '')
        ctx = task.reset_pipeline_instance_data(constants, name)
    return JsonResponse(ctx)


@require_POST
@check_user_perm_of_task([FILL_PARAMS_PERM_NAME])
def task_func_claim(request, biz_cc_id):
    task_id = request.POST.get('instance_id')
    task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=biz_cc_id)
    constants = json.loads(request.POST.get('constants'))
    name = request.POST.get('name', '')
    ctx = task.task_claim(request.user.username, constants, name)
    return JsonResponse(ctx)


@require_POST
def preview_task_tree(request, biz_cc_id):
    """
    @summary: 调整可选节点后预览任务流程，这里不创建任何实例，只返回调整后的pipeline_tree
    @param request:
    @param biz_cc_id:
    @return:
    """
    template_id = request.POST.get('template_id')
    try:
        template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    exclude_task_nodes_id = json.loads(request.POST.get('exclude_task_nodes_id', '[]'))
    pipeline_tree = template.pipeline_tree
    try:
        TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'result': False, 'message': e.message})
    return JsonResponse({'result': True, 'data': {'pipeline_tree': pipeline_tree}})


@require_POST
def query_task_count(request, biz_cc_id):
    """
    @summary: 按任务分类统计总数
    @param request:
    @param biz_cc_id:
    @return:
    """
    conditions = request.POST.get('conditions', {})
    group_by = request.POST.get('group_by')
    if not isinstance(conditions, dict):
        message = u"query_task_list params conditions[%s] are invalid dict data" % conditions
        logger.error(message)
        return JsonResponse({'result': False, 'message': message})
    if group_by not in ['category', 'create_method', 'flow_type', 'status']:
        message = u"query_task_list params group_by[%s] is invalid" % group_by
        logger.error(message)
        return JsonResponse({'result': False, 'message': message})

    filters = {'business__cc_id': biz_cc_id, 'is_deleted': False}
    filters.update(conditions)
    success, content = TaskFlowInstance.objects.extend_classified_count(group_by, filters)
    if not success:
        return JsonResponse({'result': False, 'message': content})
    return JsonResponse({'result': True, 'data': content})


def get_node_log(request, biz_cc_id, node_id):
    """
    @summary: 查看某个节点的日志
    @param request:
    @param biz_cc_id:
    @param node_id
    @return:
    """
    task_id = request.GET.get('instance_id')
    history_id = request.GET.get('history_id')

    try:
        task = TaskFlowInstance.objects.get(pk=task_id, business__cc_id=biz_cc_id)
    except TaskFlowInstance.DoesNotExist:
        return HttpResponseForbidden()

    ctx = task.log_for_node(node_id, history_id)
    return JsonResponse(ctx)
