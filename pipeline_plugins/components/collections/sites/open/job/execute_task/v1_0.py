# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


import traceback
from copy import deepcopy
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import (ArrayItemSchema, BooleanItemSchema,
                                   IntItemSchema, ObjectItemSchema,
                                   StringItemSchema)
from pipeline_plugins.components.collections.sites.open.job import JobService
from pipeline_plugins.components.collections.sites.open.job.base import \
    get_job_sops_var_dict
from pipeline_plugins.components.utils import (get_biz_ip_from_frontend,
                                               get_job_instance_url,
                                               get_node_callback_url,
                                               loose_strip)

"""
# 自动处理策略fail_auto_process_code参照表
fail_auto_process_code = [
    (0, '忽略'),
    (1, '失败的IP重试'),
    (2, '全部重试'),
]
# 在历史任务上执行动作job_history_instance_action参照表
job_history_instance_action = [
    (0, '忽略'),
    (1, '失败的IP重试'),
    (2, '全部重试'),
    (3, '继承成功状态')
]
"""

VERSION = "v1.0"

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


JOB_SUCCESS = {3}
JOB_VAR_TYPE_IP = 2

LOG_VAR_SEARCH_CONFIGS = [{"re": r"<SOPS_VAR>(.+?)</SOPS_VAR>", "kv_sep": ":"}]


class JobExecuteTaskService(JobService):
    need_get_sops_var = True
    process_action = None

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("作业模板 ID"),
                key="job_template_id",
                type="string",
                schema=StringItemSchema(description=_("需要执行的 JOB 作业模板 ID")),
            ),
            self.InputItem(
                name=_("执行方案 ID"),
                key="job_task_id",
                type="string",
                schema=StringItemSchema(description=_("需要执行的 JOB 作业执行方案 ID")),
            ),
            self.InputItem(
                name=_("全局变量"),
                key="job_global_var",
                type="array",
                schema=ArrayItemSchema(
                    description=_("作业模板执行所需的全局变量列表"),
                    item_schema=ObjectItemSchema(
                        description=_("全局变量"),
                        property_schemas={
                            "category": IntItemSchema(description=_("变量类型，云参(1) 上下文参数(2) IP(3)")),
                            "name": StringItemSchema(description=_("变量名")),
                            "value": StringItemSchema(description=_("变量值")),
                        },
                    ),
                ),
            ),
            self.InputItem(
                name=_("IP 存在性校验"),
                key="ip_is_exist",
                type="boolean",
                schema=BooleanItemSchema(description=_("是否做 IP 存在性校验，如果ip校验开关打开，校验通过的ip数量若减少，即返回错误")),
            ),
            self.InputItem(
                name=_("处理策略"), key="process_action", type="int", schema=IntItemSchema(description=_("失败自动处理等处理策略"))
            ),
            self.InputItem(
                name=_("执行历史ID"),
                key="job_history_instance_id",
                type="string",
                schema=StringItemSchema(description=_("在作业平台(JOB)的任务执行历史ID")),
            ),
            self.InputItem(
                name=_("动作"),
                key="job_history_instance_action",
                type="string",
                schema=StringItemSchema(description=_("对任务执行历史的动作，仅在填写执行历史ID时有效")),
            ),
        ]

    def outputs_format(self):
        return super(JobExecuteTaskService, self).outputs_format() + [
            self.OutputItem(
                name=_("JOB全局变量"),
                key="log_outputs",
                type="object",
                schema=ObjectItemSchema(
                    description=_(
                        "输出日志中提取的全局变量，日志中形如 <SOPS_VAR>key:val</SOPS_VAR> 的变量会被提取到 log_outputs['key'] 中，值为 val"
                    ),
                    property_schemas={
                        "name": StringItemSchema(description=_("全局变量名称")),
                        "value": StringItemSchema(description=_("全局变量值")),
                    },
                ),
            ),
        ]

    def execute(self, data, parent_data):
        self.process_action = data.get_one_of_inputs("process_action")
        job_history_instance_id = data.get_one_of_inputs("job_history_instance_id")

        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        self.client = client
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        biz_cc_id = str(data.get_one_of_inputs("biz_cc_id"))
        self.biz_cc_id = biz_cc_id
        original_global_var = deepcopy(data.get_one_of_inputs("job_global_var"))
        global_var_list = []
        ip_is_exist = data.get_one_of_inputs("ip_is_exist")
        biz_across = data.get_one_of_inputs("biz_across")

        # 历史ID操作
        if job_history_instance_id:
            job_kwargs = {
                "bk_biz_id": biz_cc_id,
                "job_instance_id": job_history_instance_id,
                "callback_url": get_node_callback_url(self.id, getattr(self, "version", "")),
            }

            job_result = client.jobv3.get_job_instance_status(job_kwargs)
            self.logger.info(job_kwargs, job_result)
            if not job_result["result"]:
                message = handle_api_error("job.get_job_instance_status", job_kwargs, job_result)
                self.logger.error(message)
                data.ouputs.ex_data = message
                return False
            if job_result["data"]["job_instance"]["status"] in JOB_SUCCESS:
                data.outputs.client = client
                return True

        for _value in original_global_var:
            val = loose_strip(_value["value"])
            # category为3,表示变量类型为IP
            if _value["category"] == 3:
                if biz_across:
                    result, ip_list = get_biz_ip_from_frontend(
                        ip_str=val,
                        executor=executor,
                        biz_cc_id=biz_cc_id,
                        data=data,
                        logger_handle=self.logger,
                        is_across=True,
                        ip_is_exist=ip_is_exist,
                        ignore_ex_data=True,
                    )

                    # 匹配不到云区域IP格式IP，尝试从当前业务下获取
                    if not result:
                        result, ip_list = get_biz_ip_from_frontend(
                            ip_str=val,
                            executor=executor,
                            biz_cc_id=biz_cc_id,
                            data=data,
                            logger_handle=self.logger,
                            is_across=False,
                            ip_is_exist=ip_is_exist,
                        )

                    if not result:
                        return False
                else:
                    result, ip_list = get_biz_ip_from_frontend(
                        ip_str=val,
                        executor=executor,
                        biz_cc_id=biz_cc_id,
                        data=data,
                        logger_handle=self.logger,
                        is_across=False,
                        ip_is_exist=ip_is_exist,
                    )
                    if not result:
                        return False

                if ip_list:
                    global_var_list.append({"name": _value["name"], "server": {"ip_list": ip_list}})
            else:
                global_var_list.append({"name": _value["name"], "value": val})

        job_kwargs = {
            "bk_biz_id": biz_cc_id,
            "job_plan_id": data.get_one_of_inputs("job_task_id"),
            "global_var_list": global_var_list,
            "callback_url": get_node_callback_url(self.id, getattr(self, "version", "")),
        }
        job_result = client.jobv3.execute_job_plan(job_kwargs)
        self.logger.info("job_result: {result}, job_kwargs: {kwargs}".format(result=job_result, kwargs=job_kwargs))

        if job_result["result"]:
            job_instance_id = job_result["data"]["job_instance_id"]
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result["data"]["job_instance_name"]
            data.outputs.client = client
            return True

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
                        "job.get_job_instance_global_var_value",
                        get_var_kwargs,
                        global_var_result,
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
            # 开始重试策略
            self.logger.info("被调度了")
            if not self.process_action:
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
                self.finish_schedule()
                return False
            else:
                # 进入重试策略,拿着job_instance_id去拿所有的步骤id,然后拿着步骤id和process_action进行重试操作 get_job_instance_status
                if self.re_execute_cou == 3:
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
                    self.finish_schedule()
                    return False
                self.re_execute_cou += 1
                job_kwargs = {"bk_biz_id": self.biz_cc_id, "job_instance_id": job_instance_id}
                job_result = self.client.jobv3.get_job_instance_status(job_kwargs)
                if not job_result["result"]:
                    message = job_handle_api_error("jobv3.get_job_instance_status", job_result, job_kwargs)
                    self.logger.error(message)
                    data.outputs.ex_data = "任务重试失败，message = {message}.".format(message=message)
                    return False
                step_instance_list = job_result["data"]["step_instance_list"]
                operate_step_kwargs = [
                    {
                        "bk_biz_id": self.biz_cc_id,
                        "job_instance_id": job_instance_id,
                        "step_instance_id": _step["step_instance_id"],
                        "operation_code": self.process_action,
                    }
                    for _step in step_instance_list
                    if _step["status"] not in JOB_SUCCESS
                ]

                re_operate_sucess = True
                for job_kwargs in operate_step_kwargs:
                    job_result = self.client.jobv3.operate_step_instance(job_kwargs)
                    if not job_result["result"]:
                        message = job_handle_api_error("jobv3.get_job_instance_status", job_result, job_kwargs)
                        self.logger.error(message)
                        data.outputs.ex_data = "任务重试失败，message = {message}.".format(message=message)
                        return False
                    if job_result["message"] != "success":
                        re_operate_sucess = False

                if re_operate_sucess:
                    data.set_outputs("重试成功！", job_instance_id)
                    self.finish_schedule()
                    return True
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
                self.finish_schedule()
                return False


class JobExecuteTaskComponent(Component):
    name = _("执行作业")
    code = "job_execute_task"
    bound_service = JobExecuteTaskService
    version = "v1.0"
    form = "%scomponents/atoms/job/job_execute_task/v1_0.js" % settings.STATIC_URL
    output_form = "%scomponents/atoms/job/job_execute_task_output.js" % settings.STATIC_URL
    desc = _("跨业务选项打开时IP参数需要按照(云区域ID:IP)格式填写，否则会尝试从本业务下获取IP信息")
