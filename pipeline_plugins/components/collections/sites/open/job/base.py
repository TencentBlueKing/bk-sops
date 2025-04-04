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

# 作业平台任务状态参照表
TASK_RESULT = [
    (0, '状态未知'),
    (1, '未执行'),
    (2, '正在执行'),
    (3, '执行成功'),
    (4, '执行失败'),
    (5, '跳过'),
    (6, '忽略错误'),
    (7, '等待用户'),
    (8, '手动结束'),
    (9, '状态异常'),
    (10, '步骤强制终止中'),
    (11, '步骤强制终止成功'),
    (12, '步骤强制终止失败'),
    (-1, '接口调用失败'),
]
"""

import re
import traceback
from functools import partial

from django.utils.translation import gettext_lazy as _
from pipeline.core.flow import StaticIntervalGenerator
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import IntItemSchema, StringItemSchema

from env import JOB_LOG_VAR_SEARCH_CUSTOM_PATTERNS
from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from gcloud.utils.handlers import handle_api_error
from packages.bkapi.jobv3_cloud.shortcuts import get_client_by_username
from pipeline_plugins.components.utils.common import batch_execute_func

# 作业状态码: 1.未执行; 2.正在执行; 3.执行成功; 4.执行失败; 5.跳过; 6.忽略错误; 7.等待用户; 8.手动结束;
# 9.状态异常; 10.步骤强制终止中; 11.步骤强制终止成功; 12.步骤强制终止失败

JOB_SUCCESS = {3}
JOB_VAR_TYPE_IP = 2

LOG_VAR_SEARCH_CONFIGS = [{"re": r"<SOPS_VAR>(.+?)</SOPS_VAR>", "kv_sep": ":"}]

for custom_patterns in JOB_LOG_VAR_SEARCH_CUSTOM_PATTERNS:
    LOG_VAR_SEARCH_CONFIGS.append(custom_patterns)

__group_name__ = _("作业平台(JOB)")

job_handle_api_error = partial(handle_api_error, __group_name__)


def get_sops_var_dict_from_log_text(log_text, service_logger):
    """
    在日志文本中提取全局变量
    :param service_logger:
    :param log_text: 日志文本，如下：
    "<SOPS_VAR>key1:value1</SOPS_VAR>\ngsectl\n-rwxr-xr-x 1 root<SOPS_VAR>key2:value2</SOPS_VAR>\n"
    或者已转义的日志文本
    &lt;SOPS_VAR&gt;key2:value2&lt;/SOPS_VAR&gt;
    :return:
    {"key1": "value1", "key2": "value2"}
    """
    sops_var_dict = {}
    # 支持跨行匹配全局变量
    service_logger.info("search log var with config: {}".format(LOG_VAR_SEARCH_CONFIGS))
    for var_search_config in LOG_VAR_SEARCH_CONFIGS:
        reg = var_search_config["re"]
        excape_reg = reg.replace("<", "&lt;").replace(">", "&gt;")
        kv_sep = var_search_config["kv_sep"]

        sops_key_val_list = re.findall(reg, log_text, re.DOTALL)
        sops_key_val_list.extend(re.findall(excape_reg, log_text, re.DOTALL))
        service_logger.info(f"search log var with sops key val list: {sops_key_val_list}")
        if len(sops_key_val_list) == 0:
            continue
        for sops_key_val in sops_key_val_list:
            if kv_sep not in sops_key_val:
                continue
            sops_key, sops_val = sops_key_val.split(kv_sep, 1)
            # 限制变量名不为空
            if len(sops_key) == 0:
                continue
            sops_var_dict.update({sops_key: sops_val})
    service_logger.info(f"search log var result: {sops_var_dict}")
    return sops_var_dict


def get_job_instance_log(
    tenant_id,
    client,
    service_logger,
    job_instance_id,
    bk_biz_id,
    target_ip=None,
    job_scope_type=JobBizScopeType.BIZ.value,
):
    """
    获取作业日志：获取某个ip每个步骤的日志
    :param client:
    :param service_logger: 组件日志对象
    :param job_instance_id: 作业实例id
    :param bk_biz_id 业务ID
    :param target_ip 希望提取日志的目标IP
    获取到的job_logs实例
    [
        {
            "status": 3,
            "step_results": [
                {
                    "tag": "",
                    "ip_logs": [
                        {
                            "total_time": 0.363,
                            "ip": "1.1.1.1",
                            "start_time": "2020-06-15 17:23:11 +0800",
                            "log_content": "<SOPS_VAR>key1:value1</SOPS_VAR>\ngsectl\n-rwxr-xr-x 1",
                            "exit_code": 0,
                            "bk_cloud_id": 0,
                            "retry_count": 0,
                            "end_time": "2020-06-15 17:23:11 +0800",
                            "error_code": 0
                        },
                    ],
                    "ip_status": 9
                }
            ],
            "is_finished": true,
            "step_instance_id": 12321,
            "name": "查看文件"
        },
    ]
    :return:
    - success { "result": True, "data": "log text of target_ip"}
    - fail { "result": False, "message": message}
    """
    get_job_instance_status_kwargs = {
        "bk_scope_type": job_scope_type,
        "bk_scope_id": str(bk_biz_id),
        "bk_biz_id": bk_biz_id,
        "job_instance_id": job_instance_id,
        "return_ip_result": True,
    }
    get_job_instance_status_return = client.api.get_job_instance_status(
        get_job_instance_status_kwargs, headers={"X-Bk-Tenant-Id": tenant_id}
    )
    if not get_job_instance_status_return["result"]:
        message = handle_api_error(
            __group_name__,
            "jobv3.get_job_instance_status",
            get_job_instance_status_kwargs,
            get_job_instance_status_return,
        )
        service_logger.warning(message)
        return {"result": False, "message": message}
    # 根据每个步骤的IP（可能有多个），循环查询作业执行日志
    log_list = []
    for step_instance in get_job_instance_status_return["data"]["step_instance_list"]:
        if not step_instance.get("step_ip_result_list"):
            continue
        # 为了防止查询时间过长，每个步骤只取一个IP的日志进行记录
        step_ip_result = None
        if target_ip:
            for ip_result in step_instance["step_ip_result_list"]:
                if ip_result["ip"] == target_ip:
                    step_ip_result = ip_result
            if step_ip_result is None:
                message = _(
                    f"执行历史请求失败: IP:[{target_ip}], 不属于IP列表: "
                    f"[{','.join([instance['ip'] for instance in step_instance['step_ip_result_list']])}]"
                    f" | get_job_instance_log"
                )
                service_logger.error(message)
                return {"result": False, "message": message}
        else:
            step_ip_result = step_instance["step_ip_result_list"][0]
        get_job_instance_ip_log_kwargs = {
            "bk_scope_type": job_scope_type,
            "bk_scope_id": str(bk_biz_id),
            "bk_biz_id": bk_biz_id,
            "job_instance_id": job_instance_id,
            "step_instance_id": step_instance["step_instance_id"],
            "bk_cloud_id": step_ip_result["bk_cloud_id"],
        }

        # 如果打开ipv6并且存在主机id的情况下，优先取bk_host_id
        if settings.ENABLE_IPV6 and step_instance.get("bk_host_id"):
            get_job_instance_ip_log_kwargs["bk_host_id"] = step_instance["bk_host_id"]
        else:
            get_job_instance_ip_log_kwargs["ip"] = step_ip_result["ip"]

        get_job_instance_ip_log_kwargs_return = client.api.get_job_instance_ip_log(
            get_job_instance_ip_log_kwargs, headers={"X-Bk-Tenant-Id": tenant_id}
        )
        if not get_job_instance_ip_log_kwargs_return["result"]:
            message = handle_api_error(
                __group_name__,
                "jobv3.get_job_instance_ip_log_kwargs",
                get_job_instance_ip_log_kwargs,
                get_job_instance_ip_log_kwargs_return,
            )
            service_logger.warning(message)
            return {"result": False, "message": message}
        log_content = get_job_instance_ip_log_kwargs_return["data"]["log_content"]
        if log_content:
            log_list.append(str(log_content))
    log_text = "\n".join(log_list)
    return {"result": True, "data": log_text}


def get_ip_from_step_ip_result(step_ip_result):
    ip = step_ip_result.get("ip")
    if not ip:
        ip = step_ip_result.get("ipv6", "")
    # 防止极端情况下，ipv6 仍然不可用
    return ip or ""


def get_job_tagged_ip_dict(
    tenant_id, client, service_logger, job_instance_id, bk_biz_id, job_scope_type=JobBizScopeType.BIZ.value
):
    """根据job步骤执行标签获取 IP 分组"""
    kwargs = {
        "bk_scope_type": job_scope_type,
        "bk_scope_id": str(bk_biz_id),
        "bk_biz_id": bk_biz_id,
        "job_instance_id": job_instance_id,
        "return_ip_result": True,
    }
    result = client.api.get_job_instance_status(kwargs, headers={"X-Bk-Tenant-Id": tenant_id})

    if not result["result"]:
        message = handle_api_error(
            __group_name__,
            "jobv3.get_job_instance_status",
            kwargs,
            result,
        )
        service_logger.warning(message)
        return False, message

    step_instance = result["data"]["step_instance_list"][-1]

    step_ip_result_list = step_instance["step_ip_result_list"]
    tagged_ip_dict = {}

    for step_ip_result in step_ip_result_list:
        tag_key = step_ip_result["tag"]
        if not tag_key:
            continue
        ip = get_ip_from_step_ip_result(step_ip_result)
        if tag_key in tagged_ip_dict:
            tagged_ip_dict[tag_key] += f",{ip}"
        else:
            tagged_ip_dict[tag_key] = ip

    return True, tagged_ip_dict


def get_job_tagged_ip_dict_complex(
    tenant_id, client, service_logger, job_instance_id, bk_biz_id, job_scope_type=JobBizScopeType.BIZ.value
):
    """根据job步骤执行标签获取 IP 分组(该类型的会返回一个新的IP分组结构)，新的ip分组协议如下
    {
        "name": "JOB执行IP分组",
        "key": "job_tagged_ip_dict",
        "value": {
            "SUCCESS": {
                "DESC": "执行成功",
                "TAGS": {
                    "success-1": "127.0.0.1,127.0.0.1",
                    "success-2": "127.0.0.1,127.0.0.1",
                    "ALL": "127.0.0.1"
                }
            },
            "SCRIPT_FAILED": {
                "DESC": "脚本返回值非0",
                "TAGS": {
                    "failed-1": "127.0.0.1",
                    "failed-2": "127.0.0.1",
                    "ALL": "127.0.0.1"
                }
            },
            "OTHER_FAILED": {
                "desc": "其他报错",
                "tags": {
                    "TASK_TIMEOUT": "127.0.0.1",
                    "LOG_ERROR": "127.0.0.1",
                    "ALL": "127.0.0.1"
                }
            }
        }
    }
    """

    JOB_STEP_IP_RESULT_STATUS_MAP = {
        0: "UNKNOWN_ERROR",
        1: "AGENT_ERROR",
        2: "HOST_NOT_EXIST",
        3: "LAST_SUCCESS",
        9: "SUCCESS",
        11: "FAILED",
        12: "SUBMIT_FAILED",
        13: "TASK_TIMEOUT",
        15: "LOG_ERROR",
        16: "GSE_SCRIPT_TIMEOUT",
        17: "GSE_FILE_TIMEOUT",
        101: "SCRIPT_FAILED",
        102: "SCRIPT_TIMEOUT",
        103: "SCRIPT_TERMINATE",
        104: "SCRIPT_NOT_ZERO_EXIT_CODE",
        202: "COPYFILE_FAILED",
        203: "COPYFILE_SOURCE_FILE_NOT_EXIST",
        301: "FILE_ERROR_UNCLASSIFIED",
        303: "GSE_TIMEOUT",
        310: "GSE_AGENT_ERROR",
        311: "GSE_USER_ERROR",
        312: "GSE_USER_PWD_ERROR",
        320: "GSE_FILE_ERROR",
        321: "GSE_FILE_SIZE_EXCEED",
        329: "GSE_FILE_TASK_ERROR",
        399: "GSE_TASK_ERROR",
        403: "GSE_TASK_TERMINATE_SUCCESS",
        404: "GSE_TASK_TERMINATE_FAILED",
        500: "UNKNOWN",
    }

    kwargs = {
        "bk_scope_type": job_scope_type,
        "bk_scope_id": str(bk_biz_id),
        "bk_biz_id": bk_biz_id,
        "job_instance_id": job_instance_id,
        "return_ip_result": True,
    }
    result = client.api.get_job_instance_status(kwargs, headers={"X-Bk-Tenant-Id": tenant_id})

    if not result["result"]:
        message = handle_api_error(
            __group_name__,
            "jobv3.get_job_instance_status",
            kwargs,
            result,
        )
        service_logger.warning(message)
        return False, message

    step_instance = result["data"]["step_instance_list"][-1]

    step_ip_result_list = step_instance.get("step_ip_result_list", [])

    success_tags_dict = {}
    success_ips = []

    failed_tags_dict = {}
    failed_ips = []

    others_tags_dict = {}
    others_ips = []

    for step_ip_result in step_ip_result_list:
        tag_key = step_ip_result["tag"]
        status = step_ip_result["status"]
        status_key = JOB_STEP_IP_RESULT_STATUS_MAP.get(status, status)
        ip = get_ip_from_step_ip_result(step_ip_result)

        # 执行成功的分类到执行成功里面，JOB_SUCCESS
        if status == 9:
            success_ips.append(ip)
            if tag_key:
                if tag_key in success_tags_dict:
                    success_tags_dict[tag_key] += f",{ip}"
                else:
                    success_tags_dict[tag_key] = ip
        # 当调用job_failed时，会有失败的tag信息
        elif status == 104:
            failed_ips.append(ip)
            if tag_key:
                if tag_key in failed_tags_dict:
                    failed_tags_dict[tag_key] += f",{ip}"
                else:
                    failed_tags_dict[tag_key] = ip
        else:
            # 其他情况就是失败了
            others_ips.append(ip)
            if tag_key:
                if status_key in others_tags_dict:
                    others_tags_dict[status_key] += f",{ip}"
                else:
                    others_tags_dict[status_key] = ip

    success_tags_dict["ALL"] = ",".join(success_ips)
    failed_tags_dict["ALL"] = ",".join(failed_ips)
    others_tags_dict["ALL"] = ",".join(others_ips)

    tagged_ip_dict = {
        "name": "JOB执行IP分组",
        "key": "job_tagged_ip_dict",
        "value": {
            "SUCCESS": {"DESC": "执行成功", "TAGS": success_tags_dict},
            "SCRIPT_NOT_ZERO_EXIT_CODE": {"DESC": "脚本返回值非零", "TAGS": failed_tags_dict},
            "OTHER_FAILED": {"desc": "其他异常", "TAGS": others_tags_dict},
        },
    }

    return True, tagged_ip_dict


def get_job_sops_var_dict(
    tenant_id, client, service_logger, job_instance_id, bk_biz_id, job_scope_type=JobBizScopeType.BIZ.value
):
    """
    解析作业日志：默认取每个步骤/节点的第一个ip_logs
    :param client:
    :param service_logger: 组件日志对象
    :param job_instance_id: 作业实例id
    :param bk_biz_id 业务ID
    :return:
    - success { "result": True, "data": {"key1": "value1"}}
    - fail { "result": False, "message": message}
    """
    get_job_instance_log_result = get_job_instance_log(
        tenant_id, client, service_logger, job_instance_id, bk_biz_id, job_scope_type=job_scope_type
    )
    if not get_job_instance_log_result["result"]:
        return get_job_instance_log_result
    log_text = get_job_instance_log_result["data"]
    return {"result": True, "data": get_sops_var_dict_from_log_text(log_text, service_logger)}


class JobService(Service):
    __need_schedule__ = True

    reload_outputs = True

    need_get_sops_var = False
    # 是否IP分组
    need_is_tagged_ip = False

    biz_scope_type = JobBizScopeType.BIZ.value

    def execute(self, data, parent_data):
        pass

    def is_need_log_outputs_even_fail(self, data):
        return data.get_one_of_inputs("need_log_outputs_even_fail", False)

    def get_tagged_ip_dict(self, data, parent_data, job_instance_id):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        result, tagged_ip_dict = get_job_tagged_ip_dict(
            parent_data.inputs.tenant_id,
            client,
            self.logger,
            job_instance_id,
            data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
            job_scope_type=self.biz_scope_type,
        )
        return result, tagged_ip_dict

    def schedule(self, data, parent_data, callback_data=None):
        try:
            job_instance_id = callback_data.get("job_instance_id", None)
            status = callback_data.get("status", None)
        except Exception as e:
            err_msg = "invalid callback_data: {}, err: {}"
            self.logger.error(err_msg.format(callback_data, traceback.format_exc()))
            data.outputs.ex_data = err_msg.format(callback_data, e)
            return False

        if not job_instance_id or not status:
            data.outputs.ex_data = "invalid callback_data, job_instance_id: %s, status: %s" % (job_instance_id, status)
            self.finish_schedule()
            return False

        job_success = status in JOB_SUCCESS
        need_log_outputs_even_fail = self.is_need_log_outputs_even_fail(data)
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        # 失败情况下也需要要进行ip tag分组
        if job_success or need_log_outputs_even_fail or self.need_is_tagged_ip:
            if not job_success:
                data.set_outputs(
                    "ex_data",
                    {
                        "exception_msg": _(
                            "任务执行失败，<a href='{job_inst_url}' target='_blank'>前往作业平台(JOB)查看详情</a>"
                        ).format(job_inst_url=data.outputs.job_inst_url),
                        "task_inst_id": job_instance_id,
                        "show_ip_log": True,
                    },
                )

            if self.reload_outputs:
                # 判断是否对IP进行Tag分组, 兼容之前的配置，默认从inputs拿
                is_tagged_ip = data.get_one_of_inputs("is_tagged_ip", False)
                tagged_ip_dict = {}
                if is_tagged_ip or self.need_is_tagged_ip:
                    result, tagged_ip_dict = self.get_tagged_ip_dict(data, parent_data, job_instance_id)
                    if not result:
                        self.logger.error(tagged_ip_dict)
                        data.outputs.ex_data = tagged_ip_dict
                        self.finish_schedule()
                        return False

                if "is_tagged_ip" in data.get_inputs() or self.need_is_tagged_ip:
                    data.set_outputs("job_tagged_ip_dict", tagged_ip_dict)

                bk_biz_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
                # 全局变量重载
                get_var_kwargs = {
                    "bk_scope_type": self.biz_scope_type,
                    "bk_scope_id": str(bk_biz_id),
                    "bk_biz_id": bk_biz_id,
                    "job_instance_id": job_instance_id,
                }
                global_var_result = client.api.get_job_instance_global_var_value(
                    get_var_kwargs, headers={"X-Bk-Tenant-Id": tenant_id}
                )
                self.logger.info("get_job_instance_global_var_value return: {}".format(global_var_result))

                if not global_var_result["result"]:
                    message = job_handle_api_error(
                        "jobv3.get_job_instance_global_var_value",
                        get_var_kwargs,
                        global_var_result,
                    )
                    self.logger.error(message)
                    data.outputs.ex_data = message
                    self.finish_schedule()
                    return False

                global_var_list = global_var_result["data"].get("step_instance_var_list", [])
                if global_var_list:
                    for global_var in global_var_list[-1]["global_var_list"] or []:
                        if global_var["type"] != JOB_VAR_TYPE_IP:
                            data.set_outputs(global_var["name"], global_var["value"])

            # 无需提取全局变量的Service直接返回
            if not self.need_get_sops_var and not need_log_outputs_even_fail:
                self.finish_schedule()
                return True if job_success else False
            get_job_sops_var_dict_return = get_job_sops_var_dict(
                tenant_id,
                client,
                self.logger,
                job_instance_id,
                data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
                self.biz_scope_type,
            )
            if not get_job_sops_var_dict_return["result"]:
                self.logger.error(
                    _("{group}.{job_service_name}: 提取日志失败，{message}").format(
                        group=__group_name__,
                        job_service_name=self.__class__.__name__,
                        message=get_job_sops_var_dict_return["message"],
                    )
                )
                data.set_outputs("log_outputs", {})
                self.finish_schedule()
                return False

            log_outputs = get_job_sops_var_dict_return["data"]
            self.logger.info(
                _("{group}.{job_service_name}：输出日志提取变量为：{log_outputs}").format(
                    group=__group_name__, job_service_name=self.__class__.__name__, log_outputs=log_outputs
                )
            )
            data.set_outputs("log_outputs", log_outputs)
            self.finish_schedule()
            return True if job_success else False
        else:
            data.set_outputs(
                "ex_data",
                {
                    "exception_msg": _("任务执行失败，<a href='{job_inst_url}' target='_blank'>前往作业平台(JOB)查看详情</a>").format(
                        job_inst_url=data.outputs.job_inst_url
                    ),
                    "task_inst_id": job_instance_id,
                    "show_ip_log": True,
                },
            )
            self.finish_schedule()
            return False

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("JOB任务ID"),
                key="job_inst_id",
                type="int",
                schema=IntItemSchema(description=_("提交的任务在 JOB 平台的实例 ID")),
            ),
            self.OutputItem(
                name=_("JOB任务链接"),
                key="job_inst_url",
                type="string",
                schema=StringItemSchema(description=_("提交的任务在 JOB 平台的 URL")),
            ),
        ]


class JobScheduleService(JobService):
    __need_schedule__ = True

    interval = StaticIntervalGenerator(5)

    need_show_failure_inst_url = False

    def schedule(self, data, parent_data, callback_data=None):
        if hasattr(data.outputs, "requests_error") and data.outputs.requests_error:
            data.outputs.ex_data = "{}\n Get Result Error:\n".format(data.outputs.requests_error)
        else:
            data.outputs.ex_data = ""
        tenant_id = parent_data.inputs.tenant_id
        params_list = [
            {
                "data": {
                    "bk_scope_type": self.biz_scope_type,
                    "bk_scope_id": str(data.inputs.biz_cc_id),
                    "bk_biz_id": data.inputs.biz_cc_id,
                    "job_instance_id": job_id,
                },
                "headers": {"X-Bk-Tenant-Id": tenant_id},
            }
            for job_id in data.outputs.job_id_of_batch_execute
        ]
        client = get_client_by_username(parent_data.inputs.executor, stage=settings.BK_APIGW_STAGE_NAME)

        batch_result_list = batch_execute_func(
            client.api.get_job_instance_status,
            params_list,
            interval_enabled=True,
        )

        self.logger.info("批量请求get_job_instance_log 结果为:{}".format(batch_result_list))

        # 重置查询 job_id
        data.outputs.job_id_of_batch_execute = []

        # 解析查询结果
        running_task_list = []

        failure_inst_url = []

        for job_result in batch_result_list:
            result = job_result["result"]
            job_id_str = job_result["params"]["data"]["job_instance_id"]
            job_urls = [url for url in data.outputs.job_inst_url if str(job_id_str) in url]
            job_detail_url = job_urls[0] if job_urls else ""
            if result["result"]:
                job_status = result["data"]["job_instance"]["status"]
                # 成功状态
                if job_status == 3:
                    data.outputs.success_count += 1
                # 失败状态
                elif job_status > 3:
                    # 出于性能考虑，不拉取对应主机IP的日志，引导用户跳转JOB平台查看
                    failure_inst_url.append(job_detail_url)
                    data.outputs.ex_data += "任务执行失败，<a href='{}' target='_blank'>前往作业平台(JOB)查看详情</a>\n".format(
                        job_detail_url
                    )
                else:
                    running_task_list.append(job_id_str)
            else:
                failure_inst_url.append(job_detail_url)
                data.outputs.ex_data += "任务执行失败，<a href='{}' target='_blank'>前往作业平台(JOB)查看详情</a>\n".format(
                    job_detail_url
                )
                self.logger.error("请求job_id({}),结果为:{}".format(job_id_str, result.get("message")))
        # 需要继续轮询的任务
        data.outputs.job_id_of_batch_execute = running_task_list
        # 结束调度
        if not data.outputs.job_id_of_batch_execute:
            # 没有报错信息
            if not data.outputs.ex_data:
                del data.outputs.ex_data
            if self.need_show_failure_inst_url:
                data.outputs.failure_inst_url = failure_inst_url
            self.finish_schedule()
            return data.outputs.final_res and data.outputs.success_count == data.outputs.request_success_count


class Jobv3Service(Service):
    __need_schedule__ = True

    reload_outputs = True

    need_get_sops_var = False

    # 是否IP分组
    need_is_tagged_ip = False

    biz_scope_type = JobBizScopeType.BIZ.value

    def execute(self, data, parent_data):
        pass

    def is_need_log_outputs_even_fail(self, data):
        return data.get_one_of_inputs("need_log_outputs_even_fail", False)

    def get_tagged_ip_dict(self, data, parent_data, job_instance_id):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        result, tagged_ip_dict = get_job_tagged_ip_dict(
            parent_data.inputs.tenant_id,
            client,
            self.logger,
            job_instance_id,
            data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
            job_scope_type=self.biz_scope_type,
        )
        return result, tagged_ip_dict

    def schedule(self, data, parent_data, callback_data=None):

        try:
            job_instance_id = callback_data.get("job_instance_id", None)
            status = callback_data.get("status", None)
        except Exception as e:
            err_msg = "invalid callback_data: {}, err: {}"
            self.logger.error(err_msg.format(callback_data, traceback.format_exc()))
            data.outputs.ex_data = err_msg.format(callback_data, e)
            return False

        if not job_instance_id or not status:
            data.outputs.ex_data = "invalid callback_data, job_instance_id: %s, status: %s" % (job_instance_id, status)
            self.finish_schedule()
            return False

        job_success = status in JOB_SUCCESS
        need_log_outputs_even_fail = self.is_need_log_outputs_even_fail(data)
        tenant_id = parent_data.inputs.tenant_id
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        # 如果打开了ip分组，失败的情况也需要进行ip分组
        if job_success or need_log_outputs_even_fail or self.need_is_tagged_ip:
            if not job_success:
                data.set_outputs(
                    "ex_data",
                    {
                        "exception_msg": _(
                            "任务执行失败，<a href='{job_inst_url}' target='_blank'>前往作业平台(JOB)查看详情</a>"
                        ).format(job_inst_url=data.outputs.job_inst_url),
                        "task_inst_id": job_instance_id,
                        "show_ip_log": True,
                    },
                )

            if self.reload_outputs:
                # 判断是否对IP进行Tag分组
                is_tagged_ip = data.get_one_of_inputs("is_tagged_ip", False)
                tagged_ip_dict = {}
                if is_tagged_ip or self.need_is_tagged_ip:
                    result, tagged_ip_dict = self.get_tagged_ip_dict(data, parent_data, job_instance_id)
                    if not result:
                        self.logger.error(tagged_ip_dict)
                        data.outputs.ex_data = tagged_ip_dict
                        self.finish_schedule()
                        return False

                if "is_tagged_ip" in data.get_inputs() or self.need_is_tagged_ip:
                    data.set_outputs("job_tagged_ip_dict", tagged_ip_dict)

                # 全局变量重载
                get_var_kwargs = {
                    "bk_scope_type": self.biz_scope_type,
                    "bk_scope_id": str(data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)),
                    "bk_biz_id": data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
                    "job_instance_id": job_instance_id,
                }
                global_var_result = client.api.get_job_instance_global_var_value(
                    get_var_kwargs, headers={"X-Bk-Tenant-Id": tenant_id}
                )
                self.logger.info("get_job_instance_global_var_value return: {}".format(global_var_result))

                if not global_var_result["result"]:
                    message = job_handle_api_error(
                        "jobv3.get_job_instance_global_var_value",
                        get_var_kwargs,
                        global_var_result,
                    )
                    self.logger.error(message)
                    data.outputs.ex_data = message
                    self.finish_schedule()
                    return False

                step_instance_var_list = global_var_result["data"].get("step_instance_var_list", [])
                if step_instance_var_list:
                    for global_var in step_instance_var_list[-1]["global_var_list"]:
                        if global_var["type"] != JOB_VAR_TYPE_IP:
                            data.set_outputs(global_var["name"], global_var["value"])

            # 无需提取全局变量的Service直接返回
            if not self.need_get_sops_var:
                self.finish_schedule()
                return True if job_success else False

            get_jobv3_sops_var_dict_return = get_job_sops_var_dict(
                tenant_id,
                client,
                self.logger,
                job_instance_id,
                data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
                self.biz_scope_type,
            )
            if not get_jobv3_sops_var_dict_return["result"]:
                self.logger.warning(
                    _("{group}.{job_service_name}: 提取日志失败，{message}").format(
                        group=__group_name__,
                        job_service_name=self.__class__.__name__,
                        message=get_jobv3_sops_var_dict_return["message"],
                    )
                )
                data.set_outputs("log_outputs", {})
                self.finish_schedule()
                return True if job_success else False

            log_outputs = get_jobv3_sops_var_dict_return["data"]
            self.logger.info(
                _("{group}.{job_service_name}：输出日志提取变量为：{log_outputs}").format(
                    group=__group_name__, job_service_name=self.__class__.__name__, log_outputs=log_outputs
                )
            )
            data.set_outputs("log_outputs", log_outputs)
            self.finish_schedule()
            return True if job_success else False
        else:
            data.set_outputs(
                "ex_data",
                {
                    "exception_msg": _("任务执行失败，<a href='{job_inst_url}' target='_blank'>前往作业平台(JOB)查看详情</a>").format(
                        job_inst_url=data.outputs.job_inst_url
                    ),
                    "task_inst_id": job_instance_id,
                    "show_ip_log": True,
                },
            )
            self.finish_schedule()
            return False

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("JOB任务ID"),
                key="job_inst_id",
                type="int",
                schema=IntItemSchema(description=_("提交的任务在 JOB 平台的实例 ID")),
            ),
            self.OutputItem(
                name=_("JOB任务链接"),
                key="job_inst_url",
                type="string",
                schema=StringItemSchema(description=_("提交的任务在 JOB 平台的 URL")),
            ),
        ]


class Jobv3ScheduleService(Jobv3Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def schedule(self, data, parent_data, callback_data=None):
        if hasattr(data.outputs, "requests_error") and data.outputs.requests_error:
            data.outputs.ex_data = "{}\n Get Result Error:\n".format(data.outputs.requests_error)
        else:
            data.outputs.ex_data = ""
        tenant_id = parent_data.inputs.tenant_id

        params_list = [
            {
                "data": {
                    "bk_scope_type": self.biz_scope_type,
                    "bk_scope_id": str(data.inputs.biz_cc_id),
                    "bk_biz_id": data.inputs.biz_cc_id,
                    "job_instance_id": job_id,
                },
                "headers": {"X-Bk-Tenant-Id": tenant_id},
            }
            for job_id in data.outputs.job_id_of_batch_execute
        ]
        client = get_client_by_username(parent_data.inputs.executor, stage=settings.BK_APIGW_STAGE_NAME)

        batch_result_list = batch_execute_func(
            client.api.get_job_instance_status,
            params_list,
            interval_enabled=True,
        )

        # 重置查询 job_id
        data.outputs.job_id_of_batch_execute = []

        # 解析查询结果
        running_task_list = []

        for job_result in batch_result_list:
            result = job_result["result"]
            job_id_str = job_result["params"]["job_instance_id"]
            job_urls = [url for url in data.outputs.job_inst_url if str(job_id_str) in url]
            job_detail_url = job_urls[0] if job_urls else ""
            if result["result"]:
                log_content = "{}\n".format(result["data"][0]["step_results"][0]["ip_logs"][0]["log_content"])
                job_status = result["data"][0]["status"]
                # 成功状态
                if job_status == 3:
                    data.outputs.success_count += 1
                # 失败状态
                elif job_status > 3:
                    data.outputs.ex_data += (
                        "任务执行失败，<a href='{}' target='_blank'>前往作业平台(JOB)查看详情</a>"
                        "\n错误信息:{}\n".format(job_detail_url, log_content)
                    )
                else:
                    running_task_list.append(job_id_str)
            else:
                data.outputs.ex_data += "任务执行失败，<a href='{}' target='_blank'>前往作业平台(JOB)查看详情</a>\n".format(
                    job_detail_url
                )

        # 需要继续轮询的任务
        data.outputs.job_id_of_batch_execute = running_task_list
        # 结束调度
        if not data.outputs.job_id_of_batch_execute:
            # 没有报错信息
            if not data.outputs.ex_data:
                del data.outputs.ex_data

            self.finish_schedule()
            return data.outputs.final_res and data.outputs.success_count == data.outputs.request_success_count


class GetJobHistoryResultMixin(object):
    def get_job_history_result(self, data, parent_data):
        # get job_instance[job_success_id] execute status
        job_success_id = data.get_one_of_inputs("job_success_id")
        tenant_id = parent_data.inputs.tenant_id
        client = get_client_by_username(parent_data.inputs.executor, stage=settings.BK_APIGW_STAGE_NAME)
        bk_scope_type = getattr(self, "biz_scope_type", JobBizScopeType.BIZ.value)
        job_kwargs = {
            "bk_scope_type": bk_scope_type,
            "bk_scope_id": str(data.inputs.biz_cc_id),
            "bk_biz_id": data.inputs.biz_cc_id,
            "job_instance_id": job_success_id,
        }
        job_result = client.api.get_job_instance_status(job_kwargs, headers={"X-Bk-Tenant-Id": tenant_id})

        if not job_result["result"]:
            message = handle_api_error(
                __group_name__,
                "jobv3.get_job_instance_status",
                job_kwargs,
                job_result,
            )
            self.logger.error(message)
            data.outputs.ex_data = message
            self.logger.info(data.outputs)
            return False

        # judge success status
        if job_result["data"]["job_instance"]["status"] not in JOB_SUCCESS:
            message = _(f"执行历史请求失败: 任务实例[ID: {job_success_id}], 异常信息: {job_result['result']} | get_job_history_result")
            self.logger.error(message)
            data.outputs.ex_data = message
            self.logger.info(data.outputs)
            return False

        # get job_var
        if not self.need_get_sops_var:
            self.logger.info(data.outputs)
            return True

        get_job_sops_var_dict_return = get_job_sops_var_dict(
            tenant_id,
            client,
            self.logger,
            job_success_id,
            data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
        )
        if not get_job_sops_var_dict_return["result"]:
            self.logger.error(
                _("{group}.{job_service_name}: 提取日志失败，{message}").format(
                    group=__group_name__,
                    job_service_name=self.__class__.__name__,
                    message=get_job_sops_var_dict_return["message"],
                )
            )
            data.set_outputs("log_outputs", {})
            self.logger.info(data.outputs)
            return False
        log_outputs = get_job_sops_var_dict_return["data"]
        self.logger.info(
            _("{group}.{job_service_name}：输出日志提取变量为：{log_outputs}").format(
                group=__group_name__, job_service_name=self.__class__.__name__, log_outputs=log_outputs
            )
        )
        data.set_outputs("log_outputs", log_outputs)
        self.logger.info(data.outputs)
        return True
