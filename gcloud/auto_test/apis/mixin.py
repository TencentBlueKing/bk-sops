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
import logging

from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from gcloud.auto_test.apis.serilaziers.common import IdsListSerializer
from gcloud.core.apis.drf.viewsets import ApiMixin

from .authentication import CsrfExemptSessionAuthentication
from .permission import EnablePermission, TestTokenPermission

logger = logging.getLogger("root")


def _queryset_has_field(queryset, field_name):
    try:
        queryset.model._meta.get_field(field_name)
    except FieldDoesNotExist:
        return False
    return True


class BaseAutoTestMixin(ApiMixin):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [EnablePermission]


class AutoTestMixin(BaseAutoTestMixin):
    permission_classes = [EnablePermission, TestTokenPermission]


class BatchDeleteMixin(AutoTestMixin):
    auto_test_require_project_id = False

    @swagger_auto_schema(method="delete", request_body=IdsListSerializer, responses={204: None})
    @action(methods=["delete"], detail=False)
    def batch_delete(self, request, *args, **kwargs):
        """批量删除"""
        data = request.data
        body_serializer = IdsListSerializer(data=data)
        body_serializer.is_valid(raise_exception=True)
        ids_list = body_serializer.validated_data.get("ids_list")
        project_id = body_serializer.validated_data.get("project_id")

        target_queryset = self.queryset.filter(id__in=ids_list)
        if self.auto_test_require_project_id:
            if not project_id:
                raise ValidationError({"project_id": "当前资源批量删除必须传入项目ID"})
            target_queryset = target_queryset.filter(project_id=project_id)

        with transaction.atomic():
            if _queryset_has_field(target_queryset, "is_deleted"):
                target_queryset.update(is_deleted=True)
                logger.info(f"自动化测试({self.__doc__})使用(update)批量删除了{ids_list}")
            else:
                target_queryset.delete()
                logger.info(f"自动化测试({self.__doc__})使用(delete)批量删除了{ids_list}")
        return Response(status=204)
