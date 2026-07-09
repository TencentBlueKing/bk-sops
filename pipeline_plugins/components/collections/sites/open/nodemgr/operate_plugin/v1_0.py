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

from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component

import env
from gcloud.conf import settings

from ..base import NodemgrBaseService, split_ip_list

__group_name__ = _("节点管理V3(Nodemgr)")

logger = logging.getLogger("root")


class NodemgrOperatePluginService(NodemgrBaseService):
    def __init__(self, *args, **kwargs):
        super(NodemgrOperatePluginService, self).__init__(*args, **kwargs)

        self.web_url = env.BK_NODEMGR_WEB_URL

    def wrap_hosts(self, data):
        operation_info = data.inputs.nodemgr_op_info
        operation_type = operation_info.get("nodemgr_operation_type", "")

        if operation_type == "install":
            hosts = []
            batch = operation_info.get("nodemgr_batch_install")
            networkarea_id = batch.get("bk_networkarea_id")

            for ip in split_ip_list(batch.get("inner_ip")):
                host = {
                    "inner_ip": ip,
                    "bk_networkarea_id": networkarea_id,
                }
                hosts.append(host)
            return hosts

        elif operation_type == "uninstall":
            hosts = []
            batch = operation_info.get("nodemgr_batch_uninstall")
            networkarea_id = batch.get("bk_networkarea_id")
            for ip in split_ip_list(batch.get("inner_ip")):
                host = {
                    "inner_ip": ip,
                    "bk_networkarea_id": networkarea_id,
                }
                hosts.append(host)
            return hosts

        else:
            raise Exception(f"Invalid nodemgr_operation_type: {operation_type}")

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
        batch = operation_info.get("nodemgr_batch_install")
        hosts = self.wrap_hosts(data)

        # 获取 host 信息
        fetched_hosts_dict = self.fetch_hosts(biz_id=biz_id, hosts=hosts, username=username)

        # 构造 install 参数
        install_plugins = []
        for host in hosts:
            networkarea_id = int(host.get("bk_networkarea_id", -1))
            inner_ip = host.get("inner_ip")

            fetched_host = fetched_hosts_dict.get(networkarea_id, {}).get(inner_ip)
            if not fetched_host:
                continue

            install_plugins.append(
                {
                    "bk_host_id": fetched_host["bk_host_id"],
                    "plugin_name": batch.get("plugin_name"),
                    "version": batch.get("plugin_version"),
                }
            )

        if not install_plugins:
            data.set_outputs("ex_data", _("没有可安装插件的有效节点"))
            return False

        result = client.plugin_install(plugins=install_plugins)

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
        workflow_url = f"{self.web_url}/#/node-manager/history/detail/{workflow_id}?active=plugin"
        data.set_outputs("workflow_url", workflow_url)

        return True

    def do_uninstall(self, username, data):
        client = self.get_client(username=username)

        biz_id = data.inputs.nodemgr_biz_id
        operation_info = data.inputs.nodemgr_op_info
        batch = operation_info.get("nodemgr_batch_uninstall")
        hosts = self.wrap_hosts(data)

        # 获取 host 信息
        fetched_hosts_dict = self.fetch_hosts(biz_id=biz_id, hosts=hosts, username=username)

        # 构造 uninstall 参数
        uninstall_plugins = []
        for host in hosts:
            networkarea_id = int(host.get("bk_networkarea_id", -1))
            inner_ip = host.get("inner_ip")

            fetched_host = fetched_hosts_dict.get(networkarea_id, {}).get(inner_ip)
            if not fetched_host:
                continue

            uninstall_plugins.append(
                {
                    "bk_host_id": fetched_host["bk_host_id"],
                    "plugin_name": batch.get("plugin_name"),
                }
            )

        if not uninstall_plugins:
            data.set_outputs("ex_data", _("没有可卸载插件的有效节点"))
            return False

        result = client.plugin_uninstall(plugins=uninstall_plugins)

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
        workflow_url = f"{self.web_url}/#/node-manager/history/detail/{workflow_id}?active=plugin"
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

            elif operation_type == "uninstall":
                if not self.do_uninstall(username=executor, data=data):
                    return False

            else:
                data.set_outputs("ex_data", _("不支持的操作类型: %s") % operation_type)
                return False

            self.logger.info(f"Nodemgr {operation_type} operation created")

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
        is_finished, is_success, success_count, failed_count, error_message = self.check_workflow_result(
            client, workflow_id, is_plugin=True
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


if env.BK_NODEMGR_ENABLE:

    class NodemgrOperatePluginComponent(Component):
        name = _("插件操作")
        code = "nodemgr_operate_plugin"
        bound_service = NodemgrOperatePluginService
        form = "%scomponents/atoms/nodemgr/operate_plugin/v1_0.js" % settings.STATIC_URL
        version = "v1.0"
        desc = _("节点管理器插件操作（安装/升级/卸载/应用配置）")
