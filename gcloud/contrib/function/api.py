# -*- coding: utf-8 -*-
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from gcloud.contrib.function.models import FunctionTask


class FunctionTaskClaimantTransferRequest(serializers.Serializer):
    key = serializers.CharField(read_only=True, help_text="变量KEY")
    value = serializers.CharField(read_only=True, help_text="变量值")


class FunctionTaskClaimantTransferResponse(serializers.Serializer):
    key = serializers.CharField(read_only=True, help_text="变量KEY")
    value = serializers.CharField(read_only=True, help_text="变量值")


class FunctionTaskClaimantTransferView(APIView):
    @swagger_auto_schema(
        method="POST", operation_summary="职能转交", request_body=FunctionTaskClaimantTransferRequest,
        responses={200: FunctionTaskClaimantTransferResponse},
    )
    @action(methods=["POST"], detail=False)
    def function_task_claimant_transfer(self, request):
        claimant = FunctionTask.objects.filter(id=request.data["id"]).values("claimant").first().get("claimant")
        username = request.user.username
        if not claimant:
            return Response({"result": False, "message": "查询不到该项目认领人"})
        elif claimant != username:
            return Response({"result": False, "message": "非该职能化认领人无法转交"})
        FunctionTask.objects.filter(id=request.data["id"]).update(claimant=username)
        return Response({"result": True, "data": []})
