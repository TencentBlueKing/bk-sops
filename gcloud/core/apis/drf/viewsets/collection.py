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

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail

from gcloud.contrib.collection.models import Collection
from gcloud.core.apis.drf.serilaziers.collection import CollectionSerializer
from gcloud.core.apis.drf.viewsets import GcloudModelViewSet
from gcloud import err_code


class CollectionViewSet(GcloudModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(username=request.user.username)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(username=request.user.username)
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(username=request.user.username)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(username=request.user.username)
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        category = serializer.validated_data["category"]
        instance_id = serializer.validated_data["instance_id"]
        if Collection.objects.filter(username=username, category=category, instance_id=instance_id).exists():
            message = "The collection of user {} with category:{} and instance_id:{} already exists".format(
                username, category, instance_id
            )
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
