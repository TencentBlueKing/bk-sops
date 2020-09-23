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
import base64
from functools import partial

from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.io import StringItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component
from pipeline_plugins.components.utils import cc_get_ips_info_by_str, get_job_instance_url, get_node_callback_url
from pipeline_plugins.components.collections.sites.open.job import JobService
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobLocalContentUploadService(JobService):
    __need_schedule__ = True

    reload_outputs = False

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("生成文件名[后缀]"), key="local_name", type="string", schema=StringItemSchema(description=_("生成文件名")),
            ),
            self.InputItem(
                name=_("文本内容"), key="local_content", type="string", schema=StringItemSchema(description=_("文本内容")),
            ),
            self.InputItem(
                name=_("目标IP"),
                key="job_ip_list",
                type="string",
                schema=StringItemSchema(
                    description=_("IP必须填写【云区域ID:IP】或者【IP】格式之一，多个用换行分隔；【IP】格式需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的")
                ),
            ),
            self.InputItem(
                name=_("目标账户"),
                key="file_account",
                type="string",
                schema=StringItemSchema(description=_("请输入在蓝鲸作业平台上注册的账户名")),
            ),
            self.InputItem(
                name=_("目标路径"), key="file_path", type="string", schema=StringItemSchema(description=_("目标路径")),
            ),
        ]

    def outputs_format(self):
        return super(JobLocalContentUploadService, self).outputs_format() + [
            self.OutputItem(
                name=_("JOB全局变量"),
                key="log_outputs",
                type="dict",
                schema=ObjectItemSchema(
                    description=_("输出日志中提取的全局变量"),
                    property_schemas={
                        "name": StringItemSchema(description=_("全局变量名称")),
                        "value": StringItemSchema(description=_("全局变量值")),
                    },
                ),
            ),
        ]

    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        biz_cc_id = parent_data.inputs.biz_cc_id
        client = get_client_by_user(executor)

        original_ip_list = data.get_one_of_inputs("job_ip_list")
        ip_info = cc_get_ips_info_by_str(
            username=executor, biz_cc_id=biz_cc_id, ip_str=original_ip_list, use_cache=False,
        )
        ip_list = [{"ip": _ip["InnerIP"], "bk_cloud_id": _ip["Source"]} for _ip in ip_info["ip_result"]]

        job_kwargs = {
            "bk_biz_id": biz_cc_id,
            "account": data.get_one_of_inputs("file_account"),
            "file_target_path": data.get_one_of_inputs("file_path"),
            "file_list": [
                {
                    "file_name": data.get_one_of_inputs("local_name"),
                    "content": base64.b64encode(data.get_one_of_inputs("local_content").encode("utf-8")).decode(
                        "utf-8"
                    ),
                }
            ],
            "ip_list": ip_list,
            "bk_callback_url": get_node_callback_url(self.id),
        }

        job_result = client.job.push_config_file(job_kwargs)
        self.logger.info("job_result: {result}, job_kwargs: {kwargs}".format(result=job_result, kwargs=job_kwargs))

        if job_result["result"]:
            job_instance_id = job_result["data"]["job_instance_id"]
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result["data"]["job_instance_name"]
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.client = client
            return True
        else:
            message = job_handle_api_error("job.push_config_file", job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

    def schedule(self, data, parent_data, callback_data=None):
        return super(JobLocalContentUploadService, self).schedule(data, parent_data, callback_data)


class JobLocalContentUploadComponent(Component):
    name = _("本地文本框内容上传")
    code = "job_local_content_upload"
    bound_service = JobLocalContentUploadService
    form = "%scomponents/atoms/job/local_content_upload/v1_0.js" % settings.STATIC_URL
    version = "1.0.0"
