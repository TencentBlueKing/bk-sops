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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from gcloud.core.apis.drf.viewsets.utils import ApiMixin

from gcloud.user_custom_config.constants import get_options_by_fileds
from gcloud.user_custom_config.serializer import UserCustomProjectConfigOptionsSerializer


class UserCustomConfigOptions(ApiMixin, APIView):
    serializer_class = UserCustomProjectConfigOptionsSerializer

    @action(methods=["get"], detail=False)
    def get(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")
        configs = request.query_params.get("configs")
        serializer = self.get_serializer(data={"project_id": project_id, "configs": configs})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        data = get_options_by_fileds(validated_data["configs"])
        return Response(data, status=status.HTTP_200_OK)
