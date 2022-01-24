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

from rest_framework import permissions, status, mixins
from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail

from gcloud.contrib.collection.models import Collection
from gcloud.core.apis.drf.serilaziers.collection import CollectionSerializer
from gcloud.core.apis.drf.viewsets import GcloudReadOnlyViewSet
from gcloud import err_code


class CollectionViewSet(GcloudReadOnlyViewSet, mixins.CreateModelMixin):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(username=self.request.user.username)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        for item in serializer.validated_data:
            username = item["username"]
            category = item["category"]
            instance_id = item["instance_id"]
            if Collection.objects.filter(username=username, category=category, instance_id=instance_id).exists():
                message = "The collection of user {} with category:{} and instance_id:{} already exists".format(
                    username, category, instance_id
                )
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
