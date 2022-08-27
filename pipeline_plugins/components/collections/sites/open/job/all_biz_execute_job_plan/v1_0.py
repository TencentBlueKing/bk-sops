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
from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import (
    StringItemSchema,
    IntItemSchema,
    ArrayItemSchema,
    ObjectItemSchema,
    BooleanItemSchema,
)

from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from pipeline_plugins.components.collections.sites.open.job.all_biz_execute_job_plan.base_service import (
    BaseAllBizJobExecuteJobPlanService,
)
from pipeline_plugins.components.utils import (
    has_biz_set,
)

__group_name__ = _("作业平台(JOB)")


class AllBizJobExecuteJobPlanService(BaseAllBizJobExecuteJobPlanService):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="all_biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("作业模板 ID"),
                key="job_template_id",
                type="string",
                schema=StringItemSchema(description=_("作业模板 ID")),
            ),
            self.InputItem(
                name=_("执行方案 ID"),
                key="job_plan_id",
                type="string",
                schema=StringItemSchema(description=_("执行方案 ID")),
            ),
            self.InputItem(
                name=_("全局变量"),
                key="job_global_var",
                type="array",
                schema=ArrayItemSchema(
                    description=_("作业方案执行所需的全局变量列表"),
                    item_schema=ObjectItemSchema(
                        description=_("全局变量"),
                        property_schemas={
                            "type": IntItemSchema(description=_("变量类型，字符串(1) 命名空间(2) IP(3) 密码(4) 数组(5)")),
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
                name=_("IP Tag 分组"),
                key="is_tagged_ip",
                type="boolean",
                schema=BooleanItemSchema(description=_("是否对 IP 进行 Tag 分组")),
            ),
        ]

    def outputs_format(self):
        return super(AllBizJobExecuteJobPlanService, self).outputs_format() + [
            self.OutputItem(
                name=_("JOB全局变量"),
                key="log_outputs",
                type="object",
                schema=ObjectItemSchema(
                    description=_("输出日志中提取的全局变量"),
                    property_schemas={
                        "name": StringItemSchema(description=_("全局变量名称")),
                        "value": StringItemSchema(description=_("全局变量值")),
                    },
                ),
            ),
            self.OutputItem(
                name=_("JOB执行IP分组"),
                key="job_tagged_ip_dict",
                type="string",
                schema=StringItemSchema(description=_("根据JOB步骤执行标签获取的IP分组")),
            ),
        ]

    def schedule(self, data, parent_data, callback_data=None):
        config_data = data.get_one_of_inputs("all_biz_job_config")
        biz_cc_id = int(config_data.get("all_biz_cc_id"))
        if not has_biz_set(int(biz_cc_id)):
            self.biz_scope_type = JobBizScopeType.BIZ.value
        return super().schedule(data, parent_data, callback_data)


class AllBizJobExecuteJobPlanComponent(Component):
    name = _("业务集执行作业")
    code = "all_biz_execute_job_plan"
    bound_service = AllBizJobExecuteJobPlanService
    form = "%scomponents/atoms/job/all_biz_execute_job_plan/all_biz_execute_job_plan.js" % settings.STATIC_URL
    output_form = "%scomponents/atoms/job/all_biz_execute_job_plan/all_biz_execute_job_plan_output.js" % (
        settings.STATIC_URL
    )
