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
from copy import deepcopy

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.io import (
    StringItemSchema,
    IntItemSchema,
    ArrayItemSchema,
    ObjectItemSchema,
    BooleanItemSchema,
)
from pipeline_plugins.components.collections.sites.open.job import JobService
from pipeline_plugins.components.utils import (
    get_job_instance_url,
    get_node_callback_url,
    loose_strip,
    get_biz_ip_from_frontend,
)
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobExecuteTaskServiceBase(JobService):
    """
    JobExecuteTaskServiceBase类是job.execute_task所有legacy与v1.0版本的父类;
    由于两个版本仅再前端处理逻辑上不同，所以两个版本的后端代码可以直接复用JobExecuteTaskServiceBase类
    """

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
                key="ip_is_exist",
                type="boolean",
                schema=BooleanItemSchema(description=_("是否做 IP 存在性校验，如果ip校验开关打开，校验通过的ip数量若减少，即返回错误")),
            ),
        ]

    def outputs_format(self):
        return super(JobExecuteTaskServiceBase, self).outputs_format() + [
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
        client.set_bk_api_ver("v2")
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        original_global_var = deepcopy(data.get_one_of_inputs("job_global_var"))
        global_vars = []
        ip_is_exist = data.get_one_of_inputs("ip_is_exist")
        biz_across = data.get_one_of_inputs("biz_across")

        for _value in original_global_var:
            val = loose_strip(_value["value"])
            # category为3,表示变量类型为IP
            if _value["category"] == 3:
                if biz_across:
                    result, ip_list = get_biz_ip_from_frontend(
                        ip_str=val,
                        executor=executor,
                        biz_cc_id=biz_cc_id,
                        data=data,
                        logger_handle=self.logger,
                        is_across=True,
                        ip_is_exist=ip_is_exist,
                        ignore_ex_data=True,
                    )

                    # 匹配不到云区域IP格式IP，尝试从当前业务下获取
                    if not result:
                        result, ip_list = get_biz_ip_from_frontend(
                            ip_str=val,
                            executor=executor,
                            biz_cc_id=biz_cc_id,
                            data=data,
                            logger_handle=self.logger,
                            is_across=False,
                            ip_is_exist=ip_is_exist,
                        )

                    if not result:
                        return False
                else:
                    result, ip_list = get_biz_ip_from_frontend(
                        ip_str=val,
                        executor=executor,
                        biz_cc_id=biz_cc_id,
                        data=data,
                        logger_handle=self.logger,
                        is_across=False,
                        ip_is_exist=ip_is_exist,
                    )
                    if not result:
                        return False

                if ip_list:
                    global_vars.append({"name": _value["name"], "ip_list": ip_list})
            else:
                global_vars.append({"name": _value["name"], "value": val})

        job_kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_job_id": data.get_one_of_inputs("job_task_id"),
            "global_vars": global_vars,
            "bk_callback_url": get_node_callback_url(self.root_pipeline_id, self.id, getattr(self, "version", "")),
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
