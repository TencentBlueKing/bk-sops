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
import hashlib
import hmac

import ujson as json


def get_signature(method, path, app_secret, params=None, data=None):
    """generate signature"""
    kwargs = {}
    if params:
        kwargs.update(params)
    if data:
        data = json.dumps(data) if isinstance(data, dict) else data
        kwargs["data"] = data
    kwargs = "&".join(["%s=%s" % (k, v) for k, v in sorted(list(kwargs.items()), key=lambda x: x[0])])
    orignal = "%s%s?%s" % (method, path, kwargs)
    signature = base64.b64encode(hmac.new(str(app_secret), orignal, hashlib.sha256).digest())
    return signature
