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

import logging
from copy import deepcopy
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import ArrayItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.components.collections.sites.open.job import JobService
from pipeline_plugins.components.collections.sites.open.job.ipv6_base import GetJobTargetServerMixin
from pipeline_plugins.components.utils import get_job_instance_url, get_node_callback_url, loose_strip

logger = logging.getLogger("celery")
__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobFastPushFileService(JobService, GetJobTargetServerMixin):
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
                            "ip": StringItemSchema(description=_("机器 IP")),
                            "files": StringItemSchema(description=_("文件路径")),
                            "account": StringItemSchema(description=_("执行账户")),
                        },
                    ),
                ),
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
        ]

    def plugin_execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        client.set_bk_api_ver("v2")
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)
        original_source_files = deepcopy(data.get_one_of_inputs("job_source_files", []))
        file_source = []
        for item in original_source_files:
            clean_result, server = self.get_target_server(
                executor,
                biz_cc_id,
                data,
                item["ip"],
                self.logger,
                False,
            )
            if not clean_result:
                return False
            file_source.append(
                {
                    "file_list": [_file.strip() for _file in item["files"].split("\n") if _file.strip()],
                    "server": server,
                    "account": {
                        "alias": loose_strip(item["account"]),
                    },
                }
            )

        original_ip_list = data.get_one_of_inputs("job_ip_list")

        clean_result, target_server = self.get_target_server(
            executor, biz_cc_id, data, original_ip_list, self.logger, False
        )
        if not clean_result:
            return False

        job_timeout = data.get_one_of_inputs("job_timeout")

        job_kwargs = {
            "bk_scope_type": JobBizScopeType.BIZ.value,
            "bk_scope_id": str(biz_cc_id),
            "bk_biz_id": biz_cc_id,
            "file_source_list": file_source,
            "target_server": target_server,
            "account_alias": data.get_one_of_inputs("job_account"),
            "file_target_path": data.get_one_of_inputs("job_target_path"),
            "callback_url": get_node_callback_url(self.root_pipeline_id, self.id, getattr(self, "version", "")),
        }
        if job_timeout:
            job_kwargs["timeout"] = int(job_timeout)

        job_result = client.jobv3.fast_transfer_file(job_kwargs)
        self.logger.info("job_result: {result}, job_kwargs: {kwargs}".format(result=job_result, kwargs=job_kwargs))
        if job_result["result"]:
            job_instance_id = job_result["data"]["job_instance_id"]
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result["data"]["job_instance_name"]
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.client = client
            return True
        else:
            message = job_handle_api_error("jobv3.fast_transfer_file", job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

    def outputs_format(self):
        return super(JobFastPushFileService, self).outputs_format()


class JobFastPushFileComponent(Component):
    name = _("快速分发文件")
    code = "job_fast_push_file"
    bound_service = JobFastPushFileService
    form = "%scomponents/atoms/job/job_fast_push_file.js" % settings.STATIC_URL
