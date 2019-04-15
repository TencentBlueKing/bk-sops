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

SYS_MODULES = 'sys.modules'
SYS_META_PATH = 'sys.meta_path'
IMP_ACQUIRE_LOCK = 'imp.acquire_lock'
IMP_RELEASE_LOCK = 'imp.release_lock'
REQUESTS_GET = 'requests.get'

IMPORTLIB_IMPORT_MODULE = 'importlib.import_module'

MODELS_BASE_SOURCE_CLS_FACTORY = 'pipeline.contrib.external_plugins.models.base.source_cls_factory'
MODELS_SOURCE_MANAGER_UPDATE_SOURCE_FROM_CONFIG = \
    'pipeline.contrib.external_plugins.models.base.SourceManager.update_source_from_config'

LOADER_SOURCE_CLS_FACTORY = 'pipeline.contrib.external_plugins.loader.source_cls_factory'
LOADER__IMPORT_MODULES_IN_SOURCE = 'pipeline.contrib.external_plugins.loader._import_modules_in_source'

UTILS_IMPORTER_BASE_EXECUTE_SRC_CODE = \
    'pipeline.contrib.external_plugins.utils.importer.base.NonstandardModuleImporter._execute_src_code'
UTILS_IMPORTER_GIT__FETCH_REPO_FILE = \
    'pipeline.contrib.external_plugins.utils.importer.git.GitRepoModuleImporter._fetch_repo_file'
UTILS_IMPORTER_GIT__FILE_URL = 'pipeline.contrib.external_plugins.utils.importer.git.GitRepoModuleImporter._file_url'
UTILS_IMPORTER_GIT_GET_SOURCE = 'pipeline.contrib.external_plugins.utils.importer.git.GitRepoModuleImporter.get_source'
UTILS_IMPORTER_GIT_GET_FILE = 'pipeline.contrib.external_plugins.utils.importer.git.GitRepoModuleImporter.get_file'
UTILS_IMPORTER_GIT_IS_PACKAGE = 'pipeline.contrib.external_plugins.utils.importer.git.GitRepoModuleImporter.is_package'
UTILS_IMPORTER__SETUP_IMPORTER = 'pipeline.contrib.external_plugins.utils.importer.utils._setup_importer'
UTILS_IMPORTER__REMOVE_IMPORTER = 'pipeline.contrib.external_plugins.utils.importer.utils._remove_importer'
