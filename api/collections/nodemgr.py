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

import env
import ujson as json

from api.client import BKComponentClient


class BKNodemgrClient(BKComponentClient):
    def __init__(self, *args, **kwargs):
        super(BKNodemgrClient, self).__init__(*args, **kwargs)

        api_entry = getattr(env, "BK_NODEMGR_API_ENTRY", "") or ""
        if not api_entry:
            raise RuntimeError(
                "BK_NODEMGR_API_ENTRY is not configured; please set the environment "
                "variable before using the Nodemgr plugin."
            )
        self.base_url = api_entry.rstrip("/")
        # app_code / app_secret 已由父类 BKComponentClient.__init__ 处理，
        # 默认回落到 settings.APP_CODE / settings.SECRET_KEY，无需在此覆盖。

    def _pre_process_headers(self, headers):
        """使用 X-Bkapi-Authorization header 传递认证信息，而非注入 body

        注意：BKComponentClient._request 调用 _pre_process_headers 时不接收返回值，
        所以必须 in-place 修改 headers，不能创建新 dict。
        """
        # in-place 设置必要 header（不能创建新 dict，否则 _request 中会丢失）
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        headers["blueking-language"] = self.language
        if self.use_test_env:
            headers["x-use-test-env"] = "1"

        auth_info = {
            "bk_app_code": self.app_code,
            "bk_app_secret": self.app_secret,
        }
        if self.username:
            auth_info["bk_username"] = self.username
        headers["X-Bkapi-Authorization"] = json.dumps(auth_info)
        return headers

    def _pre_process_data(self, data):
        """不在 body 中注入认证字段，认证已通过 header 传递"""
        pass

    # ========== Info APIs ==========
    def networkarea_list(self, offset=0, limit=1000):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/topo/networkarea/list",
            data={
                "page": {
                    "offset": offset,
                    "limit": limit,
                }
            },
        )

    def networkunit_list(self, networkarea_id: int, offset=0, limit=1000):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/topo/networkunit/list/brief",
            data={
                "page": {
                    "offset": offset,
                    "limit": limit,
                },
                "exact_include_conditions": {"bk_networkarea_id": [networkarea_id]},
            },
        )

    def host_list(self, biz_id, networkarea_id, ipv4_list=None, ipv6_list=None, offset=0, limit=1000):
        if ipv4_list is None:
            ipv4_list = []
        if ipv6_list is None:
            ipv6_list = []
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/topo/host/list",
            data={
                "page": {
                    "offset": offset,
                    "limit": limit,
                },
                "exact_include_conditions": {
                    "bk_biz_id": [biz_id],
                    "bk_networkarea_id": [networkarea_id],
                },
                "fuzzy_include_conditions": {
                    "bk_host_innerip": ipv4_list,
                    "bk_host_innerip_v6": ipv6_list,
                },
            },
        )

    def package_list(self, node_role="agent", offset=0, limit=1000, plugin_pkg_name=None):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/package/release/{node_role}/list/brief",
            data={
                "page": {
                    "offset": offset,
                    "limit": limit,
                },
                "generation": 2,
                "exact_include_conditions": {
                    "enabled": [True],
                    "name": [plugin_pkg_name] if plugin_pkg_name else [],
                },
            },
        )

    def package_distinct(self, node_role="agent"):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/package/release/{node_role}/distinct",
            data={
                "generation": 2,
                "exact_include_conditions": {"enabled": [True]},
                "distinct_field": {"os_type": True}
            },
        )

    def public_key_get(self):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/cipher/rsa/get_public_key",
            data={},
        )

    def networkunit_recommand(self, hosts=None):
        if hosts is None:
            hosts = []
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/topo/networkunit/recommend_by_network_segment",
            data={
                "items": hosts,
            },
        )

    # ========== Node Agent APIs ==========
    def node_install_check(self, hosts, node_role="agent"):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/node/{node_role}/install_check",
            data={
                "host": hosts,
            },
        )

    def node_install(self, hosts, node_role="agent"):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/node/{node_role}/install",
            data={
                "host": hosts,
                "target_version": [],
                "is_manual": False,
            },
        )

    def node_upgrade(self, hosts, node_role="agent"):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/node/{node_role}/upgrade",
            data={
                "host": hosts,
            },
        )

    def node_restart(self, hosts, node_role="agent"):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/node/{node_role}/restart",
            data={
                "host": hosts,
            },
        )

    def node_reconfig(self, hosts, node_role="agent"):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/node/{node_role}/reconfig",
            data={
                "host": hosts,
            },
        )

    def node_uninstall(self, hosts, node_role="agent"):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/node/{node_role}/uninstall",
            data={
                "host": hosts,
            },
        )

    # ========== Plugin APIs ==========
    def plugin_install(self, plugins):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/plugin/install",
            data={
                "plugin": plugins,
            },
        )

    def plugin_uninstall(self, plugins):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/plugin/uninstall",
            data={
                "plugin": plugins,
            },
        )

    def plugin_list(self, group=None, biz_id=None, offset=0, limit=500):
        if group is None:
            group = ["default"]
        if biz_id is None:
            biz_id = []
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/plugin/list",
            data={
                "page": {
                    "offset": offset,
                    "limit": limit,
                },
                "exact_include_conditions": {
                    "group": group,
                    "visible_biz_ids": biz_id,
                }
            },
        )

    # ========== Workflow Query APIs ==========
    def node_workflow_operation_list(self, workflow_id, page=None):
        normalized_page = {"offset": 0, "limit": 500}
        if page:
            normalized_page.update({k: v for k, v in page.items() if v is not None})

        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/node/workflow/operation/list",
            data={
                "workflow_id": workflow_id,
                "only_count": False,
                "page": normalized_page,
            },
        )

    def plugin_workflow_operation_list(self, workflow_id, page=None):
        normalized_page = {"offset": 0, "limit": 500}
        if page:
            normalized_page.update({k: v for k, v in page.items() if v is not None})

        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/plugin/workflow/operation/list",
            data={
                "workflow_id": workflow_id,
                "only_count": False,
                "page": normalized_page,
            },
        )

    def node_workflow_operation_instance_log_get(self, oper_inst_id):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/node/workflow/operation/instance/log/get",
            data={
                "oper_inst_id": oper_inst_id,
            },
        )

    def plugin_workflow_operation_instance_log_get(self, oper_inst_id):
        return self._request(
            method="post",
            url=f"{self.base_url}/api/v3/plugin/workflow/operation/instance/log/get",
            data={
                "oper_inst_id": oper_inst_id,
            },
        )
