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

from __future__ import absolute_import

from mock import MagicMock, patch, call  # noqa


class MockGitRepo(object):
    def __init__(self):
        self.repo_info = {}

    def clone_from(self, repo_address, to_path, branch):
        self.repo_info = {
            'repo_address': repo_address,
            'to_path': to_path,
            'branch': branch,
        }


class MockBoto3Paginator(object):
    def __init__(self):
        self.data = [
            'file0',
            'first1/file1',
            'first1/second1/file11',
            'first1/second2/file12',
            'first2/file2',
            'first2/second1/file21',
            'first2/second2/file22',
        ]

    def paginate(self, Bucket, Delimiter, Prefix):
        if not Prefix:
            return [{
                'CommonPrefixes': [{'Prefix': 'first1/'}, {'Prefix': 'first2/'}],
                'Contents': [{'Key': 'file0'}]
            }]
        else:
            result = {
                'first1/': {
                    'CommonPrefixes': [{'Prefix': 'first1/second1/'}, {'Prefix': 'first1/second2/'}],
                    'Contents': [{'Key': 'first1/file1'}]
                },
                'first1/second1/': {
                    'CommonPrefixes': [],
                    'Contents': [{'Key': 'first1/second1/file11'}]
                },
                'first1/second2/': {
                    'CommonPrefixes': [],
                    'Contents': [{'Key': 'first1/second2/file12'}]
                },
                'first2/': {
                    'CommonPrefixes': [{'Prefix': 'first2/second1/'}, {'Prefix': 'first2/second2/'}],
                    'Contents': [{'Key': 'first2/file2'}]
                },
                'first2/second1/': {
                    'CommonPrefixes': [],
                    'Contents': [{'Key': 'first2/second1/file21'}]
                },
                'first2/second2/': {
                    'CommonPrefixes': [],
                    'Contents': [{'Key': 'first2/second2/file22'}]
                }
            }
            return [result[Prefix]]


class MockBoto3Cleint(object):
    def __init__(self, name, endpoint_url, aws_access_key_id, aws_secret_access_key, files):
        self.name = name
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.files = files

    def get_paginator(self, obj):
        return MockBoto3Paginator()

    def download_file(self, Bucket, Key, Filename):
        self.files.append(Filename)

    def upload_file(self, Filename, Bucket, Key):
        self.files.append(Filename)


class MockBoto3(object):
    def __init__(self):
        self.files = []

    def client(self, name, endpoint_url, aws_access_key_id, aws_secret_access_key):
        return MockBoto3Cleint(name, endpoint_url, aws_access_key_id, aws_secret_access_key, self.files)


class MockShutil(object):
    def __init__(self):
        self.from_path = None
        self.to_path = None

    def move(self, from_path, to_path):
        self.from_path = from_path
        self.to_path = to_path


def mock_os_walk(local):
    root = local
    result = [(local, None, ['file'])]
    for path in ['first', 'second']:
        root = '%s%s/' % (root, path)
        result.append((root, None, ['file']))
    return result


class MockWriterAndReader(object):
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def write(self, sub_dir=None):
        if 'raise_exception' in self.kwargs:
            raise Exception('error')
        return True

    def read(self):
        if 'raise_exception' in self.kwargs:
            raise Exception('error')
        return True


class MockClsFactory(object):
    def __getitem__(self, key):
        return MockWriterAndReader

    def __contains__(self, key):
        return True


class MockSyncTaskModel(object):
    def __init__(self, id):
        self.id = id
        self.status = None
        self.details = None

    def finish_task(self, status, details=None):
        self.status = status
        self.details = details
