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
    CallAssertion,
    ExecuteAssertion,
    ScheduleAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.job.push_local_files.v2_0 import JobPushLocalFilesComponent


class JobPushLocalFilesComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            FILE_MANAGER_NOT_CONFIG_CASE(),
            FILE_MANAGER_TYPE_ERR_CASE(),
            PUSH_FILE_TO_IPS_FAIL_CASE(),
            SCHEDULE_FAILURE_CASE(),
            SUCCESS_MULTI_CASE(),
        ]

    def component_cls(self):
        return JobPushLocalFilesComponent


# mock path
GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.push_local_files.v2_0.get_client_by_user"
BASE_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_user"
CC_GET_IPS_INFO_BY_STR = (
    "pipeline_plugins.components.collections.sites.open.job.push_local_files.v2_0.cc_get_ips_info_by_str"
)

ENVIRONMENT_VAR_GET = (
    "pipeline_plugins.components.collections.sites.open.job.push_local_files.v2_0."
    "EnvironmentVariables.objects.get_var"
)
FACTORY_GET_MANAGER = (
    "pipeline_plugins.components.collections.sites.open.job.push_local_files.v2_0.ManagerFactory.get_manager"
)
GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.push_local_files.v2_0.get_job_instance_url"
)

JOB_HANDLE_API_ERROR = (
    "pipeline_plugins.components.collections.sites.open.job.push_local_files.v2_0.job_handle_api_error"
)


def FILE_MANAGER_NOT_CONFIG_CASE():
    return ComponentTestCase(
        name="push_local_files v2.0 file manager not config case",
        inputs={
            "biz_cc_id": "biz_cc_id",
            "job_local_files": "job_local_files",
            "job_target_ip_list": "job_target_ip_list",
            "job_target_account": "job_target_account",
            "job_local_files_info": {"job_push_multi_local_files_table": [{""}]},
        },
        parent_data={"executor": "executor", "project_id": "project_id"},
        execute_assertion=ExecuteAssertion(
            success=False, outputs={"ex_data": "File Manager configuration error, contact administrator please."}
        ),
        schedule_assertion=None,
        patchers=[Patcher(target=ENVIRONMENT_VAR_GET, return_value=None)],
    )


def FILE_MANAGER_TYPE_ERR_CASE():
    NOT_EXIST_TYPE = "NOT_EXIST_TYPE"
    MANAGER_GET_EXCEPTION = Exception("exc")

    return ComponentTestCase(
        name="push_local_files v2.0 manager type err case",
        inputs={
            "biz_cc_id": "biz_cc_id",
            "job_local_files": "job_local_files",
            "job_target_ip_list": "job_target_ip_list",
            "job_target_account": "job_target_account",
            "job_local_files_info": {"job_push_multi_local_files_table": [{""}]},
        },
        parent_data={"executor": "executor", "project_id": "project_id"},
        execute_assertion=ExecuteAssertion(
            success=False,
            outputs={
                "ex_data": "can not get file manager for type: {}\n err: {}".format(
                    NOT_EXIST_TYPE, MANAGER_GET_EXCEPTION
                )
            },
        ),
        schedule_assertion=None,
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value=NOT_EXIST_TYPE),
            Patcher(target=FACTORY_GET_MANAGER, side_effect=MANAGER_GET_EXCEPTION),
        ],
    )


def PUSH_FILE_TO_IPS_FAIL_CASE():
    PUSH_FAIL_RESULT = {
        "result": False,
        "message": "msg token",
        "job_api": "api token",
        "response": {"result": False, "message": "msg token"},
        "kwargs": "kwargs token",
    }
    PUSH_FAIL_ESB_CLIENT = MagicMock()
    PUSH_FAIL_MANAGER = MagicMock()
    PUSH_FAIL_MANAGER.push_files_to_ips = MagicMock(return_value=PUSH_FAIL_RESULT)

    return ComponentTestCase(
        name="push_local_files v2.0 manager call fail case",
        inputs={
            "biz_cc_id": "1",
            "job_target_ip_list": "job_target_ip_list",
            "job_target_account": "job_target_account",
            "job_local_files_info": {
                "job_push_multi_local_files_table": [
                    {
                        "file_info": [
                            {
                                "response": {
                                    "result": True,
                                    "tag": {"type": "upload_module", "tags": {"tag_id": "tag_id1"}},
                                }
                            }
                        ],
                        "target_path": "target_path1",
                    }
                ]
            },
        },
        parent_data={"executor": "executor", "project_id": "project_id"},
        execute_assertion=ExecuteAssertion(
            success=False,
            outputs={
                "requests_error": "Request Error:\nfailed\n",
                "job_instance_id_list": [],
                "job_id_of_batch_execute": [],
                "job_inst_url": [],
                "task_count": 1,
                "request_success_count": 0,
                "success_count": 0,
                "ex_data": "Request Error:\nfailed\n",
            },
        ),
        schedule_assertion=None,
        execute_call_assertion=[
            CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call("executor")]),
            CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call("executor", "1", "job_target_ip_list")]),
            CallAssertion(
                func=PUSH_FAIL_MANAGER.push_files_to_ips,
                calls=[
                    Call(
                        esb_client=PUSH_FAIL_ESB_CLIENT,
                        bk_biz_id="1",
                        file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id1"}}],
                        target_path="target_path1",
                        ips=[{"ip": "1.1.1.1", "bk_cloud_id": 0}],
                        account="job_target_account",
                    )
                ],
            ),
        ],
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value="a_type"),
            Patcher(target=FACTORY_GET_MANAGER, return_value=PUSH_FAIL_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=PUSH_FAIL_ESB_CLIENT),
            Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 0}]}),
            Patcher(target=JOB_HANDLE_API_ERROR, return_value="failed"),
        ],
    )


def SCHEDULE_FAILURE_CASE():
    SCHEDULE_FAILURE_RESULT = {"result": True, "data": {"job_id": 12345}}
    SCHEDULE_FAILURE_QUERY_RESULT = {
        "data": [{"status": 4, "step_results": [{"ip_logs": [{"log_content": "log_content_failed"}]}]}],
        "result": False,
    }
    SCHEDULE_FAILURE_ESB_CLIENT = MagicMock()
    SCHEDULE_FAILURE_MANAGER = MagicMock()
    SCHEDULE_FAILURE_MANAGER.push_files_to_ips = MagicMock(return_value=SCHEDULE_FAILURE_RESULT)
    SCHEDULE_FAILURE_ESB_CLIENT.job.get_job_instance_log = MagicMock(return_value=SCHEDULE_FAILURE_QUERY_RESULT)
    return ComponentTestCase(
        name="push_local_files v2 schedule failure case",
        inputs={
            "biz_cc_id": "1",
            "job_target_ip_list": "job_target_ip_list",
            "job_target_account": "job_target_account",
            "job_local_files_info": {
                "job_push_multi_local_files_table": [
                    {
                        "file_info": [
                            {
                                "response": {
                                    "result": True,
                                    "tag": {"type": "upload_module", "tags": {"tag_id": "tag_id1"}},
                                }
                            }
                        ],
                        "target_path": "target_path1",
                    }
                ]
            },
        },
        parent_data={"executor": "executor", "project_id": "project_id"},
        execute_assertion=ExecuteAssertion(
            success=True,
            outputs={
                "requests_error": "",
                "job_instance_id_list": [12345],
                "job_id_of_batch_execute": [12345],
                "job_inst_url": ["url_token"],
                "task_count": 1,
                "request_success_count": 1,
                "success_count": 0,
                "final_res": True,
            },
        ),
        schedule_assertion=ScheduleAssertion(
            success=False,
            outputs={
                "requests_error": "",
                "job_instance_id_list": [12345],
                "job_id_of_batch_execute": [],
                "job_inst_url": ["url_token"],
                "task_count": 1,
                "request_success_count": 1,
                "success_count": 0,
                "final_res": True,
                "ex_data": "任务执行失败，<a href='' target='_blank'>前往作业平台(JOB)查看详情</a>\n",
            },
            schedule_finished=True,
        ),
        execute_call_assertion=[
            CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call("executor")]),
            CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call("executor", "1", "job_target_ip_list")]),
            CallAssertion(
                func=SCHEDULE_FAILURE_MANAGER.push_files_to_ips,
                calls=[
                    Call(
                        esb_client=SCHEDULE_FAILURE_ESB_CLIENT,
                        bk_biz_id="1",
                        file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id1"}}],
                        target_path="target_path1",
                        ips=[{"ip": "1.1.1.1", "bk_cloud_id": 0}],
                        account="job_target_account",
                    )
                ],
            ),
        ],
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value="a_type"),
            Patcher(target=FACTORY_GET_MANAGER, return_value=SCHEDULE_FAILURE_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=SCHEDULE_FAILURE_ESB_CLIENT),
            Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 0}]}),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="url_token"),
        ],
    )


def SUCCESS_MULTI_CASE():
    SUCCESS_RESULT = [
        {"result": True, "data": {"job_id": 123}},
        {"result": True, "data": {"job_id": 456}},
        {"result": True, "data": {"job_id": 789}},
    ]
    SUCCESS_QUERY_RETURN = {
        "data": [{"status": 3, "step_results": [{"ip_logs": [{"log_content": "log_content_success"}]}]}],
        "result": True,
    }

    SUCCESS_ESB_CLIENT = MagicMock()
    SUCCESS_MANAGER = MagicMock()
    SUCCESS_MANAGER.push_files_to_ips = MagicMock(side_effect=SUCCESS_RESULT)
    SUCCESS_ESB_CLIENT.job.get_job_instance_log = MagicMock(side_effect=[SUCCESS_QUERY_RETURN for i in range(3)])
    return ComponentTestCase(
        name="push_local_files multi v2 success case",
        inputs={
            "biz_cc_id": "biz_cc_id",
            "job_target_ip_list": "job_target_ip_list",
            "job_target_account": "job_target_account",
            "job_local_files_info": {
                "job_push_multi_local_files_table": [
                    {
                        "file_info": [
                            {
                                "response": {
                                    "result": True,
                                    "tag": {"type": "upload_module", "tags": {"tag_id": "tag_id1"}},
                                }
                            }
                        ],
                        "target_path": "target_path1",
                    },
                    {
                        "file_info": [
                            {
                                "response": {
                                    "result": True,
                                    "tag": {"type": "upload_module", "tags": {"tag_id": "tag_id2"}},
                                }
                            }
                        ],
                        "target_path": "target_path2",
                    },
                    {
                        "file_info": [
                            {
                                "response": {
                                    "result": True,
                                    "tag": {"type": "upload_module", "tags": {"tag_id": "tag_id3"}},
                                }
                            }
                        ],
                        "target_path": "target_path3",
                    },
                ]
            },
        },
        parent_data={"executor": "executor", "project_id": "project_id"},
        execute_assertion=ExecuteAssertion(
            success=True,
            outputs={
                "requests_error": "",
                "job_instance_id_list": [123, 456, 789],
                "job_id_of_batch_execute": [123, 456, 789],
                "job_inst_url": ["url_token", "url_token", "url_token"],
                "task_count": 3,
                "request_success_count": 3,
                "success_count": 0,
                "final_res": True,
            },
        ),
        schedule_assertion=ScheduleAssertion(
            success=True,
            outputs={
                "requests_error": "",
                "job_instance_id_list": [123, 456, 789],
                "job_id_of_batch_execute": [],
                "job_inst_url": ["url_token", "url_token", "url_token"],
                "task_count": 3,
                "request_success_count": 3,
                "success_count": 3,
                "final_res": True,
            },
            schedule_finished=True,
        ),
        execute_call_assertion=[
            CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call("executor")]),
            CallAssertion(func=CC_GET_IPS_INFO_BY_STR, calls=[Call("executor", "biz_cc_id", "job_target_ip_list")]),
            CallAssertion(
                func=SUCCESS_MANAGER.push_files_to_ips,
                calls=[
                    Call(
                        account="job_target_account",
                        bk_biz_id="biz_cc_id",
                        esb_client=SUCCESS_ESB_CLIENT,
                        file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id1"}}],
                        ips=[{"ip": "1.1.1.1", "bk_cloud_id": 0}],
                        target_path="target_path1",
                    ),
                    Call(
                        account="job_target_account",
                        bk_biz_id="biz_cc_id",
                        esb_client=SUCCESS_ESB_CLIENT,
                        file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id2"}}],
                        ips=[{"ip": "1.1.1.1", "bk_cloud_id": 0}],
                        target_path="target_path2",
                    ),
                    Call(
                        account="job_target_account",
                        bk_biz_id="biz_cc_id",
                        esb_client=SUCCESS_ESB_CLIENT,
                        file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id3"}}],
                        ips=[{"ip": "1.1.1.1", "bk_cloud_id": 0}],
                        target_path="target_path3",
                    ),
                ],
            ),
        ],
        patchers=[
            Patcher(target=ENVIRONMENT_VAR_GET, return_value="a_type"),
            Patcher(target=FACTORY_GET_MANAGER, return_value=SUCCESS_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=SUCCESS_ESB_CLIENT),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=SUCCESS_ESB_CLIENT),
            Patcher(target=CC_GET_IPS_INFO_BY_STR, return_value={"ip_result": [{"InnerIP": "1.1.1.1", "Source": 0}]}),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="url_token"),
        ],
    )
