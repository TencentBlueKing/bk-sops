# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup

class Group(OperationGroup):
    @property
    def healthz(self) -> Operation:
        """
        bkapi resource healthz
        """
    @property
    def ping(self) -> Operation:
        """
        bkapi resource ping
        """

class Client(APIGatewayClient):
    """Bkapi bk_user client"""

    @property
    def api(self) -> Group:
        """api resources"""
