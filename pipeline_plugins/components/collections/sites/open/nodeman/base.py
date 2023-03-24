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
import ujson as json
from django.utils.translation import ugettext_lazy as _

from api.collections.nodeman import BKNodeManClient
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.core.flow.io import IntItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("节点管理(Nodeman)")

from gcloud.utils.ip import extract_ip_from_ip_str, get_ip_by_regex


def get_host_id_by_inner_ip(executor, logger, bk_cloud_id: int, bk_biz_id: int, ip_list: list):
    """
    根据inner_ip获取bk_host_id 对应关系dict
    """

    if not ip_list:
        return {}

    client = BKNodeManClient(username=executor)
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


def get_host_id_by_inner_ipv6(executor, logger, bk_cloud_id: int, bk_biz_id: int, ip_list: list):
    """
    根据inner_ip获取bk_host_id 对应关系dict, ipv6 版本
    """
    if not ip_list:
        return {}

    client = BKNodeManClient(username=executor)
    kwargs = {
        "bk_biz_id": [bk_biz_id],
        "pagesize": -1,
        "conditions": [{"key": "ip", "value": ip_list}, {"key": "bk_cloud_id", "value": [bk_cloud_id]}],
    }
    result = client.search_host_plugin(**kwargs)
    if not result["result"]:
        error = handle_api_error(__group_name__, "nodeman.search_host_plugin", kwargs, result)
        logger.error(error)
        return {}

    return {host["inner_ipv6"]: host["bk_host_id"] for host in result["data"]["list"]}


def get_nodeman_rsa_public_key(executor, logger):
    """
    拉取节点管理rsa公钥
    """
    client = BKNodeManClient(username=executor)
    get_rsa_result = client.get_rsa_public_key(executor)
    if not get_rsa_result["result"]:
        error = handle_api_error(__group_name__, "nodeman.get_rsa_public_key", executor, get_rsa_result)
        logger.error(error)
        return False, None
    content = get_rsa_result["data"][0]["content"]
    name = get_rsa_result["data"][0]["name"]
    return True, {"name": name, "content": content}


class NodeManBaseService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def get_ip_list(self, ip_str):
        if settings.ENABLE_IPV6:
            ipv6_list, ipv4_list, *_ = extract_ip_from_ip_str(ip_str)
            return ipv6_list + ipv4_list
        return get_ip_by_regex(ip_str)

    def get_host_id_list(self, ip_str, executor, bk_cloud_id, bk_biz_id):
        # 如果开启了ipv6的逻辑，则执行
        if settings.ENABLE_IPV6:
            ipv6_list, ipv4_list, _, _ = extract_ip_from_ip_str(ip_str)
            ip_list = ipv4_list + ipv6_list
            bk_host_id_dict_ipv6 = get_host_id_by_inner_ipv6(executor, self.logger, bk_cloud_id, bk_biz_id, ip_list)

            return list(bk_host_id_dict_ipv6.values())

        ip_list = get_ip_by_regex(ip_str)
        bk_host_id_dict = get_host_id_by_inner_ip(executor, self.logger, bk_cloud_id, bk_biz_id, ip_list)
        return [bk_host_id for bk_host_id in bk_host_id_dict.values()]

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
        client = BKNodeManClient(username=executor)

        job_id = data.get_one_of_outputs("job_id", "")

        if not job_id:
            self.finish_schedule()
            return True

        job_kwargs = {"job_id": job_id}
        job_result = client.job_details(**job_kwargs)

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
                    log=_("错误日志："),
                    log_info="{}\n{}".format(log_info[0]["step"], log_info[0]["log"]),
                )

            data.set_outputs("ex_data", error_log)
            self.finish_schedule()
            return False
