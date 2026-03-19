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

import copy
from functools import wraps

import pytz
import ujson as json
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from iam.exceptions import AuthFailedException

from gcloud import err_code
from gcloud.apigw.constants import DEFAULT_APP_WHITELIST, PROJECT_SCOPE_CMDB_BIZ
from gcloud.apigw.exceptions import InvalidUserError
from gcloud.apigw.utils import get_project_with
from gcloud.apigw.whitelist import EnvWhitelist
from gcloud.conf import settings
from gcloud.core.models import Project

app_whitelist = EnvWhitelist(transient_list=DEFAULT_APP_WHITELIST, env_key="APP_WHITELIST")
WHETHER_PREPARE_BIZ = getattr(settings, "WHETHER_PREPARE_BIZ_IN_API_CALL", True)


def check_white_apps(request):
    app_code = getattr(request.app, settings.APIGW_MANAGER_APP_CODE_KEY)
    return app_whitelist.has(app_code)


def check_allowed_limited_api_apps(request):
    if getattr(request, "app", None) is None:
        return False
    app_code = getattr(request.app, settings.APIGW_MANAGER_APP_CODE_KEY)
    return app_code in getattr(settings, "ALLOWED_LIMITED_API_APPS", [])


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
        setattr(request, "allow_limited_apis", check_allowed_limited_api_apps(request))

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
        params = json.loads(request.body) if request.body else {}
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
        try:
            result = view_func(request, *args, **kwargs)
        except AuthFailedException as e:
            result = {
                "result": False,
                "data": None,
                "message": "iam authentication exception, please check, action:{}".format(e.action.id),
                "code": 3599999,
            }
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


def _remove_keys_from_dict(data, keys_to_remove):
    """
    递归地从字典中移除指定的键
    @param data: 要处理的数据（字典或列表）
    @param keys_to_remove: 要移除的键的列表，支持 "xx.yy.zz" 格式
    @return: 处理后的数据
    """
    if not isinstance(data, (dict, list)):
        return data

    path_mappings = []
    for key in keys_to_remove:
        if "." in key:
            path_mappings.append(tuple(key.split(".")))
        else:
            path_mappings.append((key,))

    if isinstance(data, list):
        return [_remove_keys_from_dict(item, keys_to_remove) for item in data]

    result = copy.deepcopy(data)

    direct_keys = [key for key in keys_to_remove if "." not in key]
    for key in direct_keys:
        if key in result:
            del result[key]

    for path_tuple in path_mappings:
        if len(path_tuple) == 1:
            continue
        _remove_nested_key(result, path_tuple)

    return result


def is_mcp_request(request):
    """
    判断请求是否来源于 MCP

    :param request: Django request 对象
    :return: bool，True 表示是 MCP 请求，False 表示不是
    """
    if hasattr(request, "app") and request.app:
        app_code = getattr(request.app, settings.APIGW_MANAGER_APP_CODE_KEY, None)
        if app_code:
            v_mcp_prefix = getattr(settings, "APIGW_MCP_APP_CODE_PREFIX", "v_mcp")
            app_code_check = app_code.startswith(v_mcp_prefix)
            mcp_server_id_header = getattr(settings, "APIGW_MCP_SERVER_ID_HEADER", "HTTP_X_BKAPI_MCP_SERVER_ID")
            mcp_server_id = request.META.get(mcp_server_id_header, "")
            mcp_server_id_check = bool(mcp_server_id and mcp_server_id.strip())
            if app_code_check or mcp_server_id_check:
                return True
    return False


def _remove_nested_key(data, path_tuple):
    """
    递归地从嵌套字典/列表中移除指定路径的键
    支持中间层是列表的情况，会对列表中每一项递归处理

    @param data: 要处理的数据（字典或列表）
    @param path_tuple: 路径元组，如 ("data", "items", "secret")
    """
    if not path_tuple:
        return

    if len(path_tuple) == 1:
        key = path_tuple[0]
        if isinstance(data, dict) and key in data:
            del data[key]
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and key in item:
                    del item[key]
                elif isinstance(item, list):
                    _remove_nested_key(item, path_tuple)
        return

    current_key = path_tuple[0]
    remaining_path = path_tuple[1:]

    if isinstance(data, dict):
        if current_key in data:
            next_data = data[current_key]
            if isinstance(next_data, dict):
                _remove_nested_key(next_data, remaining_path)
            elif isinstance(next_data, list):
                for item in next_data:
                    _remove_nested_key(item, remaining_path)
    elif isinstance(data, list):
        for item in data:
            _remove_nested_key(item, path_tuple)


def mcp_apigw(exclude_responses=None, trim_responses=None):
    """
    装饰器：MCP 请求响应处理

    @param exclude_responses: 要无条件移除的键列表，支持 "xx.yy.zz" 格式
    @param trim_responses: 可选裁剪字段映射 {字段名: 裁剪函数}。
        字段名为 data 下的直接键名（如 "pipeline_tree"）。
        MCP 请求默认移除这些字段；客户端传入 include_{字段名}=true 时，
        调用裁剪函数处理后返回。非 MCP 请求不受影响。
    """
    if exclude_responses is None:
        exclude_responses = []
    if trim_responses is None:
        trim_responses = {}

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            request.is_mcp_request = is_mcp_request(request)
            result = view_func(request, *args, **kwargs)

            if request.is_mcp_request and (exclude_responses or trim_responses):
                if isinstance(result, JsonResponse):
                    result_data = json.loads(result.content.decode("utf-8"))
                    _apply_mcp_transforms(request, result_data, exclude_responses, trim_responses)
                    result = JsonResponse(result_data)
                elif isinstance(result, dict):
                    _apply_mcp_transforms(request, result, exclude_responses, trim_responses)

            return result

        return wrapper

    return decorator


def _apply_mcp_transforms(request, result_data, exclude_responses, trim_responses):
    """对 MCP 响应数据执行裁剪/移除操作（原地修改）"""
    data = result_data.get("data") if isinstance(result_data, dict) else None

    if trim_responses and isinstance(data, dict):
        for field, trimmer in trim_responses.items():
            if field not in data:
                continue
            include_param = "include_{}".format(field)
            if _is_param_true(request, include_param):
                data[field] = trimmer(data[field])
            else:
                del data[field]

    if exclude_responses:
        cleaned = _remove_keys_from_dict(result_data, exclude_responses)
        result_data.clear()
        result_data.update(cleaned)


def _is_param_true(request, param_name):
    """检查请求参数（GET 或 POST body）中指定参数是否为 true"""
    val = request.GET.get(param_name)
    if val is None and request.method == "POST" and request.body:
        try:
            body = json.loads(request.body)
            val = body.get(param_name)
        except Exception:
            pass
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes")
