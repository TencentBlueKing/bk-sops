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
from pipeline_plugins.components.collections.sites.open.job.local_content_upload.base_service import (
    BaseJobLocalContentUploadService,
)

__group_name__ = _("作业平台(JOB)")


class JobLocalContentUploadService(BaseJobLocalContentUploadService):
    pass


class JobLocalContentUploadComponent(Component):
    name = _("本地文本框内容上传")
    code = "job_local_content_upload"
    bound_service = JobLocalContentUploadService
    form = "%scomponents/atoms/job/local_content_upload/v1_0.js" % settings.STATIC_URL
    version = "1.0.0"
