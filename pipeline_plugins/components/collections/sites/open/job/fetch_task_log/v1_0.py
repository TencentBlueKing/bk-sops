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

from functools import partial

from bkapi.jobv3_cloud.shortcuts import get_client_by_username
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.components.collections.sites.open.job.base import get_job_instance_log

__group_name__ = _("作业平台(JOB)")

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobFetchTaskLogService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("任务ID"),
                key="job_task_id",
                type="string",
                schema=StringItemSchema(description=_("任务ID")),
            ),
            self.InputItem(
                name=_("目标 IP"),
                key="job_target_ip",
                type="string",
                schema=StringItemSchema(description=_("日志查询目标IP，仅支持一个IP")),
            ),
        ]

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("任务日志"),
                key="job_task_log",
                type="string",
                schema=StringItemSchema(description=_("任务日志")),
            )
        ]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        biz_cc_id = parent_data.get_one_of_inputs("biz_cc_id")
        job_task_id = data.get_one_of_inputs("job_task_id")
        target_ip = data.get_one_of_inputs("job_target_ip")
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))
        result = get_job_instance_log(tenant_id, client, self.logger, job_task_id, biz_cc_id, target_ip)
        if not result["result"]:
            self.logger.error(
                f"[get_job_instance_log] error: {result['message']} with params: "
                f"task_id: {job_task_id} and target_ip: {target_ip}"
            )
            data.outputs.ex_data = result["message"]
            return False
        data.outputs.job_task_log = result["data"]
        return True


class JobFetchTaskLogComponent(Component):
    name = _("获取任务日志")
    code = "job_fetch_task_log"
    bound_service = JobFetchTaskLogService
    form = "%scomponents/atoms/job/fetch_task_log/v1_0.js" % settings.STATIC_URL
    version = "v1.0"
    desc = _("出于性能考虑，该插件仅支持获取对应任务中某一IP的任务日志。")
