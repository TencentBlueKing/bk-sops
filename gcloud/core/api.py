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

import logging
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.views.decorators.http import require_POST, require_GET
from django.utils.translation import ugettext_lazy as _

from mako.template import Template

from gcloud.core import roles
from gcloud.core.footer import FOOTER
from gcloud.core.constant import TASK_CATEGORY, TASK_FLOW_TYPE, NOTIFY_TYPE
from gcloud.core.models import (
    UserDefaultProject,
    ProjectCounter,
)
from gcloud.core.utils import convert_group_name
from gcloud.core.api_adapter import get_all_users

logger = logging.getLogger("root")


@require_POST
def change_default_project(request, project_id):
    """
    @summary: 切换用户默认项目
    """
    UserDefaultProject.objects.update_or_create(
        username=request.user.username, defaults={"default_project_id": project_id}
    )

    ProjectCounter.objects.increase_or_create(username=request.user.username, project_id=project_id)

    return JsonResponse({"result": True, "data": {}, "message": _("用户默认项目切换成功")})


@require_GET
def get_roles_and_personnel(request, biz_cc_id):
    """
    @summary: 获取用户角色和业务人员
    @param request:
    @param biz_cc_id:
    @return:
    """
    use_for = request.GET.get("use_for", "")
    # 模板授权需要去掉运维角色，运维默认有所有权限，并添加职能化人员
    if use_for == "template_auth":
        role_list = [role for role in roles.CC_ROLES if role != roles.MAINTAINERS]
        # 添加职能化人员
        role_list.append(roles.FUNCTOR)
    else:
        role_list = roles.CC_ROLES

    data = []
    for key in role_list:
        name = roles.ROLES_DECS[key]
        group_name = convert_group_name(biz_cc_id, key)
        group = Group.objects.get(name=group_name)
        user_list = group.user_set.all()
        personnel_list = []
        for user in user_list:
            personnel_list.append({"text": user.full_name, "id": user.username})
        personnel_list.insert(0, {"text": _("所有%s") % name, "id": key})
        data.append({"text": name, "children": personnel_list})
    return JsonResponse({"result": True, "data": {"roles": data}})


@require_GET
def get_basic_info(request):
    """
    @summary: 获取全局变量
    @param request:
    @return:
    """
    task_categories = [{"value": item[0], "name": item[1]} for item in TASK_CATEGORY]
    flow_type_list = [{"value": item[0], "name": item[1]} for item in TASK_FLOW_TYPE]
    notify_group = list(roles.CC_PERSON_GROUP)
    notify_type_list = [{"value": item[0], "name": item[1]} for item in NOTIFY_TYPE]
    ctx = {
        "task_categories": task_categories,
        "flow_type_list": flow_type_list,
        "notify_group": notify_group,
        "notify_type_list": notify_type_list,
    }
    return JsonResponse(ctx, safe=False)


@require_GET
def get_user_list(request):
    """
    @summary: 获取当前平台所有用户
    @param request:
    @return:
    """
    result = get_all_users(request)
    return JsonResponse(result)


@require_GET
def get_footer(request):
    """
    @summary: 获取当前环境的页面 footer
    @param request:
    @return:
    """
    # 为了国际化需要在返回时调用函数来拼接字符串
    language = request.COOKIES.get("blueking_language", "zh-cn")
    return JsonResponse(
        {
            "result": True,
            "data": Template(FOOTER(language) if callable(FOOTER) else FOOTER).render(year=datetime.now().year),
        }
    )
