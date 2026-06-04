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

import logging

import env
import ujson as json
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component

from gcloud.conf import settings

from ..base import NodemgrBaseService, split_ip_list

__group_name__ = _("节点管理V3(Nodemgr)")

logger = logging.getLogger("root")

NODEMGR_DEFAULT_PROXY_INFO = {
    "relay_callback_port": 28302,
    "relay_download_port": 28303,
    "proxy_tags": ["dedicated_installer", "cluster_tunnel", "file_tunnel", "data_tunnel"]
}


class NodemgrOperateNodeService(NodemgrBaseService):
    def __init__(self, *args, **kwargs):
        super(NodemgrOperateNodeService, self).__init__(*args, **kwargs)

        self.web_url = env.BK_NODEMGR_WEB_URL

        try:
            self.proxy_info = json.loads(env.BK_NODEMGR_DEFAULT_PROXY_INFO)
        except Exception:
            self.proxy_info = NODEMGR_DEFAULT_PROXY_INFO

    def wrap_hosts(self, data):
        operation_info = data.inputs.nodemgr_op_info
        param_mode = operation_info.get("nodemgr_hosts_param_mode", None)
        operation_type = operation_info.get("nodemgr_operation_type", "")

        # 批量模式, 一个IP对应一台主机
        if param_mode == "batch":
            if operation_type == "install":
                hosts = []
                batch = operation_info.get("nodemgr_batch_install")

                inner_ip_list = split_ip_list(batch.get("inner_ip"), strip=False)
                login_ip_list = [ip for ip in split_ip_list(batch.get("login_ip"), strip=False) if ip.strip()]
                if len(login_ip_list) != 0 and len(login_ip_list) != len(inner_ip_list):
                    raise Exception("login_ip数量不匹配")

                for i in range(len(inner_ip_list)):
                    inner_ip = inner_ip_list[i]
                    login_ip = login_ip_list[i] if len(login_ip_list) > 0 else inner_ip

                    ipv = self.ip_version(inner_ip)
                    if ipv not in [4, 6]:
                        raise Exception(f"IP地址格式错误: {inner_ip}")

                    host = {
                        "bk_networkarea_id": batch.get("bk_networkarea_id"),
                        "bk_networkunit_id": batch.get("bk_networkunit_id"),
                        "bk_host_innerip": inner_ip if ipv == 4 else "",
                        "bk_host_innerip_v6": inner_ip if ipv == 6 else "",
                        "bk_addressing": batch.get("bk_addressing"),
                        "os_type": batch.get("os_type"),
                        "login_ip": login_ip,
                        "login_port": batch.get("login_port"),
                        "login_user": batch.get("login_user"),
                        "login_mode": batch.get("login_mode"),
                        "login_password": batch.get("login_password"),
                        "re_register": batch.get("re_register", False),
                    }
                    hosts.append(host)

                return hosts

            if operation_type == "upgrade":
                hosts = []
                batch = operation_info.get("nodemgr_batch_upgrade")

                inner_ip_list = split_ip_list(batch.get("inner_ip"))

                for inner_ip in inner_ip_list:
                    ipv = self.ip_version(inner_ip)
                    if ipv not in [4, 6]:
                        raise Exception(f"IP地址格式错误: {inner_ip}")

                    host = {
                        "bk_networkarea_id": batch.get("bk_networkarea_id"),
                        "inner_ip": inner_ip,
                        "upgrade_version": batch.get("upgrade_version"),
                    }
                    hosts.append(host)

                return hosts

            if operation_type == "restart":
                hosts = []
                batch = operation_info.get("nodemgr_batch_restart")
                inner_ip_list = split_ip_list(batch.get("inner_ip"))
                for inner_ip in inner_ip_list:
                    ipv = self.ip_version(inner_ip)
                    if ipv not in [4, 6]:
                        raise Exception(f"IP地址格式错误: {inner_ip}")
                    host = {
                        "bk_networkarea_id": batch.get("bk_networkarea_id"),
                        "inner_ip": inner_ip,
                    }
                    hosts.append(host)
                return hosts

            if operation_type == "uninstall":
                hosts = []
                batch = operation_info.get("nodemgr_batch_uninstall")
                inner_ip_list = split_ip_list(batch.get("inner_ip"))
                for inner_ip in inner_ip_list:
                    ipv = self.ip_version(inner_ip)
                    if ipv not in [4, 6]:
                        raise Exception(f"IP地址格式错误: {inner_ip}")
                    host = {
                        "bk_networkarea_id": batch.get("bk_networkarea_id"),
                        "inner_ip": inner_ip,
                    }
                    hosts.append(host)
                return hosts

            raise Exception(f"Invalid nodemgr_operation_type: {operation_type}")

        # 列表模式, 一行对应一台主机
        elif param_mode == "list":
            return operation_info.get("nodemgr_hosts", [])

        else:
            raise Exception("Invalid nodemgr_hosts_param_mode")

    def fetch_hosts(self, biz_id, hosts, username=None):
        """
        根据 hosts 列表中的 inner_ip 和 networkarea_id 获取 真实的 host 信息(含bk_host_id)

        返回值: 一个字典, key 为 networkarea_id, 二级key为inner_ip, value 为 host 信息列表
        {
            "0": {
                "1.1.1.1": {
                    "bk_host_id": 1,
                    ...
                }
            }
        }
        """
        networkarea_ip_dict = {}
        for host in hosts:
            networkarea_id = int(host.get("bk_networkarea_id", -1))
            if networkarea_id not in networkarea_ip_dict:
                networkarea_ip_dict[networkarea_id] = []

            inner_ip = host.get("inner_ip")
            if inner_ip:
                networkarea_ip_dict[networkarea_id].append(inner_ip)

        return self.list_host_by_ip(biz_id=biz_id, networkarea_ip_dict=networkarea_ip_dict, username=username)

    def do_install(self, username, data):
        client = self.get_client(username=username)

        biz_id = data.inputs.nodemgr_biz_id
        operation_info = data.inputs.nodemgr_op_info
        install_plugin = operation_info.get("nodemgr_install_plugin", False)
        hosts = self.wrap_hosts(data)

        node_role = operation_info.get("nodemgr_node_role")
        if node_role not in ["agent", "proxy"]:
            raise Exception(f"Invalid nodemgr_node_role: {node_role}")

        # 构造 networkunit-command 请求
        recommand_hosts = []
        for host in hosts:
            inner_ip = split_ip_list(host.get("bk_host_innerip", ""))
            inner_ipv6 = split_ip_list(host.get("bk_host_innerip_v6", ""))
            networkarea_id = host.get("bk_networkarea_id")
            networkunit_id = host.get("bk_networkunit_id")

            # 未显示指定networkunit, 需要自动推荐
            if networkunit_id is not None and networkunit_id < 0:
                recommand_hosts.append({
                    "bk_networkarea_id": networkarea_id,
                    "ip": inner_ip[0] if inner_ip else inner_ipv6[0] if inner_ipv6 else None,
                })

        recommanded_networkunits = []
        if recommand_hosts:
            result = client.networkunit_recommand(hosts=recommand_hosts)

            if result.get("code") != 0:
                error_msg = result.get("message", "Unknown error")
                data.set_outputs("ex_data", _("[节点管理器]获取推荐管控单元失败: %s") % error_msg)
                self.logger.error(f"Nodemgr API error: {error_msg}")
                return False

            recommanded_networkunits = result["data"]["items"]

        # 构造 install-check 请求
        check_hosts = []
        for host in hosts:
            inner_ip = split_ip_list(host.get("bk_host_innerip", ""))
            inner_ipv6 = split_ip_list(host.get("bk_host_innerip_v6", ""))
            single_inner_ip = inner_ip[0] if inner_ip else inner_ipv6[0] if inner_ipv6 else None
            networkarea_id = host.get("bk_networkarea_id")
            networkunit_id = host.get("bk_networkunit_id")

            # 未显示指定networkunit, 需要自动推荐
            if networkunit_id is not None and networkunit_id < 0:
                for recommanded_networkunit in recommanded_networkunits:
                    if (recommanded_networkunit.get("bk_networkarea_id") == networkarea_id
                            and recommanded_networkunit.get("ip") in (inner_ip + inner_ipv6)):
                        networkunit_id = recommanded_networkunit.get("bk_networkunit_id")
                        host["bk_networkunit_id"] = networkunit_id
                        break
            if networkunit_id is not None and networkunit_id < 0:
                error_msg = _(f"获取推荐管控单元失败{networkarea_id}:{single_inner_ip}")
                data.set_outputs("ex_data", _("节点安装失败: %s") % error_msg)
                self.logger.error(f"Nodemgr API error: {error_msg}")
                return False

            check_host = {
                "bk_biz_id": biz_id,
                "bk_networkunit_id": networkunit_id,
                "bk_host_innerip_list": inner_ip,
                "bk_host_innerip_v6_list": inner_ipv6,
            }
            check_hosts.append(check_host)

        result = client.node_install_check(hosts=check_hosts, node_role=node_role)

        if result.get("code") != 0:
            error_msg = result.get("message", "Unknown error")
            data.set_outputs("ex_data", _("[节点管理器]安装检查失败: %s") % error_msg)
            self.logger.error(f"Nodemgr API error: {error_msg}")
            return False

        checked_status = result["data"]["results"]
        if len(checked_status) != len(hosts):
            error_msg = _("节点数量不匹配")
            data.set_outputs("ex_data", _("节点检查失败: %s") % error_msg)
            self.logger.error(f"Nodemgr API error: {error_msg}")
            return False

        # 构造 install 请求
        install_hosts = []
        for i in range(len(checked_status)):
            if checked_status[i].get("status") == "error":
                continue

            host = hosts[i]
            matched_host = checked_status[i].get("matched")

            inner_ip = split_ip_list(host.get("bk_host_innerip", ""))
            inner_ipv6 = split_ip_list(host.get("bk_host_innerip_v6", ""))
            single_inner_ip = inner_ip[0] if inner_ip else inner_ipv6[0] if inner_ipv6 else None
            login_ip = split_ip_list(host.get("login_ip"))

            install_host = {
                "bk_addressing": host.get("bk_addressing", "static"),
                "bk_biz_id": biz_id,
                "bk_host_innerip": inner_ip,
                "bk_host_innerip_v6": inner_ipv6,
                "login_ip": login_ip[0] if login_ip else single_inner_ip,
                "login_port": int(host.get("login_port", 22)),
                "login_user": host.get("login_user", ""),
                "login_mode": host.get("login_mode", "password"),
                "bk_networkunit_id": host.get("bk_networkunit_id"),
                "os_type": host.get("os_type", "linux"),
                "bk_host_id": matched_host.get("bk_host_id", None) if matched_host else None,
                "install_pre_ordered_plugins": install_plugin,
                "re_register": host.get("re_register", False),
            }
            if host.get("login_mode") == "password":
                install_host["login_password"] = self.encrypt_credit(
                    username=username, auth_info=host.get("login_password"))
            elif host.get("login_mode") == "keyfile":
                install_host["login_key_file"] = self.encrypt_credit(
                    username=username, auth_info=host.get("login_password"))
            elif host.get("login_mode") == "password_vault":
                # 密码库(TJJ)模式: login_mode 透传 password_vault，凭据由 Nodemgr 侧从密码库读取，
                # 此处不携带 login_password / login_key_file（显式置空，避免上游用旧值）。
                install_host["login_password"] = ""
                install_host["login_key_file"] = ""

            # proxy 节点额外的参数内容
            if node_role == "proxy":
                install_host["relay_callback_port"] = self.proxy_info.get("relay_callback_port", 28302)
                install_host["relay_download_port"] = self.proxy_info.get("relay_download_port", 28303)
                install_host["proxy_tags"] = self.proxy_info.get("proxy_tags", [
                    "dedicated_installer", "cluster_tunnel", "file_tunnel", "data_tunnel"])

            install_hosts.append(install_host)

        if not install_hosts:
            data.set_outputs("ex_data", _("没有可安装的有效节点"))
            return False

        result = client.node_install(hosts=install_hosts, node_role=node_role)

        if result.get("code") != 0:
            error_msg = result.get("message", "Unknown error")
            data.set_outputs("ex_data", _("[节点管理器]操作失败: %s") % error_msg)
            self.logger.error(f"Nodemgr API error: {error_msg}")
            return False

        # 获取 workflow_id
        workflow_id = result.get("data", {}).get("workflow_id")
        if not workflow_id:
            data.set_outputs("ex_data", _("未获取到 workflow_id"))
            return False
        data.set_outputs("workflow_id", workflow_id)
        workflow_url = f"{self.web_url}/#/node-manager/history/detail/{workflow_id}"
        data.set_outputs("workflow_url", workflow_url)

        return True

    def do_upgrade(self, username, data):
        client = self.get_client(username=username)

        biz_id = data.inputs.nodemgr_biz_id
        operation_info = data.inputs.nodemgr_op_info
        force_restart = operation_info.get("nodemgr_force_restart", False)
        graceful_restart_timeout = int(operation_info.get("nodemgr_graceful_restart_timeout", 120))
        hosts = self.wrap_hosts(data)

        node_role = operation_info.get("nodemgr_node_role")
        if node_role not in ["agent", "proxy"]:
            raise Exception(f"Invalid nodemgr_node_role: {node_role}")

        # 获取 host 信息
        fetched_hosts_dict = self.fetch_hosts(biz_id=biz_id, hosts=hosts, username=username)

        # 构造 upgrade 请求
        upgrade_hosts = []
        for host in hosts:
            networkarea_id = int(host.get("bk_networkarea_id", -1))
            inner_ip = host.get("inner_ip")
            upgrade_version = host.get("upgrade_version")

            fetched_host = fetched_hosts_dict.get(networkarea_id, {}).get(inner_ip)
            if not fetched_host:
                continue

            info = fetched_host.get("info")
            upgrade_host = {
                "bk_host_id": fetched_host.get("bk_host_id", -1),
                "force": force_restart,
                "graceful_restart_timeout_sec": graceful_restart_timeout,
                "bk_networkunit_id": info.get("bk_networkunit_id", -1),
                "cpu_arch": info.get("cpu_arch", ""),
                "target_version": upgrade_version,
            }
            upgrade_hosts.append(upgrade_host)

        if not upgrade_hosts:
            data.set_outputs("ex_data", _("没有可升级的有效节点"))
            return False

        result = client.node_upgrade(hosts=upgrade_hosts, node_role=node_role)

        if result.get("code") != 0:
            error_msg = result.get("message", "Unknown error")
            data.set_outputs("ex_data", _("[节点管理器]操作失败: %s") % error_msg)
            self.logger.error(f"Nodemgr API error: {error_msg}")
            return False

        # 获取 workflow_id
        workflow_id = result.get("data", {}).get("workflow_id")
        if not workflow_id:
            data.set_outputs("ex_data", _("未获取到 workflow_id"))
            return False
        data.set_outputs("workflow_id", workflow_id)
        workflow_url = f"{self.web_url}/#/node-manager/history/detail/{workflow_id}"
        data.set_outputs("workflow_url", workflow_url)

        return True

    def do_restart(self, username, data):
        client = self.get_client(username=username)

        biz_id = data.inputs.nodemgr_biz_id
        operation_info = data.inputs.nodemgr_op_info
        force_restart = operation_info.get("nodemgr_force_restart", False)
        graceful_restart_timeout = int(operation_info.get("nodemgr_graceful_restart_timeout", 120))
        reconfig = operation_info.get("nodemgr_reload_config", False)
        hosts = self.wrap_hosts(data)

        node_role = operation_info.get("nodemgr_node_role")
        if node_role not in ["agent", "proxy"]:
            raise Exception(f"Invalid nodemgr_node_role: {node_role}")

        # 获取 host 信息
        fetched_hosts_dict = self.fetch_hosts(biz_id=biz_id, hosts=hosts, username=username)

        # 构造 restart 请求
        restart_hosts = []
        for host in hosts:
            networkarea_id = int(host.get("bk_networkarea_id", -1))
            inner_ip = host.get("inner_ip")

            fetched_host = fetched_hosts_dict.get(networkarea_id, {}).get(inner_ip)
            if not fetched_host:
                continue

            restart_host = {
                "bk_host_id": fetched_host.get("bk_host_id", -1),
                "force": force_restart,
                "graceful_restart_timeout_sec": graceful_restart_timeout,
            }
            restart_hosts.append(restart_host)

        if not restart_hosts:
            data.set_outputs("ex_data", _("没有可重启的有效节点"))
            return False

        if reconfig:
            result = client.node_reconfig(hosts=restart_hosts, node_role=node_role)
        else:
            result = client.node_restart(hosts=restart_hosts, node_role=node_role)

        if result.get("code") != 0:
            error_msg = result.get("message", "Unknown error")
            data.set_outputs("ex_data", _("[节点管理器]操作失败: %s") % error_msg)
            self.logger.error(f"Nodemgr API error: {error_msg}")
            return False

        # 获取 workflow_id
        workflow_id = result.get("data", {}).get("workflow_id")
        if not workflow_id:
            data.set_outputs("ex_data", _("未获取到 workflow_id"))
            return False
        data.set_outputs("workflow_id", workflow_id)
        workflow_url = f"{self.web_url}/#/node-manager/history/detail/{workflow_id}"
        data.set_outputs("workflow_url", workflow_url)

        return True

    def do_uninstall(self, username, data):
        client = self.get_client(username=username)

        biz_id = data.inputs.nodemgr_biz_id
        operation_info = data.inputs.nodemgr_op_info
        hosts = self.wrap_hosts(data)

        node_role = operation_info.get("nodemgr_node_role")
        if node_role not in ["agent", "proxy"]:
            raise Exception(f"Invalid nodemgr_node_role: {node_role}")

        # 获取 host 信息
        fetched_hosts_dict = self.fetch_hosts(biz_id=biz_id, hosts=hosts, username=username)

        # 构造 uninstall 请求
        uninstall_hosts = []
        for host in hosts:
            networkarea_id = int(host.get("bk_networkarea_id", -1))
            inner_ip = host.get("inner_ip")

            fetched_host = fetched_hosts_dict.get(networkarea_id, {}).get(inner_ip)
            if not fetched_host:
                continue

            uninstall_host = {
                "bk_host_id": fetched_host.get("bk_host_id", -1),
            }
            uninstall_hosts.append(uninstall_host)

        if not uninstall_hosts:
            data.set_outputs("ex_data", _("没有可卸载的有效节点"))
            return False

        result = client.node_uninstall(hosts=uninstall_hosts, node_role=node_role)
        if result.get("code") != 0:
            error_msg = result.get("message", "Unknown error")
            data.set_outputs("ex_data", _("[节点管理器]操作失败: %s") % error_msg)
            self.logger.error(f"Nodemgr API error: {error_msg}")
            return False

        # 获取 workflow_id
        workflow_id = result.get("data", {}).get("workflow_id")
        if not workflow_id:
            data.set_outputs("ex_data", _("未获取到 workflow_id"))
            return False
        data.set_outputs("workflow_id", workflow_id)
        workflow_url = f"{self.web_url}/#/node-manager/history/detail/{workflow_id}"
        data.set_outputs("workflow_url", workflow_url)

        return True

    def plugin_execute(self, data, parent_data):
        executor = parent_data.inputs.executor

        operation_info = data.inputs.nodemgr_op_info
        operation_type = operation_info.get("nodemgr_operation_type", "")

        try:
            # 根据操作类型调用不同的 API
            if operation_type == "install":
                if not self.do_install(username=executor, data=data):
                    return False

            elif operation_type == "upgrade":
                if not self.do_upgrade(username=executor, data=data):
                    return False

            elif operation_type == "restart":
                if not self.do_restart(username=executor, data=data):
                    return False

            elif operation_type == "uninstall":
                if not self.do_uninstall(username=executor, data=data):
                    return False

            else:
                data.set_outputs("ex_data", _("不支持的操作类型: %s") % operation_type)
                return False

            self.logger.info(
                f"Nodemgr {operation_type} operation created"
            )

            return True

        except Exception as e:
            message = _("[节点管理器]操作异常: %s") % str(e)
            data.set_outputs("ex_data", message)
            self.logger.exception(message)
            return False

    def plugin_schedule(self, data, parent_data, callback_data=None):
        executor = parent_data.inputs.executor
        workflow_id = data.get_one_of_outputs("workflow_id")

        if not workflow_id:
            self.finish_schedule()
            return True

        client = self.get_client(username=executor)

        # 检查 workflow 执行结果
        is_finished, is_success, success_count, failed_count, error_message = (
            self.check_workflow_result(client, workflow_id, is_plugin=False)
        )

        if not is_finished:
            # 继续轮询
            return True

        # 设置输出
        data.set_outputs("success_count", success_count)
        data.set_outputs("failed_count", failed_count)

        if not is_success:
            data.set_outputs("ex_data", _("Workflow 执行失败: %s") % error_message)
            self.logger.error(f"Workflow {workflow_id} failed: {error_message}")
            self.finish_schedule()
            return False

        self.logger.info(f"Workflow {workflow_id} completed successfully")
        self.finish_schedule()
        return True


class NodemgrOperateNodeComponent(Component):
    name = _("节点操作")
    code = "nodemgr_operate_node"
    bound_service = NodemgrOperateNodeService
    form = "%scomponents/atoms/nodemgr/operate_node/v1_0.js" % settings.STATIC_URL
    version = "v1.0"
    desc = _("节点管理器节点操作（安装/升级/重启/重配/卸载）")
