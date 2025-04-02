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
import base64

import ujson as json
from bkcrypto.asymmetric.ciphers import BaseAsymmetricCipher
from bkcrypto.asymmetric.interceptors import BaseAsymmetricInterceptor
from bkcrypto.constants import AsymmetricCipherType
from bkcrypto.contrib.django.ciphers import get_asymmetric_cipher
from django.utils.translation import gettext_lazy as _
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.core.flow.io import ArrayItemSchema, IntItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("节点管理(Nodeman)")

from gcloud.utils.ip import extract_ip_from_ip_str, get_ip_by_regex
from packages.bkapi.bk_nodeman.shortcuts import get_client_by_username
from pipeline_plugins.components.utils.sites.open.utils import get_nodeman_job_url


class NodeManAsymmetricInterceptor(BaseAsymmetricInterceptor):

    PREFIX: str = base64.b64encode("DEFAULT".encode()).decode(encoding="utf-8")

    @classmethod
    def after_encrypt(cls, ciphertext: str, **kwargs) -> str:
        return f"{cls.PREFIX}{ciphertext}"


def get_host_id_by_inner_ip(tenant_id, executor, logger, bk_cloud_id: int, bk_biz_id: int, ip_list: list):
    """
    根据inner_ip获取bk_host_id 对应关系dict
    """

    if not ip_list:
        return {}

    client = get_client_by_username(username=executor, stage=settings.BK_APIGW_STAGE_NAME)
    kwargs = {
        "bk_biz_id": [bk_biz_id],
        "pagesize": -1,
        "conditions": [{"key": "inner_ip", "value": ip_list}, {"key": "bk_cloud_id", "value": [bk_cloud_id]}],
    }
    result = client.api.search_host_plugin(**kwargs, headers={"X-Bk-Tenant-Id": tenant_id})

    if not result["result"]:
        error = handle_api_error(__group_name__, "nodeman.search_host_plugin", kwargs, result)
        logger.error(error)
        return {}

    return {host["inner_ip"]: host["bk_host_id"] for host in result["data"]["list"]}


def get_host_id_by_inner_ipv6(tenant_id, executor, logger, bk_cloud_id: int, bk_biz_id: int, ip_list: list):
    """
    根据inner_ip获取bk_host_id 对应关系dict, ipv6 版本
    """
    if not ip_list:
        return {}

    client = get_client_by_username(username=executor, stage=settings.BK_APIGW_STAGE_NAME)
    kwargs = {
        "bk_biz_id": [bk_biz_id],
        "pagesize": -1,
        "conditions": [{"key": "ip", "value": ip_list}, {"key": "bk_cloud_id", "value": [bk_cloud_id]}],
    }
    result = client.api.search_host_plugin(**kwargs, headers={"X-Bk-Tenant-Id": tenant_id})
    if not result["result"]:
        error = handle_api_error(__group_name__, "nodeman.search_host_plugin", kwargs, result)
        logger.error(error)
        return {}

    return {host["inner_ipv6"]: host["bk_host_id"] for host in result["data"]["list"]}


def get_nodeman_public_key(tenant_id, executor, logger):
    """
    拉取节点管理rsa公钥
    """
    client = get_client_by_username(username=executor, stage=settings.BK_APIGW_STAGE_NAME)
    pub_key_response = client.api.fetch_public_keys(executor, headers={"X-Bk-Tenant-Id": tenant_id})
    if not pub_key_response["result"]:
        error = handle_api_error(__group_name__, "nodeman.get_rsa_public_key", executor, pub_key_response)
        logger.error(error)
        return False, None
    try:
        public_key_info = pub_key_response["data"][0]
    except (AssertionError, IndexError):
        logger.error("fetch_public_keys return empty data")
        return False, None

    return True, {
        "name": public_key_info["name"],
        "content": public_key_info["content"],
        # 如果没有返回 cipher_type，说明本环境节点管理还没更新为国密适配版本，此时设置 cipher_type 为 RSA，向前兼容节点管理的接口行为
        "cipher_type": public_key_info.get("cipher_type") or AsymmetricCipherType.RSA.value,
    }


class NodeManBaseService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def execute_operate(self, tenant_id, data, host, executor, bk_biz_id):
        client = get_client_by_username(username=executor, stage=settings.BK_APIGW_STAGE_NAME)
        nodeman_op_target = data.inputs.nodeman_plugin_operate
        op_type = nodeman_op_target.get("nodeman_op_type", "")
        plugin = nodeman_op_target.get("nodeman_plugin", "")
        plugin_version = nodeman_op_target.get("nodeman_plugin_version", "")
        install_config = nodeman_op_target.get("install_config", [])

        # 拼装参数
        params = {
            "job_type": op_type,
            "bk_biz_id": [bk_biz_id],
            "bk_host_id": host,
            "plugin_params": {"name": plugin},
        }
        if plugin_version:
            params["plugin_params"]["version"] = plugin_version

        # 如果插件操作类型为停止，则固定版本传`latest`,
        if op_type == "MAIN_STOP_PLUGIN":
            params["plugin_params"]["version"] = "latest"

        if op_type == "MAIN_INSTALL_PLUGIN" and install_config:
            if "keep_config" in install_config:
                params["plugin_params"].update({"keep_config": 1})
            elif "no_restart" in install_config:
                params["plugin_params"].update({"no_restart": 1})

        result = client.api.operate_plugin(params, headers={"X-Bk-Tenant-Id": tenant_id})

        job_is_plugin = True
        if result["result"]:
            # 这里兼容节点管理新老接口
            if plugin not in result["data"]:
                job_is_plugin = False
            job_id = result["data"].get(plugin, None) or result["data"].get("job_id", None)
            data.outputs.job_url = [get_nodeman_job_url(job_id, host_id) for host_id in host]

        return self.get_job_result(result, data, "plugin_operate", params, job_is_plugin=job_is_plugin)

    def get_ip_list(self, ip_str):
        if settings.ENABLE_IPV6:
            ipv6_list, ipv4_list, *_ = extract_ip_from_ip_str(ip_str)
            return ipv6_list + ipv4_list
        return get_ip_by_regex(ip_str)

    def get_host_id_list(self, tenant_id, ip_str, executor, bk_cloud_id, bk_biz_id):
        # 如果开启了ipv6的逻辑，则执行
        if settings.ENABLE_IPV6:
            ipv6_list, ipv4_list, *_ = extract_ip_from_ip_str(ip_str)
            bk_host_id_dict_ipv6 = get_host_id_by_inner_ipv6(
                tenant_id, executor, self.logger, bk_cloud_id, bk_biz_id, ipv6_list
            )
            bk_host_id_dict = get_host_id_by_inner_ip(
                tenant_id, executor, self.logger, bk_cloud_id, bk_biz_id, ipv4_list
            )
            return list(set(bk_host_id_dict_ipv6.values()) | set(bk_host_id_dict.values()))

        ip_list = get_ip_by_regex(ip_str)
        bk_host_id_dict = get_host_id_by_inner_ip(tenant_id, executor, self.logger, bk_cloud_id, bk_biz_id, ip_list)
        return [bk_host_id for bk_host_id in bk_host_id_dict.values()]

    def parse2nodeman_ciphertext(self, tenant_id, data, executor, plaintext) -> str:
        success, public_key_info = get_nodeman_public_key(tenant_id, executor, self.logger)
        if not success:
            data.set_outputs("ex_data", _("获取节点管理公钥失败,请查看节点日志获取错误详情."))
            raise ValueError

        # 根据接口的 cipher type 和 publickey 创建 cipher
        cipher: BaseAsymmetricCipher = get_asymmetric_cipher(
            cipher_type=public_key_info["cipher_type"],
            common={"public_key_string": public_key_info["content"], "interceptor": NodeManAsymmetricInterceptor},
        )

        return cipher.encrypt(plaintext)

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("任务 ID"),
                key="job_id",
                type="int",
                schema=IntItemSchema(description=_("提交的任务的 job_id")),
            ),
            self.OutputItem(
                name=_("任务链接"),
                key="job_url",
                type="string",
                schema=StringItemSchema(description=_("任务链接")),
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

    def get_job_result(self, result, data, action, kwargs, set_output_job_id=True, job_is_plugin=False):
        """获取任务id及结果"""
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
        if action == "remove_host":  # 删除类任务无job_id
            return True
        if set_output_job_id:
            job_key = "job_id"
            if job_is_plugin:  # 插件操作类的job_id 从result["data][插件名中获取]
                job_key = kwargs["plugin_params"]["name"]
            job_id = result["data"].get(job_key)
            if not job_id:
                data.outputs.ex_data = _("获取任务job_id失败，result:{}".format(result))
                return False

            job_url = result["data"].get("job_url", "")
            # 如果接口返回job_url,以返回的为准
            if job_url:
                data.set_outputs("job_url", job_url)
            data.set_outputs("job_id", job_id)

        return True

    def schedule(self, data, parent_data, callback_data=None):
        executor = parent_data.inputs.executor
        tenant_id = parent_data.inputs.tenant_id
        client = get_client_by_username(username=executor, stage=settings.BK_APIGW_STAGE_NAME)

        job_id = data.get_one_of_outputs("job_id", "")

        if not job_id:
            self.finish_schedule()
            return True

        job_kwargs = {"job_id": job_id}
        job_result = client.api.job_retrieve_job(headers={"X-Bk-Tenant-Id": tenant_id}, path_params={"pk": job_id})

        # 获取执行结果
        if not self.get_job_result(job_result, data, "nodeman.job_details", job_kwargs, set_output_job_id=False):
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
        if result_data["status"] in ["FAILED", "PART_FAILED"]:
            fail_infos = [
                {"inner_ip": host["inner_ip"], "instance_id": host["instance_id"]}
                for host in host_list
                if host["status"] == "FAILED"
            ]

            # 查询失败任务日志
            error_log = "<br>{mes}</br>".format(mes=_("操作失败主机日志信息："))
            for fail_info in fail_infos:
                log_kwargs = {
                    "instance_id": fail_info["instance_id"],
                }
                result = client.api.get_job_log(
                    log_kwargs, headers={"X-Bk-Tenant-Id": tenant_id}, path_params={"id": job_id}
                )

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
                    log=_("错误日志："),
                    log_info="{}\n{}".format(log_info[0]["step"], log_info[0]["log"]),
                )

            data.set_outputs("ex_data", error_log)
            self.finish_schedule()
            return False


class NodeManNewBaseService(NodeManBaseService):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="bk_biz_id",
                type="int",
                schema=IntItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
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
