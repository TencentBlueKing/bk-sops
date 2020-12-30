# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
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
from gcloud.conf import settings
from pipeline.core.data.var import LazyVariable

logger = logging.getLogger("root")


class GseKitSetModuleIpSelector(LazyVariable):
    code = "gse_kit_ip_selector"
    name = _("GSEKit IP 选择器")
    type = "general"
    tag = "gse_kit_ip_selector.ip_selector"
    form = "%svariables/gse_kit/var_gse_kit_ip_selector.js" % settings.STATIC_URL

    def get_value(self):
        operator = self.pipeline_data.get("executor", "")
        var_ip_selector = self.value

        expression_scope_kwargs = {
            "bk_set_env": var_ip_selector["var_set_name"],
            "bk_set_name": var_ip_selector.get("var_set_name", "*"),
            "bk_module_name": var_ip_selector.get("var_module_name", "*"),
            "service_instance_name": var_ip_selector.get("var_service_instance_name", "*"),
            "bk_process_name": var_ip_selector.get("var_process_name", "*"),
            "bk_process_id": var_ip_selector.get("var_process_instance_id", "*"),
        }
        client = BKGseKitClient(operator)
        process_status_result = client.process_status(
            expression_scope=expression_scope_kwargs
        )
        logger.info("process_status_result {result} with {param}".format(result=process_status_result,
                                                                         param=expression_scope_kwargs))
        ip_list = [process_status["bk_host_innerip"] for process_status in process_status_result]
        ip_str = ",".join(ip_list)
        return ip_str
