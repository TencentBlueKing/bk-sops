# -*- coding: utf-8 -*-
# isort: skip_file
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

__group_name__ = _("作业平台(JOB)")

from .base import JobService, Jobv3Service  # noqa
from .cron_task import *  # noqa
from .execute_task import *  # noqa
from .fast_execute_script import *  # noqa
from .fast_push_file import *  # noqa
from .push_local_files import *  # noqa
from .local_content_upload import *  # noqa
from .all_biz_fast_push_file import *  # noqa
from .all_biz_fast_execute_script import *  # noqa
from .all_biz_execute_job_plan import *  # noqa
