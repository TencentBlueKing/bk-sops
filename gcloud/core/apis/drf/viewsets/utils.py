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

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from gcloud import err_code


class ApiMixin(GenericViewSet):

    EXEMPT_STATUS_CODES = {status.HTTP_204_NO_CONTENT}

    def finalize_response(self, request, response, *args, **kwargs):
        # 对rest_framework的Response进行统一处理
        if isinstance(response, Response):
            if response.exception is True:
                error = response.data.get(
                    "detail", ErrorDetail("Error from API exception", err_code.UNKNOWN_ERROR.code)
                )
                response.data = {"result": False, "data": response.data, "code": error.code, "message": str(error)}
            elif response.status_code not in self.EXEMPT_STATUS_CODES:
                response.data = {"result": True, "data": response.data, "code": err_code.SUCCESS.code, "message": ""}

        return super(ApiMixin, self).finalize_response(request, response, *args, **kwargs)
