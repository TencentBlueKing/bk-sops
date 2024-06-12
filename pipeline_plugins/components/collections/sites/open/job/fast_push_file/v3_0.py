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

import re
from copy import deepcopy
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import ArrayItemSchema, BooleanItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.components.collections.sites.open.job.base import JobScheduleService
from pipeline_plugins.components.collections.sites.open.job.ipv6_base import GetJobTargetServerMixin
from pipeline_plugins.components.utils import chunk_table_data, get_job_instance_url, loose_strip
from pipeline_plugins.components.utils.common import batch_execute_func

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobFastPushFileService(JobScheduleService, GetJobTargetServerMixin):
    need_show_failure_inst_url = True

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("服务器"),
                key="job_server",
                type="array",
                schema=ArrayItemSchema(
                    description=_("待分发文件列表"),
                    item_schema=ObjectItemSchema(
                        description=_("待分发文件信息"),
                        property_schemas={
                            "ip": StringItemSchema(description=_("机器 IP")),
                            "files": StringItemSchema(description=_("文件路径")),
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
                name=_("目标 IP"),
                key="job_ip_list",
                type="string",
                schema=StringItemSchema(description=_("文件分发目标机器 IP，多个用英文逗号 `,` 分隔")),
            ),
            self.InputItem(
                name=_("目标账户"),
                key="job_account",
                type="string",
                schema=StringItemSchema(description=_("文件分发目标机器账户")),
            ),
            self.InputItem(
                name=_("目标路径"),
                key="job_target_path",
                type="string",
                schema=StringItemSchema(description=_("文件分发目标路径")),
            ),
            self.InputItem(
                name=_("超时时间"), key="job_timeout", type="string", schema=StringItemSchema(description=_("超时时间"))
            ),
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

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        job_source_files_origin = data.get_one_of_inputs("job_source_files_origin")
        upload_speed_limit = data.get_one_of_inputs("upload_speed_limit")
        download_speed_limit = data.get_one_of_inputs("download_speed_limit")
        job_timeout = data.get_one_of_inputs("job_timeout")
        job_rolling_config = data.get_one_of_inputs("job_rolling_config", {})
        job_rolling_execute = job_rolling_config.get("job_rolling_execute", None)
        file_source = []
        if job_source_files_origin == "server":
            original_source_files = deepcopy(data.get_one_of_inputs("job_server", []))
            for item in original_source_files:
                clean_source_ip_result, server = self.get_target_server_hybrid(
                    executor, biz_cc_id, data, item["ip"], logger_handle=self.logger
                )
                if not clean_source_ip_result:
                    return False
                file_source.append(
                    {
                        "file_list": [_file.strip() for _file in item["files"].split("\n") if _file.strip()],
                        "server": server,
                        "account": {
                            "alias": loose_strip(item["account"]),
                        },
                        "file_type": 1,
                    }
                )
        elif job_source_files_origin == "file_source":
            original_source_files = data.get_one_of_inputs("job_source_files", [])
            for item in original_source_files:
                file_source.append(
                    {
                        "file_list": [_file.strip() for _file in re.split(r"[, \n]", item["files"]) if _file.strip()],
                        "file_source_code": item["file_source"],
                        "file_type": 3,
                    }
                )
        else:
            data.outputs.requests_error = "Request Error:\n{}".format("只支持服务器和源文件类型")
            return False

        select_method = data.get_one_of_inputs("select_method")
        break_line = data.get_one_of_inputs("break_line") or ","
        job_dispatch_attr = data.get_one_of_inputs("job_dispatch_attr")
        attr_list = []
        for attr in job_dispatch_attr:
            # 如果用户选择了单行扩展
            if select_method == "auto":
                chunk_result = chunk_table_data(attr, break_line)
                if not chunk_result["result"]:
                    data.set_outputs("ex_data", chunk_result["message"])
                    return False
                attr_list.extend(chunk_result["data"])
            else:
                # 非单行扩展的情况无需处理
                attr_list.append(attr)

        # 如果开启了滚动执行，填充rolling_config配置
        if job_rolling_execute:
            # 滚动策略
            job_rolling_expression = job_rolling_config.get("job_rolling_expression")
            # 滚动机制
            job_rolling_mode = job_rolling_config.get("job_rolling_mode")
            rolling_config = {"expression": job_rolling_expression, "mode": job_rolling_mode}

        # 拼装参数列表
        params_list = []
        for attr in attr_list:
            # 获取目标IP
            original_ip_list = attr["job_ip_list"]
            clean_result, target_server = self.get_target_server_hybrid(
                executor, biz_cc_id, data, original_ip_list, logger_handle=self.logger
            )
            if not clean_result:
                return False
            job_kwargs = {
                "bk_scope_type": JobBizScopeType.BIZ.value,
                "bk_scope_id": str(biz_cc_id),
                "bk_biz_id": biz_cc_id,
                "file_source_list": file_source,
                "target_server": target_server,
                "account_alias": attr["job_account"],
                "file_target_path": attr["job_target_path"],
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
        task_count = len(params_list)
        # 并发请求接口
        job_result_list = batch_execute_func(client.jobv3.fast_transfer_file, params_list, interval_enabled=True)
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
                name=_("分发成功数"), key="success_count", type="string", schema=StringItemSchema(description=_("上传成功数"))
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
            self.OutputItem(
                name=_("执行失败的任务URL"),
                key="failure_inst_url",
                type="string",
                schema=StringItemSchema(description=_("执行失败的任务URL")),
            ),
        ]


class JobFastPushFileComponent(Component):
    name = _("快速分发文件")
    code = "job_fast_push_file"
    bound_service = JobFastPushFileService
    form = "%scomponents/atoms/job/fast_push_file/v3_0.js" % settings.STATIC_URL
    version = "v3.0"
    desc = _(
        "1. 填参方式支持手动填写和结合模板生成（单行自动扩展）\n"
        "2. 使用单行自动扩展模式时，每一行支持填写多个已自定义分隔符或是英文逗号分隔的数据，"
        '插件后台会自动将其扩展成多行，如 "1,2,3,4" 会被扩展成四行：1 2 3 4\n'
        "3. 结合模板生成（单行自动扩展）当有一列有多条数据时，其他列要么也有相等个数的数据，要么只有一条数据\n"
        "4. v3.0版本新增文件源的支持，要求作业平台版本>=3.6.0.0"
    )
