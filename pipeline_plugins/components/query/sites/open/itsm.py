# -*- coding: utf-8 -*-
import logging

from django.conf.urls import url
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, serializers

from api.collections.itsm import BKItsmClient
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")

# 审批状态对应审批结果value
TRANSITION_MAP = {True: "TONGYI", False: "JUJUE"}


class ITSMViewRequestSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(help_text="标准运维项目id")
    task_id = serializers.IntegerField(help_text="标准运维任务id")
    node_id = serializers.CharField(help_text="标准运维节点ID")
    is_passed = serializers.BooleanField(help_text="是否通过")
    message = serializers.CharField(help_text="审批备注", allow_blank=True)


class ITSMViewResponse(serializers.Serializer):
    result = serializers.BooleanField(read_only=True, help_text="请求结果")
    message = serializers.CharField(read_only=True, help_text="请求结果失败时返回信息")


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
        serializer.is_valid(raise_exception=True)

        serializer_data = serializer.data

        # 判断是否是拒绝,如果是拒绝并且没有填写备注则失败
        if not serializer_data["is_passed"] and not serializer_data["message"]:
            return Response({"result": False, "message": "审批拒绝后需填入备注"})

        # 获取当前任务id以及节点id查询目前的itsm单据sn
        task_flow_instance_query = TaskFlowInstance.objects.filter(pk=serializer_data["task_id"],
                                                                   project_id=serializer_data["project_id"])
        if not task_flow_instance_query.count():
            return Response({"result": False, "message": "查询不到任务记录"})

        node_detail = task_flow_instance_query.first().get_node_detail(serializer_data["node_id"], operator,
                                                                       project_id=serializer_data["project_id"])
        if not node_detail:
            return Response({"result": False, "message": "获取节点数据失败"})

        node_outputs = node_detail["data"]["outputs"]

        if not node_outputs:
            return Response({"result": False, "message": "获取该节点输出参数失败"})

        # 获取单号
        sn = ""
        for node_output in node_outputs:
            if node_output["key"] == "sn":
                sn = node_output["value"]
                break
        if not sn:
            return Response({"result": False, "message": "获取该审批节点itsm单据失败"})

        # 创建client
        client = BKItsmClient(username=operator)
        ticket_info_result = client.get_ticket_info(sn)

        if not ticket_info_result["result"]:
            return Response({"result": False, "message": ticket_info_result["message"]})

        ticket_info_data = ticket_info_result["data"]
        current_steps = ticket_info_data["current_steps"]

        # 获取itsm节点id
        state_id = ""
        for current_step in current_steps:
            if current_step["name"] == "内置审批节点":
                state_id = current_step["state_id"]
                break
        if not state_id:
            return Response({"result": False, "message": "该审批流程已结束"})

        # 构建审批表单字段列表参数
        fields = []
        # 获取该单据下该节点的字段
        ticket_fields = ticket_info_data["fields"]
        for ticket_field in reversed(ticket_fields):
            if ticket_field["name"] == "备注":
                field = {"key": ticket_field["key"], "value": serializer_data["message"]}
                fields.append(field)
            elif ticket_field["name"] == "审批意见":
                field = {"key": ticket_field["key"], "value": str(serializer_data["is_passed"]).lower()}
                fields.append(field)
            if len(fields) == 3:
                break

        # 构建请求参数
        kwargs = {
            "operator": operator,
            "sn": sn,
            "state_id": state_id,
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

        return Response({"result": True, "data": None})


itsm_urlpatterns = [
    url(r"^itsm/node_transition/$", ITSMNodeTransitionView.as_view())
]
