# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os

from .managers.nfs import HostNFSManager
from .managers.upload_module import UploadModuleManager


class ManagerFactory(object):

    @classmethod
    def get_manager(cls, manager_type):
        creator = getattr(cls, '_create_{}_manager'.format(manager_type), None)
        if not creator or not callable(creator):
            raise LookupError('Can not find manager for type: {}'.format(manager_type))

        return creator()

    @classmethod
    def _create_host_nfs_manager(cls):
        location = os.getenv('BKAPP_NFS_CONTAINER_ROOT')
        server_location = os.getenv('BKAPP_NFS_HOST_ROOT')

        if not location:
            raise EnvironmentError('nfs file manager BKAPP_NFS_CONTAINER_ROOT are not config at envs')

        if not server_location:
            raise EnvironmentError('nfs file manager BKAPP_NFS_HOST_ROOT are not config at envs')

        return HostNFSManager(
            location=location,
            server_location=server_location
        )

    @classmethod
    def _create_upload_module_manager(cls):
        return UploadModuleManager()
