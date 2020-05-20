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

from django.conf import settings
from iam.contrib.django.dispatcher import DjangoBasicResourceApiDispatcher

from gcloud.iam_auth.shortcuts import get_iam_client

from .common_flow import CommonFlowResourceProvider
from .flow import FlowResourceProvider
from .mini_app import MiniAppResourceProvider
from .periodic_task import PeriodicTaskResourceProvider
from .project import ProjectResourceProvider
from .task import TaskResourceProvider

dispatcher = DjangoBasicResourceApiDispatcher(get_iam_client(), settings.APP_CODE)
dispatcher.register("project", ProjectResourceProvider())
dispatcher.register("flow", FlowResourceProvider())
dispatcher.register("task", TaskResourceProvider())
dispatcher.register("common_flow", CommonFlowResourceProvider())
dispatcher.register("mini_app", MiniAppResourceProvider())
dispatcher.register("periodic_task", PeriodicTaskResourceProvider())
