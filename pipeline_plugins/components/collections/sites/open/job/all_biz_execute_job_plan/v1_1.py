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
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import StringItemSchema

from gcloud.conf import settings
from packages.bkapi.jobv3_cloud.shortcuts import get_client_by_username
from pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.base_service import (
    BaseAllBizJobExecuteJobPlanService,
)

__group_name__ = _("作业平台(JOB)")

from pipeline_plugins.components.collections.sites.open.job.base import get_job_tagged_ip_dict_complex


class AllBizJobExecuteJobPlanService(BaseAllBizJobExecuteJobPlanService):
    need_is_tagged_ip = True

    def outputs_format(self):
        return super(AllBizJobExecuteJobPlanService, self).outputs_format() + [
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
            parent_data.get_one_of_inputs("tenant_id"),
            client,
            self.logger,
            job_instance_id,
            data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
            job_scope_type=self.biz_scope_type,
        )
        return result, tagged_ip_dict


class AllBizJobExecuteJobPlanComponent(Component):
    name = _("业务集执行作业")
    code = "all_biz_execute_job_plan"
    bound_service = AllBizJobExecuteJobPlanService
    form = "%scomponents/atoms/job/all_biz_execute_job_plan/v1_1/all_biz_execute_job_plan_v1_1.js" % settings.STATIC_URL
    version = "v1.1"
    output_form = "%scomponents/atoms/job/all_biz_execute_job_plan/all_biz_execute_job_plan_output.js" % (
        settings.STATIC_URL
    )
    desc = _("3. 业务集修改为下拉框获取，默认开启新版IP tag分组, 默认开启失败时提取变量")
