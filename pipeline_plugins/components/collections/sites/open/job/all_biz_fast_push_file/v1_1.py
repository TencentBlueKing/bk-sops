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
from pipeline_plugins.components.collections.sites.open.job.all_biz_fast_push_file.base_service import (
    BaseAllBizJobFastPushFileService,
)

__group_name__ = _("作业平台(JOB)")


class AllBizJobFastPushFileService(BaseAllBizJobFastPushFileService):
    need_show_failure_inst_url = True

    def inputs_format(self):
        input_format_list = super(AllBizJobFastPushFileService, self).inputs_format()

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

    def get_params_list(self, data, parent_data):
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        biz_cc_id = int(data.get_one_of_inputs("all_biz_cc_id"))
        upload_speed_limit = data.get_one_of_inputs("upload_speed_limit")
        download_speed_limit = data.get_one_of_inputs("download_speed_limit")
        job_timeout = data.get_one_of_inputs("job_timeout")
        file_source = self.get_file_source(data, parent_data)

        executor = parent_data.get_one_of_inputs("executor")
        job_rolling_config = data.get_one_of_inputs("job_rolling_config", {})
        job_rolling_execute = job_rolling_config.get("job_rolling_execute", None)

        # 如果开启了滚动执行，填充rolling_config配置
        if job_rolling_execute:
            # 滚动策略
            job_rolling_expression = job_rolling_config.get("job_rolling_expression")
            # 滚动机制
            job_rolling_mode = job_rolling_config.get("job_rolling_mode")
            rolling_config = {"expression": job_rolling_expression, "mode": job_rolling_mode}

        # 拼装参数列表
        params_list = []
        for attr in data.get_one_of_inputs("job_dispatch_attr"):
            job_account = attr["job_target_account"]
            job_target_path = attr["job_target_path"]
            result, target_server = self.get_target_server_biz_set(
                tenant_id, executor, [attr], logger_handle=self.logger, ip_key="job_ip_list"
            )

            if not result:
                raise Exception("目标服务器查询失败，请检查ip配置是否正确")

            job_kwargs = {
                "data": {
                    "bk_scope_type": self.biz_scope_type,
                    "bk_scope_id": str(biz_cc_id),
                    "bk_biz_id": biz_cc_id,
                    "file_source_list": file_source,
                    "target_server": target_server,
                    "account_alias": job_account,
                    "file_target_path": job_target_path,
                },
                "headers": {"X-Bk-Tenant-Id": tenant_id},
            }
            if upload_speed_limit:
                job_kwargs["upload_speed_limit"] = int(upload_speed_limit)
            if download_speed_limit:
                job_kwargs["download_speed_limit"] = int(download_speed_limit)
            if job_timeout:
                job_kwargs["timeout"] = int(job_timeout)
            if job_rolling_execute:
                job_kwargs["rolling_config"] = rolling_config
            params_list.append(job_kwargs)
        return params_list

    def outputs_format(self):
        outputs_format_list = super(AllBizJobFastPushFileService, self).outputs_format()
        return outputs_format_list + [
            self.OutputItem(
                name=_("执行失败的任务URL"),
                key="failure_inst_url",
                type="string",
                schema=StringItemSchema(description=_("执行失败的任务URL")),
            ),
        ]


class AllBizJobFastPushFileComponent(Component):
    name = _("业务集快速分发文件")
    code = "all_biz_job_fast_push_file"
    bound_service = AllBizJobFastPushFileService
    form = "%scomponents/atoms/job/all_biz_fast_push_file/v1_1.js" % settings.STATIC_URL
    version = "v1.1"
    desc = _("跨业务分发文件时需要在作业平台添加白名单, V1.1版本支持job滚动执行，要求作业平台版本>=3.6.0.0")
