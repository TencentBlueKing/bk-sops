# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # 刷新业务进程缓存
    flush_process = bind_property(
        Operation, name="flush_process", method="POST", path="/api/{bk_biz_id}/process/flush_process/"
    )

    # 创建任务
    create_job = bind_property(Operation, name="create_job", method="POST", path="/api/{bk_biz_id}/job/")
    # 查询任务状态
    job_status = bind_property(Operation, name="job_status", method="GET", path="/api/{bk_biz_id}/job/status/")


class Client(APIGatewayClient):
    """Bkapi bk_gsekit client"""

    _api_name = "bk_gsekit"

    api = bind_property(Group, name="api")
