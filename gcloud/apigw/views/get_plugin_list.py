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
def get_plugin_list(request, project_id):
    project_id = request.project.id

    exclude_component_codes = ProjectBasedComponent.objects.get_components_with_project(project_id)
    components = ComponentModel.objects.filter(status=True).exclude(code__in=exclude_component_codes)

    data = []
    for comp_model in components:
        comp = ComponentLibrary.get_component_class(comp_model.code, comp_model.version)
        data.append(
            {
                "inputs": comp.inputs_format(),
                "outputs": comp.outputs_format(),
                "desc": comp.desc,
                "code": comp.code,
                "name": comp.name,
                "group_name": comp.group_name,
                "version": comp.version,
            }
        )

    return JsonResponse({"result": True, "data": data, "code": err_code.SUCCESS.code})
