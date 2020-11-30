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
from mock import MagicMock, patch

from pipeline_plugins.variables.collections.sites.open.gse_kit.var_gse_kit_ip_selector import GseKitSetModuleIpSelector

IP_SELECTOR_SUC_VALUE = {
    "var_set_env": "3",
    "var_set_name": "set1",
    "var_module_name": "module1",
    "var_service_instance_name": "ser_id1",
    "var_process_name": "proc_name1",
    "var_process_instance_id": "proc_id1"
}

PROC_STATUS_SUCCESS_RETURN = [
    {
        "id": 11,
        "bk_biz_id": 2,
        "expression": "广东一区.game.127.0.0.1_gse_agent.gse_agent.99",
        "bk_host_innerip": "127.0.0.1",
        "bk_cloud_id": 0,
        "bk_set_env": None,
        "bk_set_id": 1,
        "bk_module_id": 11,
        "service_template_id": 111,
        "service_instance_id": 11,
        "bk_func_id": "1",
        "bk_process_id": 99,
        "process_template_id": 111,
        "process_status": 1,
        "is_auto": False,
        "bk_set_name": "广东一区",
        "bk_module_name": "game",
        "bk_service_name": "gse_agent.10.0.5.225_gse_agent",
        "bk_process_name": "gse_agent",
        "bk_cloud_name": "default area",
        "config_templates": [
            {
                "config_template_id": 1,
                "template_name": "模板1",
                "file_name": "config_tmplate1"
            }
        ]
    },
    {
        "id": 11,
        "bk_biz_id": 2,
        "expression": "广东一区.game.127.0.0.1_gse_agent.gse_agent.99",
        "bk_host_innerip": "172.0.0.1",
        "bk_cloud_id": 0,
        "bk_set_env": None,
        "bk_set_id": 1,
        "bk_module_id": 11,
        "service_template_id": 111,
        "service_instance_id": 11,
        "bk_func_id": "1",
        "bk_process_id": 99,
        "process_template_id": 111,
        "process_status": 1,
        "is_auto": False,
        "bk_set_name": "广东一区",
        "bk_module_name": "game",
        "bk_service_name": "gse_agent.10.0.5.225_gse_agent",
        "bk_process_name": "gse_agent",
        "bk_cloud_name": "default area",
        "config_templates": [
            {
                "config_template_id": 1,
                "template_name": "模板1",
                "file_name": "config_tmplate1"
            }
        ]
    }
]
PROC_STATUS_ERROR_RETURN = []

SUCCESS_RESULT = "127.0.0.1,172.0.0.1"
ERROR_RESULT = ""
BATCH_REQUEST = "pipeline_plugins.variables.collections.sites.open.gse_kit.var_gse_kit_ip_selector.batch_request"


class VarGseKitIpSelector(TestCase):
    def setUp(self):
        self.pipeline_data = {"executor": "admin", "biz_cc_id": 123, "project_id": 1}

        mock_client = MagicMock()
        mock_client.gse_kit.list_process = "list_process"
        self.get_client_by_user_patcher = patch(
            "pipeline_plugins.variables.collections.sites.open.gse_kit.var_gse_kit_ip_selector.BKGseKitClient",
            MagicMock(return_value=mock_client)
        )

        self.get_client_by_user_patcher.start()

    def tearDown(self):
        self.get_client_by_user_patcher.stop()

    @patch(BATCH_REQUEST, MagicMock(return_value=PROC_STATUS_SUCCESS_RETURN))
    def test_ip_selector_success_case(self):
        ip_selector = GseKitSetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value=IP_SELECTOR_SUC_VALUE,
            name="test_ip_selector_success_case",
            context={},
        )
        self.assertEqual(SUCCESS_RESULT, ip_selector.get_value())

    @patch(BATCH_REQUEST, MagicMock(return_value=PROC_STATUS_ERROR_RETURN))
    def test_ip_fail_case(self):
        ip_selector = GseKitSetModuleIpSelector(
            pipeline_data=self.pipeline_data,
            value=IP_SELECTOR_SUC_VALUE,
            name="test_ip_selector_failed_case",
            context={},
        )
        self.assertEqual(ERROR_RESULT, ip_selector.get_value())
