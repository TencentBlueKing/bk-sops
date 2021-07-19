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

from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.io import (
    StringItemSchema,
    IntItemSchema,
    ArrayItemSchema,
    ObjectItemSchema,
    BooleanItemSchema,
)
from pipeline_plugins.components.collections.sites.open.job.base import (
    JobFailAutoProcessService,
    CreateGloablVarKwMixin,
)
from pipeline.component_framework.component import Component
from pipeline_plugins.components.utils import (
    get_job_instance_url,
    get_node_callback_url,
)
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)
VERSION = "v1.0"


class ExecuteTaskService(JobFailAutoProcessService, CreateGloablVarKwMixin):
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
                key="job_task_id",
                type="string",
                schema=StringItemSchema(description=_("需要执行的 JOB 作业模板 ID")),
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
                name=_("失败后自动处理策略"),
                key="fail_auto_process_action",
                type="string",
                schema=StringItemSchema(description=_("执行失败后的自动处理策略（默认值：忽略错误）")),
            ),
            self.InputItem(
                name=_("历史任务ID"),
                key="job_history_id",
                type="string",
                schema=StringItemSchema(description=_("在作业平台(JOB)执行过的历史任务实例ID")),
            ),
            self.InputItem(
                name=_("在历史任务上执行对动作"),
                key="job_history_auto_process_action",
                type="string",
                schema=StringItemSchema(description=_("对所填历史任务实例ID执行的动作（默认值：继承成功状态或忽略错误）")),
            ),
        ]

    def outputs_format(self):
        return super().outputs_format() + [
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
        job_history_id = data.get_one_of_inputs("job_history_id")
        if job_history_id:
            return self.history_operate_function(self, data, parent_data)
        executor = parent_data.get_one_of_inputs("executor")
        biz_cc_id = parent_data.inputs.biz_cc_id
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        global_vars = self.globalvars(data, parent_data)
        job_plan_id = data.get_one_of_inputs("job_task_id")
        bk_callback_url = get_node_callback_url(self.id, getattr(self, "version", ""))

        job_kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_job_id": job_plan_id,
            "global_var_list": global_vars,
            "callback_url": bk_callback_url,
        }

        job_result = client.jobv3.execute_job_plan(job_kwargs)

        if job_result["result"]:
            job_instance_id = job_result["data"]["job_instance_id"]
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result["data"]["job_instance_name"]
            data.outputs.client = client
            return True
        else:
            message = job_handle_api_error("jobv3.execute_job_plan", job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

    def schedule(self, data, parent_data, callback_data=None):
        return super().schedule(self, data, parent_data, callback_data)


class ExecuteTaskComponent(Component):
    name = _("执行作业")
    code = "job_execute_task"
    bound_service = ExecuteTaskService
    form = "{static_url}components/atoms/job/execute_task/v1_0.js".format(
        static_url=settings.STATIC_URL,
    )
    version = VERSION
