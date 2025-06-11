# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from iam.contrib.tastypie.resource import IAMResourceHelper

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.resource_helpers.base import SimpleSubjectEnvHelperMixin


class ViewSetResourceHelper(SimpleSubjectEnvHelperMixin, IAMResourceHelper):
    def __init__(self, resource_func, iam, system=IAMMeta.SYSTEM_ID, id_field="id", *args, **kwargs):
        self.resource_func = resource_func
        self.id_field = id_field
        super().__init__(iam, system, *args, **kwargs)

    def get_resources(self, obj):
        return self.resource_func(obj)

    def get_resources_id(self, obj):
        resource = obj
        for field in self.id_field.split("."):
            resource = getattr(resource, field)
        return resource
