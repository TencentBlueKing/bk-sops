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
import base64
import hmac
import time

from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import BasePermission

AUTO_TEST_TOKEN_DEFAULT_EXPIRE_SECONDS = 60
AUTO_TEST_TOKEN_MAX_EXPIRE_SECONDS = 600

AUTO_TEST_SCOPE_TEMPLATE = "template"
AUTO_TEST_SCOPE_COMMON_TEMPLATE = "common_template"
AUTO_TEST_SCOPE_PERIODIC_TASK = "periodic_task"
AUTO_TEST_SCOPE_CHOICES = (
    (AUTO_TEST_SCOPE_TEMPLATE, "项目流程模版"),
    (AUTO_TEST_SCOPE_COMMON_TEMPLATE, "通用流程模版"),
    (AUTO_TEST_SCOPE_PERIODIC_TASK, "周期任务"),
)
AUTO_TEST_VALID_SCOPES = {scope for scope, _ in AUTO_TEST_SCOPE_CHOICES}
AUTO_TEST_PROJECT_SCOPES = {AUTO_TEST_SCOPE_TEMPLATE, AUTO_TEST_SCOPE_PERIODIC_TASK}

_TRUE_VALUES = {"1", "true", "yes", "on"}


def is_auto_test_enabled():
    enable = getattr(settings, "AUTO_TEST_ENABLE", False)
    if isinstance(enable, str):
        return enable.strip().lower() in _TRUE_VALUES
    return bool(enable)


def get_auto_test_secret():
    return getattr(settings, "AUTO_TEST_SECRET_KEY", "").strip()


def get_auto_test_token_max_expire_seconds():
    expire = getattr(settings, "AUTO_TEST_TOKEN_MAX_EXPIRE_SECONDS", AUTO_TEST_TOKEN_MAX_EXPIRE_SECONDS)
    if not expire:
        return AUTO_TEST_TOKEN_MAX_EXPIRE_SECONDS

    try:
        expire = int(expire)
    except ValueError:
        return AUTO_TEST_TOKEN_MAX_EXPIRE_SECONDS

    return max(1, expire)


def _normalize_project_id(project_id):
    if project_id in (None, ""):
        return ""

    try:
        return str(int(project_id))
    except (TypeError, ValueError):
        raise PermissionDenied("无效的项目ID")


def _normalize_expire(expire):
    try:
        expire = int(expire)
    except (TypeError, ValueError):
        expire = AUTO_TEST_TOKEN_DEFAULT_EXPIRE_SECONDS

    expire = max(1, expire)
    return min(expire, get_auto_test_token_max_expire_seconds())


def _validate_scope_project(scope, project_id):
    if scope not in AUTO_TEST_VALID_SCOPES:
        raise PermissionDenied("无效的资源范围")

    if scope in AUTO_TEST_PROJECT_SCOPES and not project_id:
        raise PermissionDenied("当前资源范围必须传入项目ID")

    if scope not in AUTO_TEST_PROJECT_SCOPES and project_id:
        raise PermissionDenied("当前资源范围不支持项目ID")


def _token_signature(secret, expire_ts, scope, project_id):
    payload = f"{expire_ts}:{scope}:{project_id}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), payload, "sha256").hexdigest()


def _validate_request_secret(request):
    secret = get_auto_test_secret()
    key = request.headers.get("Auto-Test-Key")
    if not (key and secret):
        raise AuthenticationFailed("无效的token")

    if not hmac.compare_digest(key, secret):
        raise AuthenticationFailed("无效的token")


class EnablePermission(BasePermission):
    """接口是否启用"""

    def has_permission(self, request, view):
        if not is_auto_test_enabled():
            raise PermissionDenied("自动化测试辅助接口未启用")

        if not get_auto_test_secret():
            raise PermissionDenied("自动化测试辅助接口密钥未配置")

        return True


class AutoTestKeyPermission(BasePermission):
    """自动化测试接口密钥校验"""

    def has_permission(self, request, view):
        _validate_request_secret(request)
        return True


class TestTokenPermission(BasePermission):
    """自动化测试接口校验"""

    def has_permission(self, request, view):
        token = request.headers.get("Auto-Test-Token")
        if not token:
            raise AuthenticationFailed("无效的token")

        _validate_request_secret(request)

        try:
            token_str = base64.urlsafe_b64decode(token).decode("utf-8")
        except Exception:  # noqa
            raise AuthenticationFailed("无效的token")

        token_list = token_str.split(":")

        if len(token_list) != 4:
            raise AuthenticationFailed("无效的token")

        ts_str, scope, project_id, signature = token_list
        try:
            expire_ts = float(ts_str)
        except ValueError:
            raise AuthenticationFailed("无效的token")

        if expire_ts < time.time():
            raise AuthenticationFailed("token已过期")

        secret = get_auto_test_secret()
        expected_signature = _token_signature(secret, ts_str, scope, project_id)
        if not hmac.compare_digest(expected_signature, signature):
            raise AuthenticationFailed("无效的token")

        view_scope = getattr(view, "auto_test_scope", None)
        if view_scope != scope:
            raise PermissionDenied("token无权访问当前资源")

        if getattr(view, "auto_test_require_project_id", False):
            request_project_id = _normalize_project_id(request.data.get("project_id"))
            if not request_project_id or request_project_id != project_id:
                raise PermissionDenied("token无权访问当前项目")
        elif project_id:
            raise PermissionDenied("token无权访问当前资源")

        return True


def generate_token(expire=AUTO_TEST_TOKEN_DEFAULT_EXPIRE_SECONDS, scope=None, project_id=None, secret=None) -> str:
    """
    生成测试token
    :param expire: 超时时间
    :param scope: 资源范围
    :param project_id: 项目ID
    :param secret: 服务端密钥
    :return: str
    """
    secret = secret if secret is not None else get_auto_test_secret()
    if not secret:
        raise PermissionDenied("自动化测试辅助接口密钥未配置")

    expire = _normalize_expire(expire)
    project_id = _normalize_project_id(project_id)
    _validate_scope_project(scope, project_id)
    ts_str = str(time.time() + expire)
    signature = _token_signature(secret, ts_str, scope, project_id)
    token = f"{ts_str}:{scope}:{project_id}:{signature}"
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))

    return b64_token.decode("utf-8")
