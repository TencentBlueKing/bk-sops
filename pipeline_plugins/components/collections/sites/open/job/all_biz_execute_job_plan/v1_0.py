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
from pipeline.core.flow.io import BooleanItemSchema, StringItemSchema

from gcloud.conf import settings
from pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.base_service import (
    BaseAllBizJobExecuteJobPlanService,
)

__group_name__ = _("作业平台(JOB)")


class AllBizJobExecuteJobPlanService(BaseAllBizJobExecuteJobPlanService):
    def inputs_format(self):
        inputs_format_list = super(AllBizJobExecuteJobPlanService, self).inputs_format()
        return inputs_format_list + [
            self.InputItem(
                name=_("IP 存在性校验"),
                key="ip_is_exist",
                type="boolean",
                schema=BooleanItemSchema(
                    description=_("是否做 IP 存在性校验，如果ip校验开关打开，校验通过的ip数量若减少，即返回错误")
                ),
            ),
            self.InputItem(
                name=_("IP Tag 分组"),
                key="is_tagged_ip",
                type="boolean",
                schema=BooleanItemSchema(description=_("是否对 IP 进行 Tag 分组")),
            ),
        ]

    def outputs_format(self):
        return super(AllBizJobExecuteJobPlanService, self).outputs_format() + [
            self.OutputItem(
                name=_("JOB执行IP分组"),
                key="job_tagged_ip_dict",
                type="string",
                schema=StringItemSchema(description=_("根据JOB步骤执行标签获取的IP分组")),
            ),
        ]


class AllBizJobExecuteJobPlanComponent(Component):
    name = _("业务集执行作业")
    code = "all_biz_execute_job_plan"
    bound_service = AllBizJobExecuteJobPlanService
    form = "%scomponents/atoms/job/all_biz_execute_job_plan/all_biz_execute_job_plan.js" % settings.STATIC_URL
    output_form = "%scomponents/atoms/job/all_biz_execute_job_plan/all_biz_execute_job_plan_output.js" % (
        settings.STATIC_URL
    )
