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

from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import BooleanItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

from ..base import GetJobHistoryResultMixin
from .execute_task_base import JobExecuteTaskServiceBase

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobExecuteTaskService(JobExecuteTaskServiceBase, GetJobHistoryResultMixin):
    def inputs_format(self):
        return super().inputs_format() + [
            self.InputItem(
                name=_("IP Tag 分组"),
                key="is_tagged_ip",
                type="boolean",
                schema=BooleanItemSchema(description=_("是否对 IP 进行 Tag 分组")),
            ),
            self.InputItem(
                name=_("IP 存在性校验"),
                key="ip_is_exist",
                type="boolean",
                schema=BooleanItemSchema(description=_("是否做 IP 存在性校验，如果ip校验开关打开，校验通过的ip数量若减少，即返回错误")),
            ),
        ]

    def outputs_format(self):
        return super().outputs_format() + [
            self.OutputItem(
                name=_("JOB执行IP分组"),
                key="job_tagged_ip_dict",
                type="string",
                schema=StringItemSchema(description=_("根据JOB步骤执行标签获取的IP分组")),
            ),
        ]

    def plugin_execute(self, data, parent_data):
        job_success_id = data.get_one_of_inputs("job_success_id")
        if not job_success_id:
            return super().plugin_execute(data, parent_data)
        history_result = self.get_job_history_result(data, parent_data)
        self.logger.info(history_result)
        if history_result:
            self.__need_schedule__ = False
        return history_result


class JobExecuteTaskComponent(Component):
    name = _("执行作业")
    code = "job_execute_task"
    bound_service = JobExecuteTaskService
    form = "%scomponents/atoms/job/execute_task/v1_1.js" % settings.STATIC_URL
    output_form = "%scomponents/atoms/job/job_execute_task_output.js" % settings.STATIC_URL
    version = "1.1"
    desc = _(
        "1.当用户选择JOB成功历史后，插件将不再创建新的JOB实例，直接继承JOB成功状态. \n"
        "2.在接收到用户编辑的全局变量后，v1.0及v1.1版本会默认用英文双引号将默认变量值包裹起来，再将得到的字符串作为一个整体在调用API时进行传参。\n"
        "如果不需要双引号包裹，可以使用legacy或v1.2版本插件，也可以手动在表格中去掉。"
    )
