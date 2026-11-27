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

import ipaddress

from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext_lazy as _

import env
from gcloud.exceptions import ApiRequestError
from gcloud.utils.handlers import handle_api_error
from packages.bkapi.bk_nodemgr.client import Client as BKNodemgrApiClient

# nodemgr 节点状态(node_status) -> nodeman agent 在线状态(bk_agent_alive) 映射
# bk_agent_alive: 1 在线 / 0 离线 / -1 未知
NODE_STATUS_AGENT_ALIVE_MAP = {
    "running": 1,
    "busy": 1,
    "starting": 1,
    "upgrade": 1,
    "init": 0,
    "uninit": 0,
    "damaged": 0,
    "stopping": 0,
    "unknown": -1,
}


class BKNodemgrClient(BKNodemgrApiClient):
    """Nodemgr API 网关 client。

    继承 packages/bkapi/bk_nodemgr SDK Client, 走统一 API 网关;
    保留原直连版的方法签名作为薄封装, 调用方无需感知底层变更。
    """

    def __init__(self, username=None, tenant_id=None, stage=None):
        # 统一走 API 网关: 网关地址由 BK_API_URL_TMPL 模板解析,
        # 如 http://bkapi.xxx.com/api/{api_name} -> http://bkapi.xxx.com/api/bk-nodemgr/{stage}
        endpoint = getattr(settings, "BK_API_URL_TMPL", "") or env.BK_APIGW_URL_TMPL
        if not endpoint:
            raise RuntimeError(
                "BK_API_URL_TMPL is not configured; please set the environment "
                "variable before using the Nodemgr plugin."
            )
        super().__init__(
            stage=stage or getattr(settings, "BK_APIGW_STAGE_NAME", "prod"),
            endpoint=endpoint,
        )

        auth = {
            "bk_app_code": settings.APP_CODE,
            "bk_app_secret": settings.SECRET_KEY,
        }
        if username:
            auth["bk_username"] = username
        self.update_bkapi_authorization(**auth)

        # 多租户场景下透传租户 ID
        if tenant_id:
            self.update_headers({"X-Bk-Tenant-Id": str(tenant_id)})

        # 与其他蓝鲸组件调用保持一致: 透传当前语言
        language = translation.get_language()
        if language:
            self.update_headers({"blueking-language": language})

    # ========== Info APIs ==========
    def networkarea_list(self, offset=0, limit=1000):
        return self.api.networkarea_list(
            data={
                "page": {
                    "offset": offset,
                    "limit": limit,
                }
            },
        )

    def networkunit_list(self, networkarea_id: int, offset=0, limit=1000):
        return self.api.networkunit_list(
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
        return self.api.host_list(
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

    def host_agent_status(self, biz_id, host_id_list=None, networkarea_ip_map=None):
        """查询主机 agent 在线状态，替代 nodeman 的 ipchooser_host_details。

        返回与 format_agent_data 输出一致的映射：
        {f"{networkarea_id}:{ip}": {"ip": ip, "bk_cloud_id": networkarea_id, "bk_agent_alive": alive}}

        :param biz_id: 业务 ID，为空时不按业务过滤（跨业务场景）
        :param host_id_list: 按主机 ID 精确查询
        :param networkarea_ip_map: 按 {网络区域ID: [ip, ...]} 精确查询
        """
        exact_conditions = {}
        if biz_id:
            exact_conditions["bk_biz_id"] = [biz_id]
        if host_id_list:
            exact_conditions["bk_host_id"] = list(host_id_list)
        if networkarea_ip_map:
            ipv4_list = []
            ipv6_list = []
            for ip_list in networkarea_ip_map.values():
                for ip in ip_list:
                    try:
                        if ipaddress.ip_address(ip).version == 6:
                            ipv6_list.append(ip)
                        else:
                            ipv4_list.append(ip)
                    except ValueError:
                        continue
            exact_conditions["bk_networkarea_id"] = list(networkarea_ip_map.keys())
            if ipv4_list:
                exact_conditions["bk_host_innerip"] = ipv4_list
            if ipv6_list:
                exact_conditions["bk_host_innerip_v6"] = ipv6_list

        hosts = []
        offset = 0
        limit = 1000
        while True:
            response = self.api.host_list(
                data={
                    "page": {"offset": offset, "limit": limit},
                    "exact_include_conditions": exact_conditions,
                }
            )
            if response.get("code") != 0:
                message = handle_api_error(_("节点管理(NODEMGR)"), "nodemgr.host_list", exact_conditions, response)
                raise ApiRequestError(message)

            items = response.get("data", {}).get("items") or []
            hosts.extend(items)
            if len(items) < limit:
                break
            offset += limit

        result = {}
        for host in hosts:
            info = host.get("info") or {}
            state = host.get("state") or {}
            networkarea_id = info.get("bk_networkarea_id")
            if networkarea_id is None:
                continue
            alive = NODE_STATUS_AGENT_ALIVE_MAP.get(state.get("node_status"), -1)
            for ip in (info.get("bk_host_innerip_list") or []) + (info.get("bk_host_innerip_v6_list") or []):
                if ip:
                    result[f"{networkarea_id}:{ip}"] = {
                        "ip": ip,
                        "bk_cloud_id": networkarea_id,
                        "bk_agent_alive": alive,
                    }
        return result

    def package_list(self, node_role="agent", offset=0, limit=1000, plugin_pkg_name=None):
        return self.api.package_list(
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
            path_params={"node_role": node_role},
        )

    def package_distinct(self, node_role="agent"):
        return self.api.package_distinct(
            data={
                "generation": 2,
                "exact_include_conditions": {"enabled": [True]},
                "distinct_field": {"os_type": True}
            },
            path_params={"node_role": node_role},
        )

    def public_key_get(self):
        return self.api.public_key_get(data={})

    def networkunit_recommand(self, hosts=None):
        # SDK 资源名为 networkunit_recommend, 此处保留原直连版方法名(含拼写)以兼容既有调用方
        if hosts is None:
            hosts = []
        return self.api.networkunit_recommend(
            data={
                "items": hosts,
            },
        )

    # ========== Node Agent APIs ==========
    def node_install_check(self, hosts, node_role="agent"):
        return self.api.node_install_check(
            data={
                "host": hosts,
            },
            path_params={"node_role": node_role},
        )

    def node_install(self, hosts, node_role="agent"):
        return self.api.node_install(
            data={
                "host": hosts,
                "target_version": [],
                "is_manual": False,
            },
            path_params={"node_role": node_role},
        )

    def node_upgrade(self, hosts, node_role="agent"):
        return self.api.node_upgrade(
            data={
                "host": hosts,
            },
            path_params={"node_role": node_role},
        )

    def node_restart(self, hosts, node_role="agent"):
        return self.api.node_restart(
            data={
                "host": hosts,
            },
            path_params={"node_role": node_role},
        )

    def node_reconfig(self, hosts, node_role="agent"):
        return self.api.node_reconfig(
            data={
                "host": hosts,
            },
            path_params={"node_role": node_role},
        )

    def node_uninstall(self, hosts, node_role="agent"):
        return self.api.node_uninstall(
            data={
                "host": hosts,
            },
            path_params={"node_role": node_role},
        )

    # ========== Plugin APIs ==========
    def plugin_install(self, plugins):
        return self.api.plugin_install(
            data={
                "plugin": plugins,
            },
        )

    def plugin_uninstall(self, plugins):
        return self.api.plugin_uninstall(
            data={
                "plugin": plugins,
            },
        )

    def plugin_list(self, group=None, biz_id=None, offset=0, limit=500):
        if group is None:
            group = ["default"]
        if biz_id is None:
            biz_id = []
        return self.api.plugin_list(
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

        return self.api.node_workflow_operation_list(
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

        return self.api.plugin_workflow_operation_list(
            data={
                "workflow_id": workflow_id,
                "only_count": False,
                "page": normalized_page,
            },
        )

    def node_workflow_operation_instance_log_get(self, oper_inst_id):
        return self.api.node_workflow_operation_instance_log_get(
            data={
                "oper_inst_id": oper_inst_id,
            },
        )

    def plugin_workflow_operation_instance_log_get(self, oper_inst_id):
        return self.api.plugin_workflow_operation_instance_log_get(
            data={
                "oper_inst_id": oper_inst_id,
            },
        )
