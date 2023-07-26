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
from cachetools import TTLCache, cached
from django.views.decorators.http import require_GET
from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.models import ComponentModel

from gcloud import err_code
from gcloud.apigw.decorators import (
    mark_request_whether_is_trust,
    project_inject,
    return_json_response,
)
from gcloud.apigw.utils import api_hash_key
from gcloud.core.models import DisabledComponent, ProjectBasedComponent


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@cached(cache=TTLCache(maxsize=1024, ttl=60), key=api_hash_key)
def get_plugin_list(request, project_id):
    project_id = request.project.id

    exclude_component_codes = ProjectBasedComponent.objects.get_components_of_other_projects(project_id)
    exclude_component_codes.extend(
        DisabledComponent.objects.get_disabled_components(
            scope=DisabledComponent.SCOPE_TYPE_FLOW, action=DisabledComponent.ACTION_TYPE_LIST
        )
    )
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
                "form": comp.form,
            }
        )

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
