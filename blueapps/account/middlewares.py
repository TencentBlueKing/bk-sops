# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.utils.module_loading import import_string

from blueapps.account.conf import ConfFixture


def load_middleware(middleware):
    path = "blueapps.account.components.{middleware}".format(middleware=middleware)
    return import_string(path)


if hasattr(ConfFixture, "LOGIN_REQUIRED_MIDDLEWARE"):
    LoginRequiredMiddleware = load_middleware(ConfFixture.LOGIN_REQUIRED_MIDDLEWARE)

if hasattr(ConfFixture, "WEIXIN_MIDDLEWARE"):
    WeixinLoginRequiredMiddleware = load_middleware(ConfFixture.WEIXIN_MIDDLEWARE)

if hasattr(ConfFixture, "RIO_MIDDLEWARE"):
    RioLoginRequiredMiddleware = load_middleware(ConfFixture.RIO_MIDDLEWARE)

if hasattr(ConfFixture, "BK_JWT_MIDDLEWARE"):
    BkJwtLoginRequiredMiddleware = load_middleware(ConfFixture.BK_JWT_MIDDLEWARE)
