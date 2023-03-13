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
import json
import logging

import requests
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

import env
from gcloud.common_template.models import CommonSpace, CommonTemplate
from gcloud.core.apis.drf.permission import IamPermission, IamPermissionInfo, HAS_OBJECT_PERMISSION
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers.common_space import CommonSpaceSerializer, ActionGrantOrRevokeSerializer
from gcloud.core.apis.drf.viewsets import GcloudModelViewSet
from gcloud.iam_auth import res_factory, IAMMeta
from gcloud.iam_auth.utils import grant_or_revoke_common_space_actions_to_user

logger = logging.getLogger("root")


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
        "get_common_space_users": IamPermissionInfo(
            IAMMeta.COMMON_SPACE_MANAGE_ACTION, res_factory.resources_for_common_space_obj, HAS_OBJECT_PERMISSION
        ),
        "grant_or_revoke_common_space_action": IamPermissionInfo(
            IAMMeta.COMMON_SPACE_MANAGE_ACTION, res_factory.resources_for_common_space_obj, HAS_OBJECT_PERMISSION
        ),
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

    @swagger_auto_schema(method="post", request_body=ActionGrantOrRevokeSerializer)
    @action(methods=["post"], detail=True)
    def grant_or_revoke_common_space_action(self, request, *args, **kwargs):
        serializer = ActionGrantOrRevokeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        operate = serializer.validated_data["operate"]
        actions = serializer.validated_data["actions"]
        users = serializer.validated_data["users"]
        for user in users:
            grant_or_revoke_common_space_actions_to_user(
                operator=request.user.username,
                username=user,
                common_space_id=kwargs["pk"],
                actions=actions,
                operate=operate,
            )
        return Response({})

    @action(methods=["get"], detail=True)
    def get_common_space_users(self, request, *args, **kwargs):
        if not env.BK_IAM_SEARCH_ENGINE_HOST:
            raise ValidationError("iam search engine is not available")
        common_space_id = kwargs["pk"]
        data = [
            {
                "system": IAMMeta.SYSTEM_ID,
                "subject_type": "user",
                "action": {"id": IAMMeta.COMMON_SPACE_JOIN_ACTION},
                "resource": [
                    {"system": IAMMeta.SYSTEM_ID, "type": "common_space", "id": str(common_space_id), "attribute": {}}
                ],
            },
            {
                "system": IAMMeta.SYSTEM_ID,
                "subject_type": "user",
                "action": {"id": IAMMeta.COMMON_SPACE_MANAGE_ACTION},
                "resource": [
                    {"system": IAMMeta.SYSTEM_ID, "type": "common_space", "id": str(common_space_id), "attribute": {}}
                ],
            },
        ]
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            f"http://{env.BK_IAM_SEARCH_ENGINE_HOST}/api/v1/engine/batch-search/",
            headers=headers,
            data=json.dumps(data),
        )
        try:
            result = response.json()
            if result["code"] != 0:
                return Response({"result": False, "message": result["message"]})
        except Exception as e:
            logger.exception(e)
            return Response({"result": False, "message": f"get users from iam search engine error: {e}"})
        join_data, manage_data = result["data"]["results"]
        return Response(
            {
                "join_users": [data["name"] for data in join_data if data["type"] == "user"],
                "manage_users": [data["name"] for data in manage_data if data["type"] == "user"],
            }
        )
