# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from . import env
from .managers.bk_repo import BKRepoManager
from .managers.nfs import HostNFSManager
from .managers.upload_module import UploadModuleManager
from .bartenders.nfs import HostNFSBartender
from .bartenders.upload_module import UploadModuleBartender
from .bartenders.bk_repo import BKRepoBartender


class ManagerFactory(object):
    @classmethod
    def get_manager(cls, manager_type):
        creator = getattr(cls, "_create_{}_manager".format(manager_type), None)
        if not creator or not callable(creator):
            raise LookupError("Can not find manager for type: {}".format(manager_type))

        return creator()

    @classmethod
    def _create_host_nfs_manager(cls):
        location = env.BKAPP_NFS_CONTAINER_ROOT
        server_location = env.BKAPP_NFS_HOST_ROOT

        if not location:
            raise EnvironmentError("nfs file manager BKAPP_NFS_CONTAINER_ROOT are not config at envs")

        if not server_location:
            raise EnvironmentError("nfs file manager BKAPP_NFS_HOST_ROOT are not config at envs")

        return HostNFSManager(location=location, server_location=server_location)

    @classmethod
    def _create_upload_module_manager(cls):
        return UploadModuleManager()

    @classmethod
    def _create_bk_repo_manager(cls):
        username = env.BKREPO_USERNAME
        password = env.BKREPO_PASSWORD
        project_id = env.BKREPO_PROJECT
        bucket = env.BKREPO_BUCKET
        endpoint_url = env.BKREPO_ENDPOINT_URL

        if any(v is None for v in [username, password, project_id, bucket, endpoint_url]):
            raise EnvironmentError(
                "bk_repo manager should be provided with username, password, project_id, bucket and endpoint_url"
            )
        return BKRepoManager(
            username=username,
            password=password,
            project_id=project_id,
            bucket=bucket,
            endpoint_url=endpoint_url,
            file_overwrite=True,
        )


class BartenderFactory(object):
    @classmethod
    def get_bartender(cls, manager_type, manager):
        creator = getattr(cls, "_create_{}_bartender".format(manager_type), None)
        if not creator or not callable(creator):
            raise LookupError("Can not find bartender for type: {}".format(manager_type))

        return creator(manager)

    @classmethod
    def _create_host_nfs_bartender(cls, manager):
        return HostNFSBartender(manager)

    @classmethod
    def _create_upload_module_bartender(cls, manager):
        return UploadModuleBartender(manager)

    @classmethod
    def _create_bk_repo_bartender(cls, manager):
        return BKRepoBartender(manager)
