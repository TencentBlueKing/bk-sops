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

from mock import MagicMock, patch
from django.test import TestCase

from files.exceptions import InvalidOperationError
from files.managers.job_repo import JobRepoManager


class JobRepoManagerTestCase(TestCase):
    def setUp(self) -> None:
        self.file_name = "file_name_token"
        self.content = "content_token"
        self.upload_url = "upload_url_token"
        self.path = "path_token"
        self.bk_biz_id = "bk_biz_id_token"

    def test_save(self):
        bk_biz = MagicMock()
        bk_biz.bk_biz_id = self.bk_biz_id
        mock_first = MagicMock()
        mock_first.first = MagicMock(return_value=bk_biz)
        qs_filter = MagicMock()
        qs_filter.only = MagicMock(return_value=mock_first)
        upload_url_return = MagicMock(
            return_value={
                "result": True,
                "data": {"url_map": {self.file_name: {"upload_url": self.upload_url, "path": self.path}}},
            }
        )

        manager = JobRepoManager()
        with patch("files.managers.job_repo.JobRepoStorage.generate_temporary_upload_url", upload_url_return):
            with patch(
                "files.managers.job_repo.JobRepoStorage.save",
                MagicMock(return_value={"result": True, "data": {"nodeInfo": {"md5": "file_md5"}}, "message": ""}),
            ):
                with patch("files.managers.job_repo.Project.objects.filter", MagicMock(return_value=qs_filter)):
                    kwargs = {"project_id": 1, "username": "user_name"}
                    tag = manager.save(name=self.file_name, content=self.content, shims=None, **kwargs)
                    manager.storage.generate_temporary_upload_url.assert_called_once_with(
                        username="user_name", bk_biz_id=self.bk_biz_id, file_names=[self.file_name]
                    )
                    manager.storage.save.assert_called_once_with(self.upload_url, self.file_name, self.content)
                    self.assertEqual(
                        tag,
                        {
                            "type": "job_repo",
                            "tags": {"file_path": self.path, "name": self.file_name},
                            "md5": "file_md5",
                        },
                    )

    def test_push_files_to_ips__success(self):
        file_tags = [
            {"type": "job_repo", "tags": {"file_path": "file/path/1/a.txt", "name": "a.txt"}},
            {"type": "job_repo", "tags": {"file_path": "file/path/2/b.txt", "name": "b.txt"}},
        ]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account_token"

        esb_client = MagicMock()
        esb_client.jobv3.fast_transfer_file = MagicMock(
            return_value={"result": True, "data": {"job_instance_id": "job_id"}}
        )

        manager = JobRepoManager()
        result = manager.push_files_to_ips(
            esb_client=esb_client,
            bk_biz_id=self.bk_biz_id,
            file_tags=file_tags,
            ips=ips,
            target_path=target_path,
            account=account,
        )

        job_kwargs = {
            "bk_scope_type": "biz",
            "bk_scope_id": str(self.bk_biz_id),
            "bk_biz_id": self.bk_biz_id,
            "account_alias": account,
            "file_target_path": target_path,
            "file_source_list": [{"file_list": ["file/path/1/a.txt", "file/path/2/b.txt"], "file_type": 2}],
            "target_server": {"ip_list": ips},
        }

        esb_client.jobv3.fast_transfer_file.assert_called_once_with(job_kwargs)

        self.assertEqual(result, {"result": True, "data": {"job_id": "job_id"}})

    def test_push_files_to_ips__with_other_tags(self):
        file_tags = [{"type": "bk_repo", "tags": {}}]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account_token"
        esb_client = "esb_client"

        manager = JobRepoManager()
        self.assertRaises(
            InvalidOperationError,
            manager.push_files_to_ips,
            esb_client=esb_client,
            bk_biz_id=self.bk_biz_id,
            file_tags=file_tags,
            target_path=target_path,
            ips=ips,
            account=account,
        )

    def test_push_files_to_ips__failed(self):
        file_tags = [
            {"type": "job_repo", "tags": {"file_path": "file/path/1/a.txt", "name": "a.txt"}},
            {"type": "job_repo", "tags": {"file_path": "file/path/2/b.txt", "name": "b.txt"}},
        ]
        target_path = "/user/data"
        ips = "ips_token"
        account = "account_token"

        job_response = {"result": False, "data": {}, "message": "fast_transfer_file failed"}
        esb_client = MagicMock()
        esb_client.jobv3.fast_transfer_file = MagicMock(return_value=job_response)

        manager = JobRepoManager()
        result = manager.push_files_to_ips(
            esb_client=esb_client,
            bk_biz_id=self.bk_biz_id,
            file_tags=file_tags,
            ips=ips,
            target_path=target_path,
            account=account,
        )

        job_kwargs = {
            "bk_scope_type": "biz",
            "bk_scope_id": str(self.bk_biz_id),
            "bk_biz_id": self.bk_biz_id,
            "account_alias": account,
            "file_target_path": target_path,
            "file_source_list": [{"file_list": ["file/path/1/a.txt", "file/path/2/b.txt"], "file_type": 2}],
            "target_server": {"ip_list": ips},
        }

        esb_client.jobv3.fast_transfer_file.assert_called_once_with(job_kwargs)

        self.assertEqual(
            result,
            {
                "result": False,
                "message": "fast_transfer_file failed",
                "response": job_response,
                "kwargs": job_kwargs,
                "job_api": "jobv3.fast_transfer_file",
            },
        )
