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

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from gcloud.user_custom_config.models import UserCustomProjectConfig
from gcloud.user_custom_config.serializer import UserCustomProjectConfigSerializer
from gcloud.core.apis.drf.viewsets.utils import ApiMixin


class UserCustomConfViewset(ApiMixin, viewsets.GenericViewSet):
    queryset = UserCustomProjectConfig.objects.all()
    serializer_class = UserCustomProjectConfigSerializer

    def _set_userconf(self, request, *args, **kwargs):
        request.data["username"] = request.user.username
        request.data["project_id"] = kwargs.get("project_id")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user_custom_config = UserCustomProjectConfig.objects.set_userconf(**validated_data)
        return user_custom_config

    def _get_userconf(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")
        username = request.user.username
        serializer = self.get_serializer(data={"project_id": project_id, "username": username})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user_custom_config = UserCustomProjectConfig.objects.get_conf(**validated_data)
        return user_custom_config

    @action(methods=["post"], detail=False)
    def set(self, request, *args, **kwargs):
        user_custom_config = self._set_userconf(request, *args, **kwargs)
        response_serializer = self.serializer_class(instance=user_custom_config)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=["get"], detail=False)
    def get(self, request, *args, **kwargs):
        user_custom_config = self._get_userconf(request, *args, **kwargs)
        response_serializer = self.serializer_class(instance=user_custom_config)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
