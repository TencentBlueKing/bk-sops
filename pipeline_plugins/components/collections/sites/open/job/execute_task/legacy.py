# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from functools import partial
from copy import deepcopy

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from gcloud.utils.ip import get_ip_by_regex
from pipeline.core.flow.io import (
    StringItemSchema,
    IntItemSchema,
    ArrayItemSchema,
    ObjectItemSchema,
    BooleanItemSchema,
)
from pipeline_plugins.components.collections.sites.open.job import JobService
from pipeline.component_framework.component import Component
from pipeline_plugins.components.utils import (
    cc_get_ips_info_by_str,
    get_job_instance_url,
    get_node_callback_url,
    loose_strip,
)
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobExecuteTaskService(JobService):
    need_get_sops_var = True

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
                key="ip_is_exit",
                type="string",
                schema=BooleanItemSchema(description=_("是否做 IP 存在性校验，如果ip校验开关打开，校验通过的ip数量若减少，即返回错误")),
            ),
        ]

    def outputs_format(self):
        return super(JobExecuteTaskService, self).outputs_format() + [
            self.OutputItem(
                name=_("JOB全局变量"),
                key="log_outputs",
                type="dict",
                schema=ObjectItemSchema(
                    description=_("输出日志中提取的全局变量"),
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
        client.set_bk_api_ver("v2")
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        original_global_var = deepcopy(data.get_one_of_inputs("job_global_var"))
        global_vars = []
        ip_is_exit = data.get_one_of_inputs("ip_is_exit")

        for _value in original_global_var:
            # 3-IP
            val = loose_strip(_value["value"])
            if _value["category"] == 3:
                var_ip = cc_get_ips_info_by_str(username=executor, biz_cc_id=biz_cc_id, ip_str=val, use_cache=False)
                ip_list = [{"ip": _ip["InnerIP"], "bk_cloud_id": _ip["Source"]} for _ip in var_ip["ip_result"]]
                if val and not ip_list:
                    data.outputs.ex_data = _("无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法")
                    return False
                # 如果ip校验开关打开，校验通过的ip数量减少，返回错误
                input_ip_list = get_ip_by_regex(val)
                difference_ip_list = list(set(input_ip_list).difference(set([ip_item["ip"] for ip_item in ip_list])))
                if ip_is_exit and len(ip_list) != len(input_ip_list):
                    data.outputs.ex_data = _("IP 校验失败，请确认输入的 IP {} 是否合法".format(",".join(difference_ip_list)))
                    return False
                if ip_list:
                    global_vars.append({"name": _value["name"], "ip_list": ip_list})
            else:
                global_vars.append({"name": _value["name"], "value": val})

        job_kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_job_id": data.get_one_of_inputs("job_task_id"),
            "global_vars": global_vars,
            "bk_callback_url": get_node_callback_url(self.id),
        }

        job_result = client.job.execute_job(job_kwargs)
        self.logger.info("job_result: {result}, job_kwargs: {kwargs}".format(result=job_result, kwargs=job_kwargs))
        if job_result["result"]:
            job_instance_id = job_result["data"]["job_instance_id"]
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result["data"]["job_instance_name"]
            data.outputs.client = client
            return True
        else:
            message = job_handle_api_error("job.execute_job", job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

    def schedule(self, data, parent_data, callback_data=None):
        return super(JobExecuteTaskService, self).schedule(data, parent_data, callback_data)


class JobExecuteTaskComponent(Component):
    name = _("执行作业")
    code = "job_execute_task"
    bound_service = JobExecuteTaskService
    form = "%scomponents/atoms/job/job_execute_task.js" % settings.STATIC_URL
