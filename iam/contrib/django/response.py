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

from django.http.response import JsonResponse

from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE


class IAMAuthFailedResponse(JsonResponse):
    def __init__(self, exc, *args, **kwargs):
        kwargs["data"] = {
            "result": False,
            "code": HTTP_AUTH_FORBIDDEN_CODE,
            "message": "you have no permission to opearte",
            "data": None,
            "permission": exc.perms_apply_data(),
        }
        kwargs["status"] = 499
        super(IAMAuthFailedResponse, self).__init__(*args, **kwargs)
