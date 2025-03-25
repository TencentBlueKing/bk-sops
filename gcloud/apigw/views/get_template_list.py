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
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.http import require_GET

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response, timezone_inject
from gcloud.apigw.views.utils import format_template_list_data, logger
from gcloud.common_template.models import CommonTemplate
from gcloud.constants import NON_COMMON_TEMPLATE_TYPES, PROJECT
from gcloud.iam_auth.conf import FLOW_ACTIONS
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.utils import get_flow_allowed_actions_for_user
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor
from gcloud.tasktmpl3.models import TaskTemplate


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@timezone_inject
@iam_intercept(ProjectViewInterceptor())
def get_template_list(request, project_id):
    template_source = request.GET.get("template_source", PROJECT)
    id_in = request.GET.get("id_in", None)
    name_keyword = request.GET.get("name_keyword", None)

    if id_in:
        try:
            id_in = id_in.split(",")
        except Exception:
            id_in = None
            logger.exception("[API] id_in[{}] resolve fail, ignore.".format(id_in))

    filter_kwargs = dict(is_deleted=False)
    if id_in:
        filter_kwargs["id__in"] = id_in
    if name_keyword and name_keyword != "":
        filter_kwargs["pipeline_template__name__icontains"] = name_keyword

    project = request.project
    if template_source in NON_COMMON_TEMPLATE_TYPES:
        filter_kwargs["project_id"] = project.id
        templates = TaskTemplate.objects.select_related("pipeline_template").filter(**filter_kwargs)
    else:
        filter_kwargs["tenant_id"] = request.user.tenant_id
        templates = CommonTemplate.objects.select_related("pipeline_template").filter(**filter_kwargs)

    template_list, template_id_list = format_template_list_data(templates, project, return_id_list=True, tz=request.tz)

    # 注入用户有权限的actions
    flow_allowed_actions = get_flow_allowed_actions_for_user(request.user.username, FLOW_ACTIONS, template_id_list)
    for template_info in template_list:
        template_id = template_info["id"]
        template_info.setdefault("auth_actions", [])
        for action, allowed in flow_allowed_actions.get(str(template_id), {}).items():
            if allowed:
                template_info["auth_actions"].append(action)

    return {"result": True, "data": template_list, "code": err_code.SUCCESS.code}
