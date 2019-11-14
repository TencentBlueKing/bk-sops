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

import ujson as json

from django.views.decorators.http import require_GET, require_POST
from django.http.response import JsonResponse

from auth_backend.plugins.shortcuts import verify_or_raise_auth_failed
from pipeline.engine.models import (
    PipelineModel,
    PipelineProcess,
    Status,
    ScheduleService
)
from pipeline.engine.utils import calculate_elapsed_time
from pipeline.core.data.var import Variable
from pipeline.service import task_service

from gcloud.core.permissions import admin_operate_resource
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.context import TaskContext

SERIALIZE_DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z'


def format_variables(variables):
    _vars = {}
    for key, var in variables.items():
        if isinstance(var, Variable):
            _vars[key] = {'name': var.name, 'value': var.value}
        elif isinstance(var, TaskContext):
            _vars[key] = {'name': key, 'value': var.__dict__}
        else:
            _vars[key] = var

    return _vars


def serialize_pipeline_context(context):
    return {
        'variables': format_variables(context.variables),
        'act_outputs': context.act_outputs,
        '_output_key': context._output_key,
        '_change_keys': getattr(context, '_change_keys'),
        '_raw_variables': format_variables(getattr(context, '_raw_variables', {}))
    }


def serialize_process_data(process):

    def serialize(process):
        data = {
            'id': process.id,
            'root_pipeline_id': process.root_pipeline_id,
            'current_node_id': process.current_node_id,
            'destination_id': process.destination_id,
            'parent_id': process.parent_id,
            'ack_num': process.ack_num,
            'need_ack': process.need_ack,
            'is_alive': process.is_alive,
            'is_sleep': process.is_sleep,
            'is_frozen': process.is_frozen,
            'children': process.children,
            'child_process': {},
            'subprocess_stack': process.subprocess_stack,
            'context': None,
            'subprocess_context': {}
        }

        if process.snapshot:
            data['in_subprocess'] = process.in_subprocess

        if process.root_pipeline:
            data['context'] = serialize_pipeline_context(process.root_pipeline.context)

        if process.pipeline_stack:
            for pipeline in process.pipeline_stack[:-1]:
                data['subprocess_context'][pipeline.id] = serialize_pipeline_context(pipeline.context)

        if process.children:
            for child in PipelineProcess.objects.filter(parent_id=process.id):
                data['child_process'][child.id] = serialize(child)

        return data

    return serialize(process)


@require_GET
def get_taskflow_detail(request):

    verify_or_raise_auth_failed(principal_type='user',
                                principal_id=request.user.username,
                                resource=admin_operate_resource,
                                action_ids=[admin_operate_resource.actions.view.id],
                                instance=None)

    task_id = request.GET.get('task_id')

    try:
        taskflow = TaskFlowInstance.objects.get(id=task_id)
    except TaskFlowInstance.DoesNotExist:
        return {
            'result': False,
            'message': f'task {task_id} not exist'
        }

    process_data = 'pipeline not run'
    if taskflow.pipeline_instance.is_started:
        engine_model = PipelineModel.objects.get(id=taskflow.pipeline_instance.instance_id)
        process_data = serialize_process_data(engine_model.process)

    return JsonResponse({
        'result': True,
        'data': process_data
    })


def hydrate_inputs(inputs):
    hydrated = {}
    for k, v in inputs.items():
        if isinstance(v, Variable):
            hydrated[k] = {
                'repr': f'{v}',
                'name': v.name,
                'value': v.value
            }
        else:
            hydrated[k] = v

    return hydrated


@require_GET
def get_taskflow_node_detail(request):
    verify_or_raise_auth_failed(principal_type='user',
                                principal_id=request.user.username,
                                resource=admin_operate_resource,
                                action_ids=[admin_operate_resource.actions.view.id],
                                instance=None)

    task_id = request.GET.get('task_id')
    node_id = request.GET.get('node_id')
    subprocess_stack = json.loads(request.GET.get('subprocess_stack', '[]'))

    data = {
        'execution_info': {},
        'inputs': 'pipeline has been destoryed',
        'outputs': 'pipeline has been destoryed',
        'history': {},
        'log': ''
    }

    taskflow = TaskFlowInstance.objects.get(id=task_id)

    if not taskflow.pipeline_instance.is_started:
        return JsonResponse({
            'result': False,
            'message': f'task[{task_id}] is not start'
        })

    if not taskflow.has_node(node_id):
        return JsonResponse({
            'result': False,
            'message': f'task[{task_id}] does not have node[{node_id}]'
        })

    status = Status.objects.get(id=node_id)

    # collect execution info
    data['execution_info'] = {
        'start_time': status.started_time.strftime(SERIALIZE_DATE_FORMAT),
        'archive_time': status.archived_time.strftime(SERIALIZE_DATE_FORMAT) if status.archived_time else None,
        'elapsed_time': calculate_elapsed_time(status.started_time, status.archived_time),
        'skip': status.skip,
        'error_ignorable': status.error_ignorable,
        'retry_times': status.retry,
        'id': status.id,
        'state': status.state,
        'loop': status.loop,
        'create_time': status.created_time,
        'version': status.version,
        'schedule_id': None,
        'is_scheduling': False,
        'schedule_times': 0,
        'wait_callback': False,
        'is_finished': False,
        'schedule_version': None,
        'callback_data': None
    }

    try:
        schedule = ScheduleService.objects.schedule_for(status.id, status.version)
    except ScheduleService.DoesNotExist:
        pass
    else:
        data['execution_info'].update({
            'schedule_id': schedule.id,
            'is_scheduling': schedule.is_scheduling,
            'schedule_times': schedule.schedule_times,
            'wait_callback': schedule.wait_callback,
            'is_finished': schedule.is_finished,
            'schedule_version': schedule.version,
            'callback_data': schedule.callback_data
        })

    # collect inputs and outputs

    process = PipelineModel.objects.get(id=taskflow.pipeline_instance.instance_id).process

    if process.root_pipeline:

        target_pipeline = process.root_pipeline

        for sub_id in subprocess_stack:
            subprocess_act = [x for x in target_pipeline.spec.activities if x.id == sub_id][0]
            target_pipeline = subprocess_act.pipeline

        act = target_pipeline.spec.objects[node_id]

        data['inputs'] = hydrate_inputs(act.data.inputs)
        data['outputs'] = act.data.outputs

    elif taskflow.pipeline_instance.is_finished or taskflow.pipeline_instance.is_revoked:
        data['inputs'] = data['outputs'] = 'pipeline had finished or had been revoked'

        # collect history
    data['history'] = task_service.get_activity_histories(node_id)

    # collect log
    data['log'] = task_service.get_plain_log_for_node(node_id)

    return JsonResponse({
        'result': True,
        'data': data
    })


@require_GET
def get_node_history_log(request):

    verify_or_raise_auth_failed(principal_type='user',
                                principal_id=request.user.username,
                                resource=admin_operate_resource,
                                action_ids=[admin_operate_resource.actions.view.id],
                                instance=None)

    node_id = request.GET.get('node_id')
    history_id = request.GET.get('history_id')

    data = {
        'log': task_service.get_plain_log_for_node(node_id, history_id)
    }

    return JsonResponse({
        'result': True,
        'data': data
    })


@require_POST
def force_fail_node(request):

    verify_or_raise_auth_failed(principal_type='user',
                                principal_id=request.user.username,
                                resource=admin_operate_resource,
                                action_ids=[admin_operate_resource.actions.edit.id],
                                instance=None)

    data = json.loads(request.body)

    task_id = data.get('task_id')
    node_id = data.get('node_id')

    taskflow = TaskFlowInstance.objects.get(id=task_id)

    if not taskflow.pipeline_instance.is_started:
        return JsonResponse({
            'result': False,
            'message': f'task[{task_id}] is not start'
        })

    if not taskflow.has_node(node_id):
        return JsonResponse({
            'result': False,
            'message': f'task[{task_id}] does not have node[{node_id}]'
        })

    result = task_service.forced_fail(node_id)

    return JsonResponse({
        'result': result.result,
        'message': result.message
    })
