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
from cachetools import cached, TTLCache
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.decorators import project_inject
from gcloud.apigw.utils import api_hash_key
from gcloud.core.models import ProjectBasedComponent
from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.models import ComponentModel

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
@project_inject
@cached(cache=TTLCache(maxsize=1024, ttl=60), key=api_hash_key)
def get_plugin_detail(request, project_id):
    project_id = request.project.id
    code = request.GET.get("code")
    version = request.GET.get("version", "legacy")

    if not code:
        return JsonResponse(
            {"result": False, "message": "parameter code need to be provided.", "code": err_code.VALIDATION_ERROR.code}
        )

    # 排除基于业务的插件，只支持公共插件
    exclude_component_codes = ProjectBasedComponent.objects.get_components_of_other_projects(project_id)
    try:
        component = ComponentModel.objects.exclude(code__in=exclude_component_codes).get(
            status=True, code=code, version=version
        )
    except ComponentModel.DoesNotExist:
        return JsonResponse(
            {
                "result": False,
                "message": "can not find suitable component with code: {} and version: {}".format(code, version),
                "code": err_code.VALIDATION_ERROR.code,
            }
        )

    component_info = ComponentLibrary.get_component_class(component.code, component.version)
    data = {
        "inputs": component_info.inputs_format(),
        "outputs": component_info.outputs_format(),
        "desc": component_info.desc,
        "code": component_info.code,
        "name": component_info.name,
        "group_name": component_info.group_name,
        "version": component_info.version,
        "form": component_info.form,
    }

    return JsonResponse({"result": True, "data": data, "code": err_code.SUCCESS.code})
