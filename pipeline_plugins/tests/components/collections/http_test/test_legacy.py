# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)

from pipeline_plugins.components.collections.common import HttpComponent


class LegacyHttpComponentValidateTestCase(TestCase, ComponentTestMixin):
    def cases(self):
        return [HTTP_CALL_REQUEST_VALIDATE_CASE]

    def component_cls(self):
        return HttpComponent


HTTP_REQUEST = "pipeline_plugins.components.collections.common.requests.request"
HTTP_VALIDATE = "pipeline_plugins.components.collections.common.DomainValidator.validate"


HTTP_CALL_REQUEST_VALIDATE_CASE = ComponentTestCase(
    name="legacy http call request validate error case",
    inputs={
        "bk_http_request_method": "GET",
        "bk_http_request_url": "http://127.0.0.1",
        "bk_http_request_body": "",
    },
    parent_data={},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=ScheduleAssertion(success=False, outputs={"ex_data": "仅允许访问域名(bk.example.com)下的URL"}),
    schedule_call_assertion=[CallAssertion(func=HTTP_REQUEST, calls=[])],
    patchers=[
        Patcher(target=HTTP_VALIDATE, return_value=(False, ["bk.example.com"])),
        Patcher(target=HTTP_REQUEST, return_value=MagicMock()),
    ],
)
