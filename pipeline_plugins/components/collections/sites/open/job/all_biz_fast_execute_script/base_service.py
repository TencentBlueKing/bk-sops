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
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from pipeline.core.flow.io import ArrayItemSchema, IntItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.components.collections.sites.open.job import JobService
from pipeline_plugins.components.utils import get_job_instance_url, has_biz_set

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class BaseAllBizJobFastExecuteScriptService(JobService):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务集 ID"),
                key="all_biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("当前操作业务集 ID")),
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
                name=_("脚本执行参数"),
                key="job_script_param",
                type="string",
                schema=StringItemSchema(description=_("脚本执行参数")),
            ),
            self.InputItem(
                name=_("目标账户"),
                key="job_target_account",
                type="string",
                schema=StringItemSchema(description=_("执行脚本的目标机器账户")),
            ),
            self.InputItem(
                name=_("脚本超时时间"), key="job_target_account", type="int", schema=IntItemSchema(description=_("脚本超时时间")),
            ),
            self.InputItem(
                name=_("脚本超时时间"), key="job_target_account", type="int", schema=IntItemSchema(description=_("脚本超时时间")),
            ),
            self.InputItem(
                name=_("执行目标信息"),
                key="job_target_ip_table",
                type="array",
                schema=ArrayItemSchema(
                    description=_("执行目标信息"),
                    item_schema=ObjectItemSchema(
                        description=_("单条目标 IP 信息"),
                        property_schemas={
                            "bk_cloud_id": StringItemSchema(description=_("管控区域ID, 默认为0")),
                            "ip": StringItemSchema(description=_("待执行目标机器 IP，多IP请使用;分隔")),
                        },
                    ),
                ),
            ),
        ]

    def outputs_format(self):
        return super(BaseAllBizJobFastExecuteScriptService, self).outputs_format() + [
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
            )
        ]

    def schedule(self, data, parent_data, callback_data=None):
        biz_cc_id = int(data.get_one_of_inputs("all_biz_cc_id"))
        if not has_biz_set(int(biz_cc_id)):
            self.biz_scope_type = JobBizScopeType.BIZ.value
        return super().schedule(data, parent_data, callback_data)

    def get_job_params(self, data, parent_data):
        """
        子类需要重新编写实现
        @param data:
        @return:
        """
        return {}

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))
        biz_cc_id = int(data.get_one_of_inputs("all_biz_cc_id"))
        data.inputs.biz_cc_id = biz_cc_id

        if not has_biz_set(int(biz_cc_id)):
            self.biz_scope_type = JobBizScopeType.BIZ.value

        job_kwargs = self.get_job_params(data, parent_data)
        job_result = client.jobv3.fast_execute_script(job_kwargs)
        self.logger.info("job_result: {result}, job_kwargs: {kwargs}".format(result=job_result, kwargs=job_kwargs))
        if job_result["result"]:
            job_instance_id = job_result["data"]["job_instance_id"]
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result["data"]["job_instance_name"]
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.client = client
            return True
        else:
            message = job_handle_api_error("jobv3.fast_execute_script", job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False
