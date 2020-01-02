# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET

from gcloud.contrib.appmaker.models import AppMaker
from gcloud.core.constant import AE
from gcloud.core.constant import TASK_CATEGORY
from gcloud.core.decorators import check_is_superuser
from gcloud.core.utils import check_and_rename_params
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate


@check_is_superuser()
@require_GET
def get_task_category(request):
    """
    @summary 获取所有模板列表
    :param request:
    :return:
    """
    groups = []
    for category in TASK_CATEGORY:
        groups.append({
            'value': category[0],
            'name': category[1],
        })
    return JsonResponse({'result': True, 'data': groups})


@check_is_superuser()
def analysis_home(request):
    """
    @param request:
    """
    context = {
        'view_mode': 'analysis',
    }
    return render(request, "core/base_vue.html", context)


@check_is_superuser()
@require_POST
def query_instance_by_group(request):
    """
    @summary 按起始时间、业务（可选）查询各类型任务实例个数和占比
    :param request
    """
    conditions = request.POST.get('conditions', {})
    page_index = int(request.POST.get('pageIndex', 1))
    limit = int(request.POST.get('limit', 10))

    group_by = request.POST.get('group_by', None)
    # 参数校验
    result_dict = check_and_rename_params(conditions, group_by)
    if not result_dict['success']:
        return JsonResponse({'result': False, 'message': result_dict['content']})
    conditions = result_dict['conditions']
    group_by = result_dict['group_by']
    # 过滤参数填写
    filters = {'is_deleted': False}
    filters.update(conditions)
    # 根据类型分组
    success, content = TaskFlowInstance.objects.extend_classified_count(group_by, filters, page_index, limit)
    if not success:
        return JsonResponse({'result': False, 'message': content})
    return JsonResponse({'result': True, 'data': content})


@check_is_superuser()
@require_POST
def query_template_by_group(request):
    """
    @summary 查询模板相关信息
    :param request:
    """
    conditions = request.POST.get('conditions', {})
    page_index = int(request.POST.get('pageIndex', 1))
    limit = int(request.POST.get('limit', 10))

    group_by = request.POST.get('group_by', None)

    # 参数校验并进行转换
    result_dict = check_and_rename_params(conditions, group_by)
    if not result_dict['success']:
        return JsonResponse({'result': False, 'message': result_dict['content']})
    conditions = result_dict['conditions']
    # 过滤参数填写
    filters = {'is_deleted': False}
    filters.update(conditions)
    # 根据类型分组
    success, content = TaskTemplate.objects.extend_classified_count(result_dict['group_by'], filters, page_index, limit)
    if not success:
        return JsonResponse({'result': False, 'message': content})
    return JsonResponse({'result': True, 'data': content})


@check_is_superuser()
@require_POST
def query_atom_by_group(request):
    """
    @summary 查询标准插件相关信息
    :param request:
    """
    conditions = request.POST.get('conditions', '{}')
    page_index = int(request.POST.get('pageIndex', 1))
    limit = int(request.POST.get('limit', 10))

    group_by = request.POST.get('group_by', None)

    # 参数校验并进行转换
    result_dict = check_and_rename_params(conditions, group_by)
    if not result_dict['success']:
        return JsonResponse({'result': False, 'message': result_dict['content']})
    conditions = result_dict['conditions']
    group_by = result_dict['group_by']
    # 过滤参数填写
    filters = {'is_deleted': False}
    filters.update(conditions)
    # 根据类型分组
    if group_by in [AE.atom_execute, AE.atom_instance]:
        success, content = TaskFlowInstance.objects.extend_classified_count(group_by, filters, page_index, limit)
    else:
        success, content = TaskTemplate.objects.extend_classified_count(group_by, filters, page_index, limit)
    if not success:
        return JsonResponse({'result': False, 'message': content})
    return JsonResponse({'result': True, 'data': content})


@check_is_superuser()
@require_POST
def query_appmaker_by_group(request):
    """
    查询appmaker信息
    :param request:
    """
    conditions = request.POST.get('conditions', {})
    page_index = int(request.POST.get('pageIndex', 1))
    limit = int(request.POST.get('limit', 10))

    group_by = request.POST.get('group_by', None)

    # 参数校验并进行转换
    result_dict = check_and_rename_params(conditions, group_by)
    if not result_dict['success']:
        return JsonResponse({'result': False, 'message': result_dict['content']})
    conditions = result_dict['conditions']
    group_by = result_dict['group_by']
    # 过滤参数填写
    filters = {'is_deleted': False}
    if group_by == AE.appmaker_instance:
        # 如果是查询标准插件流程相关 需要加上 create_method = app_maker 的条件
        filters[AE.create_method] = AE.app_maker
        filters.update(conditions)
        success, content = TaskFlowInstance.objects.extend_classified_count(group_by, filters, page_index, limit)
    else:
        filters.update(conditions)
        # 根据类型分组
        success, content = AppMaker.objects.extend_classified_count(group_by, filters)
    if not success:
        return JsonResponse({'result': False, 'message': content})
    return JsonResponse({'result': True, 'data': content})
