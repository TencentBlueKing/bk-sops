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

import copy

from pipeline.utils.http import http_post_request

from gcloud.conf import settings

BK_IAM_APPLY_URL_QUERY_URL = '{}/api/v1/apply-permission/url/'.format(settings.BK_IAM_SAAS_HOST)


def apply_permission_url(permission):
    """
    @summary: 获取到权限申请URL，在很短时间内（可能1分钟）将失效
    @param permission:
    @return:
    """
    perms = copy.deepcopy(permission)

    for perm_item in perms:
        for resource_topo in perm_item['resources']:
            for resource in resource_topo:
                resource_id = resource.get('resource_id')
                if resource_id is not None:
                    resource['resource_id'] = str(resource_id)

    result = http_post_request(BK_IAM_APPLY_URL_QUERY_URL, json={'permission': perms}, verify=False)
    return result
