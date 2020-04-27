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

import os

from mock import MagicMock
from django.test import TestCase

from files.managers.nfs import HostNFSManager
from files.exceptions import InvalidOperationError


class HostNFSManagerTestCase(TestCase):
    def setUp(self):
        self.location = "location_token"
        self.server_location = "/server_location_token"

    def test_init(self):

        manager = HostNFSManager(location=self.location, server_location=self.server_location)

        self.assertEqual(manager.location, self.location)
        self.assertEqual(manager.server_location, self.server_location)

    def test_save__with_shims(self):
        manager = HostNFSManager(location=self.location, server_location=self.server_location)

        file_name = "file_name_token"
        content = "content_token"
        shims = "shims_token"
        uid = "uid_token"
        ip = "1.1.1.1"

        manager._uniqid = MagicMock(return_value=uid)
        manager._get_host_ip = MagicMock(return_value=ip)
        manager.storage = MagicMock()

        tag = manager.save(name=file_name, content=content, shims=shims)

        manager.storage.save.assert_called_once_with(
            name=os.path.join(manager.location, shims, uid, file_name), content=content, max_length=None
        )

        self.assertEqual(tag, {"type": "host_nfs", "tags": {"uid": uid, "shims": shims, "name": file_name}})

    def test_save__without_shims(self):
        manager = HostNFSManager(location=self.location, server_location=self.server_location)

        file_name = "file_name_token"
        content = "content_token"
        uid = "uid_token"
        ip = "1.1.1.1"

        manager._uniqid = MagicMock(return_value=uid)
        manager._get_host_ip = MagicMock(return_value=ip)
        manager.storage = MagicMock()

        tag = manager.save(name=file_name, content=content)

        manager.storage.save.assert_called_once_with(
            name=os.path.join(manager.location, uid, file_name), content=content, max_length=None
        )

        self.assertEqual(tag, {"type": "host_nfs", "tags": {"uid": uid, "shims": None, "name": file_name}})

    def test_push_files_to_ips__success_with_callback_url(self):

        bk_biz_id = "bk_biz_id_token"
        file_tags = [
            {"type": "host_nfs", "tags": {"uid": "uid_1", "shims": "shims_1", "name": "file_1"}},
            {"type": "host_nfs", "tags": {"uid": "uid_2", "shims": "shims_2", "name": "file_2"}},
            {"type": "host_nfs", "tags": {"uid": "uid_3", "shims": "shims_3", "name": "file_3"}},
        ]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account_token"
        callback_url = "callback_url_token"
        host_ip = "1.1.1.1"

        job_id = "12345"
        esb_client = MagicMock()
        esb_client.job.fast_push_file = MagicMock(return_value={"result": True, "data": {"job_instance_id": job_id}})

        manager = HostNFSManager(location=self.location, server_location=self.server_location)
        manager._get_host_ip = MagicMock(return_value=host_ip)

        result = manager.push_files_to_ips(
            esb_client=esb_client,
            bk_biz_id=bk_biz_id,
            file_tags=file_tags,
            target_path=target_path,
            ips=ips,
            account=account,
            callback_url=callback_url,
        )

        esb_client.job.fast_push_file.assert_called_once_with(
            {
                "bk_biz_id": bk_biz_id,
                "account": account,
                "file_target_path": target_path,
                "file_source": [
                    {
                        "files": [
                            "/server_location_token/shims_1/uid_1/file_1",
                            "/server_location_token/shims_2/uid_2/file_2",
                            "/server_location_token/shims_3/uid_3/file_3",
                        ],
                        "account": "root",
                        "ip_list": [{"bk_cloud_id": 0, "ip": host_ip}],
                    }
                ],
                "ip_list": ips,
                "bk_callback_url": callback_url,
            }
        )

        self.assertEqual(result, {"result": True, "data": {"job_id": job_id}})

    def test_push_files_to_ips__success_no_callback_url(self):

        bk_biz_id = "bk_biz_id_token"
        file_tags = [
            {"type": "host_nfs", "tags": {"uid": "uid_1", "shims": "shims_1", "name": "file_1"}},
            {"type": "host_nfs", "tags": {"uid": "uid_2", "shims": "shims_2", "name": "file_2"}},
            {"type": "host_nfs", "tags": {"uid": "uid_3", "shims": "shims_3", "name": "file_3"}},
        ]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account_token"
        host_ip = "1.1.1.1"

        job_id = "12345"
        esb_client = MagicMock()
        esb_client.job.fast_push_file = MagicMock(return_value={"result": True, "data": {"job_instance_id": job_id}})

        manager = HostNFSManager(location=self.location, server_location=self.server_location)
        manager._get_host_ip = MagicMock(return_value=host_ip)

        result = manager.push_files_to_ips(
            esb_client=esb_client,
            bk_biz_id=bk_biz_id,
            file_tags=file_tags,
            target_path=target_path,
            ips=ips,
            account=account,
        )

        esb_client.job.fast_push_file.assert_called_once_with(
            {
                "bk_biz_id": bk_biz_id,
                "account": account,
                "file_target_path": target_path,
                "file_source": [
                    {
                        "files": [
                            "/server_location_token/shims_1/uid_1/file_1",
                            "/server_location_token/shims_2/uid_2/file_2",
                            "/server_location_token/shims_3/uid_3/file_3",
                        ],
                        "account": "root",
                        "ip_list": [{"bk_cloud_id": 0, "ip": host_ip}],
                    }
                ],
                "ip_list": ips,
            }
        )

        self.assertEqual(result, {"result": True, "data": {"job_id": job_id}})

    def test_push_files_to_ips__with_different_tags(self):
        bk_biz_id = "bk_biz_id_token"
        file_tags = [
            {"type": "host_nfs", "tags": {"uid": "uid_1", "shims": "shims_1", "name": "file_1"}},
            {"type": "s3", "tags": {"uid": "uid_2", "shims": "shims_2", "name": "file_2"}},
        ]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account_token"
        esb_client = "esb_client"

        manager = HostNFSManager(location=self.location, server_location=self.server_location)

        self.assertRaises(
            InvalidOperationError,
            manager.push_files_to_ips,
            esb_client=esb_client,
            bk_biz_id=bk_biz_id,
            file_tags=file_tags,
            target_path=target_path,
            ips=ips,
            account=account,
        )

    def test_push_files_to_ips__fail(self):

        bk_biz_id = "bk_biz_id_token"
        file_tags = [
            {"type": "host_nfs", "tags": {"uid": "uid_1", "shims": "shims_1", "name": "file_1"}},
            {"type": "host_nfs", "tags": {"uid": "uid_2", "shims": "shims_2", "name": "file_2"}},
            {"type": "host_nfs", "tags": {"uid": "uid_3", "shims": "shims_3", "name": "file_3"}},
        ]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account_token"
        host_ip = "1.1.1.1"

        esb_client = MagicMock()
        esb_client.job.fast_push_file = MagicMock(return_value={"result": False, "message": "msg token"})

        manager = HostNFSManager(location=self.location, server_location=self.server_location)
        manager._get_host_ip = MagicMock(return_value=host_ip)

        result = manager.push_files_to_ips(
            esb_client=esb_client,
            bk_biz_id=bk_biz_id,
            file_tags=file_tags,
            target_path=target_path,
            ips=ips,
            account=account,
        )

        esb_client.job.fast_push_file.assert_called_once_with(
            {
                "bk_biz_id": bk_biz_id,
                "account": account,
                "file_target_path": target_path,
                "file_source": [
                    {
                        "files": [
                            "/server_location_token/shims_1/uid_1/file_1",
                            "/server_location_token/shims_2/uid_2/file_2",
                            "/server_location_token/shims_3/uid_3/file_3",
                        ],
                        "account": "root",
                        "ip_list": [{"bk_cloud_id": 0, "ip": host_ip}],
                    }
                ],
                "ip_list": ips,
            }
        )

        self.assertEqual(result, {"result": False, "message": "msg token"})
