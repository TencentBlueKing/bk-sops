# -*- coding: utf-8 -*-
import logging

from django.conf.urls import url
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, serializers

from api.collections.itsm import BKItsmClient
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")

# 审批状态对应审批结果value
TRANSITION_MAP = {True: "TONGYI", False: "JUJUE"}


class ITSMViewRequestSerializer(serializers.Serializer):
    sn = serializers.CharField(help_text="单号")
    state_id = serializers.IntegerField(help_text="节点ID，必须是当前可处理的节点")
    is_passed = serializers.BooleanField(help_text="是否通过")
    message = serializers.CharField(help_text="审批备注", allow_blank=True)


class ITSMViewResponse(serializers.Serializer):
    result = serializers.BooleanField(read_only=True, help_text="请求结果")
    data = serializers.ListSerializer(child=serializers.DictField(), read_only=True, help_text="请求结果数据")


class ITSMNodeTransitionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        method="POST", operation_summary="提供节点审批功能", request_body=ITSMViewRequestSerializer,
        responses={200: ITSMViewResponse},
    )
    @action(methods=["POST"], detail=False)
    def post(self, request):
        # 获取请求中的参数并判断
        operator = request.user.username
        serializer = ITSMViewRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"result": False, "message": serializer.errors})

        # 创建client并获取序列化器数据
        client = BKItsmClient(username=operator)
        serializer_data = serializer.data

        # 构建审批表单字段列表参数
        fields = [
            {
                "key": "SHENPIJIEGUO",
                "value": TRANSITION_MAP[serializer_data["is_passed"]]
            },
            {
                "key": "SHENPIBEIZHU",
                "value": serializer_data["message"]
            }
        ]

        # 构建请求参数
        kwargs = {
            "operator": operator,
            "sn": serializer_data["sn"],
            "state_id": serializer_data["state_id"],
            "action_type": "TRANSITION",
            "fields": fields
        }
        itsm_result = client.operate_node(**kwargs)

        # 判断api请求结果是否成功
        if not itsm_result["result"]:
            message = handle_api_error("itsm", "node_transition", kwargs, itsm_result)
            logger.error(message)
            result = {"result": False, "message": message}
            return Response(result)

        return Response({"result": True, "data": []})


itsm_urlpatterns = [
    url(r"^itsm/node_transition/$", ITSMNodeTransitionView.as_view())
]
