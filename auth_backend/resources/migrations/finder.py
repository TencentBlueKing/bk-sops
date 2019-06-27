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
import abc
import json
import codecs

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder


class ResourceSnapshotFinder(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, snapshot_name):
        self.snapshot_name = snapshot_name

    @property
    def snapshot_dir(self):
        return 'auth_backend/resource_snapshots'

    @property
    def basedir(self):
        return os.path.join(settings.BASE_DIR, self.snapshot_dir)

    @property
    def filename(self):
        return "%s.json" % self.snapshot_name

    @property
    def path(self):
        return os.path.join(self.basedir, self.filename)


class ResourceSnapshotWriter(ResourceSnapshotFinder):
    def __init__(self, snapshot_name, snapshot):
        super(ResourceSnapshotWriter, self).__init__(snapshot_name=snapshot_name)
        self.snapshot = snapshot

    def write(self):
        snapshots_dir = os.path.dirname(self.path)
        if not os.path.isdir(snapshots_dir):
            os.mkdir(snapshots_dir)

        with codecs.open(self.path, mode='w', encoding='utf-8') as fp:
            json.dump(self.snapshot, fp=fp, cls=DjangoJSONEncoder, ensure_ascii=False, indent=4)


class ResourceSnapshotReader(ResourceSnapshotFinder):

    def read(self):
        with codecs.open(self.path, mode='r', encoding='utf-8') as fp:
            snapshot = json.load(fp=fp)

        return snapshot
