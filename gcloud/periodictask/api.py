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
from django.views.decorators.http import require_POST

from auth_backend.plugins.decorators import verify_perms

from blueapps.utils.view_decorators import post_form_validator, model_instance_inject
from gcloud.core.models import Project
from gcloud.periodictask.models import PeriodicTask
from gcloud.periodictask.permissions import periodic_task_resource
from gcloud.taskflow3.forms import (PeriodicTaskCronModifyForm,
                                    PeriodicTaskEnabledSetForm,
                                    PeriodicTaskConstantsModifyForm)


@require_POST
@post_form_validator(PeriodicTaskEnabledSetForm)
@model_instance_inject(model_cls=PeriodicTask, inject_attr='task', field_maps={
    'id': 'task_id',
    'project_id': 'project_id'
})
@verify_perms(auth_resource=periodic_task_resource,
              resource_get={'from': 'kwargs', 'key': 'task_id'},
              actions=[periodic_task_resource.actions.view, periodic_task_resource.actions.edit])
def set_enabled_for_periodic_task(request, project_id, task_id):
    enabled = request.form.clean()['enabled']

    request.task.set_enabled(enabled)

    return JsonResponse({
        'result': True,
        'message': 'success'
    })


@require_POST
@post_form_validator(PeriodicTaskCronModifyForm)
@model_instance_inject(model_cls=PeriodicTask, inject_attr='task', field_maps={
    'id': 'task_id',
    'project_id': 'project_id'
})
@model_instance_inject(model_cls=Project, inject_attr='project', field_maps={
    'id': 'project_id'
})
@verify_perms(auth_resource=periodic_task_resource,
              resource_get={'from': 'kwargs', 'key': 'task_id'},
              actions=[periodic_task_resource.actions.view, periodic_task_resource.actions.edit])
def modify_cron(request, project_id, task_id):
    cron = request.form.clean()['cron']

    try:
        request.task.modify_cron(cron, request.project.time_zone)
    except Exception as e:
        return JsonResponse({
            'result': False,
            'message': e.message
        })

    return JsonResponse({
        'result': True,
        'message': 'success'
    })


@require_POST
@post_form_validator(PeriodicTaskConstantsModifyForm)
@model_instance_inject(model_cls=PeriodicTask, inject_attr='task', field_maps={
    'id': 'task_id',
    'project_id': 'project_id'
})
@verify_perms(auth_resource=periodic_task_resource,
              resource_get={'from': 'kwargs', 'key': 'task_id'},
              actions=[periodic_task_resource.actions.view, periodic_task_resource.actions.edit])
def modify_constants(request, project_id, task_id):
    constants = request.form.clean()['constants']

    try:
        new_constants = request.task.modify_constants(constants)
    except Exception as e:
        return JsonResponse({
            'result': False,
            'message': e.message
        })

    return JsonResponse({
        'result': True,
        'message': 'success',
        'data': new_constants
    })
