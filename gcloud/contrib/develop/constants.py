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

INITIAL_CODE = """
# -*- coding: utf-8 -*-
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, IntItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

__group_name__ = '{esb_system_upper}'
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
new_handle_api_error = partial(handle_api_error, __group_name__)


class {esb_system_title}{esb_component_title}Service(Service):
    def inputs_format(self):
        return []

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        kwargs = data.get_inputs()
        result = client.{esb_system_lower}.{esb_component_lower}(kwargs)
        if result['result']:
            return True
        else:
            message = new_handle_api_error('{esb_system_lower}.{esb_component_lower}', kwargs, result)
            self.logger.error(message)
            data.set_outputs('ex_data', message)
            return False


class {esb_system_title}{esb_component_title}Component(Component):
    name = '{esb_system_lower}_{esb_component_lower}'
    code = '{esb_system_lower}_{esb_component_lower}'
    bound_service = {esb_system_title}{esb_component_title}Service
    form = '%scomponents/atoms/{esb_system_lower}/{esb_component_lower}.js' % settings.STATIC_URL

"""
