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
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)
from pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0 import CCBatchUpdateSetComponent


class CCBatchUpdateSetComponentTest(TestCase, ComponentTestMixin):
    def component_cls(self):
        return CCBatchUpdateSetComponent

    def cases(self):
        return [
            UPDATE_MODULE_SUCCESS_BY_CUSTOM,
            UPDATE_MODULE_FAILED_BY_CUSTOM,
            UPDATE_MODULE_FAILED_BY_TEMPLATE,
            UPDATE_MODULE_SUCCESS_BY_TEMPLATE,
        ]


class MockClient(object):
    def __init__(self, update_set_return_value=None, search_set_return_value=None):
        self.set_bk_api_ver = MagicMock()
        self.cc = MagicMock()
        self.cc.search_set = MagicMock(return_value=search_set_return_value)
        self.cc.update_set = MagicMock(return_value=update_set_return_value)


UPDATE_MODULE_SUCCESS_CLIENT = MockClient(
    update_set_return_value={
        "code": 0,
        "permission": None,
        "result": True,
        "request_id": "122345885",
        "message": "success",
        "data": None,
    },
    search_set_return_value={
        "code": 0,
        "permission": None,
        "result": True,
        "request_id": "122345885",
        "message": "success",
        "data": {"info": [{"bk_set_name": "3", "bk_set_id": 3}, {"bk_set_name": "4", "bk_set_id": 4}]},
    },
)

UPDATE_MODULE_FAILED_CLIENT = MockClient(
    update_set_return_value={
        "code": 0,
        "permission": None,
        "result": False,
        "request_id": "122345885",
        "message": "xxx",
        "data": None,
    },
    search_set_return_value={
        "code": 0,
        "permission": None,
        "result": True,
        "request_id": "122345885",
        "message": "success",
        "data": {"info": [{"bk_set_name": "3", "bk_set_id": 3}, {"bk_set_name": "4", "bk_set_id": 4}]},
    },
)

GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.cc.batch_update_set.v1_0.get_client_by_user"

UPDATE_MODULE_SUCCESS_BY_CUSTOM = ComponentTestCase(
    name="update set success by custom",
    inputs={
        "cc_tag_method": "custom",
        "cc_set_update_data": [
            {
                "cc_set_id": "2",
                "cc_set_name": "4",
                "bk_set_name": "test",
                "bk_set_type": "",
                "operator": "",
                "bk_bak_operator": "",
            }
        ],
        "cc_template_break_line": "",
    },
    parent_data={"executor": "executor", "biz_cc_id": 20},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "set_update_success": [
                {
                    "cc_set_id": "2",
                    "cc_set_name": "4",
                    "bk_set_name": "test",
                    "bk_set_type": "",
                    "operator": "",
                    "bk_bak_operator": "",
                }
            ],
            "set_update_failed": [],
        },
    ),
    schedule_assertion=ScheduleAssertion(success=True, schedule_finished=True, outputs={}),
    patchers=[Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_SUCCESS_CLIENT)],
)

UPDATE_MODULE_FAILED_BY_CUSTOM = ComponentTestCase(
    name="update set failed by custom",
    inputs={
        "cc_tag_method": "custom",
        "cc_set_update_data": [
            {
                "cc_set_id": "1",
                "cc_set_name": "3",
                "bk_set_name": "test",
                "bk_set_type": "",
                "operator": "",
                "bk_bak_operator": "",
            }
        ],
        "cc_template_break_line": "",
    },
    parent_data={"executor": "executor", "biz_cc_id": 20},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "set_update_success": [],
            "set_update_failed": [
                {
                    "cc_set_id": "1",
                    "cc_set_name": "3",
                    "bk_set_name": "test",
                    "bk_set_type": "",
                    "operator": "",
                    "bk_bak_operator": "",
                }
            ],
        },
    ),
    schedule_assertion=ScheduleAssertion(success=True, schedule_finished=True, outputs={}),
    patchers=[Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_FAILED_CLIENT)],
)

UPDATE_MODULE_FAILED_BY_TEMPLATE = ComponentTestCase(
    name="update set success by template",
    inputs={
        "cc_tag_method": "template",
        "cc_set_update_data": [
            {
                "cc_set_id": "1,2",
                "cc_set_name": "3,4",
                "bk_set_name": "test",
                "bk_set_type": "",
                "operator": "",
                "bk_bak_operator": "",
            }
        ],
        "cc_template_break_line": ",",
    },
    parent_data={"executor": "executor", "biz_cc_id": 20},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "set_update_success": [],
            "set_update_failed": [
                {
                    "cc_set_id": "1,2",
                    "cc_set_name": "3,4",
                    "bk_set_name": "test",
                    "bk_set_type": "",
                    "operator": "",
                    "bk_bak_operator": "",
                }
            ],
        },
    ),
    schedule_assertion=ScheduleAssertion(success=True, schedule_finished=True, outputs={}),
    patchers=[Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_FAILED_CLIENT)],
)

UPDATE_MODULE_SUCCESS_BY_TEMPLATE = ComponentTestCase(
    name="update set failed by template",
    inputs={
        "cc_tag_method": "template",
        "cc_set_update_data": [
            {
                "cc_set_id": "1,2",
                "cc_set_name": "3,4",
                "bk_set_name": "test",
                "bk_set_type": "",
                "operator": "",
                "bk_bak_operator": "",
            }
        ],
        "cc_template_break_line": ",",
    },
    parent_data={"executor": "executor", "biz_cc_id": 20},
    execute_assertion=ExecuteAssertion(
        success=True,
        outputs={
            "set_update_success": [
                {
                    "cc_set_id": "1,2",
                    "cc_set_name": "3,4",
                    "bk_set_name": "test",
                    "bk_set_type": "",
                    "operator": "",
                    "bk_bak_operator": "",
                }
            ],
            "set_update_failed": [],
        },
    ),
    schedule_assertion=ScheduleAssertion(success=True, schedule_finished=True, outputs={}),
    patchers=[Patcher(target=GET_CLIENT_BY_USER, return_value=UPDATE_MODULE_SUCCESS_CLIENT)],
)
