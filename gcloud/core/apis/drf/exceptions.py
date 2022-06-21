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
from rest_framework import status
from rest_framework.exceptions import APIException

from gcloud import err_code


class RestApiException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = err_code.UNKNOWN_ERROR.description
    default_code = err_code.UNKNOWN_ERROR.code


class ObjectDoesNotExistException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = err_code.CONTENT_NOT_EXIST.description
    default_code = err_code.CONTENT_NOT_EXIST.code


class ValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = err_code.VALIDATION_ERROR.description
    default_code = err_code.VALIDATION_ERROR.code
