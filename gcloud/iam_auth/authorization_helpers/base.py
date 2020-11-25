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

from iam import Subject
from iam.contrib.tastypie.authorization import IAMAuthorizationHelper


class EmptyEnvIAMAuthorizationHelper(IAMAuthorizationHelper):
    def get_subject(self, bundle):
        return Subject("user", bundle.request.user.username)

    def get_create_detail_environment(self, bundle):
        return {}

    def get_read_detail_environment(self, bundle):
        return {}

    def get_update_detail_environment(self, bundle):
        return {}

    def get_delete_detail_environment(self, bundle):
        return {}

    def get_read_list_environment(self, bundle):
        return {}
