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
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.commons.template.models import CommonTemplate
from gcloud.constants import PROJECT
from gcloud.tasktmpl3.constants import NON_COMMON_TEMPLATE_TYPES
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.apigw.views.utils import logger, format_template_list_data
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@iam_intercept(ProjectViewInterceptor())
def get_template_list(request, project_id):
    template_source = request.GET.get("template_source", PROJECT)
    id_in = request.GET.get("id_in", None)

    if id_in:
        try:
            id_in = id_in.split(",")
        except Exception:
            id_in = None
            logger.warning("[API] id_in[{}] relove fail, ignore.".format(id_in))

    filter_kwargs = dict(is_deleted=False)
    if id_in:
        filter_kwargs["id__in"] = id_in

    project = request.project
    if template_source in NON_COMMON_TEMPLATE_TYPES:
        filter_kwargs["project_id"] = project.id
        templates = TaskTemplate.objects.select_related("pipeline_template").filter(**filter_kwargs)
    else:
        templates = CommonTemplate.objects.select_related("pipeline_template").filter(**filter_kwargs)
    return JsonResponse(
        {"result": True, "data": format_template_list_data(templates, project), "code": err_code.SUCCESS.code}
    )
