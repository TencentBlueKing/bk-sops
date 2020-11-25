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

OS_PATH_EXISTS = 'os.path.exists'
OS_MAKEDIRS = 'os.makedirs'
OS_WALK = 'os.walk'
SHUTIL_RMTREE = 'shutil.rmtree'
SHUTIL_MOVE = 'shutil.move'

GCLOUD_EXTERNAL_PLUGINS_PROTOCOL_READERS_BOTO3 = 'gcloud.external_plugins.protocol.readers.boto3'
GCLOUD_EXTERNAL_PLUGINS_PROTOCOL_READERS_REPO = 'gcloud.external_plugins.protocol.readers.Repo'
GCLOUD_EXTERNAL_PLUGINS_PROTOCOL_WRITERS_BOTO3 = 'gcloud.external_plugins.protocol.writers.boto3'
GCLOUD_EXTERNAL_PLUGINS_PROTOCOL_WRITERS_SHUTIL = 'gcloud.external_plugins.protocol.writers.shutil'

GCLOUD_EXTERNAL_PLUGINS_MODELS_CACHE_WRITER_CLS_FACTORY = \
    'gcloud.external_plugins.models.cache.writer_cls_factory'

GCLOUD_EXTERNAL_PLUGINS_MODELS_ORIGIN_READER_CLS_FACTORY = \
    'gcloud.external_plugins.models.origin.reader_cls_factory'

GCLOUD_EXTERNAL_PLUGINS_SYNC_TASK_DELAY = 'gcloud.external_plugins.signals.handlers.sync_task.delay'
GCLOUD_EXTERNAL_PLUGINS_MODELS_GIT_ORIGINAL_PACKAGE_SOURCE_ALL = \
    'gcloud.external_plugins.models.origin.GitRepoOriginalSource.objects.all'
GCLOUD_EXTERNAL_PLUGINS_MODELS_S3_ORIGINAL_PACKAGE_SOURCE_ALL = \
    'gcloud.external_plugins.models.origin.S3OriginalSource.objects.all'
GCLOUD_EXTERNAL_PLUGINS_MODELS_FS_ORIGINAL_PACKAGE_SOURCE_ALL = \
    'gcloud.external_plugins.models.origin.FileSystemOriginalSource.objects.all'
GCLOUD_EXTERNAL_PLUGINS_MODELS_CACHE_PACKAGE_SOURCE_ALL = \
    'gcloud.external_plugins.models.CachePackageSource.objects.all'
GCLOUD_EXTERNAL_PLUGINS_MODELS_SYNC_TASK_GET = \
    'gcloud.external_plugins.models.SyncTask.objects.get'
