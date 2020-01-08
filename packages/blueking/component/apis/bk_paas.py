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

from ..base import ComponentAPI


class CollectionsBkPaas(object):
    """Collections of BK_PAAS APIS"""

    def __init__(self, client):
        self.client = client

        self.get_app_info = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/bk_paas/get_app_info/',
            description=u'获取应用信息'
        )
        self.create_app = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/bk_paas/create_app/',
            description=u'创建一个轻应用'
        )
        self.edit_app = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/bk_paas/edit_app/',
            description=u'编辑一个轻应用'
        )
        self.del_app = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/bk_paas/del_app/',
            description=u'下架一个轻应用'
        )
        self.modify_app_logo = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/bk_paas/modify_app_logo/',
            description=u'修改轻应用的 logo'
        )
