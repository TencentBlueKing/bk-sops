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
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response, timezone_inject
from gcloud.apigw.views.utils import format_template_list_data
from gcloud.common_template.models import CommonTemplate
from gcloud.iam_auth.conf import COMMON_FLOW_ACTIONS
from gcloud.iam_auth.utils import get_common_flow_allowed_actions_for_user


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@timezone_inject
def get_common_template_list(request):
    templates = CommonTemplate.objects.select_related("pipeline_template").filter(
        is_deleted=False, tenant_id=request.app.tenant_id
    )
    templates_data, common_templates_id_list = format_template_list_data(templates, return_id_list=True, tz=request.tz)
    # 注入用户有权限的actions
    common_templates_allowed_actions = get_common_flow_allowed_actions_for_user(
        request.user.username,
        COMMON_FLOW_ACTIONS,
        common_templates_id_list,
    )
    for template in templates_data:
        template_id = template["id"]
        template.setdefault("auth_actions", [])
        for action, allowed in common_templates_allowed_actions.get(str(template_id), {}).items():
            if allowed:
                template["auth_actions"].append(action)
    return {
        "result": True,
        "data": templates_data,
        "code": err_code.SUCCESS.code,
    }
