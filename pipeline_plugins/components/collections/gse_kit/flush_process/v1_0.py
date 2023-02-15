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

from django.utils.translation import ugettext_lazy as _

from api import BKGseKitClient

from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("celery")

__group_name__ = _("GSEKIT(gsekit)")
VERSION = "1.0"


class GsekitFlushProcessService(Service):
    def inputs_format(self):
        return []

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        bk_biz_id = parent_data.get_one_of_inputs("biz_cc_id")
        client = BKGseKitClient(executor)

        self.logger.info("gsekit bk_biz_id {bk_biz_id} is flushing...".format(bk_biz_id=bk_biz_id))
        flush_result = client.flush_process(bk_biz_id)
        if not flush_result["result"]:
            err_message = handle_api_error("gsekit", "gsekit.flush_process", bk_biz_id, flush_result)
            data.set_outputs("ex_data", err_message)
            return False
        return True

    def outputs_format(self):
        return []


class GsekitFlushProcessInstanceComponent(Component):
    """
    @version log（v1.0）: gsekit
    """

    name = _("刷新进程实例")
    code = "gsekit_flush_process"
    bound_service = GsekitFlushProcessService
    form = "{static_url}components/atoms/gse_kit/flush_process/v{ver}.js".format(
        static_url=settings.STATIC_URL, ver=VERSION.replace(".", "_")
    )
    version = VERSION
