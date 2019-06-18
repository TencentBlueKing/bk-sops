# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from tastypie.exceptions import ImmediateHttpResponse

from ..http import HttpResponseAuthFailed
from ..shortcuts import verify_or_return_insufficient_perms

logger = logging.getLogger('root')


def verify_or_raise_immediate_response(principal_type, principal_id, perms_tuples):
    permissions = verify_or_return_insufficient_perms(principal_type, principal_id, perms_tuples)

    if permissions:
        raise ImmediateHttpResponse(HttpResponseAuthFailed(permissions))
