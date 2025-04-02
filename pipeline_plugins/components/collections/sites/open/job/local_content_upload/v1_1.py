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
from pipeline_plugins.components.collections.sites.open.job.local_content_upload.base_service import (
    BaseJobLocalContentUploadService,
)

__group_name__ = _("作业平台(JOB)")


class JobLocalContentUploadService(BaseJobLocalContentUploadService):
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

    def get_ip_list(self, data, executor, biz_cc_id, tenant_id):
        original_ip_list = data.get_one_of_inputs("job_ip_list")
        # 获取 IP
        clean_result, target_server = self.get_target_server_hybrid(
            tenant_id, executor, biz_cc_id, data, original_ip_list, logger_handle=self.logger
        )
        return clean_result, target_server

    def get_job_kwargs(self, biz_cc_id, data, ip_list):
        job_rolling_config = data.get_one_of_inputs("job_rolling_config", {})
        job_rolling_execute = job_rolling_config.get("job_rolling_execute", None)

        job_kwargs = super(JobLocalContentUploadService, self).get_job_kwargs(biz_cc_id, data, ip_list)

        # 如果开启了滚动执行，填充rolling_config配置
        if job_rolling_execute:
            # 滚动策略
            job_rolling_expression = job_rolling_config.get("job_rolling_expression")
            # 滚动机制
            job_rolling_mode = job_rolling_config.get("job_rolling_mode")
            rolling_config = {"expression": job_rolling_expression, "mode": job_rolling_mode}
            job_kwargs.update({"rolling_config": rolling_config})

        return job_kwargs


class JobLocalContentUploadComponent(Component):
    name = _("本地文本框内容上传")
    code = "job_local_content_upload"
    bound_service = JobLocalContentUploadService
    form = "%scomponents/atoms/job/local_content_upload/v1_1.js" % settings.STATIC_URL
    version = "v1.1"
    desc = _("注：插件版本v1.1中滚动执行要求作业平台版本>=V3.6.0.0。\n" "注：插件版本v1.1版本默认开启跨业务")
