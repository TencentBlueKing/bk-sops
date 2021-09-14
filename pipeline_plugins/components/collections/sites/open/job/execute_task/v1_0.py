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
from django.utils.translation import ugettext_lazy as _

from .execute_task_base import JobExecuteTaskServiceBase
from pipeline.component_framework.component import Component
from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobExecuteTaskService(JobExecuteTaskServiceBase):
    pass


class JobExecuteTaskComponent(Component):
    name = _("执行作业")
    code = "job_execute_task"
    bound_service = JobExecuteTaskService
    form = "%scomponents/atoms/job/job_execute_task/v1_0.js" % settings.STATIC_URL
    output_form = "%scomponents/atoms/job/job_execute_task_output.js" % settings.STATIC_URL
    version = "1.0"
    desc = "在接收到用户编辑的全局变量后，v1.0版本会先去除首尾的全部双引号，然后在首尾各加上一个双引号，将得到的字符串作为调用API时的参数。"
