# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
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
    CallAssertion,
    ExecuteAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.monitor.alarm_shield_strategy.v1_1 import (
    MonitorAlarmShieldStrategyComponent,
)


class MonitorAlarmShieldStrategyComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            CREATE_SHIELD_FAIL_CASE,
            CREATE_SHIELD_SUCCESS_CASE,
        ]

    def component_cls(self):
        return MonitorAlarmShieldStrategyComponent


class MockClient(object):
    def __init__(self, create_shield_result=None, search_host=None):
        self.monitor = MagicMock()
        self.monitor.create_shield = MagicMock(return_value=create_shield_result)
        self.cc = MagicMock()
        self.cc.search_host = MagicMock(return_value=search_host)


class MockCMDB(object):
    def __init__(self):
        self.get_business_host = MagicMock(
            return_value=[
                {"bk_cloud_id": 0, "bk_host_id": 1, "bk_host_innerip": "127.0.0.1"},
                {"bk_cloud_id": 1, "bk_host_id": 2, "bk_host_innerip": "127.0.0.2"},
            ]
        )


class MockBusiness(object):
    def __init__(self):
        objects = MagicMock()
        objects.supplier_account_for_business = MagicMock(return_value="sa_token")
        self.objects = objects


# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.monitor.alarm_shield_strategy.v1_1" ".get_client_by_user"
)
CMDB_GET_BIZ_HOST = "gcloud.utils.cmdb.get_business_host"
BIZ_MODEL_SUPPLIER_ACCOUNT_FOR_BIZ = (
    "pipeline_plugins.components.collections.sites.open.monitor."
    "alarm_shield_strategy.v1_1.Business.objects.supplier_account_for_business"
)

# mock client
CREATE_SHIELD_FAIL_CLIENT = MockClient(create_shield_result={"result": False, "message": "create shield fail"})
CREATE_SHIELD_FAIL_GET_BIZ_HOST_RETURN = [
    {"bk_cloud_id": 0, "bk_host_id": 1, "bk_host_innerip": "127.0.0.1"},
    {"bk_cloud_id": 1, "bk_host_id": 2, "bk_host_innerip": "127.0.0.2"},
]
CREATE_SHIELD_FAIL_SUPPLIER_RETURN = "sa_token"

CREATE_SHIELD_SUCCESS_CLIENT = MockClient(
    create_shield_result={"result": True, "data": {"id": "1"}, "message": "success"}
)
CREATE_SHIELD_SUCCESS_GET_BIZ_HOST_RETURN = [
    {"bk_cloud_id": 0, "bk_host_id": 1, "bk_host_innerip": "127.0.0.1"},
    {"bk_cloud_id": 1, "bk_host_id": 2, "bk_host_innerip": "127.0.0.2"},
]
CREATE_SHIELD_SUCCESS_SUPPLIER_RETURN = "sa_token"

# test case
CREATE_SHIELD_FAIL_CASE = ComponentTestCase(
    name="create shield fail case",
    inputs={
        "bk_alarm_shield_strategy": "123",
        "bk_alarm_shield_IP": "10.0.1.11",
        "bk_alarm_shield_strategy_begin_time": "2019-11-04 00:00:00",
        "bk_alarm_shield_strategy_end_time": "2019-11-05 00:00:00",
        "bk_alarm_time_type": "0",
        "bk_alarm_shield_duration": "0",
    },
    parent_data={"executor": "executor", "biz_cc_id": 2},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "shield_id": "",
            "message": '调用监控平台(Monitor)接口monitor.create_shield返回失败, params={"begin_time":"2019-11-04 00:00:00",'
            '"bk_biz_id":2,"category":"strategy","cycle_config":{"begin_time":"","end_time":"","day_list":'
            '[],"week_list":[],"type":1},"description":"shield by bk_sops","dimension_config":{"id":"123",'
            '"scope_type":"ip","target":[{"ip":"127.0.0.1","bk_cloud_id":0},{"ip":"127.0.0.2",'
            '"bk_cloud_id":1}]},"end_time":"2019-11-05 00:00:00","notice_config":{},"shield_notice":false,'
            '"source":"bk_sops"}, error=create shield fail',
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_SHIELD_FAIL_CLIENT.monitor.create_shield,
            calls=[
                Call(
                    {
                        "begin_time": "2019-11-04 00:00:00",
                        "bk_biz_id": 2,
                        "category": "strategy",
                        "cycle_config": {"begin_time": "", "end_time": "", "day_list": [], "week_list": [], "type": 1},
                        "description": "shield by bk_sops",
                        "dimension_config": {
                            "id": "123",
                            "scope_type": "ip",
                            "target": [{"ip": "127.0.0.1", "bk_cloud_id": 0}, {"ip": "127.0.0.2", "bk_cloud_id": 1}],
                        },
                        "end_time": "2019-11-05 00:00:00",
                        "notice_config": {},
                        "shield_notice": False,
                        "source": "bk_sops",
                    }
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_SHIELD_FAIL_CLIENT),
        Patcher(target=CMDB_GET_BIZ_HOST, return_value=CREATE_SHIELD_FAIL_GET_BIZ_HOST_RETURN),
        Patcher(target=BIZ_MODEL_SUPPLIER_ACCOUNT_FOR_BIZ, return_value=CREATE_SHIELD_FAIL_SUPPLIER_RETURN),
    ],
)

CREATE_SHIELD_SUCCESS_CASE = ComponentTestCase(
    name="create shield success case",
    inputs={
        "bk_alarm_shield_strategy": "123",
        "bk_alarm_shield_IP": "10.0.1.11",
        "bk_alarm_shield_strategy_begin_time": "2019-11-04 00:00:00",
        "bk_alarm_shield_strategy_end_time": "2019-11-05 00:00:00",
        "bk_alarm_time_type": "0",
        "bk_alarm_shield_duration": "0",
    },
    parent_data={"executor": "executor", "biz_cc_id": 2},
    execute_assertion=ExecuteAssertion(success=True, outputs={"shield_id": "1", "message": "success"}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_SHIELD_SUCCESS_CLIENT.monitor.create_shield,
            calls=[
                Call(
                    {
                        "begin_time": "2019-11-04 00:00:00",
                        "bk_biz_id": 2,
                        "category": "strategy",
                        "cycle_config": {"begin_time": "", "end_time": "", "day_list": [], "week_list": [], "type": 1},
                        "description": "shield by bk_sops",
                        "dimension_config": {
                            "id": "123",
                            "scope_type": "ip",
                            "target": [{"ip": "127.0.0.1", "bk_cloud_id": 0}, {"ip": "127.0.0.2", "bk_cloud_id": 1}],
                        },
                        "end_time": "2019-11-05 00:00:00",
                        "notice_config": {},
                        "shield_notice": False,
                        "source": "bk_sops",
                    }
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_SHIELD_SUCCESS_CLIENT),
        Patcher(target=CMDB_GET_BIZ_HOST, return_value=CREATE_SHIELD_SUCCESS_GET_BIZ_HOST_RETURN),
        Patcher(target=BIZ_MODEL_SUPPLIER_ACCOUNT_FOR_BIZ, return_value=CREATE_SHIELD_SUCCESS_SUPPLIER_RETURN),
    ],
)
