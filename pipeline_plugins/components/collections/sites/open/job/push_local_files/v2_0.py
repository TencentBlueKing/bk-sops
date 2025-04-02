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

from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.components.collections.sites.open.job.push_local_files.base_service import (
    BaseJobPushLocalFilesService,
)

__group_name__ = _("作业平台(JOB)")

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobPushLocalFilesService(BaseJobPushLocalFilesService):
    pass


class JobPushLocalFilesComponent(Component):
    name = _("分发本地文件")
    code = "job_push_local_files"
    bound_service = JobPushLocalFilesService
    form = "%scomponents/atoms/job/job_push_local_files/v2_0.js" % settings.STATIC_URL
    version = "2.0"
    desc = _("本地上传的文件不保证长期保存并可用于多次分发，推荐勾选上传变量并在创建任务时进行上传操作。如果希望多次分发相同文件，请使用快速分发文件插件。")
