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

import base64

import rsa
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component
from pipeline_plugins.components.utils import get_ip_by_regex
from pipeline.utils.crypt import rsa_decrypt_password
from pipeline.core.flow.io import (
    IntItemSchema,
    StringItemSchema,
    ArrayItemSchema,
    ObjectItemSchema,
)

from gcloud.conf import settings

__group_name__ = _("节点管理(Nodeman)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDYvKQ/dAh499dXGDoQ2NWgwlev
GWq03EqlvJt+RSaYD1STStM6vEvsPiQ0Nc1GqxvZfqyS6v6acIbhCa1qgYKM8IGk
OVjmORwDUqVR807uCE+GXlf98PSxBbdAPp5e5dTLKd/ZSD6C70lUrMoa8mOktUp/
NnapTCnlIg0YdZjLVwIDAQAB
-----END PUBLIC KEY-----"""


def nodeman_rsa_encrypt(message):
    """
    RSA加密
    """
    message = message if isinstance(message, bytes) else message.encode("utf-8")
    return base64.b64encode(
        rsa.encrypt(message, rsa.PublicKey.load_pkcs1_openssl_pem(PUBLIC_KEY))
    )


class NodemanCreateTaskService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        client = get_client_by_user(executor)

        bk_biz_id = data.inputs.biz_cc_id
        bk_cloud_id = data.inputs.nodeman_bk_cloud_id
        node_type = data.inputs.nodeman_node_type
        op_type = data.inputs.nodeman_op_type
        nodeman_hosts = data.inputs.nodeman_hosts

        hosts = []

        for host in nodeman_hosts:
            conn_ips = get_ip_by_regex(host["conn_ips"])
            if len(conn_ips) == 0:
                data.set_outputs("ex_data", _("conn_ips 为空或输入格式错误"))
                return False

            one = {
                "os_type": host["os_type"],
                "has_cygwin": host["has_cygwin"],
                "port": host["port"],
                "account": host["account"],
                "auth_type": host["auth_type"],
            }
            auth_type = host["auth_type"]
            auth_key = host["auth_key"]

            login_ip = get_ip_by_regex(host.get("login_ip", ""))
            data_ip = get_ip_by_regex(host.get("data_ip", ""))
            cascade_ip = get_ip_by_regex(host.get("cascade_ip", ""))

            if len(login_ip):
                one.update({"login_ip": login_ip[0]})
            if len(data_ip):
                one.update({"data_ip": data_ip[0]})
            if len(cascade_ip):
                one.update({"cascade_ip": cascade_ip[0]})

            # 处理key/psw
            try:
                auth_key = rsa_decrypt_password(auth_key, settings.RSA_PRIV_KEY)
            except Exception:
                # password is not encrypted
                pass
            auth_key = nodeman_rsa_encrypt(auth_key).decode("utf-8")

            one.update({auth_type.lower(): auth_key})

            for conn_ip in conn_ips:
                dict_temp = {"conn_ips": conn_ip}
                dict_temp.update(one)
                hosts.append(dict_temp)

        agent_kwargs = {
            "bk_biz_id": bk_biz_id,
            "bk_cloud_id": bk_cloud_id,
            "node_type": node_type,
            "op_type": op_type,
            "creator": executor,
            "hosts": hosts,
        }

        agent_result = client.nodeman.create_task(agent_kwargs)
        self.logger.info(
            "nodeman created task result: {result}, api_kwargs: {kwargs}".format(
                result=agent_result, kwargs=agent_kwargs
            )
        )
        if agent_result["result"]:
            data.set_outputs("job_id", agent_result["data"]["id"])
            return True
        else:
            message = "create agent install task failed: %s" % agent_result["message"]
            data.set_outputs("ex_data", message)
            return False

    def schedule(self, data, parent_data, callback_data=None):
        bk_biz_id = data.inputs.biz_cc_id
        executor = parent_data.inputs.executor
        client = get_client_by_user(executor)

        job_id = data.get_one_of_outputs("job_id")

        job_kwargs = {"bk_biz_id": bk_biz_id, "job_id": job_id}
        job_result = client.nodeman.get_task_info(job_kwargs)

        self.logger.info(
            "nodeman get task info result: {result}, api_kwargs: {kwargs}".format(
                result=job_result, kwargs=job_kwargs
            )
        )

        # 任务执行失败
        if not job_result["result"]:
            self.logger.error(
                "nodeman get task info result: {result}, api_kwargs: {kwargs}".format(
                    result=job_result, kwargs=job_kwargs
                )
            )
            data.set_outputs("ex_data", _("查询失败，未能获得任务执行结果"))
            self.finish_schedule()
            return False

        result_data = job_result["data"]
        host_count = result_data["host_count"]
        success_num = result_data["status_count"]["success_count"]
        fail_num = result_data["status_count"]["failed_count"]
        fail_infos = []

        for host in result_data["hosts"]:
            # 安装失败
            if host["status"] == "FAILED":
                fail_infos.append(
                    {
                        "host_id": host["host"]["id"],
                        "inner_ip": host["host"]["inner_ip"],
                    }
                )

        if success_num + fail_num == host_count:
            data.set_outputs("success_num", success_num)
            data.set_outputs("fail_num", fail_num)
            if success_num == host_count:
                self.finish_schedule()
                return True
            else:
                error_log = "<br>%s</br>" % _("日志信息为：")
                for fail_info in fail_infos:
                    log_kwargs = {
                        "host_id": fail_info["host_id"],
                        "bk_biz_id": bk_biz_id,
                    }
                    result = client.nodeman.get_log(log_kwargs)
                    log_info = result["data"]["logs"]
                    error_log = "{error_log}<br><b>{host}{fail_host}</b></br><br>{log}</br>{log_info}".format(
                        error_log=error_log,
                        host=_("主机："),
                        fail_host=fail_info["inner_ip"],
                        log=_("日志："),
                        log_info=log_info,
                    )

                data.set_outputs("ex_data", error_log)
                self.finish_schedule()
                return False

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("任务 ID"),
                key="job_id",
                type="int",
                schema=IntItemSchema(description=_("提交的任务的 job_id")),
            ),
            self.OutputItem(
                name=_("安装成功个数"),
                key="success_num",
                type="int",
                schema=IntItemSchema(description=_("任务中安装成功的机器个数")),
            ),
            self.OutputItem(
                name=_("安装失败个数"),
                key="fail_num",
                type="int",
                schema=IntItemSchema(description=_("任务中安装失败的机器个数")),
            ),
        ]

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="biz_cc_id",
                type="int",
                schema=IntItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("云区域 ID"),
                key="nodeman_bk_cloud_id",
                type="string",
                schema=StringItemSchema(description=_("节点所在云区域 ID")),
            ),
            self.InputItem(
                name=_("节点类型"),
                key="nodeman_node_type",
                type="string",
                schema=StringItemSchema(
                    description=_(
                        "节点类型，可以是 AGENT（表示直连区域安装 Agent）、 "
                        "PROXY（表示安装 Proxy） 或 PAGENT（表示直连区域安装 Agent）"
                    )
                ),
            ),
            self.InputItem(
                name=_("操作类型"),
                key="nodeman_op_type",
                type="string",
                schema=StringItemSchema(
                    description=_(
                        "任务操作类型，可以是 INSTALL（安装）、  REINSTALL（重装）、"
                        " UNINSTALL （卸载）、 REMOVE （移除）或 UPGRADE （升级）"
                    )
                ),
            ),
            self.InputItem(
                name=_("主机"),
                key="nodeman_hosts",
                type="array",
                schema=ArrayItemSchema(
                    description=_("主机所在云区域 ID"),
                    item_schema=ObjectItemSchema(
                        description=_("主机相关信息"),
                        property_schemas={
                            "conn_ips": StringItemSchema(description=_("主机通信 IP")),
                            "login_ip": StringItemSchema(
                                description=_("主机登录 IP，可以为空，适配复杂网络时填写")
                            ),
                            "data_ip": StringItemSchema(
                                description=_("主机数据 IP，可以为空，适配复杂网络时填写")
                            ),
                            "cascade_ip": StringItemSchema(
                                description=_("级联 IP, 可以为空，安装 PROXY 时必填")
                            ),
                            "os_type": StringItemSchema(
                                description=_("操作系统类型，可以是 LINUX, WINDOWS, 或 AIX")
                            ),
                            "has_cygwin": StringItemSchema(
                                description=_(
                                    "是否安装了 cygwin，True：表示已安装，"
                                    "False：表示未安装, windows 操作系统时选填"
                                )
                            ),
                            "port": StringItemSchema(description=_("端口号")),
                            "account": StringItemSchema(description=_("登录帐号")),
                            "auth_type": StringItemSchema(
                                description=_("认证方式，可以是 PASSWORD 或 KEY")
                            ),
                            "auth_key": StringItemSchema(
                                description=_("认证密钥,根据认证方式，是登录密码或者登陆密钥")
                            ),
                        },
                    ),
                ),
            ),
        ]


class NodemanCreateTaskComponent(Component):
    name = _("新建任务")
    code = "nodeman_create_task"
    bound_service = NodemanCreateTaskService
    form = "%scomponents/atoms/sites/%s/nodeman/create_task/nodeman_create_task.js" % (
        settings.STATIC_URL,
        settings.RUN_VER,
    )
