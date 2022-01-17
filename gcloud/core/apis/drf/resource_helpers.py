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

from gcloud.iam_auth import res_factory, get_iam_client, IAMMeta
from gcloud.iam_auth.resource_helpers.base import SimpleSubjectEnvHelperMixin

from iam.contrib.tastypie.resource import IAMResourceHelper

iam_client = get_iam_client()


class ResourceHelper(SimpleSubjectEnvHelperMixin, IAMResourceHelper):
    def __init__(self, res_type, iam=iam_client, system=IAMMeta.SYSTEM_ID, id_field="id", *args, **kwargs):
        self.type = res_type
        self.id_field = id_field
        super().__init__(iam, system, *args, **kwargs)

    def get_resources(self, obj):
        return getattr(res_factory, self.type)(obj)

    def get_resources_id(self, obj):
        return getattr(obj, self.id_field)
