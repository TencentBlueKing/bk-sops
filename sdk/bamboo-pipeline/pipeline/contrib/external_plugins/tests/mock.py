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


from mock import MagicMock, call, patch  # noqa


def mock_s3_resource(resource, **kwargs):
    ret = {"resource": resource}
    ret.update(kwargs)
    return ret


class Object(object):
    pass


class MockResponse(object):
    def __init__(self, **kwargs):
        self.content = kwargs.get("content")
        self.ok = kwargs.get("ok", True)


class MockPackageSourceManager(object):
    def __init__(self, **kwargs):
        self.all = MagicMock(return_value=kwargs.get("all"))


class MockPackageSourceClass(object):
    def __init__(self, **kwargs):
        self.objects = MockPackageSourceManager(all=kwargs.get("all"))


class MockPackageSource(object):
    def __init__(self, **kwargs):
        self.type = MagicMock(return_value=kwargs.get("type"))
        self.importer = MagicMock(return_value=kwargs.get("importer"))
        self.modules = kwargs.get("modules", [])
