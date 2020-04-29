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

import json

from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from auth_backend.plugins.constants import AUTH_FORBIDDEN_CODE, HTTP_AUTH_FAILED_CODE


class HttpResponseAuthFailed(HttpResponse):
    status_code = HTTP_AUTH_FAILED_CODE

    def __init__(self, permission, *args, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        super(HttpResponse, self).__init__(*args, **kwargs)
        # Content is a bytestring. See the `content` property methods.
        result = {
            'result': False,
            'code': AUTH_FORBIDDEN_CODE,
            'message': 'you have no permission to operate',
            'data': {},
            'permission': permission
        }
        self.content = json.dumps(result, cls=DjangoJSONEncoder)
