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

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component
from pipeline_plugins.components.collections.sites.open.job.base import JobScheduleService
from pipeline_plugins.components.utils.common import batch_execute_func
from pipeline_plugins.components.utils import get_job_instance_url, loose_strip
from pipeline_plugins.components.utils.sites.open.utils import plat_ip_reg
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from gcloud.utils.ip import get_ip_by_regex

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class AllBizJobFastPushFileService(JobScheduleService):
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
                            "bk_cloud_id": StringItemSchema(description=_("云区域ID, 默认为0")),
                            "ip": StringItemSchema(description=_("机器 IP")),
                            "files": StringItemSchema(description=_("文件路径, 多个用换行(\\n)分隔")),
                            "account": StringItemSchema(description=_("执行账户")),
                        },
                    ),
                ),
            ),
            self.InputItem(
                name=_("上传限速"), key="upload_speed_limit", type="string", schema=StringItemSchema(description=_("MB/s")),
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
                            "bk_cloud_id": StringItemSchema(description=_("云区域ID, 默认为0")),
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

    def get_ip_info(self, ip, break_line):
        if plat_ip_reg.match(ip):
            ip_result = []
            for line in ip.split(break_line):
                line = line.split(":")
                ip_result.append({"Source": line[0], "InnerIP": line[1]})
            result = {
                "result": True,
                "ip_result": ip_result,
                "ip_count": len(ip_result),
            }
            return result
        return {"result": False}

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))
        biz_cc_id = int(data.get_one_of_inputs("all_biz_cc_id"))
        data.inputs.biz_cc_id = biz_cc_id
        upload_speed_limit = data.get_one_of_inputs("upload_speed_limit")
        download_speed_limit = data.get_one_of_inputs("download_speed_limit")
        job_timeout = data.get_one_of_inputs("job_timeout")

        file_source = [
            {
                "files": [_file.strip() for _file in item["files"].split("\n") if _file.strip()],
                "ip_list": [{"ip": item["ip"], "bk_cloud_id": int(item["bk_cloud_id"]) if item["bk_cloud_id"] else 0}],
                "account": loose_strip(item["account"]),
            }
            for item in data.get_one_of_inputs("job_source_files", [])
        ]

        # 拼装参数列表
        params_list = []
        for source in file_source:
            for attr in data.get_one_of_inputs("job_dispatch_attr"):
                job_account = attr["job_target_account"]
                job_target_path = attr["job_target_path"]
                ip_list = [
                    {"ip": _ip, "bk_cloud_id": int(attr["bk_cloud_id"]) if attr["bk_cloud_id"] else 0}
                    for _ip in get_ip_by_regex(attr["job_ip_list"])
                ]
                job_kwargs = {
                    "bk_biz_id": biz_cc_id,
                    "file_source": [source],
                    "ip_list": ip_list,
                    "account": job_account,
                    "file_target_path": job_target_path,
                }
                if upload_speed_limit:
                    job_kwargs["upload_speed_limit"] = int(upload_speed_limit)
                if download_speed_limit:
                    job_kwargs["download_speed_limit"] = int(download_speed_limit)
                if job_timeout:
                    job_kwargs["timeout"] = int(job_timeout)
                params_list.append(job_kwargs)
        task_count = len(params_list)
        # 并发请求接口
        job_result_list = batch_execute_func(client.job.fast_push_file, params_list, interval_enabled=True)
        job_instance_id_list, job_inst_name, job_inst_url = [], [], []
        data.outputs.requests_error = ""
        for index, res in enumerate(job_result_list):
            job_result = res["result"]
            if job_result["result"]:
                job_instance_id_list.append(job_result["data"]["job_instance_id"])
                job_inst_name.append(job_result["data"]["job_instance_name"])
                job_inst_url.append(get_job_instance_url(biz_cc_id, job_instance_id_list))
            else:
                message = job_handle_api_error("job.fast_push_file", params_list[index], job_result)
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
        ]


class AllBizJobFastPushFileComponent(Component):
    name = _("全业务快速分发文件")
    code = "all_biz_job_fast_push_file"
    bound_service = AllBizJobFastPushFileService
    form = "%scomponents/atoms/job/all_biz_fast_push_file/v1_0.js" % settings.STATIC_URL
    version = "v1.0"
    desc = _("跨业务分发文件时需要在作业平台添加白名单")
