# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # 创建工单
    create_ticket = bind_property(Operation, name="create_ticket", method="POST", path="/openapi/v2/tickets/")

    # 查询节点信息
    retrieve_ticket_info = bind_property(
        Operation, name="retrieve_ticket_info", method="GET", path="/openapi/v2/tickets/{ticket_id}/"
    )

    # 处理单据节点
    operate_node = bind_property(Operation, name="operate_node", method="POST", path="/v2/itsm/operate_node/")


class Client(APIGatewayClient):
    """Bkapi bk-itsm client"""

    _api_name = "bk-itsm"

    api = bind_property(Group, name="api")
