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

from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component

from api.collections.nodeman import BKNodeManClient
from gcloud.conf import settings
from gcloud.utils import crypto
from gcloud.utils.cmdb import get_business_host, get_business_host_ipv6
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.nodeman.base import NodeManNewBaseService

__group_name__ = _("节点管理(Nodeman)")

from pipeline_plugins.components.utils import parse_passwd_value

VERSION = "v4.0"

# 无需认证信息的操作
NOT_NEED_AUTH_JOB = ["RELOAD_AGENT", "RELOAD_PROXY"]


# 无需额外配置信息的操作
NOT_NEED_EXTRA_CONFIG_JOB = ["UNINSTALL_AGENT"]

# 依赖节点管理 job/install 接口的操作
INSTALL_JOB = (
    ["INSTALL_PROXY", "INSTALL_AGENT", "REINSTALL_PROXY", "REINSTALL_AGENT"]
    + NOT_NEED_EXTRA_CONFIG_JOB
    + NOT_NEED_AUTH_JOB
)

# 依赖节点管理 job/details 接口的操作
OPERATE_JOB = ["UPGRADE_AGENT", "UPGRADE_PROXY", "UNINSTALL_PROXY", "RESTART_AGENT", "RESTART_PROXY"]

# 主机其它参数
HOST_EXTRA_PARAMS = ["outer_ip", "login_ip", "data_ip", "inner_ipv6", "outer_ipv6"]

# 主机其他参数——IPV6
HOST_EXTRA_PARAMS_IPV6 = ["inner_ipv6", "outer_ipv6"]


class NodemanCreateTaskService(NodeManNewBaseService):
    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        client = BKNodeManClient(username=executor)
        bk_biz_id = data.inputs.bk_biz_id

        nodeman_op_info = data.inputs.nodeman_op_info
        node_type = nodeman_op_info.get("nodeman_node_type")
        op_type = nodeman_op_info.get("nodeman_op_type", "")
        nodeman_hosts = nodeman_op_info.get("nodeman_hosts", [])
        nodeman_other_hosts = nodeman_op_info.get("nodeman_other_hosts", [])
        nodeman_install_latest_plugins = nodeman_op_info.get("nodeman_install_latest_plugins", True)
        data.set_outputs("job_id", "")

        # 拼接任务类型
        job_name = "_".join([op_type, node_type])
        if job_name in OPERATE_JOB:
            # 获取bk_host_id
            bk_host_ids = []
            for host in nodeman_other_hosts:
                bk_cloud_id = host["nodeman_bk_cloud_id"]
                ip_str = host["nodeman_ip_str"]
                bk_host_ids.extend(self.get_host_id_list(ip_str, executor, bk_cloud_id, bk_biz_id))
            # 操作类任务（升级、卸载等）
            kwargs = {
                "job_type": job_name,
                "bk_biz_id": [bk_biz_id],
                "bk_host_id": bk_host_ids,
                "action": "job_operate",
            }
        # 安装类任务
        elif job_name in INSTALL_JOB:
            # 安装主机信息
            all_hosts, row_host_params_list = [], []
            for host in nodeman_hosts:
                bk_cloud_id = host["nodeman_bk_cloud_id"]
                install_channel_id = host.get("nodeman_bk_install_channel")
                bk_addressing = host.get("bk_addressing")
                use_inner_ip = True if host.get("inner_ip") else False
                # use_inner_ip 判定用户输入的的是ipv4还是ipv6
                inner_ip_list = self.get_ip_list(
                    host.get("inner_ipv6", "")
                    if not use_inner_ip and settings.ENABLE_IPV6
                    else host.get("inner_ip", "")
                )
                # 再不开启ipv6的条件下需要校验内网ip
                if not inner_ip_list:
                    data.set_outputs("ex_data", _("请确认内网Ip是否合法host_info:{host}".format(host=host["inner_ip"])))
                    return False

                auth_params = {}
                if job_name not in NOT_NEED_AUTH_JOB:

                    # 认证信息
                    auth_params.update(
                        {"port": host["port"], "auth_type": host["auth_type"], "account": host["account"]}
                    )

                    # 处理表格中每行的key/psw
                    auth_key: str = crypto.decrypt(parse_passwd_value(host["auth_key"]))
                    try:
                        auth_key: str = self.parse2nodeman_ciphertext(data, executor, auth_key)
                    except ValueError:
                        return False

                    if auth_params["auth_type"] == "PASSWORD":
                        auth_params["password"] = auth_key
                    else:
                        auth_params["key"] = auth_key

                # 额外配置参数
                extra_config_params = {
                    "peer_exchange_switch_for_agent": host.get("peer_exchange_switch_for_agent", 0),
                    "force_update_agent_id": host.get("force_update_agent_id", False),
                }
                speed_limit = host.get("speed_limit")
                if speed_limit:
                    extra_config_params.update({"bt_speed_limit": int(speed_limit)})

                # 表格每行基础参数
                base_params = {
                    **auth_params,
                    "bk_biz_id": bk_biz_id,
                    "bk_cloud_id": bk_cloud_id,
                    "ap_id": host["nodeman_ap_id"],
                    "os_type": host["os_type"],
                    "is_manual": False,
                }
                if install_channel_id and install_channel_id != -1:
                    base_params["install_channel_id"] = install_channel_id
                # v7.0增加字段 寻址方式bk_addressing
                if bk_addressing:
                    base_params["bk_addressing"] = bk_addressing
                # 支持表格中一行多ip操作, 拼装表格内的inner_ip参数
                for index, inner_ip in enumerate(inner_ip_list):

                    row_host_info = deepcopy(base_params)
                    if use_inner_ip:
                        row_host_info.update({"inner_ip": inner_ip})

                    # 注入额外 Agent 配置信息
                    if job_name not in NOT_NEED_EXTRA_CONFIG_JOB:
                        row_host_info.update(extra_config_params)

                    # 除了安装，其他操作需要 bk_host_id
                    if (
                        job_name
                        in ["REINSTALL_PROXY", "REINSTALL_AGENT"] + NOT_NEED_AUTH_JOB + NOT_NEED_EXTRA_CONFIG_JOB
                    ):
                        supplier_account = supplier_account_for_business(bk_biz_id)
                        host_fields = ["bk_host_id", "bk_host_innerip"]
                        # 如果开启了ipv6，并且用户输入的是ipv6的地址
                        if settings.ENABLE_IPV6 and not use_inner_ip:
                            host_fields.append("bk_host_innerip_v6")
                            host_list = get_business_host_ipv6(
                                executor, bk_biz_id, supplier_account, host_fields, inner_ip_list, bk_cloud_id
                            )
                            bk_host_id_dict = {host["bk_host_innerip_v6"]: host["bk_host_id"] for host in host_list}
                        else:
                            host_list = get_business_host(
                                executor, bk_biz_id, supplier_account, host_fields, inner_ip_list, bk_cloud_id
                            )
                            bk_host_id_dict = {host["bk_host_innerip"]: host["bk_host_id"] for host in host_list}
                        try:
                            row_host_info["bk_host_id"] = bk_host_id_dict[inner_ip]
                        except KeyError:
                            data.set_outputs("ex_data", _("获取bk_host_id失败:{},请确认管控区域是否正确".format(inner_ip)))
                            return False

                    # 组装其它可选参数, ip数量需要与inner_ip一一对应
                    for ip_type in HOST_EXTRA_PARAMS:
                        # 没有开启ipv6的情况下不对ipv6的字段做处理
                        if not settings.ENABLE_IPV6 and ip_type in HOST_EXTRA_PARAMS_IPV6:
                            continue
                        if host.get(ip_type, False):
                            others_ip_list = self.get_ip_list(host[ip_type])
                            if len(others_ip_list) == len(inner_ip_list):
                                row_host_info[ip_type] = others_ip_list[index]
                            else:
                                data.set_outputs("ex_data", _("获取{}的{}失败,请确认是否与inner_ip一一对应".format(inner_ip, ip_type)))
                                return False

                    row_host_params_list.append(row_host_info)

            all_hosts.extend(row_host_params_list)

            kwargs = {"job_type": job_name, "hosts": all_hosts, "action": "job_install"}

            if job_name in ["INSTALL_PROXY", "INSTALL_AGENT", "REINSTALL_PROXY", "REINSTALL_AGENT"]:
                kwargs.update({"is_install_latest_plugins": nodeman_install_latest_plugins})

        else:
            data.set_outputs("ex_data", _("无效的操作请求:{}".format(job_name)))
            return False

        action = kwargs.pop("action")
        result = getattr(client, action)(**kwargs)

        return self.get_job_result(result, data, action, kwargs)


class NodemanCreateTaskComponent(Component):
    name = _("新建任务")
    code = "nodeman_create_task"
    bound_service = NodemanCreateTaskService
    form = "%scomponents/atoms/nodeman/create_task/v4_0.js" % settings.STATIC_URL
    version = VERSION
    desc = _("v4.0版本 安装/重装操作新增表单项是否安装最新版本插件   \n" "卸载AGENT操作参数和重装AGENT保持一致 \n" "移除操作下线")
