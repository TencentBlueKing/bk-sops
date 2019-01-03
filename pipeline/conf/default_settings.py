# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
pipeline default settings
"""

# pipeline template context module, to use this, you need
#   1) config PIPELINE_TEMPLATE_CONTEXT in your django settings, such as
#       PIPELINE_TEMPLATE_CONTEXT = 'home_application.utils.get_template_context'
#   2) define get_template_context function in your app, which show accept one arg, such as
#         def get_template_context(obj):
#             context = {
#                 'biz_cc_id': '1',
#                 'biz_cc_name': 'test1',
#             }
#             if obj is not None:
#                 context.update({'template': '1'})
#             return context
PIPELINE_TEMPLATE_CONTEXT = ''
PIPELINE_INSTANCE_CONTEXT = ''
PIPELINE_ENGINE_ADAPTER_API = 'pipeline.service.pipeline_engine_adapter.adapter_api'
