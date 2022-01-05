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
import re
from copy import deepcopy
from functools import partial

from django.utils import translation
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
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.components.collections.sites.open.job import Jobv3Service
from pipeline_plugins.components.utils import (
    get_job_instance_url,
    get_node_callback_url,
    loose_strip,
    plat_ip_reg,
)
from pipeline_plugins.components.query.sites.open.job import JOBV3_VAR_CATEGORY_IP

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)

plat_reg = re.compile(r"(\d+:)")


class AllBizJobExecuteJobPlanService(Jobv3Service):
    need_get_sops_var = True

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

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        config_data = data.get_one_of_inputs("all_biz_job_config")
        biz_cc_id = config_data.get("all_biz_cc_id")
        is_tagged_ip = config_data.get("is_tagged_ip", False)
        data.inputs.biz_cc_id = biz_cc_id
        data.inputs.is_tagged_ip = is_tagged_ip
        original_global_var = deepcopy(config_data.get("job_global_var")) or []
        global_var_list = []

        for _value in original_global_var:
            # 3-IP
            val = loose_strip(_value["value"])
            if _value["type"] == JOBV3_VAR_CATEGORY_IP:

                plat_ip = [match.group() for match in plat_ip_reg.finditer(val)]
                ip_list = [{"ip": _ip.split(":")[1], "bk_cloud_id": _ip.split(":")[0]} for _ip in plat_ip]

                plats = plat_reg.findall(val)
                if len(ip_list) != len(plats):
                    data.outputs.ex_data = _("IP 校验失败，请确认输入的 IP {} 是否合法".format(val))
                    return False

                if ip_list:
                    global_var_list.append({"id": _value["id"], "server": {"ip_list": ip_list}})
            else:
                global_var_list.append({"id": _value["id"], "value": val})

        job_kwargs = {
            "bk_biz_id": biz_cc_id,
            "job_plan_id": config_data.get("job_plan_id"),
            "global_var_list": global_var_list,
            "callback_url": get_node_callback_url(self.root_pipeline_id, self.id, getattr(self, "version", "")),
        }

        job_result = client.jobv3.execute_job_plan(job_kwargs)
        self.logger.info("job_result: {result}, job_kwargs: {kwargs}".format(result=job_result, kwargs=job_kwargs))
        if job_result["result"]:
            job_instance_id = job_result["data"]["job_instance_id"]
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result["data"]["job_instance_name"]
            data.outputs.client = client
            data.outputs.biz_cc_id = biz_cc_id
            return True
        else:
            message = job_handle_api_error("jobv3.execute_job_plan", job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False


class AllBizJobExecuteJobPlanComponent(Component):
    name = _("全业务执行作业")
    code = "all_biz_execute_job_plan"
    bound_service = AllBizJobExecuteJobPlanService
    form = "%scomponents/atoms/job/all_biz_execute_job_plan/all_biz_execute_job_plan.js" % settings.STATIC_URL
    output_form = "%scomponents/atoms/job/all_biz_execute_job_plan/all_biz_execute_job_plan_output.js" % (
        settings.STATIC_URL
    )
