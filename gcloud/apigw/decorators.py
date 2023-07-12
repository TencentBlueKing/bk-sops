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

from functools import wraps

import pytz
import ujson as json
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from gcloud import err_code
from gcloud.apigw.exceptions import InvalidUserError
from gcloud.conf import settings
from gcloud.core.models import Project
from gcloud.apigw.utils import get_project_with
from gcloud.apigw.constants import PROJECT_SCOPE_CMDB_BIZ, DEFAULT_APP_WHITELIST
from gcloud.apigw.whitelist import EnvWhitelist

app_whitelist = EnvWhitelist(transient_list=DEFAULT_APP_WHITELIST, env_key="APP_WHITELIST")
WHETHER_PREPARE_BIZ = getattr(settings, "WHETHER_PREPARE_BIZ_IN_API_CALL", True)


def check_white_apps(request):
    app_code = getattr(request.app, settings.APIGW_MANAGER_APP_CODE_KEY)
    return app_whitelist.has(app_code)


def inject_user(request):
    user_model = get_user_model()

    if isinstance(request.user, user_model):
        return

    username = getattr(request.user, settings.APIGW_MANAGER_USER_USERNAME_KEY)
    if not username:
        raise InvalidUserError(
            "username cannot be empty, make sure api gateway has sent correct params: {}".format(username)
        )

    user, _ = user_model.objects.get_or_create(username=username)

    setattr(request, "user", user)


def mark_request_whether_is_trust(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        setattr(request, "is_trust", check_white_apps(request))

        try:
            inject_user(request)
        except InvalidUserError as e:
            return JsonResponse({"result": False, "message": str(e), "code": err_code.REQUEST_PARAM_INVALID.code})

        return view_func(request, *args, **kwargs)

    return wrapper


def _get_project_scope_from_request(request):
    if request.method == "GET":
        obj_scope = request.GET.get("scope", PROJECT_SCOPE_CMDB_BIZ)
    else:
        params = json.loads(request.body)
        obj_scope = params.get("scope", PROJECT_SCOPE_CMDB_BIZ)

    return obj_scope


def return_json_response(view_func):
    """
    将返回的dict数据转为JsonResponse
    @param view_func:
    @return:
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        result = view_func(request, *args, **kwargs)
        # 如果返回的是dict且request中有trace_id，则在响应中加上
        if isinstance(result, dict):
            if hasattr(request, "trace_id"):
                result["trace_id"] = request.trace_id
            result = JsonResponse(result)
        return result

    return _wrapped_view


def project_inject(view_func):
    @wraps(view_func)
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


def timezone_inject(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        expected_timezone = request.GET.get("expected_timezone", None)
        try:
            tz = pytz.timezone(expected_timezone) if expected_timezone else None
        except pytz.UnknownTimeZoneError:
            return JsonResponse(
                {
                    "result": False,
                    "data": "",
                    "message": f"expected_timezone {expected_timezone} is unknown.",
                    "code": err_code.VALIDATION_ERROR.code,
                }
            )
        setattr(request, "tz", tz)
        return view_func(request, *args, **kwargs)

    return wrapper
