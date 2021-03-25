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

import traceback
import re
from functools import partial

from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow import StaticIntervalGenerator
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import (
    StringItemSchema,
    IntItemSchema,
)
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

# 作业状态码: 1.未执行; 2.正在执行; 3.执行成功; 4.执行失败; 5.跳过; 6.忽略错误; 7.等待用户; 8.手动结束;
# 9.状态异常; 10.步骤强制终止中; 11.步骤强制终止成功; 12.步骤强制终止失败
from pipeline_plugins.components.utils import batch_execute_func

JOB_SUCCESS = {3}
JOB_VAR_TYPE_IP = 2

# 全局变量标签中key-value分隔符
LOG_VAR_SEPARATOR = ":"

# 全局变量标签匹配正则（<>字符已转义），用于提取key{separator}value
LOG_VAR_LABEL_ESCAPE_RE = r"&lt;SOPS_VAR&gt;(.+?)&lt;/SOPS_VAR&gt;"

# 全局变量标签匹配正则，用于提取key{separator}value
LOG_VAR_LABEL_RE = r"<SOPS_VAR>(.+?)</SOPS_VAR>"

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

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
    # 逐行匹配以便打印全局变量所在行
    for index, log_line in enumerate(log_text.splitlines(), 1):
        sops_key_val_list = re.findall(LOG_VAR_LABEL_RE, log_line)
        sops_key_val_list.extend(re.findall(LOG_VAR_LABEL_ESCAPE_RE, log_line))
        if len(sops_key_val_list) == 0:
            continue
        for sops_key_val in sops_key_val_list:
            if LOG_VAR_SEPARATOR not in sops_key_val:
                continue
            sops_key, sops_val = sops_key_val.split(LOG_VAR_SEPARATOR, 1)
            # 限制变量名不为空
            if len(sops_key) == 0:
                continue
            sops_var_dict.update({sops_key: sops_val})
        service_logger.info(
            _("[{group}]提取日志中全局变量，匹配行[{index}]：[{line}]").format(group=__group_name__, index=index, line=log_line)
        )
    return sops_var_dict


def get_job_sops_var_dict(client, service_logger, job_instance_id, bk_biz_id):
    """
    解析作业日志：默认取每个步骤/节点的第一个ip_logs
    :param client:
    :param service_logger: 组件日志对象
    :param job_instance_id: 作业实例id
    :param bk_biz_id 业务ID
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
    - success { "result": True, "data": {"key1": "value1"}}
    - fail { "result": False, "message": message}
    """
    get_job_instance_status_kwargs = {
        "job_instance_id": job_instance_id,
        "bk_biz_id": bk_biz_id,
        "return_ip_result": True,
    }
    get_job_instance_status_return = client.jobv3.get_job_instance_status(get_job_instance_status_kwargs)
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
        if "step_ip_result_list" not in step_instance:
            continue
        for step_ip_result in step_instance["step_ip_result_list"]:
            get_job_instance_ip_log_kwargs = {
                "job_instance_id": job_instance_id,
                "bk_biz_id": bk_biz_id,
                "step_instance_id": step_instance["step_instance_id"],
                "bk_cloud_id": step_ip_result["bk_cloud_id"],
                "ip": step_ip_result["ip"],
            }
            get_job_instance_ip_log_kwargs_return = client.jobv3.get_job_instance_ip_log(get_job_instance_ip_log_kwargs)
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
    return {"result": True, "data": get_sops_var_dict_from_log_text(log_text, service_logger)}


class JobService(Service):
    __need_schedule__ = True

    reload_outputs = True

    need_get_sops_var = False

    def execute(self, data, parent_data):
        pass

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

        if status in JOB_SUCCESS:

            if self.reload_outputs:

                client = data.outputs.client

                # 全局变量重载
                get_var_kwargs = {
                    "bk_biz_id": data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
                    "job_instance_id": job_instance_id,
                }
                global_var_result = client.job.get_job_instance_global_var_value(get_var_kwargs)
                self.logger.info("get_job_instance_global_var_value return: {}".format(global_var_result))

                if not global_var_result["result"]:
                    message = job_handle_api_error(
                        "job.get_job_instance_global_var_value", get_var_kwargs, global_var_result,
                    )
                    self.logger.error(message)
                    data.outputs.ex_data = message
                    self.finish_schedule()
                    return False

                global_var_list = global_var_result["data"].get("job_instance_var_values", [])
                if global_var_list:
                    for global_var in global_var_list[-1]["step_instance_var_values"]:
                        if global_var["category"] != JOB_VAR_TYPE_IP:
                            data.set_outputs(global_var["name"], global_var["value"])

            # 无需提取全局变量的Service直接返回
            if not self.need_get_sops_var:
                self.finish_schedule()
                return True

            get_job_sops_var_dict_return = get_job_sops_var_dict(
                data.outputs.client,
                self.logger,
                job_instance_id,
                data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
            )
            if not get_job_sops_var_dict_return["result"]:
                self.logger.warning(
                    _("{group}.{job_service_name}: 提取日志失败，{message}").format(
                        group=__group_name__,
                        job_service_name=self.__class__.__name__,
                        message=get_job_sops_var_dict_return["message"],
                    )
                )
                data.set_outputs("log_outputs", {})
                self.finish_schedule()
                return True

            log_outputs = get_job_sops_var_dict_return["data"]
            self.logger.info(
                _("{group}.{job_service_name}：输出日志提取变量为：{log_outputs}").format(
                    group=__group_name__, job_service_name=self.__class__.__name__, log_outputs=log_outputs
                )
            )
            data.set_outputs("log_outputs", log_outputs)
            self.finish_schedule()
            return True
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

    def schedule(self, data, parent_data, callback_data=None):
        if hasattr(data.outputs, "requests_error") and data.outputs.requests_error:
            data.outputs.ex_data = "{}\n Get Result Error:\n".format(data.outputs.requests_error)
        else:
            data.outputs.ex_data = ""

        params_list = [
            {"bk_biz_id": data.inputs.biz_cc_id, "job_instance_id": job_id}
            for job_id in data.outputs.job_id_of_batch_execute
        ]
        client = get_client_by_user(parent_data.inputs.executor)

        batch_result_list = batch_execute_func(client.job.get_job_instance_log, params_list, interval_enabled=True)

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
