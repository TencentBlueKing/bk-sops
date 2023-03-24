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
from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
    CallAssertion,
    Call,
    Patcher,
)
from mock import MagicMock

from pipeline_plugins.components.collections.sites.open.monitor.alarm_shield_strategy.v1_2 import (
    MonitorAlarmShieldStrategyComponent,
)


class MonitorAlarmShieldStrategyComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [CREATE_SHIELD_FAIL_CASE, CREATE_SHIELD_SUCCESS_CASE]

    def component_cls(self):
        return MonitorAlarmShieldStrategyComponent


class MockClient(object):
    def __init__(self, search_host=None):
        self.cc = MagicMock()
        self.cc.search_host = MagicMock(return_value=search_host)


class MockMonitorClient(object):
    def __init__(self, add_shield_result=None):
        self.add_shield = MagicMock(return_value=add_shield_result)

    def __call__(self, *args, **kwargs):
        return self


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
    "pipeline_plugins.components.collections.sites.open.monitor.alarm_shield_strategy.v1_2" ".get_client_by_user"
)
MONITOR_CLIENT = (
    "pipeline_plugins.components.collections.sites.open.monitor.alarm_shield_strategy.v1_2" ".BKMonitorClient"
)
CMDB_GET_BIZ_HOST = "gcloud.utils.cmdb.get_business_host"
BIZ_MODEL_SUPPLIER_ACCOUNT_FOR_BIZ = (
    "pipeline_plugins.components.collections.sites.open.monitor.base.Business.objects.supplier_account_for_business"
)

# mock client
CREATE_SHIELD_FAIL_CLIENT = MockMonitorClient(add_shield_result={"result": False, "message": "create shield fail"})
CREATE_SHIELD_FAIL_GET_BIZ_HOST_RETURN = [
    {"bk_cloud_id": 0, "bk_host_id": 1, "bk_host_innerip": "127.0.0.1"},
    {"bk_cloud_id": 1, "bk_host_id": 2, "bk_host_innerip": "127.0.0.2"},
]

CREATE_SHIELD_FAIL_SUPPLIER_RETURN = "sa_token"

CREATE_SHIELD_SUCCESS_CLIENT = MockMonitorClient(
    add_shield_result={"result": True, "data": {"id": "1"}, "message": "success"}
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
        "bk_alarm_shield_IP": "127.0.0.1",
        "bk_alarm_shield_begin_time": "2019-11-04 00:00:00",
        "bk_alarm_shield_end_time": "2019-11-05 00:00:00",
        "bk_alarm_time_type": "0",
        "bk_alarm_shield_duration": "0",
        "bk_dimension_select_type": "and",
        "bk_dimension_list": [{"dimension_name": "bk_biz_id", "dimension_value": "1,2"}],
    },
    parent_data={"executor": "executor", "biz_cc_id": 2},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "shield_id": "",
            "message": "调用监控平台(Monitor)接口monitor.create_shield返回失败, error=create shield fail, "
            'params={"begin_time":"2019-11-04 00:00:00",'
            '"bk_biz_id":2,"category":"strategy","cycle_config":{"begin_time":"","end_time":"","day_list":'
            '[],"week_list":[],"type":1},"description":"shield by bk_sops","dimension_config":{"id":"123",'
            '"dimension_conditions":[{"condition":"and","key":"bk_biz_id","method":"eq","value":["1","2"],'
            '"name":"bk_biz_id"}],'  # noqa
            '"scope_type":"ip","target":[{"ip":"127.0.0.1","bk_cloud_id":0},{"ip":"127.0.0.2",'
            '"bk_cloud_id":1}]},"end_time":"2019-11-05 00:00:00","notice_config":{},"shield_notice":false}',
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_SHIELD_FAIL_CLIENT.add_shield,
            calls=[
                Call(
                    **{
                        "begin_time": "2019-11-04 00:00:00",
                        "bk_biz_id": 2,
                        "category": "strategy",
                        "cycle_config": {"begin_time": "", "end_time": "", "day_list": [], "week_list": [], "type": 1},
                        "description": "shield by bk_sops",
                        "dimension_config": {
                            "id": "123",
                            "scope_type": "ip",
                            "dimension_conditions": [
                                {
                                    "condition": "and",
                                    "key": "bk_biz_id",
                                    "method": "eq",
                                    "value": ["1", "2"],
                                    "name": "bk_biz_id",
                                }
                            ],
                            "target": [{"ip": "127.0.0.1", "bk_cloud_id": 0}, {"ip": "127.0.0.2", "bk_cloud_id": 1}],
                        },
                        "end_time": "2019-11-05 00:00:00",
                        "notice_config": {},
                        "shield_notice": False,
                    }
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=MONITOR_CLIENT, return_value=CREATE_SHIELD_FAIL_CLIENT),
        Patcher(target=CMDB_GET_BIZ_HOST, return_value=CREATE_SHIELD_FAIL_GET_BIZ_HOST_RETURN),
        Patcher(target=BIZ_MODEL_SUPPLIER_ACCOUNT_FOR_BIZ, return_value=CREATE_SHIELD_FAIL_SUPPLIER_RETURN),
    ],
)

CREATE_SHIELD_SUCCESS_CASE = ComponentTestCase(
    name="create shield success case",
    inputs={
        "bk_alarm_shield_strategy": "123",
        "bk_alarm_shield_IP": "127.0.0.1",
        "bk_alarm_shield_begin_time": "2019-11-04 00:00:00",
        "bk_alarm_shield_end_time": "2019-11-05 00:00:00",
        "bk_alarm_time_type": "0",
        "bk_alarm_shield_duration": "0",
        "bk_dimension_select_type": "and",
        "bk_dimension_list": [{"dimension_name": "bk_biz_id", "dimension_value": "1,2"}],
    },
    parent_data={"executor": "executor", "biz_cc_id": 2},
    execute_assertion=ExecuteAssertion(success=True, outputs={"shield_id": "1", "message": "success"}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_SHIELD_SUCCESS_CLIENT.add_shield,
            calls=[
                Call(
                    **{
                        "begin_time": "2019-11-04 00:00:00",
                        "bk_biz_id": 2,
                        "category": "strategy",
                        "cycle_config": {"begin_time": "", "end_time": "", "day_list": [], "week_list": [], "type": 1},
                        "description": "shield by bk_sops",
                        "dimension_config": {
                            "id": "123",
                            "scope_type": "ip",
                            "dimension_conditions": [
                                {
                                    "condition": "and",
                                    "key": "bk_biz_id",
                                    "method": "eq",
                                    "value": ["1", "2"],
                                    "name": "bk_biz_id",
                                }
                            ],
                            "target": [{"ip": "127.0.0.1", "bk_cloud_id": 0}, {"ip": "127.0.0.2", "bk_cloud_id": 1}],
                        },
                        "end_time": "2019-11-05 00:00:00",
                        "notice_config": {},
                        "shield_notice": False,
                    }
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=MONITOR_CLIENT, return_value=CREATE_SHIELD_SUCCESS_CLIENT),
        Patcher(target=CMDB_GET_BIZ_HOST, return_value=CREATE_SHIELD_SUCCESS_GET_BIZ_HOST_RETURN),
        Patcher(target=BIZ_MODEL_SUPPLIER_ACCOUNT_FOR_BIZ, return_value=CREATE_SHIELD_SUCCESS_SUPPLIER_RETURN),
    ],
)
