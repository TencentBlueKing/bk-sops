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
from pipeline_plugins.components.collections.sites.open.job.push_local_files.base_service import (
    BaseJobPushLocalFilesService,
)

__group_name__ = _("作业平台(JOB)")


class JobPushLocalFilesService(BaseJobPushLocalFilesService):
    def inputs_format(self):
        input_format_list = super().inputs_format()
        return input_format_list + [
            self.InputItem(
                name=_("滚动执行"),
                key="job_rolling_execute",
                type="boolean",
                schema=BooleanItemSchema(description=_("是否开启滚动执行")),
            ),
            self.InputItem(
                name=_("滚动策略"),
                key="job_rolling_expression",
                type="string",
                schema=StringItemSchema(description=_("滚动策略，仅在滚动执行开启时生效")),
            ),
            self.InputItem(
                name=_("滚动机制"),
                key="job_rolling_mode",
                type="string",
                schema=StringItemSchema(description=_("滚动机制，仅在滚动执行开启时生效")),
            ),
        ]

    def get_ip_list(self, data, target_ip_list, executor, biz_cc_id, tenant_id):
        clean_result, target_server = self.get_target_server_hybrid(
            tenant_id, executor, biz_cc_id, data, target_ip_list, self.logger
        )
        return clean_result, target_server

    def get_params_list(self, tenant_id, client, data, target_server, local_files_and_target_path):
        biz_cc_id = data.inputs.biz_cc_id
        job_rolling_config = data.get_one_of_inputs("job_rolling_config", {})
        job_rolling_execute = job_rolling_config.get("job_rolling_execute", None)
        # 如果开启了滚动执行，填充rolling_config配置
        rolling_config = None
        if job_rolling_execute:
            # 滚动策略
            job_rolling_expression = job_rolling_config.get("job_rolling_expression")
            # 滚动机制
            job_rolling_mode = job_rolling_config.get("job_rolling_mode")
            rolling_config = {"expression": job_rolling_expression, "mode": job_rolling_mode}

        target_account = data.inputs.job_target_account.strip()
        params_list = [
            {
                "esb_client": client,
                "bk_biz_id": biz_cc_id,
                "file_tags": [
                    _file["response"]["tag"]
                    for _file in push_files_info["file_info"]
                    if _file["response"]["result"] is True
                ],
                "target_path": push_files_info["target_path"].strip(),
                "ips": None,
                "target_server": target_server,
                "account": target_account.strip(),
                "rolling_config": rolling_config,
                "headers": {"X-Bk-Tenant-Id": tenant_id},
            }
            for push_files_info in local_files_and_target_path
        ]
        return params_list


class JobPushLocalFilesComponent(Component):
    name = _("分发本地文件")
    code = "job_push_local_files"
    bound_service = JobPushLocalFilesService
    form = "%scomponents/atoms/job/job_push_local_files/v2_1.js" % settings.STATIC_URL
    version = "v2.1"
    desc = _(
        "本地上传的文件不保证长期保存并可用于多次分发，推荐勾选上传变量并在创建任务时进行上传操作。如果希望多次分发相同文件，请使用快速分发文件插件。" "注：插件版本v2.1中滚动执行要求作业平台版本>=V3.6.0.0。\n"
    )
