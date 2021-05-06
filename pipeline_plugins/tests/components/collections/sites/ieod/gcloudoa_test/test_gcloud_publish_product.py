# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    CallAssertion,
    ExecuteAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.sites.ieod.gcloudoa.publish_product.v1_0 import (
    GcloudPublishProductComponent,
)


class GcloudPublishProductComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [PUBLISH_PRODUCT_SUCCESS_CASE, PUBLISH_PRODUCT_FAIL_CASE]

    def component_cls(self):
        return GcloudPublishProductComponent


class MockClient(object):
    def __init__(self, publish_product_return=None):
        self.gcloud = MagicMock()
        self.gcloud.publish_product = MagicMock(return_value=publish_product_return)


# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites." "ieod.gcloudoa.publish_product.v1_0.ESB_GET_OLD_CLIENT_BY_USER"
)

# mock clients
PUBLISH_PRODUCT_SUCCESS_CLIENT = MockClient(publish_product_return={"result": True, "message": "success"})

PUBLISH_PRODUCT_FAIL_CLIENT = MockClient(
    publish_product_return={"result": False, "message": "failed", "request_id": "123456"}
)

# test case
PUBLISH_PRODUCT_SUCCESS_CASE = ComponentTestCase(
    name="publish product success case",
    inputs={
        "gcloud_region": "idc",
        "gcloud_game_id": 0,
        "gcloud_access_id": "access_id",
        "gcloud_access_key": "access_key",
        "gcloud_product_id": 560,
    },
    parent_data={"executor": "admin"},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=PUBLISH_PRODUCT_SUCCESS_CLIENT.gcloud.publish_product,
            calls=[
                Call(
                    {
                        "region": "idc",
                        "game_id": 0,
                        "access_id": "access_id",
                        "access_key": "access_key",
                        "product_id": 560,
                    }
                )
            ],
        ),
    ],
    patchers=[Patcher(target=GET_CLIENT_BY_USER, return_value=PUBLISH_PRODUCT_SUCCESS_CLIENT)],
)

PUBLISH_PRODUCT_FAIL_CASE = ComponentTestCase(
    name="publish product fail case",
    inputs={
        "gcloud_region": "idc",
        "gcloud_game_id": 1,
        "gcloud_access_id": "access_id",
        "gcloud_access_key": "access_key",
        "gcloud_product_id": 1,
    },
    parent_data={"executor": "admin"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": "调用游戏区服管理(GCLOUD)接口gcloud.publish_product返回失败,"
            ' params={"region":"idc","game_id":1,"access_id":"access_id"'
            ',"access_key":"access_key","product_id":1}, error=failed, request_id=123456'
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=PUBLISH_PRODUCT_FAIL_CLIENT.gcloud.publish_product,
            calls=[
                Call(
                    {
                        "region": "idc",
                        "game_id": 1,
                        "access_id": "access_id",
                        "access_key": "access_key",
                        "product_id": 1,
                    }
                )
            ],
        ),
    ],
    patchers=[Patcher(target=GET_CLIENT_BY_USER, return_value=PUBLISH_PRODUCT_FAIL_CLIENT)],
)
