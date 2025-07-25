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
import keyword
import logging
import re
from datetime import datetime

from blueapps.account.decorators import login_exempt
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST
from drf_yasg.utils import swagger_auto_schema
from mako.template import Template
from rest_framework.decorators import api_view

import env
from gcloud.conf import settings
from gcloud.constants import NOTIFY_TYPE, TASK_CATEGORY, TASK_FLOW_TYPE
from gcloud.core import roles
from gcloud.core.api_adapter import get_all_users
from gcloud.core.footer import FOOTER, FOOTER_INFO
from gcloud.core.models import ProjectCounter, UserDefaultProject
from gcloud.core.utils import convert_group_name
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
                year=datetime.now().year,
                desktop_link=settings.BK_PAAS_HOST,
                sops_version=settings.STATIC_VERSION,
                static_url=settings.STATIC_URL,
            ),
        }
    )


@require_GET
def get_footer_info(request):
    """
    @summary: 获取当前环境的页面 footer 信息
    """
    return JsonResponse(
        {
            "result": True,
            "data": {
                "env": env.RUN_VER,
                "sops_version": settings.STATIC_VERSION,
                "year": datetime.now().year,
                **FOOTER_INFO,
            },
        }
    )


@require_GET
def get_msg_types(request):
    client = get_client_by_user(request.user.username)
    result = client.cmsi.get_msg_type()
    if settings.ENABLE_BK_CHAT_CHANNEL and not request.GET.get("only_cmsi"):
        bk_chat = {
            "type": "bkchat",
            "icon": "iVBORw0KGgoAAAANSUhEUgAAACQAAAAgCAMAAABNTyq8AAAAAXNSR0IArs4c6QAAAAlwSFlzAAAWJQAAFiUBSVIk8AAAAOpQTF"
            "RF////GX3/Fmj/IcH/M6P+FXD/AOvpF4P/IL7/H7r/FnT/Hrb/Jcb/Fmv/Jcr/AP7iF3j/APLmJc7/HrD/Tpf/IKn/G5f/ALP81Oz/Vov/"
            "AP/o+/3/GqP/ANfwGY//AMf2AM/zALz6APnm4fb/MLb/HJ37gbH/FGH/AOXsK9P/Bq7+Qp3/IdH/e9T/oOr/GIj/A8H4hcn/AOHuEWH/AN"
            "zvaqL/Y+D6c73/uNn/F4D/AHfdC6zpSOr2te3+yPb7AMHWKvHzg9/97fr/ALHKOY3/qvP7BYfmALnnmb7/1vX/df/0SLn/PNX/GWj/cm/M"
            "ZQAAAWBJREFUeNp9zmFXgjAUgOFVhpqVmkoImIZOSUVFRCkVhBTU8v//nS6yTers9OzcbR/eDxcF+zpH1UFp+5NlWb0YeQF86pJCQWRb1z"
            "w9u0s5CrIfuE7bKuMg+5YvFe2RfcdV2g4YE9klPjFDxdEVH84wEL3z4Rpjom6WGZ/vpMmqfQaiMTUww/DjLAxFtf/MGKj7QjlSBuPlslLI"
            "50A+HS1oI0pKO200eSUgEomBhIBCBvicCMfR4QDNOqnWE2KOFhhjFQ7OxFEQQNQmUTMRRyrAMBAxJCJIVIvnb7RrEXNk1ijnn6hCfTnSBa"
            "zlNogVREyhc2EoKJiyyChwdWDD1SwRR3me3HznbqYJiHJ8M53ZIOOGbyYIugDghuiebypQEPmPfHqZ0ZD/xDUU0tH6e8i8pQgaIyPFHVF+"
            "y4uiaAmiZqNc1MiBKMX1PoHnNfSyVkw5/ooEoazJslwEciJ+j8oPxRxtqFiEHPIAAAAASUVORK5CYII=",
            "label": "bkchat",
            "tips": ("获取群ID方法：<br>" "1. 群聊右上角添加联系人：bkchat(蓝鲸信息流)<br>" '2. 输入 "小鲸 群ID" 获取群ID<br>' "3. 将获取到的群ID粘贴到输入框"),
            "is_active": True,
        }
        result["data"].append(bk_chat)
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
        message = _(f"{variable_key}变量创建失败: 变量KEY仅支持英文字母、数字、下划线, 且以英文字母、下划线开头")
        logger.error(message)
        return JsonResponse({"result": False, "data": None, "message": message})
    return JsonResponse({"result": True, "data": None, "message": "Success"})
