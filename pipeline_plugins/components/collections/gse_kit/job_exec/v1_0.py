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
from functools import partial

from django.utils.translation import ugettext_lazy as _

from api import BKGseKitClient

from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.core.flow.io import StringItemSchema
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("gsekit(gsekit)")
VERSION = "v1.0"

__register_ignore__ = True

cc_handle_api_error = partial(handle_api_error, __group_name__)


class JobStatus(object):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


JOB_STATUS_CHOICES = (
    (JobStatus.PENDING, _("等待中")),
    (JobStatus.RUNNING, _("执行中")),
    (JobStatus.SUCCEEDED, _("执行成功")),
    (JobStatus.FAILED, _("执行失败")),
)


class GsekitJobExecService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)  # 每隔5秒钟进行重启结果状态轮询

    def schedule(self, data, parent_data, callback_data=None):
        """
        gsekit-轮询服务重启结果
        """
        executor = parent_data.get_one_of_inputs("executor")
        client = BKGseKitClient(executor)
        job_task_id = data.outputs.gsekit_job_task_id

        job_task_status = client.job_status(job_task_id=job_task_id)
        self.logger.info("gsekit job {id} with status {status}".format(id=job_task_id, status=job_task_status))

        if not job_task_status["result"]:
            err_message = handle_api_error("gsekit", "gsekit.check_job_task_status", job_task_id, job_task_status)
            data.set_outputs("ex_data", err_message)
            return False

        code = job_task_status["data"]["status"]

        if code == JobStatus.SUCCEEDED:
            self.finish_schedule()
            return True
        elif code in (JobStatus.PENDING, JobStatus.RUNNING):
            return True
        else:
            self.logger.error(
                "unexpect gsekit job task status code: {}, gsekit response: {}".format(code, job_task_status)
            )
            data.set_outputs("ex_data", "unexpect gsekit job task status code: {}".format(code))
            return False

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("环境类型"), key="gsekit_bk_env", type="string", schema=StringItemSchema(description=_("当前业务的环境类型")),
            ),
            self.InputItem(
                name=_("操作对象"),
                key="gsekit_job_object_choices",
                type="string",
                schema=StringItemSchema(description=_("操作对象"), enum=["CONFIGFILE", "PROCESS"]),
            ),
            self.InputItem(
                name=_("操作类型"),
                key="gsekit_job_action_choices",
                type="string",
                schema=StringItemSchema(description=_("操作类型")),
            ),
            self.InputItem(
                name=_("集群ID"), key="gsekit_set", type="string", schema=StringItemSchema(description=_("集群ID")),
            ),
            self.InputItem(
                name=_("模块ID"), key="gsekit_module", type="string", schema=StringItemSchema(description=_("模块ID"),),
            ),
            self.InputItem(
                name=_("服务实例"),
                key="gsekit_service_id",
                type="string",
                schema=StringItemSchema(description=_("服务实例ID"),),
            ),
            self.InputItem(
                name=_("进程"), key="gsekit_process_name", type="string", schema=StringItemSchema(description=_("进程ID"),),
            ),
            self.InputItem(
                name=_("进程实例"),
                key="gsekit_process_id",
                type="string",
                schema=StringItemSchema(description=_("进程实例ID"),),
            ),
        ]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        biz_cc_id = data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id)

        gsekit_bk_env = data.get_one_of_inputs("gsekit_bk_env")
        gsekit_job_object_choices = data.get_one_of_inputs("gsekit_job_object_choices")
        gsekit_job_action_choices = data.get_one_of_inputs("gsekit_job_action_choices")

        gsekit_set = data.get_one_of_inputs("gsekit_set")
        gsekit_module = data.get_one_of_inputs("gsekit_module")
        gsekit_service_id = data.get_one_of_inputs("gsekit_service_id")
        gsekit_process_name = data.get_one_of_inputs("gsekit_process_name")
        gsekit_process_id = data.get_one_of_inputs("gsekit_process_id")
        scope_param = {
            "bk_set_env": gsekit_bk_env,
            "bk_set_ids": [gsekit_set],
            "bk_module_ids": [gsekit_module],
            "bk_service_ids": [gsekit_service_id],  # 服务实例id 列表
            "bk_process_names": [gsekit_process_name],
            "bk_process_ids": [gsekit_process_id],
        }

        client = BKGseKitClient(executor)
        job_result = client.create_job(
            bk_biz_id=biz_cc_id,
            job_object=gsekit_job_object_choices,
            job_action=gsekit_job_action_choices,
            scope=scope_param,
        )
        self.logger.info("start gsekit job task with param {0}".format(scope_param))
        if job_result["result"]:
            job_id = job_result["data"]["job_id"]
            data.set_outputs("gsekit_job_task_id", job_id)
            return True
        else:
            self.logger.error("unexpect gsekit job task: {}, gsekit response: {}".format(scope_param, job_result))
            err_message = handle_api_error("gsekit", "gsekit.", scope_param, job_result)
            data.set_outputs("ex_data", err_message)
            return False

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("gsekit_job_task_ID"),
                key="gsekit_job_task_id",
                type="string",
                schema=StringItemSchema(description=_("gsekit的任务ID")),
            )
        ]


class GsekitJobExecComponent(Component):
    """
    @version log（v1.0）: gsekit, 固定命令列表
    """

    name = _("gsekit执行命令")
    code = "gsekit_job_exec"
    bound_service = GsekitJobExecService
    form = "{static_url}components/atoms/gsekit/job_exec/{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
