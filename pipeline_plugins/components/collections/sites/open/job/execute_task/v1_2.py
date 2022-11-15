# -*- coding: utf-8 -*-
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

from .execute_task_base import JobExecuteTaskServiceBase
from ..base import GetJobHistoryResultMixin, get_job_tagged_ip_dict_complex
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import StringItemSchema
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobExecuteTaskService(JobExecuteTaskServiceBase, GetJobHistoryResultMixin):
    need_get_sops_var = True
    need_is_tagged_ip = True

    def outputs_format(self):
        return super().outputs_format() + [
            self.OutputItem(
                name=_("JOB执行IP分组"),
                key="job_tagged_ip_dict",
                type="string",
                schema=StringItemSchema(
                    description=_(
                        '按照执行结果将 IP 进行分组：1. 使用 job_tagged_ip_dict["value"]["SUCCESS"]["TAGS"]["ALL"]  获取「执行成功」的 IP， '
                        "ALL 代表所有 IP，可指定分组名获取特定分组的 IP ；"
                        '2. 使用 job_tagged_ip_dict["value"]["SCRIPT_NOT_ZERO_EXIT_CODE"]["TAGS"]["ALL"]'
                        " 获取「脚本返回值非零」的 IP"
                    )
                ),
            ),
        ]

    def is_need_log_outputs_even_fail(self, data):
        """
        默认开启失败时提取变量
        """
        return True

    def check_ip_is_exist(self, data):
        """
        默认不校验IP
        """
        return False

    def get_tagged_ip_dict(self, data, parent_data, job_instance_id):
        """
        默认使用ip新版分组
        """
        result, tagged_ip_dict = get_job_tagged_ip_dict_complex(
            data.outputs.client,
            self.logger,
            job_instance_id,
            data.get_one_of_inputs("biz_cc_id", parent_data.inputs.biz_cc_id),
            job_scope_type=self.biz_scope_type,
        )
        return result, tagged_ip_dict

    def execute(self, data, parent_data):
        job_success_id = data.get_one_of_inputs("job_success_id")
        if not job_success_id:
            return super().execute(data, parent_data)
        history_result = self.get_job_history_result(data, parent_data)
        self.logger.info(history_result)
        if history_result:
            self.__need_schedule__ = False
        return history_result


class JobExecuteTaskComponent(Component):
    name = _("执行作业")
    code = "job_execute_task"
    bound_service = JobExecuteTaskService
    form = "%scomponents/atoms/job/execute_task/v1_2.js" % settings.STATIC_URL
    output_form = "%scomponents/atoms/job/job_execute_task_output.js" % settings.STATIC_URL
    version = "1.2"
    desc = _(
        "1.当用户选择JOB成功历史后，插件将不再创建新的JOB实例，直接继承JOB成功状态. \n"
        "2.在接收到用户编辑的全局变量后，v1.0及以上版本会默认用英文双引号将默认变量值包裹起来，再将得到的字符串作为一个整体在调用API时进行传参。\n"
        "如果不需要双引号包裹，可以使用legacy版本插件，也可以手动在表格中去掉。\n"
        "3. 去除IP存在性校验，默认开启新版IP tag分组, 默认开启失败时提取变量，job成功历史调整为只在重试时显示"
    )
