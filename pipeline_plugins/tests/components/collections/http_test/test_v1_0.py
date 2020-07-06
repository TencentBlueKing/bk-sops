# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from mock import MagicMock

from pipeline.component_framework.test import (
    ComponentTestCase,
    ComponentTestMixin,
    CallAssertion,
    ExecuteAssertion,
    ScheduleAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.http.v1_0 import HttpComponent


class HttpComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            HTTP_CALL_REQUEST_ERR_CASE,
            HTTP_CALL_RESP_NOT_JSON_CASE,
            HTTP_CALL_RESP_STATUS_CODE_ERR_CASE,
            HTTP_CALL_EXP_TEST_ERR_CASE,
            HTTP_CALL_NO_HEADER_CASE,
            HTTP_CALL_WITH_HEADER_CASE,
            HTTP_CALL_EXP_FAIL_CASE,
            HTTP_CALL_EXP_SUCCESS_CASE,
        ]

    def component_cls(self):
        return HttpComponent


HTTP_REQUEST = "pipeline_plugins.components.collections.http.v1_0.request"
HTTP_BOOLRULE = "pipeline_plugins.components.collections.http.v1_0.BoolRule"

# ------------------------------------------------

HTTP_CALL_REQUEST_ERR_CASE = ComponentTestCase(
    name="http call request error case",
    inputs={
        "bk_http_request_method": "method_token",
        "bk_http_request_url": "url_token",
        "bk_http_request_body": "body_token",
        "bk_http_request_header": [],
        "bk_http_success_exp": "exp_token",
        "bk_http_timeout": 0,
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=ScheduleAssertion(success=False, outputs={"ex_data": u"请求异常，详细信息: exc_token1"}),
    schedule_call_assertion=[
        CallAssertion(
            func=HTTP_REQUEST,
            calls=[
                Call(
                    method="method_token",
                    url="url_token",
                    verify=False,
                    data="body_token".encode("utf-8"),
                    timeout=30,
                    headers={"Content-type": "application/json"},
                )
            ],
        )
    ],
    patchers=[Patcher(target=HTTP_REQUEST, side_effect=Exception("exc_token1"))],
)

# ------------------------------------------------

NOT_JSON_RESPONSE = MagicMock()
NOT_JSON_RESPONSE.json = MagicMock(side_effect=Exception("exc_token2"))
NOT_JSON_RESPONSE.status_code = 200

HTTP_CALL_RESP_NOT_JSON_CASE = ComponentTestCase(
    name="http call response is not json case",
    inputs={
        "bk_http_request_method": "method_token",
        "bk_http_request_url": "url_token",
        "bk_http_request_body": "body_token",
        "bk_http_request_header": [],
        "bk_http_success_exp": "exp_token",
        "bk_http_timeout": 0,
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=ScheduleAssertion(
        success=False, outputs={"ex_data": u"请求响应数据格式非 JSON", "status_code": NOT_JSON_RESPONSE.status_code}
    ),
    schedule_call_assertion=[
        CallAssertion(
            func=HTTP_REQUEST,
            calls=[
                Call(
                    method="method_token",
                    url="url_token",
                    verify=False,
                    data="body_token".encode("utf-8"),
                    timeout=30,
                    headers={"Content-type": "application/json"},
                )
            ],
        )
    ],
    patchers=[Patcher(target=HTTP_REQUEST, return_value=NOT_JSON_RESPONSE)],
)

# ------------------------------------------------

STAUS_500_RESPONSE = MagicMock()
STAUS_500_RESPONSE.json = MagicMock(return_value="json_token1")
STAUS_500_RESPONSE.status_code = 500

HTTP_CALL_RESP_STATUS_CODE_ERR_CASE = ComponentTestCase(
    name="http call response status 500 case",
    inputs={
        "bk_http_request_method": "method_token",
        "bk_http_request_url": "url_token",
        "bk_http_request_body": "body_token",
        "bk_http_request_header": [],
        "bk_http_success_exp": "exp_token",
        "bk_http_timeout": 100,
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "ex_data": u"请求失败，状态码: {}，响应: {}".format(STAUS_500_RESPONSE.status_code, STAUS_500_RESPONSE.json()),
            "data": STAUS_500_RESPONSE.json(),
            "status_code": STAUS_500_RESPONSE.status_code,
        },
    ),
    schedule_call_assertion=[
        CallAssertion(
            func=HTTP_REQUEST,
            calls=[
                Call(
                    method="method_token",
                    url="url_token",
                    verify=False,
                    data="body_token".encode("utf-8"),
                    timeout=30,
                    headers={"Content-type": "application/json"},
                )
            ],
        )
    ],
    patchers=[Patcher(target=HTTP_REQUEST, return_value=STAUS_500_RESPONSE)],
)

# ------------------------------------------------

TEST_ERR_BOOLRULE = MagicMock()
TEST_ERR_BOOLRULE.test = MagicMock(side_effect=Exception("exc_token3"))

EXP_TEST_ERR_RESPONSE = MagicMock()
EXP_TEST_ERR_RESPONSE.json = MagicMock(return_value="json_token2")
EXP_TEST_ERR_RESPONSE.status_code = 200

HTTP_CALL_EXP_TEST_ERR_CASE = ComponentTestCase(
    name="http call bool rule test err case",
    inputs={
        "bk_http_request_method": "method_token",
        "bk_http_request_url": "url_token",
        "bk_http_request_body": "body_token",
        "bk_http_request_header": [],
        "bk_http_success_exp": "exp_token",
        "bk_http_timeout": 5,
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "data": EXP_TEST_ERR_RESPONSE.json(),
            "status_code": EXP_TEST_ERR_RESPONSE.status_code,
            "ex_data": u"请求成功条件判定出错: exc_token3",
        },
    ),
    schedule_call_assertion=[
        CallAssertion(
            func=HTTP_REQUEST,
            calls=[
                Call(
                    method="method_token",
                    url="url_token",
                    verify=False,
                    data="body_token".encode("utf-8"),
                    timeout=5,
                    headers={"Content-type": "application/json"},
                )
            ],
        ),
        CallAssertion(func=TEST_ERR_BOOLRULE.test, calls=[Call(context={"resp": EXP_TEST_ERR_RESPONSE.json()})]),
    ],
    patchers=[
        Patcher(target=HTTP_REQUEST, return_value=EXP_TEST_ERR_RESPONSE),
        Patcher(target=HTTP_BOOLRULE, return_value=TEST_ERR_BOOLRULE),
    ],
)

# ------------------------------------------------

HTTP_CALL_NO_HEADER_RESPONSE = MagicMock()
HTTP_CALL_NO_HEADER_RESPONSE.json = MagicMock(return_value="json_token3")
HTTP_CALL_NO_HEADER_RESPONSE.status_code = 200

HTTP_CALL_NOT_HEADER_BOOLRULE = MagicMock()

HTTP_CALL_NO_HEADER_CASE = ComponentTestCase(
    name="http call no header case",
    inputs={
        "bk_http_request_method": "method_token",
        "bk_http_request_url": "url_token",
        "bk_http_request_body": "body_token",
        "bk_http_request_header": [],
        "bk_http_success_exp": "",
        "bk_http_timeout": -1,
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=ScheduleAssertion(
        success=True,
        schedule_finished=True,
        outputs={"data": HTTP_CALL_NO_HEADER_RESPONSE.json(), "status_code": HTTP_CALL_NO_HEADER_RESPONSE.status_code},
    ),
    schedule_call_assertion=[
        CallAssertion(
            func=HTTP_REQUEST,
            calls=[
                Call(
                    method="method_token",
                    url="url_token",
                    verify=False,
                    data="body_token".encode("utf-8"),
                    headers={"Content-type": "application/json"},
                    timeout=1,
                )
            ],
        ),
        CallAssertion(func=HTTP_CALL_NOT_HEADER_BOOLRULE.test, calls=[]),
    ],
    patchers=[
        Patcher(target=HTTP_REQUEST, return_value=HTTP_CALL_NO_HEADER_RESPONSE),
        Patcher(target=HTTP_BOOLRULE, return_value=HTTP_CALL_NOT_HEADER_BOOLRULE),
    ],
)

# ------------------------------------------------

HTTP_CALL_WITH_HEADER_RESPONSE = MagicMock()
HTTP_CALL_WITH_HEADER_RESPONSE.json = MagicMock(return_value="json_token3")
HTTP_CALL_WITH_HEADER_RESPONSE.status_code = 200

HTTP_CALL_WITH_HEADER_BOOLRULE = MagicMock()

HTTP_CALL_WITH_HEADER_CASE = ComponentTestCase(
    name="http call with header case",
    inputs={
        "bk_http_request_method": "method_token",
        "bk_http_request_url": "url_token",
        "bk_http_request_body": "body_token",
        "bk_http_request_header": [{"name": "name1", "value": "value1"}, {"name": "name2", "value": "value2"}],
        "bk_http_success_exp": "",
        "bk_http_timeout": 1,
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=ScheduleAssertion(
        success=True,
        schedule_finished=True,
        outputs={
            "data": HTTP_CALL_WITH_HEADER_RESPONSE.json(),
            "status_code": HTTP_CALL_WITH_HEADER_RESPONSE.status_code,
        },
    ),
    schedule_call_assertion=[
        CallAssertion(
            func=HTTP_REQUEST,
            calls=[
                Call(
                    method="method_token",
                    url="url_token",
                    verify=False,
                    data="body_token".encode("utf-8"),
                    headers={"name2": "value2", "Content-type": "application/json", "name1": "value1"},
                    timeout=1,
                )
            ],
        ),
        CallAssertion(func=HTTP_CALL_WITH_HEADER_BOOLRULE.test, calls=[]),
    ],
    patchers=[
        Patcher(target=HTTP_REQUEST, return_value=HTTP_CALL_WITH_HEADER_RESPONSE),
        Patcher(target=HTTP_BOOLRULE, return_value=HTTP_CALL_WITH_HEADER_BOOLRULE),
    ],
)

# ------------------------------------------------

HTTP_CALL_EXP_FAIL_RESPONSE = MagicMock()
HTTP_CALL_EXP_FAIL_RESPONSE.json = MagicMock(return_value="json_token4")
HTTP_CALL_EXP_FAIL_RESPONSE.status_code = 200

HTTP_CALL_EXP_FAIL_BOOLRULE = MagicMock()
HTTP_CALL_EXP_FAIL_BOOLRULE.test = MagicMock(return_value=False)

HTTP_CALL_EXP_FAIL_CASE = ComponentTestCase(
    name="http call expression fail case",
    inputs={
        "bk_http_request_method": "GET",
        "bk_http_request_url": "url_token",
        "bk_http_request_body": "body_token",
        "bk_http_request_header": [],
        "bk_http_success_exp": "exp_token1",
        "bk_http_timeout": 0,
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=ScheduleAssertion(
        success=False,
        outputs={
            "data": HTTP_CALL_EXP_FAIL_RESPONSE.json(),
            "status_code": HTTP_CALL_EXP_FAIL_RESPONSE.status_code,
            "ex_data": u"请求成功判定失败",
        },
    ),
    schedule_call_assertion=[
        CallAssertion(
            func=HTTP_REQUEST, calls=[Call(method="GET", url="url_token", verify=False, timeout=30, headers={})]
        ),
        CallAssertion(func=HTTP_CALL_EXP_FAIL_BOOLRULE.test, calls=[Call(context={"resp": "json_token4"})]),
    ],
    patchers=[
        Patcher(target=HTTP_REQUEST, return_value=HTTP_CALL_EXP_FAIL_RESPONSE),
        Patcher(target=HTTP_BOOLRULE, return_value=HTTP_CALL_EXP_FAIL_BOOLRULE),
    ],
)

# ------------------------------------------------

HTTP_CALL_EXP_SUCCESS_RESPONSE = MagicMock()
HTTP_CALL_EXP_SUCCESS_RESPONSE.json = MagicMock(return_value="json_token5")
HTTP_CALL_EXP_SUCCESS_RESPONSE.status_code = 200

HTTP_CALL_EXP_SUCCESS_BOOLRULE = MagicMock()
HTTP_CALL_EXP_SUCCESS_BOOLRULE.test = MagicMock(return_value=True)

HTTP_CALL_EXP_SUCCESS_CASE = ComponentTestCase(
    name="http call expression success case",
    inputs={
        "bk_http_request_method": "method_token",
        "bk_http_request_url": "url_token",
        "bk_http_request_body": "body_token",
        "bk_http_request_header": [],
        "bk_http_success_exp": "exp_token2",
        "bk_http_timeout": 0,
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=ScheduleAssertion(
        success=True,
        schedule_finished=True,
        outputs={
            "data": HTTP_CALL_EXP_SUCCESS_RESPONSE.json(),
            "status_code": HTTP_CALL_EXP_SUCCESS_RESPONSE.status_code,
        },
    ),
    schedule_call_assertion=[
        CallAssertion(
            func=HTTP_REQUEST,
            calls=[
                Call(
                    method="method_token",
                    url="url_token",
                    verify=False,
                    data="body_token".encode("utf-8"),
                    timeout=30,
                    headers={"Content-type": "application/json"},
                )
            ],
        ),
        CallAssertion(func=HTTP_CALL_EXP_SUCCESS_BOOLRULE.test, calls=[Call(context={"resp": "json_token5"})]),
    ],
    patchers=[
        Patcher(target=HTTP_REQUEST, return_value=HTTP_CALL_EXP_SUCCESS_RESPONSE),
        Patcher(target=HTTP_BOOLRULE, return_value=HTTP_CALL_EXP_SUCCESS_BOOLRULE),
    ],
)
