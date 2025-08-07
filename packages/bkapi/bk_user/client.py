# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # bkapi resource healthz
    healthz = bind_property(
        Operation,
        name="healthz",
        method="GET",
        path="/healthz/",
    )

    # bkapi resource ping
    ping = bind_property(
        Operation,
        name="ping",
        method="GET",
        path="/ping/",
    )

    list_tenant = bind_property(
        Operation,
        name="tenants",
        method="GET",
        path="/api/v3/open/tenants/",
    )

    retrieve_user = bind_property(
        Operation,
        name="retrieve_user",
        method="GET",
        path="/api/v3/open/tenant/users/{bk_username}/",
    )

    list_user = bind_property(
        Operation,
        name="list_user",
        method="GET",
        path="/api/v3/open/tenant/users/",
    )

    display_info = bind_property(
        Operation,
        name="batch_query_user_display_info",
        method="GET",
        path="/api/v3/open/tenant/users/-/display_info/",
    )

    batch_lookup_virtual_user = bind_property(
        Operation,
        name="batch_lookup_virtual_user",
        method="GET",
        path="/api/v3/open/tenant/virtual-users/-/lookup/",
    )


class Client(APIGatewayClient):
    """Bkapi bk_user client"""

    _api_name = "bk-user"

    api = bind_property(Group, name="api")
