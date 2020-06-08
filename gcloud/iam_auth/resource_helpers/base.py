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

from iam import Resource, Subject
from iam.contrib.tastypie.resource import IAMResourceHelper

from gcloud.iam_auth.conf import SYSTEM_ID


class SimpleSubjectEnvHelperMixin(object):
    def get_subject_for_alter_list(self, request, data):
        return Subject("user", request.user.username)

    def get_environment_for_alter_list(self, request, data):
        return {}

    def get_subject_for_alter_detail(self, request, data):
        return Subject("user", request.user.username)

    def get_environment_for_alter_detail(self, request, data):
        return {}


class SimpleResourceHelper(SimpleSubjectEnvHelperMixin, IAMResourceHelper):
    def __init__(self, type, id_field, creator_field, *args, **kwargs):
        self.type = type
        self.id_field = id_field
        self.creator_field = creator_field
        super().__init__(*args, **kwargs)

    def get_resources(self, bundle):

        attributes = {}
        if self.creator_field:
            attributes["iam_resource_owner"] = getattr(bundle.obj, self.creator_field)

        return [Resource(SYSTEM_ID, self.type, str(getattr(bundle.obj, self.id_field)), attributes)]

    def get_resources_id(self, bundle):
        return getattr(bundle.obj, self.id_field)
