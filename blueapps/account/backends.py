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

from blueapps.account.conf import ConfFixture
from blueapps.account.utils import load_backend

if hasattr(ConfFixture, "USER_BACKEND"):
    UserBackend = load_backend(ConfFixture.USER_BACKEND)

if hasattr(ConfFixture, "WEIXIN_BACKEND"):
    WeixinBackend = load_backend(ConfFixture.WEIXIN_BACKEND)

if hasattr(ConfFixture, "RIO_BACKEND"):
    RioBackend = load_backend(ConfFixture.RIO_BACKEND)

if hasattr(ConfFixture, "BK_JWT_BACKEND"):
    BkJwtBackend = load_backend(ConfFixture.BK_JWT_BACKEND)
