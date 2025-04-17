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

import base64

from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import BooleanItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from packages.bkapi.jobv3_cloud.shortcuts import get_client_by_username
from pipeline_plugins.components.collections.sites.open.job.all_biz_fast_execute_script.base_service import (
    BaseAllBizJobFastExecuteScriptService,
)
from pipeline_plugins.components.collections.sites.open.job.base import get_job_tagged_ip_dict_complex
from pipeline_plugins.components.collections.sites.open.job.ipv6_base import GetJobTargetServerMixin
from pipeline_plugins.components.utils import get_node_callback_url

__group_name__ = _("作业平台(JOB)")


class AllBizJobFastExecuteScriptService(BaseAllBizJobFastExecuteScriptService, GetJobTargetServerMixin):
    need_get_sops_var = True
    need_is_tagged_ip = True

    biz_scope_type = JobBizScopeType.BIZ_SET.value

    def inputs_format(self):
        input_format_list = super().inputs_format()
        return input_format_list + [
            self.InputItem(
                name=_("滚动执行"),
                key="job_rolling_execute",
                type="boolean",
                schema=BooleanItemSchema(description=_("是否开启滚动执行")),
            ),
            self.InputItem(
                name=_("滚动策略"),
                key="job_rolling_expression",
                type="string",
                schema=StringItemSchema(description=_("滚动策略，仅在滚动执行开启时生效")),
            ),
            self.InputItem(
                name=_("滚动机制"),
                key="job_rolling_mode",
                type="string",
                schema=StringItemSchema(description=_("滚动机制，仅在滚动执行开启时生效")),
            ),
        ]

    def outputs_format(self):
        return super(AllBizJobFastExecuteScriptService, self).outputs_format() + [
            self.OutputItem(
                name=_("JOB执行IP分组"),
                key="job_tagged_ip_dict",
                type="string",
                schema=StringItemSchema(
                    description=_(
                        '按照执行结果将 IP 进行分组：1. 使用 job_tagged_ip_dict["value"]["SUCCESS"]["TAGS"]["ALL"]  获取「执行成功」的 IP， '
                        "ALL 代表所有 IP，可指定分组名获取特定分组的 IP ；"
                        '2. 使用 job_tagged_ip_dict["value"]["SCRIPT_NOT_ZERO_EXIT_CODE"]["TAGS"]["ALL"]'
                        " 获取「脚本返回值非零」的 IP"
                    )
                ),
            ),
        ]

    def is_need_log_outputs_even_fail(self, data):
        return True

    def get_tagged_ip_dict(self, data, parent_data, job_instance_id):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        result, tagged_ip_dict = get_job_tagged_ip_dict_complex(
            parent_data.inputs.tenant_id,
            client,
            self.logger,
            job_instance_id,
            data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
            job_scope_type=self.biz_scope_type,
        )
        return result, tagged_ip_dict

    def get_job_params(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        biz_cc_id = int(data.get_one_of_inputs("all_biz_cc_id"))
        script_param = str(data.get_one_of_inputs("job_script_param"))
        job_script_timeout = data.get_one_of_inputs("job_script_timeout")
        ip_info = data.get_one_of_inputs("job_target_ip_table")
        job_rolling_config = data.get_one_of_inputs("job_rolling_config", {})
        job_rolling_execute = job_rolling_config.get("job_rolling_execute", None)

        # 拼装ip_list， bk_cloud_id为空则值为0
        result, target_server = self.get_target_server_biz_set(
            tenant_id, executor, ip_info, logger_handle=self.logger
        )

        if not result:
            raise Exception("[AllBizJobFastExecuteScriptService]->get_job_params 查询主机失败, 请检查ip配置是否正确")

        job_kwargs = {
            "bk_scope_type": self.biz_scope_type,
            "bk_scope_id": str(biz_cc_id),
            "bk_biz_id": biz_cc_id,
            "account_alias": data.get_one_of_inputs("job_target_account"),
            "target_server": target_server,
            "callback_url": get_node_callback_url(self.root_pipeline_id, self.id, getattr(self, "version", "")),
        }

        # 如果开启了滚动执行，填充rolling_config配置
        if job_rolling_execute:
            # 滚动策略
            job_rolling_expression = job_rolling_config.get("job_rolling_expression")
            # 滚动机制
            job_rolling_mode = job_rolling_config.get("job_rolling_mode")
            rolling_config = {"expression": job_rolling_expression, "mode": job_rolling_mode}
            job_kwargs.update({"rolling_config": rolling_config})

        if script_param:
            job_kwargs.update({"script_param": base64.b64encode(script_param.encode("utf-8")).decode("utf-8")})
        if job_script_timeout:
            job_kwargs.update({"timeout": int(job_script_timeout)})

        job_kwargs.update(
            {
                "script_language": data.get_one_of_inputs("job_script_type"),
                "script_content": base64.b64encode(data.get_one_of_inputs("job_content").encode("utf-8")).decode(
                    "utf-8"
                ),
            }
        )

        return job_kwargs


class AllBizJobFastExecuteScriptComponent(Component):
    name = _("业务集快速执行脚本")
    code = "all_biz_job_fast_execute_script"
    bound_service = AllBizJobFastExecuteScriptService
    version = "v1.1"
    form = "%scomponents/atoms/job/all_biz_fast_execute_script/v1_1.js" % settings.STATIC_URL
    desc = _("业务集快速执行脚本，新增滚动执行功能,需要作业平台版本>=V3.6.0.0")
