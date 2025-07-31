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

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AnonymousUser


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

        user = self.user_maker(bk_username)
        user.tenant_id = tenant_id  # type: ignore
        return user
