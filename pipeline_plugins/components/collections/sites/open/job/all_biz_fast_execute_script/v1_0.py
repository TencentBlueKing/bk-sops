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
from pipeline_plugins.components.collections.sites.open.job.all_biz_fast_execute_script.base_service import (
    BaseAllBizJobFastExecuteScriptService,
)
from pipeline_plugins.components.collections.sites.open.job.ipv6_base import GetJobTargetServerMixin
from pipeline_plugins.components.utils import get_node_callback_url

__group_name__ = _("作业平台(JOB)")


class AllBizJobFastExecuteScriptService(BaseAllBizJobFastExecuteScriptService, GetJobTargetServerMixin):
    need_get_sops_var = True

    biz_scope_type = JobBizScopeType.BIZ_SET.value

    def inputs_format(self):
        input_format_list = super().inputs_format()
        return input_format_list + [
            self.InputItem(
                name=_("IP Tag 分组"),
                key="is_tagged_ip",
                type="boolean",
                schema=BooleanItemSchema(description=_("是否对 IP 进行 Tag 分组")),
            ),
        ]

    def outputs_format(self):
        return super(AllBizJobFastExecuteScriptService, self).outputs_format() + [
            self.OutputItem(
                name=_("JOB执行IP分组"),
                key="job_tagged_ip_dict",
                type="string",
                schema=StringItemSchema(description=_("根据JOB步骤执行标签获取的IP分组")),
            ),
        ]

    def get_job_params(self, data, parent_data):
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        biz_cc_id = int(data.get_one_of_inputs("all_biz_cc_id"))
        executor = parent_data.get_one_of_inputs("executor")
        script_param = str(data.get_one_of_inputs("job_script_param"))
        job_script_timeout = data.get_one_of_inputs("job_script_timeout")
        ip_info = data.get_one_of_inputs("job_target_ip_table")

        result, target_server = self.get_target_server_biz_set(
            tenant_id, executor, ip_info, logger_handle=self.logger
        )
        if not result:
            raise Exception("[AllBizJobFastExecuteScriptService]->get_job_params 查询主机失败")

        job_kwargs = {
            "bk_scope_type": self.biz_scope_type,
            "bk_scope_id": str(biz_cc_id),
            "bk_biz_id": biz_cc_id,
            "account_alias": data.get_one_of_inputs("job_target_account"),
            "target_server": target_server,
            "callback_url": get_node_callback_url(self.root_pipeline_id, self.id, getattr(self, "version", "")),
        }

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
    version = "v1.0"
    form = "%scomponents/atoms/job/all_biz_fast_execute_script/v1_0.js" % settings.STATIC_URL
