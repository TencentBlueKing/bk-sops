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

from functools import wraps

import ujson as json
from django.http import JsonResponse
from django.utils.decorators import available_attrs

from gcloud import err_code
from gcloud.conf import settings
from gcloud.core.models import Project
from gcloud.apigw.utils import get_project_with
from gcloud.apigw.constants import PROJECT_SCOPE_CMDB_BIZ, DEFAULT_APP_WHITELIST
from gcloud.apigw.whitelist import EnvWhitelist

app_whitelist = EnvWhitelist(transient_list=DEFAULT_APP_WHITELIST, env_key="APP_WHITELIST")
WHETHER_PREPARE_BIZ = getattr(settings, "WHETHER_PREPARE_BIZ_IN_API_CALL", True)


def check_white_apps(request):
    app_code = getattr(request.app, settings.APIGW_APP_CODE_KEY)
    return app_whitelist.has(app_code)


def mark_request_whether_is_trust(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def wrapper(request, *args, **kwargs):
        setattr(request, "is_trust", check_white_apps(request))

        return view_func(request, *args, **kwargs)

    return wrapper


def _get_project_scope_from_request(request):
    if request.method == "GET":
        obj_scope = request.GET.get("scope", PROJECT_SCOPE_CMDB_BIZ)
    else:
        params = json.loads(request.body)
        obj_scope = params.get("scope", PROJECT_SCOPE_CMDB_BIZ)

    return obj_scope


def project_inject(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def wrapper(request, *args, **kwargs):

        obj_id = kwargs.get("project_id")
        try:
            obj_scope = _get_project_scope_from_request(request)
        except Exception:
            return JsonResponse(
                {"result": False, "message": "invalid param format", "code": err_code.REQUEST_PARAM_INVALID.code}
            )

        try:
            project = get_project_with(obj_id=obj_id, scope=obj_scope)
        except Project.DoesNotExist:
            return JsonResponse(
                {
                    "result": False,
                    "message": "project({id}) with scope({scope}) does not exist.".format(id=obj_id, scope=obj_scope),
                    "code": err_code.CONTENT_NOT_EXIST.code,
                }
            )

        setattr(request, "project", project)
        return view_func(request, *args, **kwargs)

    return wrapper
