# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import keyword
import logging
import re
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.views.decorators.http import require_POST, require_GET
from django.utils.translation import ugettext_lazy as _
from drf_yasg.utils import swagger_auto_schema

from mako.template import Template
from rest_framework.decorators import api_view

from blueapps.account.decorators import login_exempt
from gcloud.core import roles
from gcloud.conf import settings
from gcloud.core.footer import FOOTER
from gcloud.constants import TASK_CATEGORY, TASK_FLOW_TYPE, NOTIFY_TYPE
from gcloud.core.models import (
    UserDefaultProject,
    ProjectCounter,
)
from gcloud.core.utils import convert_group_name
from gcloud.core.api_adapter import get_all_users
from gcloud.openapi.schema import AnnotationAutoSchema

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

formatted_key_pattern = re.compile(r"^\${(.*?)}$")


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
    return JsonResponse({"result": True, "data": ctx})


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
            "data": Template(FOOTER(language) if callable(FOOTER) else FOOTER).render(
                year=datetime.now().year, desktop_link=settings.BK_PAAS_HOST
            ),
        }
    )


@require_GET
def get_msg_types(request):
    client = get_client_by_user(request.user.username)
    result = client.cmsi.get_msg_type()
    return JsonResponse(result)


@require_GET
@login_exempt
def healthz(request):
    return JsonResponse({"result": True, "data": None, "message": "OK"})


@swagger_auto_schema(methods=["get"], auto_schema=AnnotationAutoSchema)
@api_view(["GET"])
def check_variable_key(request):
    """
    检验变量key值是否合法

    param: key: 变量key, string, query, required

    return: 根据result字段判断是否合法
    {
        "result": "是否合法(boolean)",
        "data": "占位字段(None)",
        "message": "错误时提示(string)"
    }
    """
    variable_key = request.GET.get("key")
    # 处理格式为${xxx}的情况
    if formatted_key_pattern.match(variable_key):
        variable_key = variable_key[2:-1]
    if not variable_key or keyword.iskeyword(variable_key) or variable_key in settings.VARIABLE_KEY_BLACKLIST:
        return JsonResponse(
            {"result": False, "data": None, "message": "{} is not allow to be the key of variable".format(variable_key)}
        )
    return JsonResponse({"result": True, "data": None, "message": "Success"})
