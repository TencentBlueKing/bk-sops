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

import base64
import traceback
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import (BooleanItemSchema, IntItemSchema,
                                   ObjectItemSchema, StringItemSchema)
from pipeline_plugins.components.collections.sites.open.job import JobService
from pipeline_plugins.components.collections.sites.open.job.base import \
    get_job_sops_var_dict
from pipeline_plugins.components.utils import (get_biz_ip_from_frontend,
                                               get_job_instance_url,
                                               get_node_callback_url)

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)

VERSION = "v2.0"

JOB_SUCCESS = {3}
JOB_VAR_TYPE_IP = 2

LOG_VAR_SEARCH_CONFIGS = [{"re": r"<SOPS_VAR>(.+?)</SOPS_VAR>", "kv_sep": ":"}]


class JobFastExecuteScriptService(JobService):
    need_get_sops_var = True
    process_action = None
    re_execute_cou = 0

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("脚本来源"),
                key="job_script_source",
                type="string",
                schema=StringItemSchema(
                    description=_("待执行的脚本来源，手动(manual)，业务脚本(general)，公共脚本(public)"),
                    enum=["manual", "general", "public"],
                ),
            ),
            self.InputItem(
                name=_("脚本类型"),
                key="job_script_type",
                type="string",
                schema=StringItemSchema(
                    description=_("待执行的脚本类型：shell(1) bat(2) perl(3) python(4) powershell(5)" "，仅在脚本来源为手动时生效"),
                    enum=["1", "2", "3", "4", "5"],
                ),
            ),
            self.InputItem(
                name=_("脚本内容"),
                key="job_content",
                type="string",
                schema=StringItemSchema(description=_("待执行的脚本内容，仅在脚本来源为手动时生效")),
            ),
            self.InputItem(
                name=_("公共脚本"),
                key="job_script_list_public",
                type="string",
                schema=StringItemSchema(description=_("待执行的公共脚本 ID，仅在脚本来源为公共脚本时生效")),
            ),
            self.InputItem(
                name=_("业务脚本"),
                key="job_script_list_general",
                type="string",
                schema=StringItemSchema(description=_("待执行的业务脚本 ID，仅在脚本来源为业务脚本时生效")),
            ),
            self.InputItem(
                name=_("脚本执行参数"),
                key="job_script_param",
                type="string",
                schema=StringItemSchema(description=_("脚本执行参数")),
            ),
            self.InputItem(
                name=_("是否允许跨业务"),
                key="job_across_biz",
                type="bool",
                schema=BooleanItemSchema(description=_("是否允许跨业务(跨业务需在作业平台添加白名单)，允许时，源文件IP格式需为【云区域ID:IP】")),
            ),
            self.InputItem(
                name=_("目标 IP"),
                key="job_ip_list",
                type="string",
                schema=StringItemSchema(description=_("执行脚本的目标机器 IP，多个用英文逗号 `,` 分隔")),
            ),
            self.InputItem(
                name=_("目标账户"),
                key="job_account",
                type="string",
                schema=StringItemSchema(description=_("执行脚本的目标机器账户")),
            ),
            self.InputItem(
                name=_("IP 存在性校验"),
                key="ip_is_exist",
                type="string",
                schema=BooleanItemSchema(description=_("是否做 IP 存在性校验，如果ip校验开关打开，校验通过的ip数量若减少，即返回错误")),
            ),
            self.InputItem(
                name=_("处理策略"),
                key="job_script_process_action",
                type="int",
                schema=IntItemSchema(description=_("失败自动处理等处理策略")),
            ),
            self.InputItem(
                name=_("执行历史ID"),
                key="job_script_history_tag",
                type="string",
                schema=StringItemSchema(description=_("在作业平台(JOB)的任务执行历史ID")),
            ),
            self.InputItem(
                name=_("动作"),
                key="job",
                type="string",
                schema=StringItemSchema(description=_("对任务执行历史的动作，仅在填写执行历史ID时有效")),
            ),
        ]

    def outputs_format(self):
        return super(JobFastExecuteScriptService, self).outputs_format() + [
            self.OutputItem(
                name=_("JOB全局变量"),
                key="log_outputs",
                type="dict",
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
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        self.client = client
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))
        biz_cc_id = data.get_one_of_inputs("biz_cc_id")
        self.biz_cc_id = biz_cc_id
        script_source = data.get_one_of_inputs("job_script_source")
        across_biz = data.get_one_of_inputs("job_across_biz")
        original_ip_list = data.get_one_of_inputs("job_ip_list")
        ip_is_exist = data.get_one_of_inputs("ip_is_exist")

        process_action = data.get_one_of_inputs("job_script_process_action")
        self.process_action = process_action
        job_script_history_instance_id = data.get_one_of_inputs("job_script_history_instance_id")

        if job_script_history_instance_id:

            history_job_kwargs = {"bk_biz_id": biz_cc_id, "job_instance_id": job_script_history_instance_id}
            history_job_result = client.jobv3.get_job_instance_status(history_job_kwargs)
            if not history_job_result["result"]:
                message = handle_api_error("job.get_job_instance_status", history_job_kwargs, history_job_result)
                self.logger.error(message)
                data.outputs.ex_data = message
                return False
            if history_job_result["data"]["job_instance"]["status"] in JOB_SUCCESS:
                data.outputs.client = client
                return True
        # 获取ip
        clean_result, ip_list = get_biz_ip_from_frontend(
            original_ip_list, executor, biz_cc_id, data, self.logger, across_biz, ip_is_exist
        )
        if not clean_result:
            return False

        job_kwargs = {
            "bk_biz_id": biz_cc_id,
            "account_alias": data.get_one_of_inputs("job_account"),
            "target_server": {"ip_list": ip_list},
            "callback_url": get_node_callback_url(self.id, getattr(self, "version", "")),
        }

        script_params = str(data.get_one_of_inputs("job_script_param"))

        if script_params:
            job_kwargs.update({"script_param": base64.b64encode(script_params.encode("utf-8")).decode("utf-8")})

        if script_source in ["general", "public"]:
            script_name = data.get_one_of_inputs("job_script_list_{}".format(script_source))

            kwargs = {"name": script_name}
            if script_source == "general":
                kwargs.update({"bk_biz_id": biz_cc_id})
                scripts = client.jobv3.get_script_list(kwargs)
            else:
                scripts = client.jobv3.get_public_script_list(kwargs)
            self.logger.info(scripts)

            select_script = None
            # JOB平台v3获取脚本列表接口使用模糊匹配，在这里需要进行精确匹配
            for script in scripts["data"]["data"]:
                if script_name == script["name"]:
                    select_script = script

            if not select_script:
                api_name = "jobv3.get_script_list" if script_source == "general" else "jobv3.get_public_script_list"
                message = job_handle_api_error(api_name, kwargs, scripts)
                message += "Data validation error：can't find a script exactly named {}.".format(script_name)
                self.logger.error(message)
                data.outputs.ex_data = message
                return False

            script_id = select_script["id"]
            job_kwargs.update({"script_id": script_id})

        else:
            script_language = int(data.get_one_of_inputs("job_script_type"))
            script_content = base64.b64encode(data.get_one_of_inputs("job_content").encode("utf-8")).decode("utf-8")
            job_kwargs.update({"script_language": script_language, "script_content": script_content})
        self.logger.info(job_kwargs)
        job_result = client.jobv3.fast_execute_script(job_kwargs)
        self.logger.info(job_result)
        if job_result["result"]:
            self.logger.info("api调用成功了")
            job_instance_id = job_result["data"]["job_instance_id"]
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result["data"]["job_instance_name"]
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.client = client
            return True
        else:
            self.logger.info("api调用失败了")
            self.logger.info(job_result)
            message = job_handle_api_error("jobv3.fast_execute_script", job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

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
                self.logger.info("走了这里")
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
                    self.re_execute_cou = 0
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
                self.logger.info("走到这里还是失败了")
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


class FastExecuteScriptComponent(Component):
    name = "快速执行脚本"
    version = "v2.0"
    code = "job_fast_execute_script"
    bound_service = JobFastExecuteScriptService
    form = "{static_url}components/atoms/job/fast_execute_script/{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
