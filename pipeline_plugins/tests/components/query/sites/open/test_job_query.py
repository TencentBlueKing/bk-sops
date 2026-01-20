# -*- coding: utf-8 -*-
import json

from django.http import JsonResponse
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.query.sites.open import job as job_query


class MockUser(object):
    def __init__(self, username="tester", tenant_id="system"):
        self.username = username
        self.tenant_id = tenant_id


class MockRequest(object):
    def __init__(self, user=None, get_params=None):
        self.user = user or MockUser()
        self.GET = get_params or {}


def parse_json_response(resp: JsonResponse):
    return json.loads(resp.content.decode("utf-8"))


class JobQueryTests(TestCase):
    @patch("pipeline_plugins.components.query.sites.open.job.batch_request")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_get_script_name_list_and_public(self, mock_get_client, mock_batch):
        client = type("C", (), {"api": MagicMock()})()
        mock_get_client.return_value = client
        # 脚本含 online_script_version_id 的才进入结果
        mock_batch.return_value = [
            {"name": "s1", "online_script_version_id": 1},
            {"name": "s2"},  # 无 online_script_version_id
            {"name": "s3", "online_script_version_id": 2},
        ]
        req = MockRequest(get_params={"script_type": 1})
        res1 = job_query.job_get_script_name_list(req, biz_cc_id=2)
        data1 = parse_json_response(res1)
        self.assertTrue(data1["result"])
        self.assertEqual({d["value"] for d in data1["data"]}, {"s1", "s3"})

        # 公共脚本
        req_pub = MockRequest(get_params={"type": "public"})
        res2 = job_query.job_get_public_script_name_list(req_pub)
        data2 = parse_json_response(res2)
        self.assertTrue(data2["result"])
        self.assertEqual({d["value"] for d in data2["data"]}, {"s1", "s3"})

    @patch("pipeline_plugins.components.query.sites.open.job.batch_request")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_get_script_list_value_field(self, mock_get_client, mock_batch):
        client = type("C", (), {"api": MagicMock()})()
        mock_get_client.return_value = client
        mock_batch.return_value = [
            {"name": "s1", "id": 3},
            {"name": "s1", "id": 5},
            {"name": "s2", "id": 4},
            {"name": "s3", "id": "str-id"},  # 非 int 不参与
        ]
        req = MockRequest(get_params={"value_field": "id"})
        res = job_query.job_get_script_list(req, biz_cc_id=2)
        data = parse_json_response(res)
        self.assertTrue(data["result"])
        # s1 取最大 5
        self.assertIn({"text": "s1", "value": 5}, data["data"])
        self.assertIn({"text": "s2", "value": 4}, data["data"])

    @patch("pipeline_plugins.components.query.sites.open.job.check_and_raise_raw_auth_fail_exception")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_get_script_by_version_success_and_fail(self, mock_get_client, mock_check):
        client = type("C", (), {"api": MagicMock()})()
        client.api.get_script_version_detail = MagicMock(return_value={"result": True, "data": {"name": "script-x"}})
        mock_get_client.return_value = client
        req = MockRequest(get_params={"script_version": 10})
        res = job_query.job_get_script_by_script_version(req, biz_cc_id=2)
        data = parse_json_response(res)
        self.assertTrue(data["result"])
        self.assertEqual(data["data"]["script_name"], "script-x")

        # 接口失败分支
        client.api.get_script_version_detail = MagicMock(return_value={"result": False, "message": "denied"})
        res_fail = job_query.job_get_script_by_script_version(req, biz_cc_id=2)
        data_fail = parse_json_response(res_fail)
        self.assertFalse(data_fail["result"])
        self.assertIn("denied", data_fail.get("message", ""))

    @patch("pipeline_plugins.components.query.sites.open.job.batch_request")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_get_job_tasks_by_biz(self, mock_get_client, mock_batch):
        client = type("C", (), {"api": MagicMock()})()
        mock_get_client.return_value = client
        mock_batch.return_value = [{"id": 1, "name": "p1"}, {"id": 2, "name": "p2"}]
        req = MockRequest()
        res = job_query.job_get_job_tasks_by_biz(req, biz_cc_id=2)
        data = parse_json_response(res)
        self.assertTrue(data["result"])
        self.assertEqual(data["data"], [{"value": 1, "text": "p1"}, {"value": 2, "text": "p2"}])

    @patch("pipeline_plugins.components.query.sites.open.job.settings.ENABLE_IPV6", True)
    @patch(
        "pipeline_plugins.components.query.sites.open.job.format_host_with_ipv6", lambda h, with_cloud=True: "0:fe80::1"
    )
    @patch("pipeline_plugins.components.query.sites.open.job.get_business_set_host")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_get_job_task_detail_ipv6_and_unknown_var(self, mock_get_client, mock_get_hosts):
        # 接口成功，包含 IPv6 变量与未知类型变量
        client = type("C", (), {"api": MagicMock()})()
        mock_get_client.return_value = client
        mock_get_hosts.return_value = [{"bk_host_id": 1, "bk_host_innerip": "127.0.0.1"}]
        job_result = {
            "result": True,
            "data": {
                "global_var_list": [
                    {
                        "id": 1,
                        "type": job_query.JOB_VAR_CATEGORY_IP,
                        "name": "ip",
                        "description": "",
                        "server": {"ip_list": [{"bk_host_id": 1, "ip": "fe80::1", "bk_cloud_id": 0}]},
                    },
                    {"id": 2, "type": 999, "name": "unknown", "description": ""},  # 未知类型，跳过
                    {"id": 3, "type": job_query.JOB_VAR_CATEGORY_CLOUD, "name": "str", "value": "v", "description": ""},
                ],
                "step_list": [
                    {"id": 11, "name": "s", "type": 1, "script_info": {"script_param": "p", "account": {"id": "root"}}}
                ],
            },
        }
        client.api.get_job_plan_detail = MagicMock(return_value=job_result)
        req = MockRequest()
        res = job_query.job_get_job_task_detail(req, biz_cc_id=2, task_id=1)
        data = parse_json_response(res)
        self.assertTrue(data["result"])
        gv = data["data"]["global_var"]
        # IPv6 被格式化
        self.assertTrue(any(item["name"] == "ip" and item["value"] == "0:fe80::1" for item in gv))
        # 未知类型不在结果
        self.assertFalse(any(item["name"] == "unknown" for item in gv))

    @patch("pipeline_plugins.components.query.sites.open.job.check_and_raise_raw_auth_fail_exception")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_get_job_task_detail_fail(self, mock_get_client, mock_check):
        client = type("C", (), {"api": MagicMock()})()
        mock_get_client.return_value = client
        client.api.get_job_plan_detail = MagicMock(return_value={"result": False, "message": "bad"})
        req = MockRequest()
        res = job_query.job_get_job_task_detail(req, biz_cc_id=2, task_id=1)
        data = parse_json_response(res)
        self.assertFalse(data["result"])
        self.assertIn("请求执行方案失败", data["message"])

    @patch("pipeline_plugins.components.query.sites.open.job.check_and_raise_raw_auth_fail_exception")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_get_instance_detail_success_and_fail(self, mock_get_client, mock_check):
        client = type("C", (), {"api": MagicMock()})()
        mock_get_client.return_value = client
        job_result = {
            "result": True,
            "data": [
                {
                    "step_instance_id": 1,
                    "step_results": [{"ip_logs": [{"ip": "1.1.1.1", "log_content": "log", "exit_code": 0}]}],
                }
            ],
        }
        client.api.get_job_instance_ip_log = MagicMock(return_value=job_result)
        req = MockRequest(
            get_params={
                "bk_scope_type": job_query.JobBizScopeType.BIZ.value,
                "step_instance_id": 1,
                "bk_cloud_id": 0,
                "ip": "1.1.1.1",
            }
        )
        res = job_query.job_get_instance_detail(req, biz_cc_id=2, task_id=1)
        data = parse_json_response(res)
        self.assertTrue(data["result"])
        self.assertEqual(data["data"][0]["ip"], "1.1.1.1")
        self.assertIn("log", data["data"][0]["log"])

        # 失败分支
        client.api.get_job_instance_ip_log = MagicMock(return_value={"result": False, "message": "denied"})
        res_fail = job_query.job_get_instance_detail(req, biz_cc_id=2, task_id=1)
        data_fail = parse_json_response(res_fail)
        self.assertFalse(data_fail["result"])
        self.assertIn("执行历史请求失败", data_fail["message"])

    @patch("pipeline_plugins.components.query.sites.open.job.batch_request")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_jobv3_get_job_template_and_plan_list(self, mock_get_client, mock_batch):
        client = type("C", (), {"api": MagicMock()})()
        mock_get_client.return_value = client
        mock_batch.return_value = [{"id": 1, "name": "t1"}]
        req = MockRequest()
        data_tmpl = parse_json_response(job_query.jobv3_get_job_template_list(req, biz_cc_id=2))
        self.assertTrue(data_tmpl["result"])
        self.assertEqual(data_tmpl["data"], [{"value": 1, "text": "t1"}])

        mock_batch.return_value = [{"id": 7, "name": "p7"}]
        data_plan = parse_json_response(job_query.jobv3_get_job_plan_list(req, biz_cc_id=2, job_template_id=1))
        self.assertTrue(data_plan["result"])
        self.assertEqual(data_plan["data"], [{"value": 7, "text": "p7"}])

    @patch("pipeline_plugins.components.query.sites.open.job.settings.ENABLE_IPV6", False)
    @patch("pipeline_plugins.components.query.sites.open.job.check_and_raise_raw_auth_fail_exception")
    @patch("pipeline_plugins.components.query.sites.open.job.handle_api_error")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_jobv3_get_job_plan_detail_fail_and_success(self, mock_get_client, mock_handle_error, mock_check):
        client = type("C", (), {"api": MagicMock()})()
        mock_get_client.return_value = client
        # 失败分支
        client.api.get_job_plan_detail = MagicMock(return_value={"result": False, "message": "bad"})
        req = MockRequest(get_params={"bk_scope_type": job_query.JobBizScopeType.BIZ.value})
        res_fail = job_query.jobv3_get_job_plan_detail(req, biz_cc_id=2, job_plan_id=1)
        data_fail = parse_json_response(res_fail)
        self.assertFalse(data_fail["result"])

        # 成功分支，包含 IP 变量（IPv4）
        client.api.get_job_plan_detail = MagicMock(
            return_value={
                "result": True,
                "data": {
                    "global_var_list": [
                        {
                            "id": 1,
                            "type": job_query.JOBV3_VAR_CATEGORY_IP,
                            "name": "ip",
                            "description": "",
                            "server": {"ip_list": [{"ip": "127.0.0.1", "bk_cloud_id": 0}]},
                        },
                        {
                            "id": 2,
                            "type": job_query.JOBV3_VAR_CATEGORY_STRING,
                            "name": "str",
                            "value": "v",
                            "description": "",
                        },
                    ]
                },
            }
        )
        res_ok = job_query.jobv3_get_job_plan_detail(req, biz_cc_id=2, job_plan_id=1)
        data_ok = parse_json_response(res_ok)
        self.assertTrue(data_ok["result"])
        self.assertTrue(any(item["name"] == "ip" and item["value"] == "0:127.0.0.1" for item in data_ok["data"]))

    @patch("pipeline_plugins.components.query.sites.open.job.check_and_raise_raw_auth_fail_exception")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_jobv3_get_instance_list_fail_and_empty(self, mock_get_client, mock_check):
        client = type("C", (), {"api": MagicMock()})()
        mock_get_client.return_value = client
        req = MockRequest(get_params={"bk_scope_type": job_query.JobBizScopeType.BIZ.value, "type": 1, "status": 3})

        # 失败分支
        client.api.get_job_instance_list = MagicMock(return_value={"result": False, "message": "bad"})
        data_fail = parse_json_response(job_query.jobv3_get_instance_list(req, biz_cc_id=2, type=1, status=3))
        self.assertFalse(data_fail["result"])

        # 空列表分支
        client.api.get_job_instance_list = MagicMock(return_value={"result": True, "data": {"data": []}})
        data_empty = parse_json_response(job_query.jobv3_get_instance_list(req, biz_cc_id=2, type=1, status=3))
        self.assertTrue(data_empty["result"])
        self.assertEqual(data_empty["data"], [])

    @patch("pipeline_plugins.components.query.sites.open.job.batch_request")
    @patch("pipeline_plugins.components.query.sites.open.job.get_client_by_username")
    def test_get_job_account_list(self, mock_get_client, mock_batch):
        client = type("C", (), {"api": MagicMock()})()
        mock_get_client.return_value = client

        # 空
        mock_batch.return_value = []
        req = MockRequest(get_params={"bk_scope_type": job_query.JobBizScopeType.BIZ.value})
        data_empty = parse_json_response(job_query.get_job_account_list(req, biz_cc_id=2))
        self.assertTrue(data_empty["result"])
        self.assertEqual(data_empty["data"], [])

        # 有数据
        mock_batch.return_value = [{"alias": "root"}]
        data_ok = parse_json_response(job_query.get_job_account_list(req, biz_cc_id=2))
        self.assertTrue(data_ok["result"])
        self.assertEqual(data_ok["data"], [{"text": "root", "value": "root"}])
