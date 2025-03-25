# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from gcloud.constants import AE, TASK_CATEGORY
from gcloud.contrib.analysis.analyse_items import app_maker, task_flow_instance, task_template
from gcloud.contrib.analysis.decorators import standardize_params
from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.core.models import Project
from gcloud.err_code import REQUEST_PARAM_INVALID
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.statistics import StatisticsViewInpterceptor
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.utils.components import get_all_components


@require_GET
def get_task_category(request):
    """
    @summary 获取所有模板分类列表
    :param request:
    :return:
    """
    groups = []
    for category in TASK_CATEGORY:
        groups.append({"value": category[0], "name": category[1]})
    return JsonResponse({"result": True, "data": groups})


@require_GET
def get_biz_useage(request, query):
    """
    @summary 获取正在使用业务数量、总业务数量
    :param request:
    :param query:模板/任务
    :return:
    """
    total = Project.objects.filter(tenant_id=request.user.tenant_id).count()

    if query == "template":
        count = (
            TaskTemplate.objects.filter(project__tenant_id=request.user.tenant_id)
            .values("project__id")
            .distinct()
            .count()
        )
    elif query == "task":
        count = (
            TaskFlowInstance.objects.filter(project__tenant_id=request.user.tenant_id)
            .values("project__id")
            .distinct()
            .count()
        )
    else:
        return JsonResponse(
            {"result": False, "code": REQUEST_PARAM_INVALID.code, "message": REQUEST_PARAM_INVALID.description}
        )
    data = {"total": total, "count": count}
    return JsonResponse({"result": True, "data": data})


@iam_intercept(StatisticsViewInpterceptor())
def analysis_home(request):
    """
    @param request:
    """
    context = {
        "view_mode": "analysis",
    }
    bk_audit_add_event(username=request.user.username, action_id=IAMMeta.STATISTICS_VIEW_ACTION)
    return render(request, "core/base_vue.html", context)


@require_POST
@iam_intercept(StatisticsViewInpterceptor())
@standardize_params
def query_instance_by_group(*args):
    """
    @summary 按起始时间、业务（可选）查询各类型任务实例个数和占比
    :param args: (group_by, filters, page_index, limit)
    """
    success, content = task_flow_instance.dispatch(*args)
    return success, content


@require_POST
@iam_intercept(StatisticsViewInpterceptor())
@standardize_params
def query_template_by_group(*args):
    """
    @summary 查询模板相关信息
    :param args: (group_by, filters, page_index, limit)
    """
    success, content = task_template.dispatch(*args)
    return success, content


@require_POST
@iam_intercept(StatisticsViewInpterceptor())
@standardize_params
def query_atom_by_group(*args):
    """
    @summary 查询标准插件相关信息
    :param args: (group_by, filters, page_index, limit)
    """
    group_by = args[0]
    if group_by in AE.atom_dimensions:
        success, content = task_flow_instance.dispatch(*args)
    else:
        success, content = task_template.dispatch(*args)
    return success, content


@require_POST
@iam_intercept(StatisticsViewInpterceptor())
@standardize_params
def query_appmaker_by_group(*args):
    """
    查询appmaker信息
    :param args: (group_by, filters, page_index, limit)
    """
    group_by = args[0]
    filters = args[1]
    if group_by == AE.appmaker_instance:
        # 如果是查询标准插件流程相关 需要加上 create_method = app_maker 的条件
        filters[AE.create_method] = AE.app_maker
        success, content = task_flow_instance.dispatch(*args)
    else:
        # 根据类型分组
        success, content = app_maker.dispatch(group_by, filters)
    return success, content


@require_GET
@iam_intercept(StatisticsViewInpterceptor())
def get_component_list(request):
    """
    获取所有插件列表（含第三方插件）
    """
    components = get_all_components()
    return JsonResponse({"result": True, "data": components})
