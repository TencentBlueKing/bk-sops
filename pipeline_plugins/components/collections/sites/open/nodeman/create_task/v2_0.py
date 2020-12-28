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
import itertools
import ujson as json

from django.utils.translation import ugettext_lazy as _

from api.collections.nodeman import BKNodeManClient
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component
from pipeline.utils.crypt import rsa_decrypt_password

from pipeline.core.flow.io import (
    IntItemSchema,
    StringItemSchema,
    ArrayItemSchema,
    ObjectItemSchema,
)

from gcloud.conf import settings
from gcloud.utils.ip import get_ip_by_regex
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("节点管理(Nodeman)")
VERSION = "v2.0"

# 安装类任务(job_install)
INSTALL_JOB = ["INSTALL_PROXY", "INSTALL_AGENT", "REINSTALL_PROXY", "REINSTALL_AGENT"]

# 操作类任务(job_operate)
OPERATE_JOB = ["UPGRADE_PROXY", "UPGRADE_AGENT", "UNINSTALL_AGENT", "UNINSTALL_PROXY"]

# 移除(remove_host)
REMOVE_JOB = ["REMOVE_AGENT", "REMOVE_PROXY"]

# 主机其它参数
HOST_EXTRA_PARAMS = ["outer_ip", "login_ip", "data_ip"]


def get_host_id_by_inner_ip(client, logger, bk_cloud_id: int, bk_biz_id: int, ip_list: list):
    """
    根据inner_ip获取bk_host_id 对应关系dict
    """
    kwargs = {
        "bk_biz_id": [bk_biz_id],
        "pagesize": -1,
        "conditions": [{"key": "inner_ip", "value": ip_list}, {"key": "bk_cloud_id", "value": [bk_cloud_id]}],
    }
    result = client.search_host_plugin(**kwargs)

    if not result["result"]:
        error = handle_api_error(__group_name__, "nodeman.search_host_plugin", kwargs, result)
        logger.error(error)
        return {}

    return {host["inner_ip"]: host["bk_host_id"] for host in result["data"]["list"]}


class NodemanCreateTaskService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        client = BKNodeManClient(username=executor)
        bk_biz_id = data.inputs.bk_biz_id

        nodeman_op_target = data.inputs.nodeman_op_target
        bk_cloud_id = nodeman_op_target.get("nodeman_bk_cloud_id", "")
        node_type = nodeman_op_target.get("nodeman_node_type", "")

        nodeman_op_info = data.inputs.nodeman_op_info
        op_type = nodeman_op_info.get("nodeman_op_type", "")
        nodeman_hosts = nodeman_op_info.get("nodeman_hosts", [])
        ap_id = nodeman_op_info.get("nodeman_ap_id", "")
        ip_str = nodeman_op_info.get("nodeman_ip_str", "")

        data.set_outputs("job_id", "")

        # 拼接任务类型
        job_name = "_".join([op_type, node_type])

        if job_name in itertools.chain.from_iterable([OPERATE_JOB, REMOVE_JOB]):

            # 获取bk_host_id
            ip_list = get_ip_by_regex(ip_str)
            bk_host_id_dict = get_host_id_by_inner_ip(client, self.logger, bk_cloud_id, bk_biz_id, ip_list)
            bk_host_ids = [bk_host_id for bk_host_id in bk_host_id_dict.values()]
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
                auth_type = host["auth_type"]
                auth_key = host["auth_key"]
                inner_ip_list = get_ip_by_regex(host.get("inner_ip"))
                if not inner_ip_list:
                    data.set_outputs("ex_data", _("请确认内网Ip是否合法host_info:{host}".format(host=host["inner_ip"])))
                    return False

                # 处理表格中每行的key/psw
                try:
                    auth_key = rsa_decrypt_password(auth_key, settings.RSA_PRIV_KEY)
                except Exception:
                    # password is not encrypted
                    pass

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
                    one = {"inner_ip": inner_ip}
                    if auth_type == "PASSWORD":
                        one["password"] = auth_key
                    else:
                        one["key"] = auth_key

                    # 重装必须要bk_host_id
                    if job_name in ["REINSTALL_PROXY", "REINSTALL_AGENT"]:
                        bk_host_id_dict = get_host_id_by_inner_ip(
                            client, self.logger, bk_cloud_id, bk_biz_id, inner_ip_list
                        )
                        try:
                            one["bk_host_id"] = bk_host_id_dict[inner_ip]
                        except KeyError:
                            data.set_outputs("ex_data", _("获取bk_host_id失败:{},请确认云区域是否正确".format(inner_ip)))
                            return False

                    # 组装其它可选参数, ip数量需要与inner_ip一一对应
                    for ip_type in HOST_EXTRA_PARAMS:
                        if host.get(ip_type, False):
                            others_ip_list = get_ip_by_regex(host[ip_type])
                            if len(others_ip_list) == len(inner_ip_list):
                                one[ip_type] = others_ip_list[index]
                            else:
                                data.set_outputs("ex_data", _("获取{}的{}失败,请确认是否与inner_ip一一对应".format(inner_ip, ip_type)))
                                return False
                    one.update(base_params)

                    row_host_params_list.append(one)

            all_hosts.extend(row_host_params_list)

            kwargs = {
                "job_type": job_name,
                "hosts": all_hosts,
                "action": "job_install",
            }
        else:
            data.set_outputs("ex_data", _("无效的操作请求:{}".format(job_name)))
            return False

        action = kwargs.pop("action")
        result = getattr(client, action)(**kwargs)
        if not result["result"]:
            # 接口失败详细日志都存在 data 中，需要打印出来
            try:
                message = json.dumps(result.get("data", ""), ensure_ascii=False)
            except TypeError:
                message = ""
            result["message"] += message

            error = handle_api_error(
                system=__group_name__, api_name="nodeman.%s" % action, params=kwargs, result=result
            )
            data.set_outputs("ex_data", error)
            self.logger.error(error)
            return False

        job_id = result["data"].get("job_id", None)
        data.set_outputs("job_id", job_id)
        return True

    def schedule(self, data, parent_data, callback_data=None):
        executor = parent_data.inputs.executor
        client = BKNodeManClient(username=executor)
        job_id = data.get_one_of_outputs("job_id", "")
        if not job_id:
            self.finish_schedule()
            return True

        job_kwargs = {"job_id": job_id}
        job_result = client.job_details(**job_kwargs)
        if not job_result["result"]:
            # 接口失败详细日志都存在 data 中，需要打印出来
            try:
                message = json.dumps(job_result.get("data", ""), ensure_ascii=False)
            except TypeError:
                message = ""
            job_result["message"] += message

            error = handle_api_error(__group_name__, "nodeman.job_details", job_kwargs, job_result)
            data.set_outputs("ex_data", error)
            self.finish_schedule()
            return False

        result_data = job_result["data"]
        job_statistics = result_data["statistics"]
        success_num = job_statistics["success_count"]
        fail_num = job_statistics["failed_count"]
        host_list = result_data["list"]

        data.set_outputs("success_num", success_num)
        data.set_outputs("fail_num", fail_num)

        if result_data["status"] == "SUCCESS":
            self.finish_schedule()
            return True

        # 失败任务信息
        if result_data["status"] == "FAILED":
            fail_infos = [
                {"inner_ip": host["inner_ip"], "instance_id": host["instance_id"]}
                for host in host_list
                if host["status"] == "FAILED"
            ]

            # 查询失败任务日志
            error_log = "<br>{mes}</br>".format(mes=_("日志信息为："))
            for fail_info in fail_infos:
                log_kwargs = {
                    "job_id": job_id,
                    "instance_id": fail_info["instance_id"],
                }
                result = client.get_job_log(**log_kwargs)

                if not result["result"]:
                    result["message"] += json.dumps(result["data"], ensure_ascii=False)
                    error = handle_api_error(__group_name__, "nodeman.get_job_log", log_kwargs, result)
                    data.set_outputs("ex_data", error)
                    self.finish_schedule()
                    return False

                # 提取出错步骤日志
                log_info = [_log for _log in result["data"] if _log["status"] == "FAILED"]

                error_log = "{error_log}<br><b>{host}{fail_host}</b></br><br>{log}</br>{log_info}".format(
                    error_log=error_log,
                    host=_("主机："),
                    fail_host=fail_info["inner_ip"],
                    log=_("日志："),
                    log_info=json.dumps(log_info[0], ensure_ascii=False),
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
                key="bk_biz_id",
                type="int",
                schema=IntItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("操作对象"),
                key="nodeman_op_target",
                type="object",
                schema=ObjectItemSchema(
                    _("需要操作的对象"),
                    property_schemas={
                        "nodeman_bk_cloud_id": StringItemSchema(description=_("云区域 ID")),
                        "nodeman_node_type": StringItemSchema(
                            description=_("节点类型，可以是 AGENT（表示直连区域安装 Agent）、 PROXY（表示安装 Proxy）")
                        ),
                    },
                ),
            ),
            self.InputItem(
                name=_("操作详情"),
                key="nodeman_op_info",
                type="object",
                schema=ObjectItemSchema(
                    _("操作内容信息"),
                    property_schemas={
                        "nodeman_ap_id": StringItemSchema(description=_("接入点 ID")),
                        "nodeman_op_type": StringItemSchema(
                            description=_(
                                "任务操作类型，可以是 INSTALL（安装）、  REINSTALL（重装）、" " UNINSTALL （卸载）、 REMOVE （移除）或 UPGRADE （升级）"
                            )
                        ),
                        "nodeman_ip_str": StringItemSchema(description=_("IP(升级，卸载，移除时需要)")),
                        "nodeman_hosts": ArrayItemSchema(
                            description=_("需要被操作的主机信息(安装与重装时需要)"),
                            item_schema=ObjectItemSchema(
                                description=_("主机相关信息"),
                                property_schemas={
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
                    },
                ),
            ),
        ]


class NodemanCreateTaskComponent(Component):
    name = _("新建任务")
    code = "nodeman_create_task"
    bound_service = NodemanCreateTaskService
    form = "%scomponents/atoms/nodeman/create_task/v2_0.js" % settings.STATIC_URL
    version = VERSION
