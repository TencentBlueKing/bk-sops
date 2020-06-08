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

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.resource_helpers.base import SimpleSubjectEnvHelperMixin


from iam import Resource
from iam.contrib.tastypie.resource import IAMResourceHelper


class MiniAppResourceHelper(SimpleSubjectEnvHelperMixin, IAMResourceHelper):
    def get_resources(self, bundle):

        return [
            Resource(
                IAMMeta.SYSTEM_ID,
                IAMMeta.MINI_APP_RESOURCE,
                str(bundle.obj.id),
                {"iam_resource_owner": bundle.obj.creator, "path": "/project,{}/".format(bundle.obj.project_id)},
            )
        ]

    def get_resources_id(self, bundle):
        return bundle.obj.id
