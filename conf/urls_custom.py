# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
'''
@summary: 用户自定义URLconf
'''

from django.conf.urls import include, url

# 用户自定义 urlconf
urlpatterns_custom = [
    url(r'^', include('gcloud.core.urls')),
    url(r'^config/', include('gcloud.config.urls')),
    url(r'^apigw/', include('gcloud.apigw.urls')),
    url(r'^template/', include('gcloud.tasktmpl3.urls')),
    url(r'^taskflow/', include('gcloud.taskflow3.urls')),
    url(r'^', include('gcloud.webservice3.urls')),
    url(r'^pipeline/', include('pipeline.components.urls')),
]
