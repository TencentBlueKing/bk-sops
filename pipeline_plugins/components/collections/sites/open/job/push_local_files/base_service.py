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

import traceback
from functools import partial

from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, ObjectItemSchema
from pipeline.core.flow.activity import StaticIntervalGenerator

from pipeline_plugins.components.collections.sites.open.job.ipv6_base import GetJobTargetServerMixin
from pipeline_plugins.components.collections.sites.open.job.base import JobScheduleService
from pipeline_plugins.components.utils.common import batch_execute_func
from pipeline_plugins.components.utils import get_job_instance_url
from files.factory import ManagerFactory
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from gcloud.core.models import EnvironmentVariables

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class BaseJobPushLocalFilesService(JobScheduleService, GetJobTargetServerMixin):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("目标IP"), key="job_target_ip_list", type="string", schema=StringItemSchema(description=_("目标IP"))
            ),
            self.InputItem(
                name=_("执行账号"), key="job_target_account", type="string", schema=StringItemSchema(description=_("执行账号"))
            ),
            self.InputItem(
                name=_("本地文件信息"),
                key="job_local_files_info",
                type="object",
                schema=ObjectItemSchema(
                    description=_("本地文件信息"),
                    property_schemas={
                        "job_push_multi_local_files_table": ArrayItemSchema(
                            description=_("文件信息表"),
                            item_schema=ObjectItemSchema(
                                description=_("文件信息与目标路径"),
                                property_schemas={
                                    "file_info": ArrayItemSchema(
                                        description=_("本地文件"),
                                        item_schema=ObjectItemSchema(
                                            description=_("需要操作的文件"),
                                            property_schemas={
                                                "tag": ObjectItemSchema(
                                                    description=_("tag"),
                                                    property_schemas={
                                                        "type": StringItemSchema(
                                                            description=_("文件类型"), enum=["upload_module", "host_nfs"]
                                                        ),
                                                        "tags": ObjectItemSchema(
                                                            description=_(
                                                                "tags，文件类型为upload_module， tag_id必填。"
                                                                "文件类型为host_nfs， uid shims name必填"
                                                            ),
                                                            property_schemas={
                                                                "tag_id": StringItemSchema(description=_("tag_id")),
                                                                "uid": StringItemSchema(description=_("uid")),
                                                                "shims": StringItemSchema(description=_("shims")),
                                                                "name": StringItemSchema(description=_("name")),
                                                            },
                                                        ),
                                                    },
                                                )
                                            },
                                        ),
                                    ),
                                    "target_path": StringItemSchema(description=_("目标地址")),
                                },
                            ),
                        )
                    },
                ),
            ),
            self.InputItem(
                name=_("超时时间"), key="job_timeout", type="string", schema=StringItemSchema(description=_("超时时间"))
            ),
        ]

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("总任务数"), key="task_count", type="string", schema=StringItemSchema(description=_("总任务数"))
            ),
            self.OutputItem(
                name=_("上传请求成功数"),
                key="request_success_count",
                type="string",
                schema=StringItemSchema(description=_("上传请求成功数")),
            ),
            self.OutputItem(
                name=_("上传成功数"), key="success_count", type="string", schema=StringItemSchema(description=_("上传成功数"))
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

    def get_ip_list(self, data, target_ip_list, executor, biz_cc_id):
        across_biz = data.get_one_of_inputs("job_across_biz", False)
        # 获取 IP
        clean_result, target_server = self.get_target_server(
            executor, biz_cc_id, data, target_ip_list, self.logger, False, is_across=across_biz
        )
        return clean_result, target_server

    def get_params_list(self, client, data, target_server, local_files_and_target_path):
        biz_cc_id = data.inputs.biz_cc_id
        target_account = data.inputs.job_target_account
        params_list = [
            {
                "esb_client": client,
                "bk_biz_id": biz_cc_id,
                "file_tags": [
                    _file["response"]["tag"]
                    for _file in push_files_info["file_info"]
                    if _file["response"]["result"] is True
                ],
                "target_path": push_files_info["target_path"],
                "ips": None,
                "account": target_account,
                "target_server": target_server,
            }
            for push_files_info in local_files_and_target_path
        ]

        return params_list

    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        biz_cc_id = data.inputs.biz_cc_id
        local_files_and_target_path = data.inputs.job_local_files_info["job_push_multi_local_files_table"]
        target_ip_list = data.inputs.job_target_ip_list
        job_timeout = data.get_one_of_inputs("job_timeout")
        task_count = len(local_files_and_target_path)

        file_manager_type = EnvironmentVariables.objects.get_var("BKAPP_FILE_MANAGER_TYPE")
        if not file_manager_type:
            data.outputs.ex_data = "File Manager configuration error, contact administrator please."
            return False

        try:
            file_manager = ManagerFactory.get_manager(manager_type=file_manager_type)
        except Exception as e:
            err_msg = "can not get file manager for type: {}\n err: {}"
            self.logger.error(err_msg.format(file_manager_type, traceback.format_exc()))
            data.outputs.ex_data = err_msg.format(file_manager_type, e)
            return False

        client = get_client_by_user(executor)

        # filter 跨业务 IP
        clean_result, target_server = self.get_ip_list(data, target_ip_list, executor, biz_cc_id)
        if not clean_result:
            data.outputs.ex_data = "ip查询失败，请检查ip配置是否正常"
            return False

        params_list = self.get_params_list(client, data, target_server, local_files_and_target_path)

        if job_timeout:
            for param in params_list:
                param["timeout"] = int(job_timeout)

        # 批量上传请求
        if len(params_list) == task_count:
            push_results = batch_execute_func(file_manager.push_files_to_ips, params_list, interval_enabled=True)
        else:
            data.outputs.ex_data = _("执行参数为空，请确认")
            return False
        # 校验请求结果
        job_instance_id_list = []
        data.outputs.requests_error = ""
        for push_object in push_results:
            push_result = push_object["result"]
            if not push_result["result"]:
                err_message = job_handle_api_error(
                    push_result["job_api"], push_result["kwargs"], push_result["response"]
                )
                self.logger.error(err_message)
                data.outputs.requests_error += "{}\n".format(err_message)
            else:
                job_instance_id_list.append(push_result["data"]["job_id"])

        if data.outputs.requests_error:
            data.outputs.requests_error = "Request Error:\n{}".format(data.outputs.requests_error)

        data.outputs.job_instance_id_list = job_instance_id_list

        # 批量请求使用
        data.outputs.job_id_of_batch_execute = job_instance_id_list

        data.outputs.job_inst_url = [get_job_instance_url(biz_cc_id, job_id) for job_id in job_instance_id_list]
        # 总任务数
        data.outputs.task_count = task_count
        # 请求成功数
        data.outputs.request_success_count = len(job_instance_id_list)
        # 执行成功数
        data.outputs.success_count = 0
        # 所有请求都失败，则返回
        if not data.outputs.request_success_count:
            data.outputs.ex_data = data.outputs.requests_error
            return False

        # 任务结果
        data.outputs.final_res = task_count == len(job_instance_id_list)
        return True

    def schedule(self, data, parent_data, callback_data=None):
        return super(BaseJobPushLocalFilesService, self).schedule(data, parent_data, callback_data)
