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
from mock import MagicMock, patch

import env

# 兜底注入 env 中的 nodemgr 配置
if not getattr(env, "BK_NODEMGR_WEB_URL", None):
    env.BK_NODEMGR_WEB_URL = "http://nodemgr.test"
if not getattr(env, "BK_NODEMGR_DEFAULT_PROXY_INFO", None):
    env.BK_NODEMGR_DEFAULT_PROXY_INFO = ""

from pipeline_plugins.components.collections.sites.open.nodemgr.base import (  # noqa: E402
    NodemgrBaseService,
    split_ip_list,
)
from pipeline_plugins.components.collections.sites.open.nodemgr.operate_node.v1_0 import (  # noqa: E402
    NodemgrOperateNodeService,
)
from pipeline_plugins.components.collections.sites.open.nodemgr.operate_plugin.v1_0 import (  # noqa: E402
    NodemgrOperatePluginService,
)

GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.nodemgr.base.BKNodemgrClient"
CRYPTO_DECRYPT = "pipeline_plugins.components.collections.sites.open.nodemgr.base.crypto.decrypt"
LOAD_PEM_PUBLIC_KEY = (
    "pipeline_plugins.components.collections.sites.open.nodemgr.base.serialization.load_pem_public_key"
)


def _fake_pubkey():
    pk = MagicMock()
    pk.encrypt = MagicMock(return_value=b"cipher-bytes")
    return pk


class SplitIpListTestCase(TestCase):
    """split_ip_list 工具函数"""

    def test_strip_default(self):
        self.assertEqual(split_ip_list(" a , b ;c\nd"), ["a", "b", "c", "d"])

    def test_no_strip(self):
        self.assertEqual(split_ip_list("a;b", strip=False), ["a", "b"])

    def test_empty(self):
        self.assertEqual(split_ip_list(""), [])


class IpVersionTestCase(TestCase):
    """ip_version 工具方法"""

    def setUp(self):
        self.svc = NodemgrOperateNodeService()

    def test_ipv4(self):
        self.assertEqual(self.svc.ip_version("1.1.1.1"), 4)

    def test_ipv6(self):
        self.assertEqual(self.svc.ip_version("::1"), 6)

    def test_invalid(self):
        self.assertIsNone(self.svc.ip_version("not-an-ip"))


class EncryptCreditTestCase(TestCase):
    """encrypt_credit: 默认 auth_info=None 走兜底分支"""

    def test_auth_info_none_branch(self):
        svc = NodemgrOperateNodeService()
        client = MagicMock()
        client.public_key_get = MagicMock(return_value={"data": {"public_key": "FAKE-PEM"}})
        with patch(GET_CLIENT_BY_USER, return_value=client), patch(CRYPTO_DECRYPT, return_value="plain"), patch(
            LOAD_PEM_PUBLIC_KEY, return_value=_fake_pubkey()
        ):
            out = svc.encrypt_credit(username="u", auth_info=None)
        # base64('\x01' + b'cipher-bytes') = 'AWNpcGhlci1ieXRlcw=='
        import base64 as _b64

        self.assertEqual(_b64.b64decode(out)[:1], b"\x01")

    def test_get_public_key_empty_raises(self):
        svc = NodemgrOperateNodeService()
        client = MagicMock()
        client.public_key_get = MagicMock(return_value={"data": {"public_key": ""}})
        with patch(GET_CLIENT_BY_USER, return_value=client):
            with self.assertRaises(Exception):
                svc.get_public_key(username="u")


class ListHostByIpTestCase(TestCase):
    """list_host_by_ip 多分支覆盖"""

    def test_default_dict_and_ipv6_and_invalid_ip(self):
        """同时覆盖: networkarea_ip_dict=None 兜底 + ipv6 分支 + 无效 IP continue"""
        svc = NodemgrOperateNodeService()
        client = MagicMock()
        client.host_list = MagicMock(
            return_value={
                "code": 0,
                "data": {
                    "items": [
                        {
                            "info": {
                                "bk_host_innerip_list": ["1.1.1.1"],
                                "bk_host_innerip_v6_list": ["fe80::1"],
                            }
                        }
                    ]
                },
            }
        )
        with patch(GET_CLIENT_BY_USER, return_value=client):
            # 1) None 默认参数: 不抛异常, 走 networkarea_ip_dict={}
            self.assertEqual(svc.list_host_by_ip(biz_id=1, networkarea_ip_dict=None), {})
            # 2) ipv6 + 无效 IP 混合输入
            r = svc.list_host_by_ip(
                biz_id=1,
                networkarea_ip_dict={1: ["fe80::1", "bad-ip", "1.1.1.1"]},
                username="u",
            )
            self.assertIn(1, r)
            self.assertIn("1.1.1.1", r[1])
            self.assertIn("fe80::1", r[1])

    def test_all_invalid_ip_continue(self):
        """全部 IP 都不合法 -> 不发起 host_list 请求, 命中 continue 分支"""
        svc = NodemgrOperateNodeService()
        client = MagicMock()
        client.host_list = MagicMock()
        with patch(GET_CLIENT_BY_USER, return_value=client):
            r = svc.list_host_by_ip(biz_id=1, networkarea_ip_dict={1: ["bad", "also-bad"]})
        self.assertEqual(r, {})
        client.host_list.assert_not_called()

    def test_invalid_ip_else_branch(self):
        """显式覆盖 else: continue (ip 既不是 v4 也不是 v6)"""
        svc = NodemgrOperateNodeService()
        client = MagicMock()
        client.host_list = MagicMock(return_value={"code": 0, "data": {"items": []}})
        with patch(GET_CLIENT_BY_USER, return_value=client):
            # 混合: 一个无效 + 一个有效, 强制走过 else 分支再继续处理有效 IP
            svc.list_host_by_ip(biz_id=1, networkarea_ip_dict={1: ["bad-ip-here", "1.2.3.4"]})
        # 仅有有效 IP 被作为 ipv4 调用
        self.assertEqual(client.host_list.call_count, 1)


class PluginScheduleNoWorkflowIdTestCase(TestCase):
    """plugin_schedule 在拿不到 workflow_id 时应立即 finish_schedule 并返回 True

    覆盖 operate_node v1_0 543-545 / operate_plugin v1_0 229-230
    """

    def _build_data(self, workflow_id=None):
        data = MagicMock()
        # 让 get_one_of_outputs("workflow_id") 返回 workflow_id
        data.get_one_of_outputs = MagicMock(
            side_effect=lambda key, default=None: workflow_id if key == "workflow_id" else default
        )
        return data

    def _build_parent(self):
        parent = MagicMock()
        parent.inputs.executor = "tester"
        return parent

    def test_node_schedule_no_workflow_id(self):
        svc = NodemgrOperateNodeService()
        svc.finish_schedule = MagicMock()
        result = svc.plugin_schedule(self._build_data(None), self._build_parent())
        self.assertTrue(result)
        svc.finish_schedule.assert_called_once()

    def test_plugin_schedule_no_workflow_id(self):
        svc = NodemgrOperatePluginService()
        svc.finish_schedule = MagicMock()
        result = svc.plugin_schedule(self._build_data(None), self._build_parent())
        self.assertTrue(result)
        svc.finish_schedule.assert_called_once()


class CheckWorkflowResultExceptionTestCase(TestCase):
    """check_workflow_result 调用过程中抛异常 -> 返回 (True, False, 0, 0, str(e))"""

    def _build_svc(self):
        svc = NodemgrBaseService()
        svc.logger = MagicMock()
        return svc

    def test_exception_branch(self):
        svc = self._build_svc()
        client = MagicMock()
        client.node_workflow_operation_list = MagicMock(side_effect=RuntimeError("boom"))
        is_finished, is_success, sc, fc, err = svc.check_workflow_result(client, "wf-x", is_plugin=False)
        self.assertTrue(is_finished)
        self.assertFalse(is_success)
        self.assertEqual(sc, 0)
        self.assertEqual(fc, 0)
        self.assertEqual(err, "boom")

    def test_failed_without_op_id(self):
        """failed_count > 0 但所有 op 都没有 operation_id -> error_message 为 'Some operations failed'"""
        svc = self._build_svc()
        client = MagicMock()
        client.node_workflow_operation_list = MagicMock(
            return_value={
                "code": 0,
                "data": {
                    "operations": [
                        {"latest_oper_inst_brief_data": {"life_cycle": "FAILED"}},  # 没 operation_id
                    ]
                },
            }
        )
        is_finished, is_success, sc, fc, err = svc.check_workflow_result(client, "wf-x", is_plugin=False)
        self.assertTrue(is_finished)
        self.assertFalse(is_success)
        self.assertEqual(fc, 1)
        self.assertEqual(err, "Some operations failed")
