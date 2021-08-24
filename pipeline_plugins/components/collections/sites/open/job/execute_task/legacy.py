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

from .execute_task_base import JobExecuteTaskServiceBase
from pipeline.component_framework.component import Component
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


class JobExecuteTaskService(JobExecuteTaskServiceBase):
    need_get_sops_var = True

    def inputs_format(self):
        return super(JobExecuteTaskService, self).inputs_format()

    def outputs_format(self):
        return super(JobExecuteTaskService, self).outputs_format()

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
            "bk_callback_url": get_node_callback_url(self.id, getattr(self, "version", "")),
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
    output_form = "%scomponents/atoms/job/job_execute_task_output.js" % settings.STATIC_URL
    desc = _("跨业务选项打开时IP参数需要按照(云区域ID:IP)格式填写，否则会尝试从本业务下获取IP信息")
    version = "legacy"
