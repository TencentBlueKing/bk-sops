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

from django.utils import translation
from django.utils.translation import gettext_lazy as _
from pipeline.core.flow.io import ArrayItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from gcloud.utils.handlers import handle_api_error
from packages.bkapi.jobv3_cloud.shortcuts import get_client_by_username
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.job.base import JobScheduleService
from pipeline_plugins.components.collections.sites.open.job.ipv6_base import GetJobTargetServerMixin
from pipeline_plugins.components.utils import batch_execute_func, get_job_instance_url, has_biz_set, loose_strip

__group_name__ = _("作业平台(JOB)")

job_handle_api_error = partial(handle_api_error, __group_name__)


class BaseAllBizJobFastPushFileService(JobScheduleService, GetJobTargetServerMixin):
    biz_scope_type = JobBizScopeType.BIZ_SET.value

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("源文件"),
                key="job_source_files",
                type="array",
                schema=ArrayItemSchema(
                    description=_("待分发文件列表"),
                    item_schema=ObjectItemSchema(
                        description=_("待分发文件信息"),
                        property_schemas={
                            "bk_cloud_id": StringItemSchema(description=_("管控区域ID, 默认为0")),
                            "ip": StringItemSchema(description=_("机器 IP")),
                            "files": StringItemSchema(description=_("文件路径, 多个用换行(\\n)分隔")),
                            "account": StringItemSchema(description=_("执行账户")),
                        },
                    ),
                ),
            ),
            self.InputItem(
                name=_("上传限速"),
                key="upload_speed_limit",
                type="string",
                schema=StringItemSchema(description=_("MB/s")),
            ),
            self.InputItem(
                name=_("下载限速"),
                key="download_speed_limit",
                type="string",
                schema=StringItemSchema(description=_("MB/s")),
            ),
            self.InputItem(
                name=_("分发配置"),
                key="job_dispatch_attr",
                type="array",
                schema=ArrayItemSchema(
                    description=_("待分发至目标信息列表"),
                    item_schema=ObjectItemSchema(
                        description=_("待分发至目标信息列表"),
                        property_schemas={
                            "bk_cloud_id": StringItemSchema(description=_("管控区域ID, 默认为0")),
                            "job_ip_list": StringItemSchema(description=_("待分发机器 IP，多IP请使用;分隔")),
                            "job_target_path": StringItemSchema(description=_("分发目标绝对路径，(可用[FILESRCIP]代替源IP)")),
                            "job_target_account": StringItemSchema(description=_("执行账户，输入在蓝鲸作业平台上注册的账户名")),
                        },
                    ),
                ),
            ),
            self.InputItem(
                name=_("超时时间"), key="job_timeout", type="string", schema=StringItemSchema(description=_("超时时间"))
            ),
        ]

    def schedule(self, data, parent_data, callback_data=None):
        biz_cc_id = int(data.get_one_of_inputs("all_biz_cc_id"))
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        if not has_biz_set(tenant_id, int(biz_cc_id)):
            self.biz_scope_type = JobBizScopeType.BIZ.value
        return super().schedule(data, parent_data, callback_data)

    def get_file_source(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        biz_cc_id = int(data.get_one_of_inputs("all_biz_cc_id"))
        supplier_account = supplier_account_for_business(biz_cc_id)

        file_source = []
        for item in data.get_one_of_inputs("job_source_files", []):
            result, server = self.get_target_server_biz_set(
                tenant_id, executor, [item], supplier_account, logger_handle=self.logger
            )
            if not result:
                raise Exception("源文件信息处理失败，请检查ip配置是否正确, ip_list={}".format(item))

            file_source.append(
                {
                    "file_list": [_file.strip() for _file in item["files"].split("\n") if _file.strip()],
                    "server": server,
                    "account": {"alias": loose_strip(item["account"])},
                }
            )

        return file_source

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)

        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))
        biz_cc_id = int(data.get_one_of_inputs("all_biz_cc_id"))
        data.inputs.biz_cc_id = biz_cc_id

        if not has_biz_set(tenant_id, int(biz_cc_id)):
            self.biz_scope_type = JobBizScopeType.BIZ.value

        params_list = self.get_params_list(data, parent_data)
        task_count = len(params_list)
        # 并发请求接口
        job_result_list = batch_execute_func(client.api.fast_transfer_file, params_list, interval_enabled=True)
        job_instance_id_list, job_inst_name, job_inst_url = [], [], []
        data.outputs.requests_error = ""
        for index, res in enumerate(job_result_list):
            job_result = res["result"]
            if job_result["result"]:
                job_instance_id_list.append(job_result["data"]["job_instance_id"])
                job_inst_name.append(job_result["data"]["job_instance_name"])
                job_inst_url.append(get_job_instance_url(biz_cc_id, job_instance_id_list))
            else:
                message = job_handle_api_error("jobv3.fast_transfer_file", params_list[index], job_result)
                self.logger.error(message)
                data.outputs.requests_error += "{}\n".format(message)
        if data.outputs.requests_error:
            data.outputs.requests_error = "Request Error:\n{}".format(data.outputs.requests_error)

        # 总任务数
        data.outputs.task_count = task_count
        data.outputs.job_instance_id_list = job_instance_id_list
        # 批量请求使用
        data.outputs.job_id_of_batch_execute = job_instance_id_list
        data.outputs.job_inst_url = [get_job_instance_url(biz_cc_id, job_id) for job_id in job_instance_id_list]
        # 请求成功数
        data.outputs.request_success_count = len(job_instance_id_list)
        # 执行成功数
        data.outputs.success_count = 0
        # 所有请求都失败，则返回
        if not data.outputs.request_success_count:
            data.outputs.ex_data = data.outputs.requests_error
            return False
        data.outputs.final_res = task_count == len(job_instance_id_list)
        return True

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("总任务数"), key="task_count", type="string", schema=StringItemSchema(description=_("总任务数"))
            ),
            self.OutputItem(
                name=_("分发请求成功数"),
                key="request_success_count",
                type="string",
                schema=StringItemSchema(description=_("分发请求成功数")),
            ),
            self.OutputItem(
                name=_("分发成功数"),
                key="success_count",
                type="string",
                schema=StringItemSchema(description=_("上传成功数")),
            ),
            self.OutputItem(
                name=_("任务id"),
                key="job_instance_id_list",
                type="string",
                schema=StringItemSchema(description=_("任务id")),
            ),
            self.OutputItem(
                name=_("任务url"), key="job_inst_url", type="string", schema=StringItemSchema(description=_("任务url"))
            ),
        ]
