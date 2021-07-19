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

import base64
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.io import (
    StringItemSchema,
    ObjectItemSchema,
    BooleanItemSchema,
)
from pipeline.component_framework.component import Component
from pipeline_plugins.components.collections.sites.open.job.base import (
    JobFailAutoProcessService,
    CreateGloablVarKwMixin,
)
from pipeline_plugins.components.utils import get_job_instance_url, get_node_callback_url, get_biz_ip_from_frontend

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)
VERSION = "v2.0"


class FastExecuteScriptService(JobFailAutoProcessService, CreateGloablVarKwMixin):
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
        job_history_id = data.get_one_of_inputs("job_history_id")
        if job_history_id:
            return self.history_operate_function(self, data, parent_data)
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))
        biz_cc_id = parent_data.inputs.biz_cc_id
        script_source = data.get_one_of_inputs("job_script_source")
        original_ip_list = data.get_one_of_inputs("job_ip_list")
        ip_is_exist = data.get_one_of_inputs("ip_is_exist")
        across_biz = data.get_one_of_inputs("job_across_biz", False)

        # 获取 IP
        clean_result, ip_list = get_biz_ip_from_frontend(
            original_ip_list, executor, biz_cc_id, data, self.logger, across_biz, ip_is_exist=ip_is_exist
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
        job_result = client.jobv3.fast_execute_script(job_kwargs)
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


class FastExecuteScriptComponent(Component):
    name = _("快速执行脚本")
    code = "job_fast_execute_script"
    bound_service = FastExecuteScriptService
    version = "v2.0"
    form = "%scomponents/atoms/job/fast_execute_script/v2_0.js" % settings.STATIC_URL
    desc = (
        "插件版本legacy会依据脚本id来执行脚本，JOB平台脚本上线版本变动仍执行原来脚本。\n"
        "插件版本v1.0会依据脚本名称来执行脚本，自动同步JOB平台当前上线版本进行执行。\n"
        "插件版本v2.0新增失败自动处理功能，自动向JOB平台发起一次重试/忽略操作。\n"
        "注：插件版本v1.0和v2.0中跨业务执行脚本时需要在作业平台添加白名单"
    )
