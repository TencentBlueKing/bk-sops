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
import os
import time

from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import BasePermission


class EnablePermission(BasePermission):
    """接口是否启用"""

    def has_permission(self, request, view):
        if os.environ.get("BKAPP_AUTO_TEST_ENABLE", False):
            return True
        else:
            raise PermissionDenied("自动化测试辅助接口未启用")


class TestTokenPermission(BasePermission):
    """自动化测试接口校验"""

    def has_permission(self, request, view):
        key = request.headers.get("Auto-Test-Key")
        token = request.headers.get("Auto-Test-Token")
        if not (token and key):
            raise AuthenticationFailed("无效的token")
        try:
            token_str = base64.urlsafe_b64decode(token).decode("utf-8")
        except Exception:  # noqa
            raise AuthenticationFailed("无效的token")

        token_list = token_str.split(":")

        if len(token_list) != 2:
            raise AuthenticationFailed("无效的token")

        ts_str = token_list[0]
        if float(ts_str) < time.time():
            raise AuthenticationFailed("token已过期")

        sha256 = hmac.new(key.encode("utf-8"), ts_str.encode("utf-8"), "sha256")
        if sha256.hexdigest() != token_list[1]:
            raise AuthenticationFailed("无效的token")
        return (None, None)


def generate_token(key: str, expire=60) -> str:
    """
    生成测试token
    :param key: 加密的key
    :param expire: 超时时间
    :return: str
    """
    ts_str = str(time.time() + expire)
    ts_byte = ts_str.encode("utf-8")
    sha256_tshex_str = hmac.new(key.encode("utf-8"), ts_byte, "sha256").hexdigest()
    token = ts_str + ":" + sha256_tshex_str
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))

    return b64_token.decode("utf-8")
