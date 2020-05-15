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

from __future__ import unicode_literals

FINDER_CODECS_OPEN = 'auth_backend.resources.migrations.finder.codecs.open'
FINDER_JSON_LOAD = 'auth_backend.resources.migrations.finder.json.load'
FINDER_JSON_DUMP = 'auth_backend.resources.migrations.finder.json.dump'
FINDER_OS_PATH_IS_DIR = 'auth_backend.resources.migrations.finder.os.path.isdir'
FINDER_OS_PATH_IS_FILE = 'auth_backend.resources.migrations.finder.os.path.isfile'
FINDER_OS_MK_DIR = 'auth_backend.resources.migrations.finder.os.mkdir'
FINDER_RENDER_TO_STRING = 'auth_backend.resources.migrations.finder.render_to_string'
FINDER_OPEN = 'auth_backend.resources.migrations.finder.open'

LOADER_APP_LABEL = 'auth_backend.resources.migrations.loader.APP_LABEL'

MIGRATION_MIGRATION_CLASS = 'auth_backend.resources.migrations.migration.settings.AUTH_BACKEND_RESOURCE_MIGRATION_CLASS'
MIGRATION_IMPORT_STRING = 'auth_backend.resources.migrations.migration.import_string'
MIGRATION_DIFFER_SETTINGS = 'auth_backend.resources.migrations.differ.settings'

SNAPPER_RESOURCE_TYPE_LIB = 'auth_backend.resources.migrations.snapper.resource_type_lib'

RESOURCE_BASE_CONF_SYSTEM_ID = 'auth_backend.resources.base.conf.SYSTEM_ID'
RESOURCE_BASE_CONF_SYSTEM_NAME = 'auth_backend.resources.base.conf.SYSTEM_NAME'
RESOURCE_DJANGO_POST_SAVE = 'auth_backend.resources.django.post_save'
RESOURCE_DJANGO_POST_DELETE = 'auth_backend.resources.django.post_delete'

RESOURCE_CLEAN_INSTANCE = 'auth_backend.resources.base.Resource.clean_instances'
RESOURCE_REAL_SCOPE_ID = 'auth_backend.resources.base.Resource.real_scope_id'
RESOURCE_REGISTER_INSTANCE = 'auth_backend.resources.base.Resource.register_instance'
RESOURCE_DELETE_INSTANCE = 'auth_backend.resources.base.Resource.delete_instance'
RESOURCE_UPDATE_INSTANCE = 'auth_backend.resources.base.Resource.update_instance'

DJANGO_MODEL_RESOURCE_DISPATCH_HANDLERS = 'auth_backend.resources.django.DjangoModelResource._dispatch_handlers'

BACKEND_BKIAM_RESOURCE_ID_FOR = 'auth_backend.backends.bkiam.resource_id_for'
BACKEND_BKIAM_SIGNALS = 'auth_backend.backends.bkiam.signals'
BACKEND_UTILS_RESOURCE_ID_FOR = 'auth_backend.backends.utils.resource_id_for'

SHORTCUTS_VERIFY_OR_RETURN_PERMS = 'auth_backend.plugins.shortcuts.verify_or_return_insufficient_perms'
SHORTCUTS_GET_BACKEND_FROM_CONFIG = 'auth_backend.plugins.shortcuts.get_backend_from_config'
SHORTCUTS_BUILD_NEED_PERMISSION = 'auth_backend.plugins.shortcuts.build_need_permission'
SHORTCUTS_RESOURCE_TYPE_LIB = 'auth_backend.plugins.shortcuts.resource_type_lib'

CONF_SCOPE_TYPE_NAMES = 'auth_backend.conf.SCOPE_TYPE_NAMES'

DUMMY_BACKEND_UTILS_RESOURCE_ID_FOR = 'auth_backend.backends.dummy.utils.resource_id_for'
DUMMY_BACKEND_UTILS_RESOURCE_ACTIONS_FOR = 'auth_backend.backends.dummy.utils.resource_actions_for'
DUMMY_BACKEND_GET_USER_MODEL = 'auth_backend.backends.dummy.get_user_model'
