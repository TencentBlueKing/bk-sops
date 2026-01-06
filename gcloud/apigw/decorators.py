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
            # 针对权限中心的异常进行统一的处理
            result = {
                "result": False,
                "data": None,
                "message": "iam authentication exception, please check, action:{}".format(e.action.id),
                "code": 3599999,
            }
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


def _remove_keys_from_dict(data, keys_to_remove):
    """
    递归地从字典中移除指定的键
    @param data: 要处理的数据（字典或列表）
    @param keys_to_remove: 要移除的键的列表，支持 "xx.yy.zz" 格式
    @return: 处理后的数据
    """
    if not isinstance(data, (dict, list)):
        return data

    # 构建路径映射，将 "xx.yy.zz" 转换为 [("xx", "yy", "zz"), ...]
    path_mappings = []
    for key in keys_to_remove:
        if "." in key:
            path_mappings.append(tuple(key.split(".")))
        else:
            path_mappings.append((key,))

    if isinstance(data, list):
        return [_remove_keys_from_dict(item, keys_to_remove) for item in data]

    # 深拷贝避免修改原数据
    result = copy.deepcopy(data)

    # 处理直接键
    direct_keys = [key for key in keys_to_remove if "." not in key]
    for key in direct_keys:
        if key in result:
            del result[key]

    # 处理路径键（如 "xx.yy.zz"）
    for path_tuple in path_mappings:
        if len(path_tuple) == 1:
            # 已经在上面处理了
            continue

        # 递归查找并删除
        _remove_nested_key(result, path_tuple)

    return result


def _remove_nested_key(data, path_tuple):
    """
    递归地从嵌套字典/列表中移除指定路径的键
    支持中间层是列表的情况，会对列表中每一项递归处理

    例如：路径 "data.items.secret"
    - 如果 data.items 是列表，会对列表中每一项删除 secret 键
    - 如果 data.items 是字典，会删除字典中的 secret 键

    @param data: 要处理的数据（字典或列表）
    @param path_tuple: 路径元组，如 ("data", "items", "secret")
    """
    if not path_tuple:
        return

    if len(path_tuple) == 1:
        # 到达目标键，删除它
        key = path_tuple[0]
        if isinstance(data, dict) and key in data:
            del data[key]
        elif isinstance(data, list):
            # 如果是列表，对每个元素递归处理
            for item in data:
                if isinstance(item, dict) and key in item:
                    del item[key]
                elif isinstance(item, list):
                    # 如果列表中的项也是列表，继续递归
                    _remove_nested_key(item, path_tuple)
        return

    # 继续递归
    current_key = path_tuple[0]
    remaining_path = path_tuple[1:]

    if isinstance(data, dict):
        if current_key in data:
            next_data = data[current_key]
            if isinstance(next_data, dict):
                # 下一层是字典，继续递归
                _remove_nested_key(next_data, remaining_path)
            elif isinstance(next_data, list):
                # 下一层是列表，对列表中每一项递归处理剩余路径
                for item in next_data:
                    _remove_nested_key(item, remaining_path)
    elif isinstance(data, list):
        # 当前数据是列表，对列表中每一项递归处理完整路径
        # 因为列表中的每一项应该都有完整的路径结构
        for item in data:
            _remove_nested_key(item, path_tuple)


def mcp_apigw(exclude_responses=None):
    """
    装饰器：根据app_code前缀决定是否从响应中排除指定的键
    只有当request.app存在且app_code以settings.APIGW_MCP_APP_CODE_PREFIX配置的值开头时，才启用排除逻辑

    @param exclude_responses: 要排除的键列表，支持 "xx.yy.zz" 格式的嵌套路径
    @return: 装饰器函数

    使用示例:
        @mcp_apigw(exclude_responses=["sensitive_key", "data.items.secret"])
        @return_json_response
        def my_view(request):
            return {
                "result": True,
                "data": {
                    "items": [{"name": "item1", "secret": "value1"}],
                    "sensitive_key": "value"
                }
            }

        如果app_code以settings.APIGW_MCP_APP_CODE_PREFIX配置的值开头（默认"v_mcp"），
        则返回的响应中会排除"sensitive_key"和"data.items.secret"字段。
    """
    if exclude_responses is None:
        exclude_responses = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 执行原始视图函数
            result = view_func(request, *args, **kwargs)

            # 检查是否需要启用排除逻辑
            should_exclude = False

            # 检查 request.app 是否存在
            if hasattr(request, "app") and request.app:
                # 获取 app_code
                app_code = getattr(request.app, settings.APIGW_MANAGER_APP_CODE_KEY, None)
                if app_code:
                    # 从 settings 获取 v_mcp 前缀
                    v_mcp_prefix = getattr(settings, "APIGW_MCP_APP_CODE_PREFIX", "v_mcp")
                    # 检查 app_code 是否以指定前缀开头
                    app_code_check = app_code.startswith(v_mcp_prefix)
                    # 从 settings 获取 MCP Server ID HTTP Header 名称
                    mcp_server_id_header = getattr(settings, "APIGW_MCP_SERVER_ID_HEADER", "HTTP_X_BKAPI_MCP_SERVER_ID")
                    # 检查 request.META 中是否有指定的 header 且值不为空
                    mcp_server_id = request.META.get(mcp_server_id_header, "")
                    mcp_server_id_check = bool(mcp_server_id and mcp_server_id.strip())
                    # 两个条件都需要满足
                    if app_code_check and mcp_server_id_check:
                        should_exclude = True

            # 如果需要排除且返回的是字典或JsonResponse，则进行过滤
            if should_exclude and exclude_responses:
                if isinstance(result, JsonResponse):
                    # JsonResponse 的内容需要提取、处理、然后重新创建
                    result_data = json.loads(result.content.decode("utf-8"))
                    result_data = _remove_keys_from_dict(result_data, exclude_responses)
                    result = JsonResponse(result_data)
                elif isinstance(result, dict):
                    # 直接处理字典
                    result = _remove_keys_from_dict(result, exclude_responses)

            return result

        return wrapper

    return decorator
