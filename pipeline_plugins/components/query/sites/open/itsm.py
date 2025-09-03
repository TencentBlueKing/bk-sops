# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.urls import re_path
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from gcloud.iam_auth.utils import check_and_raise_raw_auth_fail_exception
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.utils.handlers import handle_api_error
from packages.bkapi.bk_itsm4.shortcuts import get_client_by_username as get_itsm4_client_by_username
from packages.bkapi.bk_itsm.shortcuts import get_client_by_username

logger = logging.getLogger("root")

# 审批状态对应审批结果value
TRANSITION_MAP = {True: "TONGYI", False: "JUJUE"}


class ITSMViewRequestSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(help_text="标准运维项目id")
    task_id = serializers.IntegerField(help_text="标准运维任务id")
    node_id = serializers.CharField(help_text="标准运维节点ID")
    is_passed = serializers.BooleanField(help_text="是否通过")
    message = serializers.CharField(help_text="审批备注", allow_blank=True)
    subprocess_id = serializers.CharField(help_text="父流程ID, 当有子流程当时候传", required=False)


class ITSMViewResponse(serializers.Serializer):
    result = serializers.BooleanField(read_only=True, help_text="请求结果")
    message = serializers.CharField(read_only=True, help_text="请求结果失败时返回信息")


class ITSMNodeTransitionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_common_data(self, request):
        # 获取请求中的参数并判断
        # 由于序列化器bool字段会默认给值,所以需要提前在序列化器校验之前校验is_passed
        if "is_passed" not in request.data:
            return Response({"result": False, "message": "is_passed 该字段是必填项"})
        operator = request.user.username
        serializer = ITSMViewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer_data = serializer.data

        # 判断是否是拒绝,如果是拒绝并且没有填写备注则失败
        if not serializer_data["is_passed"] and not serializer_data["message"]:
            return Response({"result": False, "message": "审批拒绝后需填入备注"})

        # 获取当前任务id以及节点id查询目前的itsm单据sn
        task_flow_instance_query = TaskFlowInstance.objects.filter(
            pk=serializer_data["task_id"], project_id=serializer_data["project_id"]
        )
        if not task_flow_instance_query.exists():
            return Response({"result": False, "message": "查询不到任务记录"})

        subprocess_stack = []
        subprocess_id = serializer_data.get("subprocess_id")
        if subprocess_id is not None:
            subprocess_stack = subprocess_id.split(",")

        # 获取节点详情
        node_detail = task_flow_instance_query.first().get_node_detail(
            serializer_data["node_id"],
            operator,
            project_id=serializer_data["project_id"],
            subprocess_stack=subprocess_stack,
        )
        if not node_detail["result"]:
            message = node_detail["message"]
            logger.error(message)
            result = {"result": False, "message": message}
            return Response(result)

        # 获取节点输出
        node_outputs = node_detail["data"]["outputs"]
        if not node_outputs:
            return Response({"result": False, "message": "获取该节点输出参数为空"})

        return serializer_data, node_outputs

    @swagger_auto_schema(
        method="POST",
        operation_summary="提供旧版节点审批功能",
        request_body=ITSMViewRequestSerializer,
        responses={200: ITSMViewResponse},
    )
    @action(methods=["POST"], detail=False)
    def post(self, request):
        serializer_data, node_outputs = self._get_common_data(request)
        operator = request.user.username

        # 从node_outputs中获取单号
        sn = ""
        for node_output in node_outputs:
            if node_output["key"] == "sn":
                sn = node_output["value"]
                break
        if not sn:
            return Response({"result": False, "message": "该审批节点输出参数中没有itsm单据(sn)"})

        # 创建client
        client = get_client_by_username(username=operator, stage=settings.BK_APIGW_STAGE_NAME)

        # 获取单据信息查询节点id
        ticket_info_result = client.api.get_ticket_info({"sn": sn}, headers={"X-Bk-Tenant-Id": request.user.tenant_id})
        if not ticket_info_result["result"]:
            message = handle_api_error("itsm", "get_ticket_info", request.data, ticket_info_result)
            logger.error(message)
            check_and_raise_raw_auth_fail_exception(ticket_info_result, message)
            result = {"result": False, "message": message}
            return Response(result)

        # 获取当前单据的步骤
        ticket_info_data = ticket_info_result["data"]
        current_steps = ticket_info_data["current_steps"]

        # 获取itsm节点id部分
        state_id = ""
        # 由于标准运维生成的审批流程是itsm特定的,所以当审批步骤的name为"内置审批节点"时
        # 则可以认为该节点是审批节点
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
            # 由于审批时,审批通过和审批拒绝时的"备注"字段是不同的,并且不可区分
            # 所以不管是通过还是拒绝,都需要将两个备注字段赋值写入
            # 并且审批是否通过的布尔值小写写入,所以一共需要写入三个字段
            # 所以此处判断fields长度为3时即可以认为两个备注和一个审批意见都已写入,使用break结束循环
            if len(fields) == 3:
                break

        # 构建请求参数
        kwargs = {"operator": operator, "sn": sn, "state_id": state_id, "action_type": "TRANSITION", "fields": fields}

        itsm_result = client.api.operate_node(kwargs)

        # 判断api请求结果是否成功
        if not itsm_result["result"]:
            message = handle_api_error("itsm", "node_transition", kwargs, itsm_result)
            logger.error(message)
            check_and_raise_raw_auth_fail_exception(itsm_result, message)
            result = {"result": False, "message": message}
            return Response(result)

        return Response({"result": True, "data": None})


class ITSMNodeTransitionNewView(ITSMNodeTransitionView):
    @swagger_auto_schema(
        method="POST",
        operation_summary="提供新版节点审批功能",
        request_body=ITSMViewRequestSerializer,
        responses={200: ITSMViewResponse},
    )
    @action(methods=["POST"], detail=False)
    def post(self, request):
        operator = request.user.username
        serializer_data, node_outputs = self._get_common_data(request)
        ticket_id = ""
        task_id = ""
        for node_output in node_outputs:
            if node_output["key"] == "id":
                ticket_id = node_output["value"]
                break
        if not ticket_id:
            return Response({"result": False, "message": "该审批节点输出参数中没有itsm工单id"})
        client = get_itsm4_client_by_username(username=operator, stage=settings.BK_APIGW_STAGE_NAME)
        ticket_info_result = client.api.ticket_detail(
            {"id": ticket_id}, headers={"X-Bk-Tenant-Id": request.user.tenant_id}
        )
        for processor in ticket_info_result["data"]["current_processors"]:
            task_id = processor["task_id"]
            break
        if not ticket_info_result["result"]:
            message = handle_api_error("bk-itsm4", "ticket_detail", request.data, ticket_info_result)
            logger.error(message)
            check_and_raise_raw_auth_fail_exception(ticket_info_result, message)
            result = {"result": False, "message": message}
            return Response(result)
        kwargs = {
            "ticket_id": ticket_id,
            "task_id": task_id,
            "operator": operator,
            "operator_type": "user",
            "system_id": ticket_info_result["data"]["system_id"] or "",
            "action": "approve" if serializer_data["is_passed"] else "refuse",
            "desc": serializer_data["message"],
        }

        itsm_result = client.api.handle_approval_node(kwargs, headers={"X-Bk-Tenant-Id": request.user.tenant_id})

        if not itsm_result["result"]:
            message = handle_api_error("bk-itsm4", "handle_approval_node", kwargs, itsm_result)
            logger.error(message)
            check_and_raise_raw_auth_fail_exception(itsm_result, message)
            result = {"result": False, "message": message}
            return Response(result)

        return Response({"result": True, "data": None})


itsm_urlpatterns = [
    re_path(r"^itsm/node_transition/$", ITSMNodeTransitionView.as_view()),
    re_path(r"^itsm/node_transition_new/$", ITSMNodeTransitionNewView.as_view()),
]
