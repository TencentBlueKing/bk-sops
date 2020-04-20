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
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.views.decorators.http import require_POST, require_GET
from django.utils.translation import ugettext_lazy as _

from auth_backend.backends import get_backend_from_config
from auth_backend.resources import resource_type_lib

from gcloud.core import roles
from gcloud.core.footer import FOOTER
from gcloud.core.constant import TASK_CATEGORY, TASK_FLOW_TYPE, NOTIFY_TYPE
from gcloud.core.models import (
    UserDefaultProject,
    ProjectCounter,
)
from gcloud.core.utils import (
    convert_group_name,
    apply_permission_url,
)
from gcloud.core.permissions import project_resource
from gcloud.core.api_adapter import get_all_users

auth_backend = get_backend_from_config()
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


@require_POST
def query_apply_permission_url(request):
    """
    @summary: 获取无权限时申请权限的URL，该接口无需鉴权，获取到申请URL后在很短时间内（可能1分钟）将失效
    @param request:
    @return:
    """
    try:
        permission = json.loads(request.POST.get("permission"))
    except Exception:
        ctx = {"result": False, "data": {}, "message": _("请求参数错误，permission不是json格式的列表"), "code": -1}
        return JsonResponse(ctx)
    return JsonResponse(apply_permission_url(permission))


@require_POST
def query_resource_verify_perms(request):
    """
    @summary: 查询用户是否有某个资源的某些权限
    @param request:
    @return:
    """
    resource_type = request.POST.get("resource_type")
    action_ids = json.loads(request.POST.get("action_ids"))
    instance_id = request.POST.get("instance_id") or None
    if resource_type not in resource_type_lib:
        ctx = {"result": False, "data": {}, "message": _("请求资源[resource_type=%s]未注册" % resource_type), "code": -1}
        return JsonResponse(ctx)

    resource = resource_type_lib[resource_type]
    verify_result = auth_backend.verify_perms(
        resource=resource,
        principal_type="user",
        principal_id=request.user.username,
        action_ids=action_ids,
        instance=instance_id,
    )
    if not verify_result["result"]:
        logger.error(
            "Search authorized resources of Resource[{resource}] return error: {error}".format(
                resource=project_resource.name, error=verify_result["message"]
            )
        )
        return JsonResponse(verify_result)

    verified_resources = verify_result["data"]
    is_pass = all([action_resource["is_pass"] for action_resource in verified_resources])
    ctx = {"result": True, "data": {"is_pass": is_pass, "details": verified_resources}, "message": "", "code": -1}
    return JsonResponse(ctx)


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
    return JsonResponse({"result": True, "data": FOOTER})
