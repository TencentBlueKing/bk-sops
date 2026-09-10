# -*- coding: utf-8 -*-
import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from gcloud.contrib.function.models import FunctionTask
from gcloud.contrib.function.serializers import (
    FunctionTaskClaimantTransferRequestSerializer,
    FunctionTaskClaimantTransferResponse,
)
from gcloud.iam_auth import IAMMeta, PermissionCheck, PermissionService, res_factory

logger = logging.getLogger("root")


class FunctionTaskClaimantTransferView(APIView):
    @swagger_auto_schema(
        method="POST",
        operation_summary="职能转交",
        request_body=FunctionTaskClaimantTransferRequestSerializer,
        responses={200: FunctionTaskClaimantTransferResponse},
    )
    @action(methods=["POST"], detail=False)
    def post(self, request):
        username = request.user.username

        # 获取请求参数并校验
        serializer = FunctionTaskClaimantTransferRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 查询传进来的id职能化任务是否有效
        serializer_data = serializer.validated_data
        with transaction.atomic():
            function_task = (
                FunctionTask.objects.select_for_update()
                .select_related("task__project")
                .filter(id=serializer_data["id"], task__project__tenant_id=request.user.tenant_id)
                .first()
            )
            if function_task is None:
                raise Http404
            PermissionService().require(
                username,
                request.user.tenant_id,
                PermissionCheck(
                    IAMMeta.TASK_CLAIM_ACTION,
                    res_factory.resources_for_task_obj(function_task.task)[0],
                ),
            )
            if function_task.claimant != username:
                raise ValidationError("only current claimant can transfer task")
            if (
                not get_user_model()
                .objects.filter(username=serializer_data["claimant"], tenant_id=request.user.tenant_id)
                .exists()
            ):
                raise ValidationError("target claimant does not belong to tenant")
            function_task.claimant = serializer_data["claimant"]
            function_task.save(update_fields=["claimant"])
        return Response({"result": True, "data": None})
