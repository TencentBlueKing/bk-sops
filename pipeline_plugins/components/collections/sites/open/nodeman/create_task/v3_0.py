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
import itertools

from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import ArrayItemSchema, IntItemSchema, ObjectItemSchema, StringItemSchema

from api.collections.nodeman import BKNodeManClient
from gcloud.conf import settings
from gcloud.utils.crypto import decrypt_auth_key, encrypt_auth_key
from pipeline_plugins.components.collections.sites.open.nodeman.base import (
    NodeManBaseService,
    get_host_id_by_inner_ip,
    get_host_id_by_inner_ipv6,
    get_nodeman_rsa_public_key,
)

__group_name__ = _("节点管理(Nodeman)")
VERSION = "v3.0"

# 安装类任务(job_install)
INSTALL_JOB = ["INSTALL_PROXY", "INSTALL_AGENT", "REINSTALL_PROXY", "REINSTALL_AGENT"]

# 操作类任务(job_operate)
OPERATE_JOB = ["UPGRADE_PROXY", "UPGRADE_AGENT", "UNINSTALL_AGENT", "UNINSTALL_PROXY"]

# 移除(remove_host)
REMOVE_JOB = ["REMOVE_AGENT", "REMOVE_PROXY"]

# 主机其它参数
HOST_EXTRA_PARAMS = ["outer_ip", "login_ip", "data_ip", "inner_ipv6", "outer_ipv6"]

# 主机其他参数——IPV6
HOST_EXTRA_PARAMS_IPV6 = ["inner_ipv6", "outer_ipv6"]


class NodemanCreateTaskService(NodeManBaseService):
    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        client = BKNodeManClient(username=executor)
        bk_biz_id = data.inputs.bk_biz_id

        node_type = data.inputs.nodeman_node_type

        nodeman_ticket = data.get_one_of_inputs("nodeman_ticket", {})
        nodeman_tjj_ticket = nodeman_ticket.get("nodeman_tjj_ticket", "")
        if nodeman_tjj_ticket:
            try:
                nodeman_tjj_ticket = decrypt_auth_key(nodeman_tjj_ticket, settings.RSA_PRIV_KEY)
            except Exception:
                # password is not encrypted
                pass

        nodeman_op_info = data.inputs.nodeman_op_info
        op_type = nodeman_op_info.get("nodeman_op_type", "")
        nodeman_hosts = nodeman_op_info.get("nodeman_hosts", [])
        nodeman_other_hosts = nodeman_op_info.get("nodeman_other_hosts", [])

        data.set_outputs("job_id", "")

        # 拼接任务类型
        job_name = "_".join([op_type, node_type])
        if job_name in itertools.chain.from_iterable([OPERATE_JOB, REMOVE_JOB]):

            # 获取bk_host_id
            bk_host_ids = []
            for host in nodeman_other_hosts:
                bk_cloud_id = host["nodeman_bk_cloud_id"]
                ip_str = host["nodeman_ip_str"]
                bk_host_ids.extend(self.get_host_id_list(ip_str, executor, bk_cloud_id, bk_biz_id))
            # 操作类任务（升级、卸载等）
            if job_name in OPERATE_JOB:
                kwargs = {
                    "job_type": job_name,
                    "bk_biz_id": [bk_biz_id],
                    "bk_host_id": bk_host_ids,
                    "action": "job_operate",
                }

            # 移除主机
            elif job_name in REMOVE_JOB:
                kwargs = {
                    "bk_biz_id": [bk_biz_id],
                    "bk_host_id": bk_host_ids,
                    "is_proxy": True if "PROXY" in job_name else False,  # 是否移除PROXY
                    "action": "remove_host",
                }
            else:
                return False

        # 安装类任务
        elif job_name in INSTALL_JOB:

            # 安装主机信息
            all_hosts, row_host_params_list = [], []
            for host in nodeman_hosts:
                bk_cloud_id = host["nodeman_bk_cloud_id"]
                ap_id = host["nodeman_ap_id"]
                auth_type = host["auth_type"]
                auth_key = host["auth_key"]
                use_inner_ip = True if host.get("inner_ip") else False
                # use_inner_ip 判定用户输入的的是ipv4还是ipv6
                inner_ip_list = self.get_ip_list(
                    host.get("inner_ipv6", "")
                    if not use_inner_ip and settings.ENABLE_IPV6
                    else host.get("inner_ip", "")
                )

                if not inner_ip_list:
                    data.set_outputs("ex_data", _("请确认内网Ip是否合法host_info:{host}".format(host=host["inner_ip"])))
                    return False

                # 处理表格中每行的key/psw
                try:
                    auth_key = decrypt_auth_key(auth_key, settings.RSA_PRIV_KEY)
                except Exception:
                    # password is not encrypted
                    pass
                # auth_key加密
                success, ras_public_key = get_nodeman_rsa_public_key(executor, self.logger)
                if not success:
                    data.set_outputs("ex_data", _("获取节点管理公钥失败,请查看节点日志获取错误详情."))
                    return False
                auth_key = encrypt_auth_key(auth_key, ras_public_key["name"], ras_public_key["content"])
                # 表格每行基础参数
                base_params = {
                    "bk_biz_id": bk_biz_id,
                    "bk_cloud_id": bk_cloud_id,
                    "os_type": host["os_type"],
                    "port": host["port"],
                    "account": host["account"],
                    "auth_type": auth_type,
                    "ap_id": ap_id,
                    "is_manual": False,  # 不手动操作
                    "peer_exchange_switch_for_agent": 0,  # 不加速
                }

                # 支持表格中一行多ip操作, 拼装表格内的inner_ip参数
                for index, inner_ip in enumerate(inner_ip_list):
                    one = {}
                    if use_inner_ip:
                        one = {"inner_ip": inner_ip}
                    if auth_type == "PASSWORD":
                        one["password"] = auth_key
                    else:
                        one["key"] = auth_key

                    # 重装必须要bk_host_id
                    if job_name in ["REINSTALL_PROXY", "REINSTALL_AGENT"]:
                        if settings.ENABLE_IPV6 and not use_inner_ip:
                            bk_host_id_dict = get_host_id_by_inner_ipv6(
                                executor, self.logger, bk_cloud_id, bk_biz_id, inner_ip_list
                            )
                        else:
                            bk_host_id_dict = get_host_id_by_inner_ip(
                                executor, self.logger, bk_cloud_id, bk_biz_id, inner_ip_list
                            )
                        try:
                            one["bk_host_id"] = bk_host_id_dict[inner_ip]
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
                                one[ip_type] = others_ip_list[index]
                            else:
                                data.set_outputs("ex_data", _("获取{}的{}失败,请确认是否与inner_ip一一对应".format(inner_ip, ip_type)))
                                return False
                    one.update(base_params)
                    row_host_params_list.append(one)
            all_hosts.extend(row_host_params_list)

            kwargs = {"job_type": job_name, "hosts": all_hosts, "action": "job_install"}

            if nodeman_tjj_ticket:
                kwargs.update({"tcoa_ticket": nodeman_tjj_ticket})
        else:
            data.set_outputs("ex_data", _("无效的操作请求:{}".format(job_name)))
            return False

        action = kwargs.pop("action")
        result = getattr(client, action)(**kwargs)

        return self.get_job_result(result, data, action, kwargs)

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"), key="bk_biz_id", type="int", schema=IntItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("节点类型"),
                key="nodeman_node_type",
                type="string",
                schema=StringItemSchema(description=_("AGENT（表示直连区域安装 Agent）、 PROXY（表示安装 Proxy）")),
            ),
            self.InputItem(
                name=_("操作详情"),
                key="nodeman_op_info",
                type="object",
                schema=ObjectItemSchema(
                    description=_("操作内容信息"),
                    property_schemas={
                        "nodeman_ap_id": StringItemSchema(description=_("接入点 ID")),
                        "nodeman_op_type": StringItemSchema(
                            description=_(
                                "任务操作类型，可以是 INSTALL（安装）、  REINSTALL（重装）、" " UNINSTALL （卸载）、 REMOVE （移除）或 UPGRADE （升级）"
                            )
                        ),
                        "nodeman_hosts": ArrayItemSchema(
                            description=_("需要被操作的主机信息(安装与重装时需要)"),
                            item_schema=ObjectItemSchema(
                                description=_("主机相关信息"),
                                property_schemas={
                                    "nodeman_bk_cloud_id": StringItemSchema(description=_("管控区域ID")),
                                    "nodeman_ap_id": StringItemSchema(description=_("接入点")),
                                    "inner_ip": StringItemSchema(description=_("内网 IP")),
                                    "login_ip": StringItemSchema(description=_("主机登录 IP，可以为空，适配复杂网络时填写")),
                                    "data_ip": StringItemSchema(description=_("主机数据 IP，可以为空，适配复杂网络时填写")),
                                    "outer_ip": StringItemSchema(description=_("外网 IP, 可以为空")),
                                    "os_type": StringItemSchema(description=_("操作系统类型，可以是 LINUX, WINDOWS, 或 AIX")),
                                    "port": StringItemSchema(description=_("端口号")),
                                    "account": StringItemSchema(description=_("登录帐号")),
                                    "auth_type": StringItemSchema(description=_("认证方式，可以是 PASSWORD 或 KEY")),
                                    "auth_key": StringItemSchema(description=_("认证密钥,根据认证方式，是登录密码或者登陆密钥")),
                                },
                            ),
                        ),
                        "nodeman_other_hosts": ArrayItemSchema(
                            description=_("需要被操作的主机信息(升级，卸载，移除时需要)"),
                            item_schema=ObjectItemSchema(
                                description=_("主机相关信息"),
                                property_schemas={
                                    "nodeman_bk_cloud_id": StringItemSchema(description=_("管控区域ID")),
                                    "nodeman_ip_str": StringItemSchema(description=_("IP")),
                                },
                            ),
                        ),
                    },
                ),
            ),
        ]


class NodemanCreateTaskComponent(Component):
    name = _("新建任务")
    code = "nodeman_create_task"
    bound_service = NodemanCreateTaskService
    form = "%scomponents/atoms/nodeman/create_task/v3_0.js" % settings.STATIC_URL
    version = VERSION
    desc = _("v3.0版本支持多管控区域主机新建任务 \n" "注意：节点类型PROXY仅支持非直连区域")
