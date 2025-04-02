# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # 新增告警屏蔽
    add_shield = bind_property(Operation, name="add_shield", method="POST", path="/app/shield/add/")

    # 接触告警屏蔽
    disable_shield = bind_property(Operation, name="disable_shield", method="POST", path="/app/shield/disable/")

    # 查询告警策略
    search_alarm_strategy = bind_property(
        Operation,
        name="search_alarm_strategy",
        method="POST",
        path="/app/alarm_strategy/search/",
    )


class Client(APIGatewayClient):
    """Bkapi bk-monitor client"""

    _api_name = "bk-monitor"

    api = bind_property(Group, name="api")
