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
from django.conf import settings
from django.test import TestCase
from mock import MagicMock
from pipeline.component_framework.test import (
    Call,
    CallAssertion,
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)

from pipeline_plugins.components.collections.sites.open.job.push_local_files.v2_0 import JobPushLocalFilesComponent
from pipeline_plugins.tests.components.collections.sites.open.utils.cc_ipv6_mock_utils import (
    create_mock_cmdb_client_with_hosts,
)


class JobPushLocalFilesComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            FILE_MANAGER_NOT_CONFIG_CASE(),
            FILE_MANAGER_TYPE_ERR_CASE(),
            PUSH_FILE_TO_IPS_FAIL_CASE(),
            SCHEDULE_FAILURE_CASE(),
            SUCCESS_MULTI_CASE(),
            SUCCESS_MULTI_CASE_WITH_TIMEOUT(),
        ]

    def component_cls(self):
        return JobPushLocalFilesComponent


# mock path
GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.open.job.push_local_files.base_service.get_client_by_username"
)
GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"

BASE_GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username"

# 添加 CC client mock 路径，用于 IPv6 支持
CC_GET_CLIENT_BY_USERNAME = "pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"
BATCH_REQUEST = "api.utils.request.batch_request"
CC_GET_IPS_INFO_BY_STR_PATCH = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str"


CC_GET_IPS_INFO_BY_STR = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str"
CMDB_GET_CLIENT_BY_USERNAME = "gcloud.utils.cmdb.get_client_by_username"

ENVIRONMENT_VAR_GET = (
    "pipeline_plugins.components.collections.sites.open.job.push_local_files.base_service."
    "EnvironmentVariables.objects.get_var"
)
FACTORY_GET_MANAGER = (
    "pipeline_plugins.components.collections.sites.open.job.push_local_files.base_service.ManagerFactory.get_manager"
)
GET_JOB_INSTANCE_URL = (
    "pipeline_plugins.components.collections.sites.open.job.push_local_files.base_service.get_job_instance_url"
)

JOB_HANDLE_API_ERROR = (
    "pipeline_plugins.components.collections.sites.open.job.push_local_files.base_service.job_handle_api_error"
)


# 辅助函数：根据当前环境返回对应的 target_server 格式
def is_ipv6_enabled():
    """检查是否启用 IPv6 模式"""
    return getattr(settings, "ENABLE_IPV6", False)


def get_expected_target_server_for_push_files(host_id):
    """获取期望的 target_server 格式"""
    if is_ipv6_enabled():
        return {"host_id_list": [host_id]}
    else:
        return {"ip_list": [{"ip": "1.1.1.1", "bk_cloud_id": 0}]}


def get_expected_call_assertions_for_push_files(
    manager_mock, esb_client_mock, file_tags_list, target_paths, timeout=None
):
    """
    生成环境感知的 CallAssertion
    Args:
        manager_mock: 管理器 mock 对象
        esb_client_mock: ESB 客户端 mock 对象
        file_tags_list: 文件标签列表
        target_paths: 目标路径列表
        timeout: 超时时间（可选）
    """
    target_server = get_expected_target_server_for_push_files(1)
    calls = []
    for file_tags, target_path in zip(file_tags_list, target_paths):
        call_kwargs = {
            "account": "job_target_account",
            "bk_biz_id": "biz_cc_id",
            "esb_client": esb_client_mock,
            "file_tags": file_tags,
            "ips": None,
            "target_path": target_path,
            "target_server": target_server,
            "headers": {"X-Bk-Tenant-Id": "system"},
        }
        if timeout is not None:
            call_kwargs["timeout"] = timeout
        calls.append(Call(**call_kwargs))

    return [
        CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call("executor", stage="dev")]),
        CallAssertion(func=manager_mock.push_files_to_ips, calls=calls),
    ]


def mock_cc_get_ips_info_by_str_with_host_id(host_id):
    """
    Mock cc_get_ips_info_by_str to return a specific host_id
    """

    def _mock(*args, **kwargs):
        return {
            "result": True,
            "ip_result": [
                {
                    "bk_host_id": host_id,
                    "bk_host_innerip": "1.1.1.1",
                    "bk_cloud_id": 0,
                    "InnerIP": "1.1.1.1",
                    "Source": 0,
                }
            ],
            "ip_count": 1,
        }

    return _mock


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
        parent_data={"executor": "executor", "project_id": "project_id", "tenant_id": "system"},
        execute_assertion=ExecuteAssertion(
            success=False, outputs={"ex_data": "File Manager configuration error, contact administrator please."}
        ),
        schedule_assertion=None,
        patchers=[
            Patcher(target=CC_GET_CLIENT_BY_USERNAME, return_value=create_mock_cmdb_client_with_hosts([])),
            Patcher(target=CMDB_GET_CLIENT_BY_USERNAME, return_value=create_mock_cmdb_client_with_hosts([])),
            Patcher(target=ENVIRONMENT_VAR_GET, return_value=None),
        ],
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
        parent_data={"executor": "executor", "project_id": "project_id", "tenant_id": "system"},
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

    # Mock CMDB client with proper api.list_biz_hosts
    PUSH_FAIL_CMDB_CLIENT = MagicMock()
    PUSH_FAIL_CMDB_CLIENT.api.list_biz_hosts = MagicMock(
        return_value={
            "result": True,
            "data": {
                "count": 1,
                "info": [
                    {
                        "bk_host_id": 1,
                        "bk_host_innerip": "1.1.1.1",
                        "bk_cloud_id": 0,
                        "bk_host_innerip_v6": "",
                        "bk_agent_id": "agent1",
                    }
                ],
            },
        }
    )

    return ComponentTestCase(
        name="push_local_files v2.0 manager call fail case",
        inputs={
            "biz_cc_id": "1",
            "job_target_ip_list": "1.1.1.1",
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
        parent_data={"executor": "executor", "project_id": "project_id", "tenant_id": "system"},
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
            CallAssertion(
                func=PUSH_FAIL_MANAGER.push_files_to_ips,
                calls=[
                    Call(
                        esb_client=PUSH_FAIL_ESB_CLIENT,
                        bk_biz_id="1",
                        file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id1"}}],
                        target_path="target_path1",
                        ips=None,
                        account="job_target_account",
                        target_server=get_expected_target_server_for_push_files(1),
                        headers={"X-Bk-Tenant-Id": "system"},
                    )
                ],
            )
        ],
        patchers=[
            Patcher(
                target=CC_GET_CLIENT_BY_USERNAME,
                return_value=create_mock_cmdb_client_with_hosts(
                    [
                        {
                            "bk_host_id": 1,
                            "bk_host_innerip": "1.1.1.1",
                            "bk_cloud_id": 0,
                            "bk_host_innerip_v6": "",
                            "bk_agent_id": "agent1",
                        }
                    ]
                ),
            ),
            Patcher(
                target=CMDB_GET_CLIENT_BY_USERNAME,
                return_value=create_mock_cmdb_client_with_hosts(
                    [
                        {
                            "bk_host_id": 1,
                            "bk_host_innerip": "1.1.1.1",
                            "bk_cloud_id": 0,
                            "bk_host_innerip_v6": "",
                            "bk_agent_id": "agent1",
                        }
                    ]
                ),
            ),
            Patcher(target=CC_GET_IPS_INFO_BY_STR_PATCH, side_effect=mock_cc_get_ips_info_by_str_with_host_id(1)),
            Patcher(target=ENVIRONMENT_VAR_GET, return_value="a_type"),
            Patcher(target=FACTORY_GET_MANAGER, return_value=PUSH_FAIL_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=PUSH_FAIL_ESB_CLIENT),
            Patcher(target=JOB_HANDLE_API_ERROR, return_value="failed"),
        ],
    )


def SCHEDULE_FAILURE_CASE():
    SCHEDULE_FAILURE_RESULT = {"result": True, "data": {"job_id": 12345}}
    SCHEDULE_FAILURE_QUERY_RESULT = {
        "data": {"finished": True, "job_instance": {"status": 4}},
        "result": False,
    }
    SCHEDULE_FAILURE_ESB_CLIENT = MagicMock()
    SCHEDULE_FAILURE_MANAGER = MagicMock()
    SCHEDULE_FAILURE_MANAGER.push_files_to_ips = MagicMock(return_value=SCHEDULE_FAILURE_RESULT)
    SCHEDULE_FAILURE_ESB_CLIENT.api.get_job_instance_status = MagicMock(return_value=SCHEDULE_FAILURE_QUERY_RESULT)

    # Mock CMDB client with proper api.list_biz_hosts
    SCHEDULE_FAILURE_CMDB_CLIENT = MagicMock()
    SCHEDULE_FAILURE_CMDB_CLIENT.api.list_biz_hosts = MagicMock(
        return_value={
            "result": True,
            "data": {
                "count": 1,
                "info": [
                    {
                        "bk_host_id": 1,
                        "bk_host_innerip": "1.1.1.1",
                        "bk_cloud_id": 0,
                        "bk_host_innerip_v6": "",
                        "bk_agent_id": "agent1",
                    }
                ],
            },
        }
    )

    # 生成环境感知的 call assertion
    target_server = get_expected_target_server_for_push_files(1)
    execute_call_assertion = [
        CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call("executor", stage="dev")]),
        CallAssertion(
            func=SCHEDULE_FAILURE_MANAGER.push_files_to_ips,
            calls=[
                Call(
                    esb_client=SCHEDULE_FAILURE_ESB_CLIENT,
                    bk_biz_id="1",
                    file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id1"}}],
                    target_path="target_path1",
                    ips=None,
                    account="job_target_account",
                    target_server=target_server,
                    headers={"X-Bk-Tenant-Id": "system"},
                )
            ],
        ),
    ]

    return ComponentTestCase(
        name="push_local_files v2 schedule failure case",
        inputs={
            "biz_cc_id": "1",
            "job_target_ip_list": "1.1.1.1",
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
        parent_data={"executor": "executor", "project_id": "project_id", "tenant_id": "system"},
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
        execute_call_assertion=execute_call_assertion,
        patchers=[
            Patcher(
                target=CC_GET_CLIENT_BY_USERNAME,
                return_value=create_mock_cmdb_client_with_hosts(
                    [
                        {
                            "bk_host_id": 1,
                            "bk_host_innerip": "1.1.1.1",
                            "bk_cloud_id": 0,
                            "bk_host_innerip_v6": "",
                            "bk_agent_id": "agent1",
                        }
                    ]
                ),
            ),
            Patcher(
                target=CMDB_GET_CLIENT_BY_USERNAME,
                return_value=create_mock_cmdb_client_with_hosts(
                    [
                        {
                            "bk_host_id": 1,
                            "bk_host_innerip": "1.1.1.1",
                            "bk_cloud_id": 0,
                            "bk_host_innerip_v6": "",
                            "bk_agent_id": "agent1",
                        }
                    ]
                ),
            ),
            Patcher(target=CC_GET_IPS_INFO_BY_STR_PATCH, side_effect=mock_cc_get_ips_info_by_str_with_host_id(1)),
            Patcher(target=ENVIRONMENT_VAR_GET, return_value="a_type"),
            Patcher(target=FACTORY_GET_MANAGER, return_value=SCHEDULE_FAILURE_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=SCHEDULE_FAILURE_ESB_CLIENT),
            Patcher(target=GET_CLIENT_BY_USERNAME, return_value=SCHEDULE_FAILURE_ESB_CLIENT),
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
        "data": {"finished": True, "job_instance": {"status": 3}},
        "result": True,
    }

    SUCCESS_ESB_CLIENT = MagicMock()
    SUCCESS_MANAGER = MagicMock()
    SUCCESS_MANAGER.push_files_to_ips = MagicMock(side_effect=SUCCESS_RESULT)
    SUCCESS_ESB_CLIENT.api.get_job_instance_status = MagicMock(side_effect=[SUCCESS_QUERY_RETURN for i in range(3)])

    # Mock CMDB client with proper api.list_biz_hosts
    SUCCESS_CMDB_CLIENT = MagicMock()
    SUCCESS_CMDB_CLIENT.api.list_biz_hosts = MagicMock(
        return_value={
            "result": True,
            "data": {
                "count": 1,
                "info": [
                    {
                        "bk_host_id": 1,
                        "bk_host_innerip": "1.1.1.1",
                        "bk_cloud_id": 0,
                        "bk_host_innerip_v6": "",
                        "bk_agent_id": "agent1",
                    }
                ],
            },
        }
    )

    # 生成环境感知的 call assertion
    target_server = get_expected_target_server_for_push_files(1)
    execute_call_assertion = [
        CallAssertion(func=GET_CLIENT_BY_USER, calls=[Call("executor", stage="dev")]),
        CallAssertion(
            func=SUCCESS_MANAGER.push_files_to_ips,
            calls=[
                Call(
                    account="job_target_account",
                    bk_biz_id="biz_cc_id",
                    esb_client=SUCCESS_ESB_CLIENT,
                    file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id1"}}],
                    ips=None,
                    target_path="target_path1",
                    target_server=target_server,
                    headers={"X-Bk-Tenant-Id": "system"},
                ),
                Call(
                    account="job_target_account",
                    bk_biz_id="biz_cc_id",
                    esb_client=SUCCESS_ESB_CLIENT,
                    file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id2"}}],
                    ips=None,
                    target_path="target_path2",
                    target_server=target_server,
                    headers={"X-Bk-Tenant-Id": "system"},
                ),
                Call(
                    account="job_target_account",
                    bk_biz_id="biz_cc_id",
                    esb_client=SUCCESS_ESB_CLIENT,
                    file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id3"}}],
                    ips=None,
                    target_path="target_path3",
                    target_server=target_server,
                    headers={"X-Bk-Tenant-Id": "system"},
                ),
            ],
        ),
    ]

    return ComponentTestCase(
        name="push_local_files multi v2 success case",
        inputs={
            "biz_cc_id": "biz_cc_id",
            "job_target_ip_list": "1.1.1.1",
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
        parent_data={"executor": "executor", "project_id": "project_id", "tenant_id": "system"},
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
        execute_call_assertion=execute_call_assertion,
        patchers=[
            Patcher(
                target=CC_GET_CLIENT_BY_USERNAME,
                return_value=create_mock_cmdb_client_with_hosts(
                    [
                        {
                            "bk_host_id": 1,
                            "bk_host_innerip": "1.1.1.1",
                            "bk_cloud_id": 0,
                            "bk_host_innerip_v6": "",
                            "bk_agent_id": "agent1",
                        }
                    ]
                ),
            ),
            Patcher(
                target=CMDB_GET_CLIENT_BY_USERNAME,
                return_value=create_mock_cmdb_client_with_hosts(
                    [
                        {
                            "bk_host_id": 1,
                            "bk_host_innerip": "1.1.1.1",
                            "bk_cloud_id": 0,
                            "bk_host_innerip_v6": "",
                            "bk_agent_id": "agent1",
                        }
                    ]
                ),
            ),
            Patcher(target=CC_GET_IPS_INFO_BY_STR_PATCH, side_effect=mock_cc_get_ips_info_by_str_with_host_id(1)),
            Patcher(target=ENVIRONMENT_VAR_GET, return_value="a_type"),
            Patcher(target=FACTORY_GET_MANAGER, return_value=SUCCESS_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=SUCCESS_ESB_CLIENT),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=SUCCESS_ESB_CLIENT),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="url_token"),
        ],
    )


def SUCCESS_MULTI_CASE_WITH_TIMEOUT():
    SUCCESS_RESULT = [
        {"result": True, "data": {"job_id": 123}},
        {"result": True, "data": {"job_id": 456}},
        {"result": True, "data": {"job_id": 789}},
    ]
    SUCCESS_QUERY_RETURN = {
        "data": {"finished": True, "job_instance": {"status": 3}},
        "result": True,
    }

    SUCCESS_ESB_CLIENT = MagicMock()
    SUCCESS_MANAGER = MagicMock()
    SUCCESS_MANAGER.push_files_to_ips = MagicMock(side_effect=SUCCESS_RESULT)
    SUCCESS_ESB_CLIENT.api.get_job_instance_status = MagicMock(side_effect=[SUCCESS_QUERY_RETURN for i in range(3)])

    # Mock CMDB client with proper api.list_biz_hosts
    SUCCESS_TIMEOUT_CMDB_CLIENT = MagicMock()
    SUCCESS_TIMEOUT_CMDB_CLIENT.api.list_biz_hosts = MagicMock(
        return_value={
            "result": True,
            "data": {
                "count": 1,
                "info": [
                    {
                        "bk_host_id": 1,
                        "bk_host_innerip": "1.1.1.1",
                        "bk_cloud_id": 0,
                        "bk_host_innerip_v6": "",
                        "bk_agent_id": "agent1",
                    }
                ],
            },
        }
    )

    return ComponentTestCase(
        name="push_local_files multi v2 with timeout parameter success case",
        inputs={
            "biz_cc_id": "biz_cc_id",
            "job_target_ip_list": "1.1.1.1",
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
            "job_timeout": "1000",
        },
        parent_data={"executor": "executor", "project_id": "project_id", "tenant_id": "system"},
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
            CallAssertion(
                func=SUCCESS_MANAGER.push_files_to_ips,
                calls=[
                    Call(
                        account="job_target_account",
                        bk_biz_id="biz_cc_id",
                        esb_client=SUCCESS_ESB_CLIENT,
                        file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id1"}}],
                        ips=None,
                        target_path="target_path1",
                        timeout=1000,
                        target_server=get_expected_target_server_for_push_files(1),
                        headers={"X-Bk-Tenant-Id": "system"},
                    ),
                    Call(
                        account="job_target_account",
                        bk_biz_id="biz_cc_id",
                        esb_client=SUCCESS_ESB_CLIENT,
                        file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id2"}}],
                        ips=None,
                        target_path="target_path2",
                        timeout=1000,
                        target_server=get_expected_target_server_for_push_files(1),
                        headers={"X-Bk-Tenant-Id": "system"},
                    ),
                    Call(
                        account="job_target_account",
                        bk_biz_id="biz_cc_id",
                        esb_client=SUCCESS_ESB_CLIENT,
                        file_tags=[{"type": "upload_module", "tags": {"tag_id": "tag_id3"}}],
                        ips=None,
                        target_path="target_path3",
                        timeout=1000,
                        target_server=get_expected_target_server_for_push_files(1),
                        headers={"X-Bk-Tenant-Id": "system"},
                    ),
                ],
            )
        ],
        patchers=[
            Patcher(
                target=CC_GET_CLIENT_BY_USERNAME,
                return_value=create_mock_cmdb_client_with_hosts(
                    [
                        {
                            "bk_host_id": 1,
                            "bk_host_innerip": "1.1.1.1",
                            "bk_cloud_id": 0,
                            "bk_host_innerip_v6": "",
                            "bk_agent_id": "agent1",
                        }
                    ]
                ),
            ),
            Patcher(
                target=CMDB_GET_CLIENT_BY_USERNAME,
                return_value=create_mock_cmdb_client_with_hosts(
                    [
                        {
                            "bk_host_id": 1,
                            "bk_host_innerip": "1.1.1.1",
                            "bk_cloud_id": 0,
                            "bk_host_innerip_v6": "",
                            "bk_agent_id": "agent1",
                        }
                    ]
                ),
            ),
            Patcher(target=CC_GET_IPS_INFO_BY_STR_PATCH, side_effect=mock_cc_get_ips_info_by_str_with_host_id(1)),
            Patcher(target=ENVIRONMENT_VAR_GET, return_value="a_type"),
            Patcher(target=FACTORY_GET_MANAGER, return_value=SUCCESS_MANAGER),
            Patcher(target=GET_CLIENT_BY_USER, return_value=SUCCESS_ESB_CLIENT),
            Patcher(target=BASE_GET_CLIENT_BY_USER, return_value=SUCCESS_ESB_CLIENT),
            Patcher(target=GET_JOB_INSTANCE_URL, return_value="url_token"),
        ],
    )
