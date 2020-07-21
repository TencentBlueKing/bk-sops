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

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import (
    StringItemSchema,
    IntItemSchema,
)
from pipeline.component_framework.component import Component
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobCronTaskService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("定时作业名称"),
                key="job_cron_name",
                type="string",
                schema=StringItemSchema(description=_("待创建的定时作业名称")),
            ),
            self.InputItem(
                name=_("定时规则"),
                key="job_cron_expression",
                type="string",
                schema=StringItemSchema(description=_("待创建的定时作业定时规则")),
            ),
            self.InputItem(
                name=_("定时作业状态"),
                key="job_cron_status",
                type="string",
                schema=IntItemSchema(description=_("待创建的定时作业状态，暂停(1) 启动(2)"), enum=[1, 2]),
            ),
        ]

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("定时作业ID"), key="cron_id", type="int", schema=IntItemSchema(description=_("成功创建的定时作业 ID")),
            ),
            self.OutputItem(
                name=_("定时作业状态"), key="status", type="string", schema=StringItemSchema(description=_("成功创建的定时作业状态")),
            ),
        ]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        biz_cc_id = parent_data.get_one_of_inputs("biz_cc_id")
        job_cron_job_id = data.get_one_of_inputs("job_cron_job_id")
        job_cron_name = data.get_one_of_inputs("job_cron_name")
        job_cron_expression = data.get_one_of_inputs("job_cron_expression")
        job_kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_job_id": job_cron_job_id,
            "cron_name": job_cron_name,
            "cron_expression": job_cron_expression,
        }
        client = get_client_by_user(executor)

        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        # 新建作业
        job_save_result = client.job.save_cron(job_kwargs)
        self.logger.info("job_result: {result}, job_kwargs: {kwargs}".format(result=job_save_result, kwargs=job_kwargs))
        if not job_save_result["result"]:
            message = job_handle_api_error("job.save_cron", job_kwargs, job_save_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

        data.outputs.cron_id = job_save_result["data"]["cron_id"]
        data.outputs.status = _("暂停")
        # 更新作业状态
        job_cron_status = data.get_one_of_inputs("job_cron_status")
        if job_cron_status == 1:
            job_update_cron_kwargs = {
                "bk_biz_id": biz_cc_id,
                "cron_status": 1,
                "cron_id": job_save_result["data"]["cron_id"],
            }
            job_update_result = client.job.update_cron_status(job_update_cron_kwargs)
            if job_update_result["result"]:
                data.outputs.status = _("启动")
            else:
                message = _("新建定时任务成功但是启动失败：{error}").format(
                    error=job_handle_api_error("job.update_cron_status", job_update_cron_kwargs, job_update_result,)
                )
                self.logger.error(message)
                data.outputs.ex_data = message
                return False

        return True


class JobCronTaskComponent(Component):
    name = _("新建定时作业")
    code = "job_cron_task"
    bound_service = JobCronTaskService
    form = "%scomponents/atoms/job/job_cron_task.js" % settings.STATIC_URL
