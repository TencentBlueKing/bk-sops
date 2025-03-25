# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # bkapi resource announcement_get_current_announcements
    # Get announcement list
    announcement_get_current_announcements = bind_property(
        Operation,
        name="announcement_get_current_announcements",
        method="GET",
        path="/apigw/v1/announcement/get_current_announcements/",
    )

    # bkapi resource register_application
    # register for the application
    register_application = bind_property(
        Operation,
        name="register_application",
        method="POST",
        path="/apigw/v1/register/",
    )


class Client(APIGatewayClient):
    """Bkapi bk_notice client"""

    _api_name = "bk-notice"

    api = bind_property(Group, name="api")
