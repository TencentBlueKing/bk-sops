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
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from gcloud.core.apis.drf.viewsets import ApiMixin
from gcloud.auto_test.apis.serilaziers.common import IdsListSerializer
from .permission import EnablePermission, TestTokenPermission
from .authentication import CsrfExemptSessionAuthentication

logger = logging.getLogger("root")


class BaseAutoTestMixin(ApiMixin):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [EnablePermission]


class AutoTestMixin(BaseAutoTestMixin):
    permission_classes = [EnablePermission, TestTokenPermission]


class BatchDeleteMixin(AutoTestMixin):
    @swagger_auto_schema(method="delete", request_body=IdsListSerializer, responses={204: None})
    @action(methods=["delete"], detail=False)
    def batch_delete(self, request, *args, **kwargs):
        """批量删除"""
        data = request.data
        body_serializer = IdsListSerializer(data=data)
        body_serializer.is_valid(raise_exception=True)
        ids_list = body_serializer.validated_data.get("ids_list")

        try:
            self.queryset.filter(id__in=ids_list).update(is_deleted=True)
            logger.info(f"自动化测试({self.__doc__})使用(update)批量删除了{ids_list}")
        except Exception:  # noqa
            self.queryset.filter(id__in=ids_list).delete()
            logger.info(f"自动化测试({self.__doc__})使用(delete)批量删除了{ids_list}")
        return Response(status=204)
