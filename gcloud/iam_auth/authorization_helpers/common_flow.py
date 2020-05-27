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

from iam import Resource

from gcloud.iam_auth.conf import IAMMeta
from gcloud.iam_auth.authorization_helpers.base import EmptyEnvIAMAuthorizationHelper


class CommonFlowIAMAuthorizationHelper(EmptyEnvIAMAuthorizationHelper):
    def _get_flow_resources(self, bundle):
        return [
            Resource(
                IAMMeta.SYSTEM_ID,
                IAMMeta.COMMON_FLOW_RESOURCE,
                str(bundle.obj.id),
                {"iam_resource_owner": bundle.obj.creator},
            )
        ]

    def get_create_detail_resources(self, bundle):
        return []

    def get_read_detail_resources(self, bundle):
        return self._get_flow_resources(bundle)

    def get_update_detail_resources(self, bundle):
        return self._get_flow_resources(bundle)

    def get_delete_detail_resources(self, bundle):
        return self._get_flow_resources(bundle)
