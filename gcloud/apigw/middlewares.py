# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from apigw_manager.apigw.authentication import ApiGatewayJWTUserMiddleware
from blueapps.account import get_user_model
from django.http import JsonResponse

from gcloud import err_code


class CustomApiGatewayJWTUserMiddleware(ApiGatewayJWTUserMiddleware):
    def get_user(self, request, api_name=None, bk_username=None, verified=False, **credentials):
        if not bk_username:
            return JsonResponse(
                {
                    "result": False,
                    "message": "bk_username cannot be empty, make sure api gateway has sent correct params",
                    "code": err_code.REQUEST_PARAM_INVALID.code,
                }
            )

        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(username=bk_username)
        return user
