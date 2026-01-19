# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase
from mock import MagicMock, patch

from files.exceptions import InvalidOperationError
from files.managers.upload_module import UploadModuleManager
from files.models import UploadModuleFileTag

UPLOAD_MODULE_TAG_OBJECTS_FILTER = "files.models.UploadModuleFileTag.objects.filter"


class UploadModuleManagerTestCase(TestCase):
    def test_init(self):
        manager = UploadModuleManager()
        self.assertIsNone(manager.storage)

    def test_save(self):
        manager = UploadModuleManager()
        file_name = "file_name"
        source_ip = "source_ip"
        file_path = "file_path"
        tag = manager.save(name=file_name, content=None, source_ip=source_ip, file_path=file_path)
        self.assertEqual("upload_module", tag["type"])
        self.assertIsInstance(tag["tags"]["tag_id"], int)

        tag_model = UploadModuleFileTag.objects.get(id=tag["tags"]["tag_id"])
        self.assertEqual(tag_model.source_ip, source_ip)
        self.assertEqual(tag_model.file_name, file_name)
        self.assertEqual(tag_model.file_path, file_path)

    def test_push_files_to_ips__success_with_callback_url(self):
        tag_model_1 = MagicMock()
        tag_model_2 = MagicMock()
        tag_model_3 = MagicMock()

        tag_model_1.file_path = "path1"
        tag_model_1.source_ip = "source_ip1"
        tag_model_1.file_name = "file_name1"
        tag_model_2.file_path = "path2"
        tag_model_2.source_ip = "source_ip2"
        tag_model_2.file_name = "file_name2"
        tag_model_3.file_path = "path3"
        tag_model_3.source_ip = "source_ip3"
        tag_model_3.file_name = "file_name3"

        with patch(UPLOAD_MODULE_TAG_OBJECTS_FILTER, MagicMock(return_value=[tag_model_1, tag_model_2, tag_model_3])):

            bk_biz_id = "bk_biz_id_token"
            file_tags = [
                {"type": "upload_module", "tags": {"tag_id": 1}},
                {"type": "upload_module", "tags": {"tag_id": 2}},
                {"type": "upload_module", "tags": {"tag_id": 3}},
            ]
            target_path = "/user/data"
            ips = "ips_token"
            account = "account_token"
            callback_url = "callback_url_token"

            job_id = "12345"
            esb_client = MagicMock()
            esb_client.api.fast_transfer_file = MagicMock(
                return_value={"result": True, "data": {"job_instance_id": job_id}}
            )

            manager = UploadModuleManager()

            result = manager.push_files_to_ips(
                esb_client=esb_client,
                bk_biz_id=bk_biz_id,
                file_tags=file_tags,
                target_path=target_path,
                ips=ips,
                account=account,
                callback_url=callback_url,
            )

            UploadModuleFileTag.objects.filter.assert_called_once_with(id__in=[1, 2, 3])

            job_kwargs = {
                "bk_scope_type": "biz",
                "bk_scope_id": "bk_biz_id_token",
                "bk_biz_id": "bk_biz_id_token",
                "account_alias": "account_token",
                "file_target_path": "/user/data",
                "file_source_list": [
                    {
                        "file_list": ["path1/file_name1"],
                        "account": {"alias": "root"},
                        "server": {"ip_list": [{"bk_cloud_id": 0, "ip": "source_ip1"}]},
                    },
                    {
                        "file_list": ["path2/file_name2"],
                        "account": {"alias": "root"},
                        "server": {"ip_list": [{"bk_cloud_id": 0, "ip": "source_ip2"}]},
                    },
                    {
                        "file_list": ["path3/file_name3"],
                        "account": {"alias": "root"},
                        "server": {"ip_list": [{"bk_cloud_id": 0, "ip": "source_ip3"}]},
                    },
                ],
                "target_server": {"ip_list": "ips_token"},
                "callback_url": "callback_url_token",
            }

            esb_client.api.fast_transfer_file.assert_called_once()
            call_args = esb_client.api.fast_transfer_file.call_args
            self.assertEqual(call_args[0][0], job_kwargs)

            self.assertEqual(result, {"result": True, "data": {"job_id": job_id}})

    def test_push_files_to_ips__success_no_callback_url(self):
        tag_model_1 = MagicMock()
        tag_model_2 = MagicMock()
        tag_model_3 = MagicMock()

        tag_model_1.file_path = "path1"
        tag_model_1.source_ip = "source_ip1"
        tag_model_1.file_name = "file_name1"
        tag_model_2.file_path = "path2"
        tag_model_2.source_ip = "source_ip2"
        tag_model_2.file_name = "file_name2"
        tag_model_3.file_path = "path3"
        tag_model_3.source_ip = "source_ip3"
        tag_model_3.file_name = "file_name3"

        with patch(UPLOAD_MODULE_TAG_OBJECTS_FILTER, MagicMock(return_value=[tag_model_1, tag_model_2, tag_model_3])):

            bk_biz_id = "bk_biz_id_token"
            file_tags = [
                {"type": "upload_module", "tags": {"tag_id": 1}},
                {"type": "upload_module", "tags": {"tag_id": 2}},
                {"type": "upload_module", "tags": {"tag_id": 3}},
            ]
            target_path = "/user/data"
            ips = "ips_token"
            account = "account_token"

            job_id = "12345"
            esb_client = MagicMock()
            esb_client.api.fast_transfer_file = MagicMock(
                return_value={"result": True, "data": {"job_instance_id": job_id}}
            )

            manager = UploadModuleManager()

            result = manager.push_files_to_ips(
                esb_client=esb_client,
                bk_biz_id=bk_biz_id,
                file_tags=file_tags,
                target_path=target_path,
                ips=ips,
                account=account,
            )

            UploadModuleFileTag.objects.filter.assert_called_once_with(id__in=[1, 2, 3])

            job_kwargs = {
                "bk_scope_type": "biz",
                "bk_scope_id": "bk_biz_id_token",
                "bk_biz_id": "bk_biz_id_token",
                "account_alias": "account_token",
                "file_target_path": "/user/data",
                "file_source_list": [
                    {
                        "file_list": ["path1/file_name1"],
                        "account": {"alias": "root"},
                        "server": {"ip_list": [{"bk_cloud_id": 0, "ip": "source_ip1"}]},
                    },
                    {
                        "file_list": ["path2/file_name2"],
                        "account": {"alias": "root"},
                        "server": {"ip_list": [{"bk_cloud_id": 0, "ip": "source_ip2"}]},
                    },
                    {
                        "file_list": ["path3/file_name3"],
                        "account": {"alias": "root"},
                        "server": {"ip_list": [{"bk_cloud_id": 0, "ip": "source_ip3"}]},
                    },
                ],
                "target_server": {"ip_list": "ips_token"},
            }

            esb_client.api.fast_transfer_file.assert_called_once()
            call_args = esb_client.api.fast_transfer_file.call_args
            self.assertEqual(call_args[0][0], job_kwargs)

            self.assertEqual(result, {"result": True, "data": {"job_id": job_id}})

    def test_push_files_to_ips__with_different_tags(self):
        bk_biz_id = "bk_biz_id_token"
        file_tags = [
            {"type": "upload_module", "tags": {"uid": "uid_1", "shims": "shims_1", "name": "file_1"}},
            {"type": "host_nfs", "tags": {"uid": "uid_2", "shims": "shims_2", "name": "file_2"}},
        ]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account_token"
        esb_client = "esb_client"

        manager = UploadModuleManager()

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
        tag_model_1 = MagicMock()
        tag_model_2 = MagicMock()
        tag_model_3 = MagicMock()

        tag_model_1.file_path = "path1"
        tag_model_1.source_ip = "source_ip1"
        tag_model_1.file_name = "file_name1"
        tag_model_2.file_path = "path2"
        tag_model_2.source_ip = "source_ip2"
        tag_model_2.file_name = "file_name2"
        tag_model_3.file_path = "path3"
        tag_model_3.source_ip = "source_ip3"
        tag_model_3.file_name = "file_name3"

        with patch(UPLOAD_MODULE_TAG_OBJECTS_FILTER, MagicMock(return_value=[tag_model_1, tag_model_2, tag_model_3])):

            bk_biz_id = "bk_biz_id_token"
            file_tags = [
                {"type": "upload_module", "tags": {"tag_id": 1}},
                {"type": "upload_module", "tags": {"tag_id": 2}},
                {"type": "upload_module", "tags": {"tag_id": 3}},
            ]
            target_path = "/user/data"
            ips = "ips_token"
            account = "account_token"
            callback_url = "callback_url_token"

            esb_client = MagicMock()
            esb_client.api.fast_transfer_file = MagicMock(return_value={"result": False, "message": "msg token"})

            manager = UploadModuleManager()

            result = manager.push_files_to_ips(
                esb_client=esb_client,
                bk_biz_id=bk_biz_id,
                file_tags=file_tags,
                target_path=target_path,
                ips=ips,
                account=account,
                callback_url=callback_url,
            )

            UploadModuleFileTag.objects.filter.assert_called_once_with(id__in=[1, 2, 3])

            job_kwargs = {
                "bk_scope_type": "biz",
                "bk_scope_id": "bk_biz_id_token",
                "bk_biz_id": "bk_biz_id_token",
                "account_alias": "account_token",
                "file_target_path": "/user/data",
                "file_source_list": [
                    {
                        "file_list": ["path1/file_name1"],
                        "account": {"alias": "root"},
                        "server": {"ip_list": [{"bk_cloud_id": 0, "ip": "source_ip1"}]},
                    },
                    {
                        "file_list": ["path2/file_name2"],
                        "account": {"alias": "root"},
                        "server": {"ip_list": [{"bk_cloud_id": 0, "ip": "source_ip2"}]},
                    },
                    {
                        "file_list": ["path3/file_name3"],
                        "account": {"alias": "root"},
                        "server": {"ip_list": [{"bk_cloud_id": 0, "ip": "source_ip3"}]},
                    },
                ],
                "target_server": {"ip_list": "ips_token"},
                "callback_url": "callback_url_token",
            }

            esb_client.api.fast_transfer_file.assert_called_once()
            call_args = esb_client.api.fast_transfer_file.call_args
            self.assertEqual(call_args[0][0], job_kwargs)

            self.assertEqual(
                result,
                {
                    "result": False,
                    "message": "msg token",
                    "kwargs": job_kwargs,
                    "response": {"result": False, "message": "msg token"},
                    "job_api": "jobv3.fast_transfer_file",
                },
            )
