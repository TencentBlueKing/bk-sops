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

from django.utils.decorators import method_decorator

from rest_framework.response import Response
from blueapps.account.decorators import login_exempt

from ..mixin import BaseAutoTestMixin
from ..serilaziers.common import AutoTestTokenSerialzer
from ..permission import generate_token


@method_decorator(login_exempt, name="dispatch")
class AutoTestTokenViewSet(BaseAutoTestMixin):
    """自动测试接口token"""

    serializer_class = AutoTestTokenSerialzer

    def create(self, request, *args, **kwargs):
        """生成测试token"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = generate_token(**serializer.validated_data)
        return Response(data=token)
