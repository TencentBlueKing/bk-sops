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
import logging

from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger("root")


class CustomUserModelBackend(ModelBackend):
    """Get users by username"""

    def __init__(self):
        super().__init__()

        user_model = get_user_model()

        # 未将用户保存到 db，防止未预期添加用户数据
        # 未查询 db 中用户，因用户可能在 db 中不存在
        self.user_maker = lambda username: user_model(**{user_model.USERNAME_FIELD: username})

    def make_anonymous_user(self, bk_username=None):
        user = AnonymousUser()
        user.username = bk_username  # type: ignore
        # set the tenant_id
        user.tenant_id = ""  # type: ignore
        return user

    def authenticate(self, request, gateway_name, bk_username, tenant_id, verified, **credentials):
        # if not verified:
        #     return self.make_anonymous_user(bk_username=bk_username)
        logger.info("-------------------------------------")
        logger.info(f"gateway_name: {gateway_name}")
        logger.info(f"bk_username: {bk_username}")
        logger.info(f"tenant_id: {tenant_id}")
        logger.info(f"verified: {verified}")
        logger.info("-------------------------------------")
        user = self.user_maker(bk_username)
        user.tenant_id = tenant_id  # type: ignore
        return user


class ApiGatewayJWTUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def get_user(self, request, gateway_name=None, bk_username=None, tenant_id=None, verified=False, **credentials):
        # 传递 gateway_name 参数的用途：
        # 1. 来明确标识这个请求来自于网关
        # 2. 用户已经过认证，后端无需再认证
        # 3. 避免非预期调用激活对应后端使得用户认证被绕过
        return auth.authenticate(
            request,
            gateway_name=gateway_name,
            bk_username=bk_username,
            tenant_id=tenant_id,
            verified=verified,
            **credentials,
        )

    def __call__(self, request):
        jwt_info = getattr(request, "jwt", None)
        logger.info(f"-----jwt_info----- :{jwt_info}")
        logger.info(f"requests.headers: {request.headers}")
        if not jwt_info:
            return self.get_response(request)

        # skip when authenticated
        if hasattr(request, "user") and request.user.is_authenticated:
            return self.get_response(request)

        jwt_user = (jwt_info.payload.get("user") or {}).copy()
        logger.info(f"jwt_user :{jwt_user}")
        jwt_user.setdefault("bk_username", jwt_user.pop("username", None))

        request.user = self.get_user(request, gateway_name=jwt_info.gateway_name, **jwt_user)
        return self.get_response(request)
