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
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.apigw.views.utils import paginate_list_data
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.iam_auth.conf import MINI_APP_ACTIONS
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.utils import get_mini_app_allowed_actions_for_user
from gcloud.iam_auth.view_interceptors.apigw import ProjectViewInterceptor


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(ProjectViewInterceptor())
def get_mini_app_list(request, project_id):
    tenant_id = request.user.tenant_id
    mini_apps = AppMaker.objects.filter(is_deleted=False, project_id=request.project.id, project__tenant_id=tenant_id)
    try:
        mini_apps, count = paginate_list_data(request, mini_apps)
    except Exception as e:
        return {"result": False, "data": "", "message": e, "code": err_code.INVALID_OPERATION.code}

    mini_app_ids = [mini_app.id for mini_app in mini_apps]

    # 获取用户轻应用权限
    appmaker_allowed_actions = get_mini_app_allowed_actions_for_user(
        request.user.username, MINI_APP_ACTIONS, mini_app_ids, tenant_id
    )

    mini_apps_data = []
    mini_app_return_fields = [
        "id",
        "name",
        "code",
        "link",
        "category",
        "task_template_id",
        "template_scheme_id",
    ]
    for mini_app in mini_apps:
        mini_app_allowed_action = appmaker_allowed_actions.get(str(mini_app.id), {})
        mini_app_data = {
            "auth_actions": [action for action, allowed in mini_app_allowed_action.items() if allowed],
        }
        mini_app_data.update({field: getattr(mini_app, field) for field in mini_app_return_fields})
        mini_apps_data.append(mini_app_data)

    return {"result": True, "data": mini_apps_data, "count": count, "code": err_code.SUCCESS.code}
