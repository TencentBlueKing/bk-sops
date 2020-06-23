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

_BK_SOPS_PREFIX = "35"


class ErrorCode(object):
    def __init__(self, code, description, ignore_prefix=False):
        self.code = int(code) if ignore_prefix else int(f"{_BK_SOPS_PREFIX}{code}")
        self.description = description

    def __str__(self):
        return self.code


SUCCESS = ErrorCode(code="0", description="success", ignore_prefix=True)

REQUEST_PARAM_INVALID = ErrorCode(code="40000", description="the content of param in your request is invalid")
REQUEST_FORBIDDEN_INVALID = ErrorCode(code="40100", description="you have no permission")
CONTENT_NOT_EXIST = ErrorCode(code="40400", description="the content you reqeust does not exist")
INVALID_OPERATION = ErrorCode(code="45000", description="invalid operation")
OPERATION_FAIL = ErrorCode(code="45100", description="invalid operation")
VALIDATION_ERROR = ErrorCode(code="46100", description="validation error")

ENV_ERROR = ErrorCode(code="55000", description="environment error")

UNKNOWN_ERROR = ErrorCode(code="99999", description="unknow error")
