# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # bkapi resource healthz
    get_bk_token_userinfo = bind_property(
        Operation,
        name="bk_token_userinfo",
        method="GET",
        path="/login/api/v3/open/bk-tokens/userinfo/",
    )


class Client(APIGatewayClient):
    """Bkapi bk_user client"""

    _api_name = "bk-login"

    api = bind_property(Group, name="api")
