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
import ipaddress
import re

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from django.utils.translation import gettext_lazy as _
from pipeline.core.flow.activity import StaticIntervalGenerator
from pipeline.core.flow.io import IntItemSchema, StringItemSchema

from api.collections.nodemgr import BKNodemgrClient
from gcloud.utils import crypto
from pipeline_plugins.base import BasePluginService
from pipeline_plugins.components.utils import parse_passwd_value

__group_name__ = _("节点管理V3(Nodemgr)")


def split_ip_list(text, strip=True):
    items = re.split(r"[,;\n]", text)
    if strip:
        return [item.strip() for item in items if item.strip()]
    else:
        return items


class NodemgrBaseService(BasePluginService):
    """Nodemgr 插件基类"""

    __need_schedule__ = True
    interval = StaticIntervalGenerator(10)  # 10秒轮询一次

    def get_client(self, username=None):
        """获取 BKNodemgrClient 实例"""
        return BKNodemgrClient(username=username)

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("Workflow ID"),
                key="workflow_id",
                type="string",
                schema=StringItemSchema(description=_("提交的任务的 workflow_id")),
            ),
            self.OutputItem(
                name=_("Workflow URL"),
                key="workflow_url",
                type="string",
                schema=StringItemSchema(description=_("Workflow 详情页链接")),
            ),
            self.OutputItem(
                name=_("成功个数"),
                key="success_count",
                type="int",
                schema=IntItemSchema(description=_("任务中成功的 operation 个数")),
            ),
            self.OutputItem(
                name=_("失败个数"),
                key="failed_count",
                type="int",
                schema=IntItemSchema(description=_("任务中失败的 operation 个数")),
            ),
        ]

    def check_workflow_result(self, client, workflow_id, is_plugin=False):
        """
        检查 workflow 执行结果
        返回: (is_finished, is_success, success_count, failed_count, error_message)
        """
        try:
            if is_plugin:
                result = client.plugin_workflow_operation_list(workflow_id)
            else:
                result = client.node_workflow_operation_list(workflow_id)

            if result.get("code") != 0:
                error_msg = result.get("message", "Unknown error")
                self.logger.error(f"Query workflow failed: {error_msg}")
                return True, False, 0, 0, error_msg

            self.logger.info(f"Query workflow result: {result}")

            operations = result.get("data", {}).get("operations", [])
            if not operations:
                return False, False, 0, 0, None

            success_states = {"SUCCESS", "SUCCEEDED"}
            success_states_lower = {"success"}
            failed_states = {"FAILED", "FAILURE"}
            failed_states_lower = {"failed", "timeout", "terminated"}

            def normalize_life_cycle_state(latest_data):
                life_cycle = latest_data.get("life_cycle", "")
                if isinstance(life_cycle, dict):
                    state = life_cycle.get("state", "")
                else:
                    state = life_cycle
                return str(state).strip()

            success_count = 0
            failed_count = 0
            running_count = 0
            failed_operation_ids = []

            for op in operations:
                latest_data = op.get("latest_oper_inst_brief_data", None)
                if not latest_data:
                    running_count += 1
                    continue

                state = normalize_life_cycle_state(latest_data)
                state_upper = state.upper()
                state_lower = state.lower()

                if state_upper in success_states or state_lower in success_states_lower:
                    success_count += 1
                elif state_upper in failed_states or state_lower in failed_states_lower:
                    failed_count += 1
                    op_id = op.get("operation_id")
                    if op_id:
                        failed_operation_ids.append(op_id)
                else:
                    running_count += 1

            if running_count > 0:
                self.logger.info(
                    f"Workflow {workflow_id}: {success_count} succeeded, "
                    f"{failed_count} failed, {running_count} running"
                )
                return False, False, success_count, failed_count, None

            is_success = failed_count == 0
            error_message = None

            if not is_success:
                error_logs = [f"Operation {operation_id} failed" for operation_id in failed_operation_ids]
                error_message = "; ".join(error_logs) if error_logs else "Some operations failed"

            return True, is_success, success_count, failed_count, error_message

        except Exception as e:
            self.logger.exception(f"Check workflow result error: {e}")
            return True, False, 0, 0, str(e)

    def get_public_key(self, username=None):
        client = self.get_client(username=username)
        public_key_result = client.public_key_get()
        public_key = public_key_result.get("data", {}).get("public_key", "")
        if public_key == "":
            raise Exception("获取公钥失败")

        return public_key

    def encrypt_credit(self, username=None, auth_info=None):
        """加密password或key, 传入的auth_info为js内定义的password类型传递的dict"""
        if auth_info is None:
            auth_info = {}
        auth_credit: str = crypto.decrypt(parse_passwd_value(auth_info))
        public_key = self.get_public_key(username=username)
        public_key = serialization.load_pem_public_key(public_key.encode())

        rsa_label = b"com.example.crypto.rsa.v1"
        ciphertext = public_key.encrypt(
            auth_credit.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=rsa_label,
            ),
        )

        # prepend version byte 0x01
        out = b"\x01" + ciphertext
        return base64.b64encode(out).decode()

    def ip_version(self, ip):
        try:
            return ipaddress.ip_address(ip).version  # 4 或 6
        except ValueError:
            return None

    def list_host_by_ip(self, biz_id, networkarea_ip_dict=None, username=None):
        if networkarea_ip_dict is None:
            networkarea_ip_dict = {}
        client = self.get_client(username=username)
        result = {}

        for networkarea_id, ip_list in networkarea_ip_dict.items():
            ipv4_list = []
            ipv6_list = []
            for ip in ip_list:
                ipv = self.ip_version(ip)
                if ipv == 4:
                    ipv4_list.append(ip)
                elif ipv == 6:
                    ipv6_list.append(ip)
                else:
                    continue

            if not ipv4_list and not ipv6_list:
                continue

            response = client.host_list(
                biz_id=biz_id,
                networkarea_id=networkarea_id,
                ipv4_list=ipv4_list,
                ipv6_list=ipv6_list,
            )
            if response.get("code") != 0:
                raise Exception(f"获取host列表失败: {response.get('message', 'Unknown error')}")

            if networkarea_id not in result:
                result[networkarea_id] = {}
            r = result[networkarea_id]

            for host in response.get("data", {}).get("items", []):
                host_info = host.get("info")
                for ip in host_info.get("bk_host_innerip_list") or []:
                    if ip:
                        r[ip] = host
                for ip in host_info.get("bk_host_innerip_v6_list") or []:
                    if ip:
                        r[ip] = host

        return result
