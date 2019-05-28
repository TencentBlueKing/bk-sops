# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.conf.urls import include, url
from tastypie.api import Api

from pipeline.contrib.web.webresource.resource import (PipelineTemplateResource,
                                                       ComponentModelResource,
                                                       PipelineInstanceResource,
                                                       TemplateSchemeResource)
from pipeline.contrib.web import urls_v1, urls_web
from pipeline_plugins.components import urls

v1_api = Api(api_name='v1')
v1_api.register(PipelineTemplateResource())
v1_api.register(ComponentModelResource())
v1_api.register(PipelineInstanceResource())
v1_api.register(TemplateSchemeResource())


urlpatterns = [
    url(r'^', include(urls_web)),
    url(r'^api/', include(v1_api.urls)),
    url(r'^api/v1/', include(urls_v1)),
    url(r'^', include(urls)),
]
