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

from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component

from gcloud.conf import settings

from .v2_0 import JobExecuteTaskService as JobExecuteTaskServiceV20


class JobExecuteTaskService(JobExecuteTaskServiceV20):
    """执行作业 v2.1：支持使用节点名称+时间戳作为 job 任务名"""

    use_node_task_name = True


class JobExecuteTaskComponent(Component):
    name = _("执行作业")
    code = "job_execute_task"
    bound_service = JobExecuteTaskService
    form = "%scomponents/atoms/job/execute_task/v2_0.js" % settings.STATIC_URL
    output_form = "%scomponents/atoms/job/job_execute_task_output.js" % settings.STATIC_URL
    version = "2.1"
    desc = _(
        "1.当用户选择JOB成功历史后，插件将不再创建新的JOB实例，直接继承JOB成功状态. \n"
        "2.在接收到用户编辑的全局变量后，v1.0及v1.1会默认用英文双引号将默认变量值包裹起来，再将得到的字符串作为一个整体在调用API时进行传参。\n"
        "如果不需要双引号包裹，可以使用legacy或v1.2及以上版本插件，也可以手动在表格中去掉。\n"
        "3. 去除IP存在性校验，默认开启新版IP tag分组, 默认开启失败时提取变量，job成功历史调整为只在重试时显示\n"
        "4. V2.0版本支持在全局变量的IP参数中传入host_id，插件会自动识别并构造相应的调用参数。\n"
        "5. V2.1版本支持使用节点名称+时间戳作为 job 任务名，便于在作业平台中识别任务来源。\n"
    )
