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
from copy import deepcopy

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, ObjectItemSchema, BooleanItemSchema
from pipeline.component_framework.component import Component
from pipeline_plugins.components.collections.sites.open.job.base import JobScheduleService
from pipeline_plugins.components.utils import (
    cc_get_ips_info_by_str,
    get_job_instance_url,
    get_node_callback_url,
    loose_strip,
    chunk_table_data,
    batch_execute_func,
)
from pipeline_plugins.components.utils.sites.open.utils import plat_ip_reg
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobFastPushFileService(JobScheduleService):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("是否允许跨业务"),
                key="job_across_biz",
                type="bool",
                schema=BooleanItemSchema(description=_("是否允许跨业务，如果允许，源文件IP格式需为【云区域ID:IP】")),
            ),
            self.InputItem(
                name=_("源文件"),
                key="job_source_files",
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
                name=_("上传限速"), key="upload_speed_limit", type="string", schema=StringItemSchema(description=_("MB/s")),
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
                name=_("目标账户"), key="job_account", type="string", schema=StringItemSchema(description=_("文件分发目标机器账户")),
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

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        original_source_files = deepcopy(data.get_one_of_inputs("job_source_files", []))
        across_biz = data.get_one_of_inputs("job_across_biz", False)
        upload_speed_limit = data.get_one_of_inputs("upload_speed_limit")
        download_speed_limit = data.get_one_of_inputs("download_speed_limit")
        job_timeout = data.get_one_of_inputs("job_timeout")
        file_source = []
        for item in original_source_files:
            if across_biz:
                ip_info = {"ip_result": []}
                ip_str = item["ip"]
                if plat_ip_reg.match(ip_str):
                    for match in plat_ip_reg.finditer(ip_str):
                        ip = match.group()
                        cloud_id, inner_ip = ip.strip().split(":")
                        ip_info["ip_result"].append({"InnerIP": inner_ip, "Source": cloud_id})
                else:
                    message = _("允许跨业务时IP格式需满足：【云区域ID:IP】")
                    self.logger.error(message)
                    data.set_outputs("ex_data", message)
                    return False
            else:
                ip_info = cc_get_ips_info_by_str(
                    username=executor, biz_cc_id=biz_cc_id, ip_str=item["ip"], use_cache=False,
                )
            file_source.append(
                {
                    "files": [_file.strip() for _file in item["files"].split("\n") if _file.strip()],
                    "ip_list": [{"ip": _ip["InnerIP"], "bk_cloud_id": _ip["Source"]} for _ip in ip_info["ip_result"]],
                    "account": loose_strip(item["account"]),
                }
            )

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
        # 拼装参数列表
        params_list = []
        for source in file_source:
            for attr in attr_list:
                original_ip_list = attr["job_ip_list"]
                job_account = attr["job_account"]
                # 将[FILESRCIP]替换成源IP
                job_target_path = attr["job_target_path"].replace("[FILESRCIP]", source["ip_list"][0]["ip"])
                # 如果允许跨业务，则调用不去查云区域ID的方法
                target_ip_info = (
                    self.get_ip_info(original_ip_list, break_line)
                    if across_biz
                    else cc_get_ips_info_by_str(executor, biz_cc_id, original_ip_list)
                )

                ip_list = [{"ip": _ip["InnerIP"], "bk_cloud_id": _ip["Source"]} for _ip in target_ip_info["ip_result"]]

                job_kwargs = {
                    "bk_biz_id": biz_cc_id,
                    "file_source": source,
                    "ip_list": ip_list,
                    "account": job_account,
                    "file_target_path": job_target_path,
                    "bk_callback_url": get_node_callback_url(self.id),
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
        job_instance_id, job_inst_name, job_inst_url, ex_data = [], [], [], []
        for index, res in enumerate(job_result_list):
            job_result = res["result"]
            if job_result:
                job_instance_id.append(job_result["data"]["job_instance_id"])
                job_inst_name.append(job_result["data"]["job_instance_name"])
                job_inst_url.append(get_job_instance_url(biz_cc_id, job_instance_id))
            else:
                message = job_handle_api_error("job.fast_push_file", params_list[index], job_result)
                self.logger.error(message)
                ex_data.append(message)

        data.outputs.job_instance_id_list = job_instance_id
        # 批量请求使用
        data.outputs.job_id_of_batch_execute = job_instance_id
        # 请求成功数
        data.outputs.request_success_count = len(job_result_list)
        # 执行成功数
        data.outputs.success_count = 0
        # 所有请求都失败，则返回
        if not data.outputs.request_success_count:
            data.outputs.ex_data = data.outputs.requests_error
            return False
        data.outputs.final_res = task_count == len(job_result_list)
        return True

    def schedule(self, data, parent_data, callback_data=None):
        return super(JobScheduleService, self).schedule(data, parent_data, callback_data)

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


class JobFastPushFileComponent(Component):
    name = _("快速分发文件")
    code = "job_fast_push_file"
    bound_service = JobFastPushFileService
    form = "%scomponents/atoms/job/fast_push_file/v2_0.js" % settings.STATIC_URL
    version = "v2.0"
