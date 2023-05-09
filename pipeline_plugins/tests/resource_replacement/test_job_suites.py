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

from copy import deepcopy

from django.test import TestCase

from pipeline_plugins.resource_replacement import base, suites

from . import base as local_base


class JobLocalContentUploadSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "job_local_content_upload",
        "data": {
            "local_name": {"hook": False, "need_render": True, "value": ".conf"},
            "local_content": {"hook": False, "need_render": True, "value": "111"},
            "job_ip_list": {"hook": False, "need_render": True, "value": "1:127.0.0.1\n127.0.0.1"},
            "file_account": {"hook": False, "need_render": True, "value": "administrator"},
            "file_path": {"hook": False, "need_render": True, "value": "/tmp/"},
            "job_rolling_config": {
                "hook": False,
                "need_render": True,
                "value": {"job_rolling_execute": [], "job_rolling_expression": "", "job_rolling_mode": 1},
            },
        },
        "version": "v1.1",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.JobLocalContentUploadSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            "127.0.0.1\n10001:127.0.0.1",
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["job_ip_list"]["value"],
        )


class JobPushLocalFilesSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "job_push_local_files",
        "data": {
            "biz_cc_id": {"hook": False, "need_render": True, "value": 2},
            "job_local_files_info": {
                "hook": False,
                "need_render": True,
                "value": {
                    "job_local_files": [],
                    "job_target_path": "/tmp/",
                    "add_files": "",
                    "job_push_multi_local_files_table": [
                        {
                            "show_file": "xxx.png",
                            "file_info": [
                                {
                                    "status": "success",
                                    "name": "xxx.png",
                                    "size": 286460,
                                    "percentage": 100,
                                    "uid": 1681437569692,
                                    "raw": {"uid": 1681437569692},
                                    "response": {
                                        "result": True,
                                        "tag": {
                                            "type": "job_repo",
                                            "tags": {"file_path": "xxx.png", "name": "xxx.png"},
                                        },
                                        "md5": "59565321355a381aab43dbcd975445e3",
                                    },
                                }
                            ],
                            "target_path": "/tmp/",
                            "md5": "59565321355a381aab43dbcd975445e3",
                        }
                    ],
                },
            },
            "job_across_biz": {"hook": False, "need_render": True, "value": False},
            "job_target_ip_list": {"hook": True, "need_render": True, "value": "2:127.0.0.1"},
            "job_target_account": {"hook": False, "need_render": True, "value": "root"},
            "job_timeout": {"hook": False, "need_render": True, "value": ""},
        },
        "version": "2.0",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.JobPushLocalFilesSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            1002,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["biz_cc_id"]["value"],
        )
        self.assertEqual(
            "10002:127.0.0.1",
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["job_target_ip_list"][
                "value"
            ],
        )


class JobFastPushFileSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "job_fast_push_file",
        "data": {
            "biz_cc_id": {"hook": False, "need_render": True, "value": 2},
            "job_source_files": {
                "hook": False,
                "need_render": True,
                "value": [
                    {"ip": "127.0.0.1", "files": "/tmp/tmp.conf", "account": "root"},
                    {"ip": "1:127.0.0.1", "files": "/tmp/tmp.conf", "account": "root"},
                ],
            },
            "job_ip_list": {"hook": False, "need_render": True, "value": "127.0.0.1\n127.0.0.2"},
            "job_account": {"hook": False, "need_render": True, "value": "root"},
            "job_target_path": {"hook": False, "need_render": True, "value": "/tmp/tmp.conf"},
            "job_timeout": {"hook": False, "need_render": True, "value": ""},
            # v2
            "job_dispatch_attr": {
                "hook": False,
                "need_render": True,
                "value": [
                    {"job_ip_list": "1:127.0.0.1\n2:127.0.0.1", "job_target_path": "/tmp/", "job_account": "root"}
                ],
            },
        },
        "version": "legacy",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.JobFastPushFileSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            1002,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["biz_cc_id"]["value"],
        )
        self.assertEqual(
            [
                {"ip": "127.0.0.1", "files": "/tmp/tmp.conf", "account": "root"},
                {"ip": "10001:127.0.0.1", "files": "/tmp/tmp.conf", "account": "root"},
            ],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["job_source_files"]["value"],
        )
        self.assertEqual(
            [{"job_ip_list": "10001:127.0.0.1\n10002:127.0.0.1", "job_target_path": "/tmp/", "job_account": "root"}],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["job_dispatch_attr"][
                "value"
            ],
        )


class JobCronTaskSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "job_cron_task",
        "data": {
            "biz_cc_id": {"hook": False, "need_render": True, "value": 2},
            "job_cron_job_id": {"hook": False, "need_render": True, "value": 35},
            "job_cron_name": {"hook": False, "need_render": True, "value": "sops_task"},
            "job_cron_expression": {"hook": False, "need_render": True, "value": "1111"},
            "job_cron_status": {"hook": False, "need_render": True, "value": 2},
        },
        "version": "legacy",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.JobCronTaskSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            1002,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["biz_cc_id"]["value"],
        )
        self.assertEqual(
            100035,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["job_cron_job_id"]["value"],
        )


class JobExecuteTaskSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "job_execute_task",
        "data": {
            "biz_cc_id": {"hook": False, "need_render": True, "value": 2},
            "job_task_id": {"hook": False, "need_render": True, "value": 35},
            "button_refresh": {"hook": False, "need_render": True, "value": ""},
            "job_global_var": {
                "hook": False,
                "need_render": True,
                "value": [
                    {"id": 51, "category": 3, "name": "ip_list", "value": '"30308"', "description": ""},
                    {"id": 52, "category": 3, "name": "ip_list", "value": "2:127.0.0.1", "description": ""},
                ],
            },
            "job_success_id": {"hook": False, "need_render": True, "value": ""},
            "button_refresh_2": {"hook": False, "need_render": True, "value": ""},
        },
        "version": "1.2",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.JobExecuteTaskSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            1002,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["biz_cc_id"]["value"],
        )
        self.assertEqual(
            100035,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["job_task_id"]["value"],
        )
        self.assertEqual(
            [
                {"id": 100051, "category": 3, "name": "ip_list", "value": '"30308"', "description": ""},
                {"id": 100052, "category": 3, "name": "ip_list", "value": "10002:127.0.0.1", "description": ""},
            ],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["job_global_var"]["value"],
        )


class JobAllBizJobFastPushFileSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "all_biz_job_fast_push_file",
        "data": {
            "all_biz_cc_id": {"hook": False, "need_render": True, "value": 9991001},
            "job_source_files": {
                "hook": False,
                "need_render": True,
                "value": [
                    {"bk_cloud_id": "0", "ip": "127.0.0.1", "files": "/tmp/tmp.conf", "account": "root"},
                    {"bk_cloud_id": "2", "ip": "127.0.0.1", "files": "/tmp/tmp.conf", "account": "root"},
                ],
            },
            "upload_speed_limit": {"hook": False, "need_render": True, "value": ""},
            "download_speed_limit": {"hook": False, "need_render": True, "value": ""},
            "job_dispatch_attr": {
                "hook": False,
                "need_render": True,
                "value": [
                    {
                        "bk_cloud_id": "0",
                        "job_ip_list": "127.0.0.1",
                        "job_target_path": "/tmp/",
                        "job_target_account": "root",
                    },
                    {
                        "bk_cloud_id": "1",
                        "job_ip_list": "127.0.0.1",
                        "job_target_path": "/tmp/",
                        "job_target_account": "root",
                    },
                ],
            },
            "job_timeout": {"hook": False, "need_render": True, "value": ""},
            "job_rolling_config": {
                "hook": False,
                "need_render": True,
                "value": {"job_rolling_execute": [], "job_rolling_expression": "", "job_rolling_mode": 1},
            },
        },
        "version": "v1.1",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.JobAllBizJobFastPushFileSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            [
                {"bk_cloud_id": "0", "ip": "127.0.0.1", "files": "/tmp/tmp.conf", "account": "root"},
                {"bk_cloud_id": "10002", "ip": "127.0.0.1", "files": "/tmp/tmp.conf", "account": "root"},
            ],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["job_source_files"]["value"],
        )
        self.assertEqual(
            [
                {
                    "bk_cloud_id": "0",
                    "job_ip_list": "127.0.0.1",
                    "job_target_path": "/tmp/",
                    "job_target_account": "root",
                },
                {
                    "bk_cloud_id": "10001",
                    "job_ip_list": "127.0.0.1",
                    "job_target_path": "/tmp/",
                    "job_target_account": "root",
                },
            ],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["job_dispatch_attr"][
                "value"
            ],
        )


class JobAllBizJobFastExecuteScriptSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "all_biz_job_fast_execute_script",
        "data": {
            "all_biz_cc_id": {"hook": False, "need_render": True, "value": 9991001},
            "job_script_type": {"hook": False, "need_render": True, "value": "1"},
            "job_content": {"hook": False, "need_render": True, "value": "ls -al\n"},
            "job_script_param": {"hook": False, "need_render": True, "value": ""},
            "job_script_timeout": {"hook": False, "need_render": True, "value": ""},
            "job_target_account": {"hook": False, "need_render": True, "value": "root"},
            "job_target_ip_table": {
                "hook": False,
                "need_render": True,
                "value": [
                    {"bk_cloud_id": "0", "ip": "127.0.0.1\n127.0.0.2"},
                    {"bk_cloud_id": "999", "ip": "127.0.0.1\n127.0.0.2"},
                ],
            },
            "job_rolling_config": {
                "hook": False,
                "need_render": True,
                "value": {"job_rolling_execute": [], "job_rolling_expression": "", "job_rolling_mode": 1},
            },
        },
        "version": "v1.1",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.JobAllBizJobFastExecuteScriptSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            [
                {"bk_cloud_id": "0", "ip": "127.0.0.1\n127.0.0.2"},
                {"bk_cloud_id": "10999", "ip": "127.0.0.1\n127.0.0.2"},
            ],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["job_target_ip_table"][
                "value"
            ],
        )


class JobAllBizJobExecuteJobPlanSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "all_biz_execute_job_plan",
        "data": {
            "all_biz_job_config": {
                "hook": False,
                "need_render": True,
                "value": {
                    "all_biz_cc_id": 9991001,
                    "pull_job_template_list": "",
                    "job_template_id": 41,
                    "job_plan_id": 46,
                    "job_global_var": [
                        {"id": 62, "type": 2, "name": "ipv6", "description": ""},
                        {"id": 63, "type": 3, "name": "iplist", "value": "587,612,613", "description": ""},
                    ],
                },
            }
        },
        "version": "v1.1",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.JobAllBizJobExecuteJobPlanSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            {
                "all_biz_cc_id": 9991001,
                "pull_job_template_list": "",
                "job_template_id": 100041,
                "job_plan_id": 100046,
                "job_global_var": [
                    {"id": 100062, "type": 2, "name": "ipv6", "description": ""},
                    {"id": 100063, "type": 3, "name": "iplist", "value": "587,612,613", "description": ""},
                ],
            },
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["all_biz_job_config"][
                "value"
            ],
        )
