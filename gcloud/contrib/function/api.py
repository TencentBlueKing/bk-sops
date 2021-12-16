# -*- coding: utf-8 -*-
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from gcloud.contrib.function.models import FunctionTask
from gcloud.contrib.function.serializers import FunctionTaskClaimantTransferRequestSerializer, \
    FunctionTaskClaimantTransferResponse
from gcloud.core.api_adapter.user_role import is_user_role
from gcloud.iam_auth import IAMMeta


class FunctionTaskClaimantTransferView(APIView):

    @swagger_auto_schema(
        method="POST", operation_summary="职能转交", request_body=FunctionTaskClaimantTransferRequestSerializer,
        responses={200: FunctionTaskClaimantTransferResponse},
    )
    @action(methods=["POST"], detail=False)
    def post(self, request):
        # 获取用户名鉴权是否拥有职能化权限
        username = request.user.username
        if not is_user_role(username, IAMMeta.FUNCTION_VIEW_ACTION):
            return Response({"result": False, "message": "没有查看职能化任务权限"})

        # 获取请求参数并校验
        serializer = FunctionTaskClaimantTransferRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 查询传进来的id职能化任务是否有效
        serializer_data = serializer.data
        function_task_query = FunctionTask.objects.filter(id=serializer_data["id"]).values("claimant")
        if not function_task_query.count():
            return Response({"result": False, "message": "该id查询不到职能化任务"})

        # 查询当前任务是否有认领人判断是否已认领,并且请求的用户是否是认领人
        claimant = function_task_query.first().get("claimant")
        if not claimant:
            return Response({"result": False, "message": "查询不到该职能化任务认领人"})
        elif claimant != username:
            return Response({"result": False, "message": "非该职能化任务认领人无法转交"})

        # 修改并返回结果
        FunctionTask.objects.filter(id=serializer_data["id"]).update(claimant=serializer_data["claimant"])
        return Response({"result": True, "data": None})
