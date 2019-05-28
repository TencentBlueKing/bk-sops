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
import traceback
import logging
import functools

from django.http.response import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from pipeline.exceptions import PipelineException
from pipeline.models import PipelineInstance, PipelineTemplate
from pipeline.contrib.web import forms
from pipeline.parser import pipeline_parser
from pipeline.service import task_service
from pipeline.component_framework import library
from pipeline.utils.context import get_pipeline_context
from pipeline.log.models import LogEntry

from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('root')

actions_for_instance = {
    'start': None,
    'pause': task_service.pause_pipeline,
    'resume': task_service.resume_pipeline,
    'revoke': task_service.revoke_pipeline
}

actions_for_node = {
    'revoke': task_service.revoke_activity,
    'retry': task_service.retry_activity,
    'skip': task_service.skip_activity,
    'call_back': task_service.callback,
    'skip_exg': task_service.skip_exclusive_gateway,
    'pause': task_service.pause_activity,
    'resume': task_service.resume_activity,
    'pause_subproc': task_service.pause_pipeline,
    'resume_subproc': task_service.resume_pipeline,
}


def action_result(result, message, status=200, data=None):
    ret_data = {
        'result': result,
        'message': message
    }
    if data is not None:
        ret_data['data'] = data
    return JsonResponse(status=status, data=ret_data)


def message_result(message, status=200):
    return JsonResponse(status=status, data={
        'message': message
    })


def post_form_validator(form_cls):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            form = form_cls(request.POST)
            if not form.is_valid():
                return JsonResponse(status=400, data=form.errors)
            setattr(request, 'form', form)
            return func(request, *args, **kwargs)

        return wrapper

    return decorate


def get_form_validator(form_cls):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            form = form_cls(request.GET)
            if not form.is_valid():
                return JsonResponse(status=400, data=form.errors)
            setattr(request, 'form', form)
            return func(request, *args, **kwargs)

        return wrapper

    return decorate


@csrf_exempt
@post_form_validator(forms.InstanceActionForm)
def handle_instance_action(request, action):
    form = request.form.clean()

    if action not in actions_for_instance:
        raise Http404()

    instance_id = form.get('instance_id')

    if action == 'start':
        return start_pipeline(instance_id, request.user.username)

    try:
        result = actions_for_instance[action](instance_id)
    except Exception as e:
        logger.exception(traceback.format_exc(e))
        return action_result(False, 'An error occurred, please contact developer.', status=500)
    return action_result(result.result, result.message)


def start_pipeline(instance_id, username):  # get pipeline obj from parser
    instance = PipelineInstance.objects.get(instance_id=instance_id)
    try:
        result = instance.start(username)
    except PipelineException as e:
        logger.exception(traceback.format_exc(e))
        return action_result(False, 'Invalid pipeline data.', status=400)
    except Exception as e:
        logger.exception(traceback.format_exc(e))
        return action_result(False, 'An error occurred, please contact developer.', status=500)

    if not result.result:
        return action_result(result.result, result.message, status=400)

    return action_result(result.result, result.message)


@csrf_exempt
@post_form_validator(forms.NodeActionForm)
def handle_node_action(request, action):
    if action not in actions_for_node:
        raise Http404()

    if action == 'callback':
        return activity_callback(request)

    form = request.form.clean()
    node_id = form.get('node_id')

    inputs = request.POST.get('inputs', '{}')
    flow_id = request.POST.get('flow_id', '')
    try:
        inputs = json.loads(inputs)
    except Exception:
        return action_result(False, 'Invalid inputs format.', status=400)

    kwargs = {}
    kwargs = {'inputs': inputs} if inputs else kwargs
    kwargs = {'flow_id': flow_id} if flow_id else kwargs

    try:
        result = actions_for_node[action](node_id, **kwargs)
    except Exception as e:
        logger.exception(traceback.format_exc(e))
        return action_result(False, 'An error occurred, please contact developer.', status=500)
    return action_result(result.result, result.message)


def activity_callback(request):
    form = request.form.clean()
    node_id = form.get('node_id')
    data = request.POST.get('data')
    try:
        data = json.loads(data)
    except Exception:
        return action_result(False, 'Invalid data format.', status=400)

    try:
        result = task_service.callback(node_id, data)
    except Exception as e:
        logger.exception(traceback.format_exc(e))
        return action_result(False, 'An error occurred, please contact developer.', status=500)
    return action_result(result.result, result.message)


@csrf_exempt
def get_state(request):
    instance_id = request.GET.get('instance_id')
    try:
        instance = PipelineInstance.objects.get(instance_id=instance_id)
        if not instance.is_started:
            return JsonResponse({
                "finish_time": None,
                "state": "CREATED",
                "retry": 0,
                "start_time": None,
                "children": {}})
    except PipelineInstance.DoesNotExist:
        pass

    try:
        state = task_service.get_state(instance_id)
        return JsonResponse(state)
    except Exception as e:
        logger.exception(traceback.format_exc(e))
        return JsonResponse(status=400, data={
            'message': 'invalid activity id.'
        })


@csrf_exempt
def get_form_for_retry(request):
    act_id = request.GET.get('act_id')
    act_data = task_service.get_inputs(act_id)
    return JsonResponse(act_data, safe=True)


@csrf_exempt
def get_form_for_subproc(request):
    template_id = request.GET.get('template_id')
    template = PipelineTemplate.objects.get(template_id=template_id)

    form = template.get_form()
    outputs = template.get_outputs()
    return JsonResponse({
        'form': form,
        'outputs': outputs
    })


@csrf_exempt
def get_constants_for_subproc(request, template_id):
    try:
        template = PipelineTemplate.objects.get(template_id=template_id)
    except PipelineTemplate.DoesNotExist:
        return JsonResponse(status=400, data={
            'message': 'invalid template id.'
        })

    data = template.data
    constants = data['constants']

    outputs_key = data['outputs']
    outputs = {}
    for key in outputs_key:
        outputs[key] = data['constants'][key]

    return JsonResponse({
        'constants': {k: c for k, c in constants.items() if constants[k]['show_type'] == 'show'},
        'outputs': outputs
    })


def form_for_activity(form):
    try:
        inputs = task_service.get_inputs(form['act_id'])
        outputs = task_service.get_outputs(form['act_id'])
    except Exception:
        subprocess_stack = form['subprocess_stack']
        act_id = form['act_id']
        instance_data = PipelineInstance.objects.get(instance_id=form['instance_id']).execution_data
        inputs = pipeline_parser.WebPipelineAdapter(instance_data).get_act_inputs(act_id=act_id,
                                                                                  subprocess_stack=subprocess_stack)
        outputs = {}

    component = library.ComponentLibrary.get_component_class(form['component_code'])
    # append inputs
    inputs_table = inputs

    # append outputs
    outputs_table = []
    outputs_format = component.outputs_format()
    for outputs_item in outputs_format:
        value = outputs.get('outputs', {}).get(outputs_item['key'], '')
        outputs_table.append({
            'name': outputs_item['name'],
            'value': value
        })

    data = {
        'inputs': inputs_table,
        'outputs': outputs_table,
        'ex_data': outputs.get('ex_data', '')
    }
    return data


@csrf_exempt
@get_form_validator(forms.ActivityInputsForm)
def get_data_for_activity(request):
    form = request.form.clean()
    return JsonResponse(form_for_activity(form))


@csrf_exempt
@get_form_validator(forms.ActivityInputsForm)
def get_detail_for_activity(request):
    form = request.form.clean()
    data = form_for_activity(form)
    result = task_service.get_state(form['act_id'])
    result.update(data)
    result['histories'] = task_service.get_activity_histories(form['act_id'])
    return JsonResponse(result)


@csrf_exempt
@post_form_validator(forms.InstanceConstantsModifyForm)
def modify_instance_constants(request):
    form = request.form.clean()
    instance_id = form['instance_id']
    instance = PipelineInstance.objects.get(instance_id=instance_id)
    if instance.is_started:
        return action_result(False, 'pipeline already started.', status=400)

    exec_data = instance.execution_data
    for key, value in form['constants'].items():
        if key in exec_data['constants']:
            exec_data['constants'][key]['value'] = value
    instance.set_execution_data(exec_data)

    return action_result(True, 'success')


def clone_template(request):
    template_id = request.GET.get('template_id')

    # clone template
    template = PipelineTemplate.objects.get(template_id=template_id)
    new_data = template.clone_data()
    # name = template.name[10:] if len(template.name) >= MAX_LEN_OF_NAME - 10 else template.name
    name = 'clone%s' % timezone.now().strftime('%Y%m%d%H%m%S')

    return action_result(True, 'success', data={'name': name, 'data': json.dumps(new_data)})


@csrf_exempt
@post_form_validator(forms.InstanceCloneForm)
def clone_instance(request):
    form = request.form.clean()
    instance_id = form['instance_id']
    creator = form['creator']

    instance = PipelineInstance.objects.get(instance_id=instance_id)
    new_instance = instance.clone(creator=creator)

    return action_result(True, 'success', data={'new_instance_id': new_instance.instance_id})


@csrf_exempt
@post_form_validator(forms.ResetTimerForm)
def reset_timer(request):
    form = request.form.clean()
    node_id = form['node_id']

    result = task_service.forced_fail(node_id)
    if not result.result:
        return action_result(False, _(u"计时器不存在或已完成，或 pipeline 当前状态不允许重置计时器"))

    inputs = form['inputs']
    result = task_service.retry_activity(node_id, inputs)
    if not result.result:
        return action_result(False, _(u"重试计时器失败，请稍后再次尝试"))

    return action_result(True, 'success')


@csrf_exempt
def get_template_context(request):
    template_id = request.GET.get('template_id')
    if template_id:
        try:
            template = PipelineTemplate.objects.get(template_id=template_id)
        except PipelineTemplate.DoesNotExist:
            return action_result(False, 'PipelineTemplate object of template_id:%s does not exist' % template_id)
    else:
        template = None
    context = get_pipeline_context(template, 'template')
    return JsonResponse(context)


@csrf_exempt
def get_instance_context(request):
    instance_id = request.GET.get('instance_id')
    if instance_id:
        try:
            instance = PipelineInstance.objects.get(instance_id=instance_id)
        except PipelineInstance.DoesNotExist:
            return action_result(False, 'PipelineInstance object of instance_id:%s does not exist' % instance_id)
    else:
        instance = None
    context = get_pipeline_context(instance, 'instance')
    return JsonResponse(context)


@csrf_exempt
def get_node_log(request, node_id):
    history_id = request.GET.get('history_id', -1)

    if not node_id:
        return JsonResponse({
            'result': False,
            'data': None,
            'message': 'node_id can not be None'
        })

    plain_log = LogEntry.objects.plain_log_for_node(node_id, history_id)
    return JsonResponse({
        'result': True if plain_log else False,
        'data': plain_log,
        'message': 'node with history_id(%s) does not exist or log already expired' % history_id if not plain_log
        else ''
    })
