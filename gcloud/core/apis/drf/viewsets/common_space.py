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
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination

from gcloud.common_template.models import CommonSpace, CommonTemplate
from gcloud.core.apis.drf.permission import IamPermission, IamPermissionInfo, HAS_OBJECT_PERMISSION
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers.common_space import CommonSpaceSerializer
from gcloud.core.apis.drf.viewsets import GcloudModelViewSet
from gcloud.iam_auth import res_factory, IAMMeta


class CommonSpacePermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(pass_all=True),
        "retrieve": IamPermissionInfo(pass_all=True),
        "destroy": IamPermissionInfo(
            IAMMeta.COMMON_SPACE_MANAGE_ACTION, res_factory.resources_for_common_space_obj, HAS_OBJECT_PERMISSION
        ),
        "update": IamPermissionInfo(
            IAMMeta.COMMON_SPACE_MANAGE_ACTION, res_factory.resources_for_common_space_obj, HAS_OBJECT_PERMISSION
        ),
        "create": IamPermissionInfo(IAMMeta.COMMON_SPACE_CREATE_ACTION),
    }


class CommonSpaceViewSet(GcloudModelViewSet):
    queryset = CommonSpace.objects.all()
    serializer_class = CommonSpaceSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [permissions.IsAuthenticated, CommonSpacePermission]
    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_common_space_obj,
        actions=[IAMMeta.COMMON_SPACE_MANAGE_ACTION, IAMMeta.COMMON_SPACE_JOIN_ACTION],
    )

    def destroy(self, request, *args, **kwargs):
        can_delete = CommonSpace.objects.can_delete(kwargs["pk"])
        if not can_delete:
            ids = CommonTemplate.objects.filter(space_id=kwargs["pk"]).values_list("id", flat=True)
            raise ValidationError(f"公共空间删除失败: 该公共空间下存在公共流程，id列表: [{','.join(list(ids))}]，不允许删除")
        return super(CommonSpaceViewSet, self).destroy(request, *args, **kwargs)
