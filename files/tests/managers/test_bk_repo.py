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

import os

from mock import MagicMock, patch
from django.test import TestCase

from files.managers.bk_repo import BKRepoManager
from files.models import BKJobFileSource


class MockClient:
    def __init__(self, username, password, project_id, bucket, endpoint_url):
        self.username = username
        self.password = password
        self.project = project_id
        self.bucket = bucket
        self.endpoint_url = endpoint_url


class MockBKRepoStorage:
    def __init__(self, username, password, project_id, bucket, endpoint_url, file_overwrite):
        self.file_overwrite = file_overwrite
        self.client = MockClient(username, password, project_id, bucket, endpoint_url)
        self.save = MagicMock()


class BKRepoManagerTestCase(TestCase):
    def setUp(self):
        self.username = "username"
        self.password = "password"
        self.project_id = "project_id"
        self.bucket = "bucket"
        self.endpoint_url = "endpoint_url"
        self.file_overwrite = True
        self.patch_path = "files.managers.bk_repo"

        with patch(f"{self.patch_path}.BKRepoStorage", MockBKRepoStorage):
            self.manager = BKRepoManager(
                username=self.username,
                password=self.password,
                project_id=self.project_id,
                bucket=self.bucket,
                endpoint_url=self.endpoint_url,
                file_overwrite=self.file_overwrite,
            )
            self.manager._uniq_id = MagicMock(return_value="uniq_id")

    def test_init(self):
        self.assertEqual(self.manager.storage.client.username, self.username)
        self.assertEqual(self.manager.storage.client.password, self.password)
        self.assertEqual(self.manager.storage.client.project, self.project_id)
        self.assertEqual(self.manager.storage.client.bucket, self.bucket)
        self.assertEqual(self.manager.storage.client.endpoint_url, self.endpoint_url)
        self.assertEqual(self.manager.storage.file_overwrite, self.file_overwrite)

    def test_generate_temporary_url(self):
        project_id = bk_biz_id = 1
        name = "test_file.txt"
        test_result_url = "test_result_url"
        shims = f"prefix/{project_id}"

        self.manager.storage.client.generate_presigned_url = MagicMock(return_value=test_result_url)
        test_result = self.manager.generate_temporary_url(bk_biz_id=bk_biz_id, name=name, shims=shims)

        self.assertEqual(test_result["result"], True)
        self.assertEqual(test_result["data"]["url"], test_result_url)
        self.assertEqual(test_result["data"]["file_path"], f"{shims}/uniq_id/{name}")

    def test_save__without_shims(self):
        name = "file_name"
        content = "file_content"
        tag = self.manager.save(name=name, content=content)
        self.manager.storage.save.assert_called_once_with(os.path.join("", "uniq_id", name), content)
        self.assertEqual(tag, {"type": "bk_repo", "tags": {"uid": "uniq_id", "shims": None, "name": name}})

    def test_save__with_shims(self):
        name = "file_name"
        content = "file_content"
        shims = "shims"
        tag = self.manager.save(name=name, content=content, shims=shims)
        self.manager.storage.save.assert_called_once_with(os.path.join("", shims, "uniq_id", name), content)
        self.assertEqual(tag, {"type": "bk_repo", "tags": {"uid": "uniq_id", "shims": shims, "name": name}})

    def test_push_files_to_ips__success(self):
        bk_biz_id = 1
        bk_job_file_source = MagicMock()
        bk_job_file_source.file_source_id = "file_source_id"
        JOB_FILE_BIZ_ID = 1

        file_tags = [
            {"type": "bk_repo", "tags": {"uid": "uid_1", "shims": "shims_1", "name": "file_1"}},
            {"type": "bk_repo", "tags": {"uid": "uid_2", "shims": "shims_2", "name": "file_2"}},
            {"type": "bk_repo", "tags": {"uid": "uid_3", "shims": "shims_3", "name": "file_3"}},
        ]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account"

        job_id = "12345"
        esb_client = MagicMock()
        esb_client.jobv3.fast_transfer_file = MagicMock(
            return_value={"result": True, "data": {"job_instance_id": job_id}}
        )

        with patch("files.managers.bk_repo.BKJobFileSource.objects.get", MagicMock(return_value=bk_job_file_source)):
            with patch("files.env.JOB_FILE_BIZ_ID", JOB_FILE_BIZ_ID):
                result = self.manager.push_files_to_ips(
                    esb_client=esb_client,
                    bk_biz_id=bk_biz_id,
                    file_tags=file_tags,
                    target_path=target_path,
                    ips=ips,
                    account=account,
                )

                esb_client.jobv3.fast_transfer_file.assert_called_once_with(
                    {
                        "bk_biz_id": JOB_FILE_BIZ_ID,
                        "account_alias": account,
                        "file_target_path": target_path,
                        "file_source_list": [
                            {
                                "file_list": [
                                    os.path.join(self.project_id, self.bucket, "shims_1", "uid_1", "file_1"),
                                    os.path.join(self.project_id, self.bucket, "shims_2", "uid_2", "file_2"),
                                    os.path.join(self.project_id, self.bucket, "shims_3", "uid_3", "file_3"),
                                ],
                                "file_type": 3,
                                "file_source_id": bk_job_file_source.file_source_id,
                            }
                        ],
                        "target_server": {"ip_list": ips},
                    }
                )

                self.assertEqual(result, {"result": True, "data": {"job_id": job_id}})

    def test_push_files_to_ips__fail(self):
        bk_biz_id = 1
        bk_job_file_source = MagicMock()
        bk_job_file_source.file_source_id = "file_source_id"
        JOB_FILE_BIZ_ID = 1

        file_tags = [
            {"type": "bk_repo", "tags": {"uid": "uid_1", "shims": "shims_1", "name": "file_1"}},
            {"type": "bk_repo", "tags": {"uid": "uid_2", "shims": "shims_2", "name": "file_2"}},
            {"type": "bk_repo", "tags": {"uid": "uid_3", "shims": "shims_3", "name": "file_3"}},
        ]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account"

        esb_client = MagicMock()
        esb_client.jobv3.fast_transfer_file = MagicMock(return_value={"result": False, "message": "fail msg"})

        with patch("files.managers.bk_repo.BKJobFileSource.objects.get", MagicMock(return_value=bk_job_file_source)):
            with patch("files.env.JOB_FILE_BIZ_ID", JOB_FILE_BIZ_ID):
                result = self.manager.push_files_to_ips(
                    esb_client=esb_client,
                    bk_biz_id=bk_biz_id,
                    file_tags=file_tags,
                    target_path=target_path,
                    ips=ips,
                    account=account,
                )

                job_kwargs = {
                    "bk_biz_id": JOB_FILE_BIZ_ID,
                    "account_alias": account,
                    "file_target_path": target_path,
                    "file_source_list": [
                        {
                            "file_list": [
                                os.path.join(self.project_id, self.bucket, "shims_1", "uid_1", "file_1"),
                                os.path.join(self.project_id, self.bucket, "shims_2", "uid_2", "file_2"),
                                os.path.join(self.project_id, self.bucket, "shims_3", "uid_3", "file_3"),
                            ],
                            "file_type": 3,
                            "file_source_id": bk_job_file_source.file_source_id,
                        }
                    ],
                    "target_server": {"ip_list": ips},
                }
                esb_client.jobv3.fast_transfer_file.assert_called_once_with(job_kwargs)

                self.assertEqual(
                    result,
                    {
                        "result": False,
                        "message": "fail msg",
                        "response": {"result": False, "message": "fail msg"},
                        "kwargs": job_kwargs,
                        "job_api": "jobv3.fast_transfer_file",
                    },
                )

    def test_push_files_to_ips__without_job_info(self):
        bk_biz_id = 1
        file_source_id = "file_source_id"
        credential_id = "credential_id"
        JOB_FILE_BIZ_ID = 1

        file_tags = [
            {"type": "bk_repo", "tags": {"uid": "uid_1", "shims": "shims_1", "name": "file_1"}},
            {"type": "bk_repo", "tags": {"uid": "uid_2", "shims": "shims_2", "name": "file_2"}},
            {"type": "bk_repo", "tags": {"uid": "uid_3", "shims": "shims_3", "name": "file_3"}},
        ]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account"

        job_id = "12345"
        esb_client = MagicMock()
        esb_client.jobv3.fast_transfer_file = MagicMock(
            return_value={"result": True, "data": {"job_instance_id": job_id}}
        )

        credential_create = MagicMock(return_value={"result": True, "data": credential_id})
        file_source_create = MagicMock(return_value={"result": True, "data": file_source_id})

        with patch(
            "files.managers.bk_repo.BKJobFileSource.objects.get", MagicMock(side_effect=BKJobFileSource.DoesNotExist)
        ):
            with patch(
                "files.managers.bk_repo.BKJobFileCredential.objects.get_or_create_credential", credential_create
            ):
                with patch(
                    "files.managers.bk_repo.BKJobFileSource.objects.get_or_create_file_source", file_source_create
                ):
                    with patch("files.env.JOB_FILE_BIZ_ID", JOB_FILE_BIZ_ID):
                        result = self.manager.push_files_to_ips(
                            esb_client=esb_client,
                            bk_biz_id=bk_biz_id,
                            file_tags=file_tags,
                            target_path=target_path,
                            ips=ips,
                            account=account,
                        )
                        credential_create.assert_called_once_with(bk_biz_id=JOB_FILE_BIZ_ID, esb_client=esb_client)
                        file_source_create.assert_called_once_with(JOB_FILE_BIZ_ID, credential_id, esb_client)

                        esb_client.jobv3.fast_transfer_file.assert_called_once_with(
                            {
                                "bk_biz_id": JOB_FILE_BIZ_ID,
                                "account_alias": account,
                                "file_target_path": target_path,
                                "file_source_list": [
                                    {
                                        "file_list": [
                                            os.path.join(self.project_id, self.bucket, "shims_1", "uid_1", "file_1"),
                                            os.path.join(self.project_id, self.bucket, "shims_2", "uid_2", "file_2"),
                                            os.path.join(self.project_id, self.bucket, "shims_3", "uid_3", "file_3"),
                                        ],
                                        "file_type": 3,
                                        "file_source_id": file_source_id,
                                    }
                                ],
                                "target_server": {"ip_list": ips},
                            }
                        )

                        self.assertEqual(result, {"result": True, "data": {"job_id": job_id}})
