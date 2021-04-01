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

import imp
import sys

from django.test import TestCase

from pipeline.contrib.external_plugins.tests.mock import *  # noqa
from pipeline.contrib.external_plugins.tests.mock_settings import *  # noqa
from pipeline.contrib.external_plugins.utils.importer.base import NonstandardModuleImporter


class DummyImporter(NonstandardModuleImporter):
    def __init__(self, **kwargs):
        super(DummyImporter, self).__init__(modules=kwargs.get("modules", []))
        self._is_package = kwargs.get("is_package")
        self._get_code = kwargs.get("get_code")
        self._get_source = kwargs.get("get_source")
        self._get_file = kwargs.get("get_file")
        self._get_path = kwargs.get("get_path")

        self._accept_find_module_request_hook = MagicMock()
        self._pre_load_module_hook = MagicMock()
        self._post_load_module_hook = MagicMock()
        self._import_error_hook = MagicMock()

    def is_package(self, fullname):
        return self._is_package

    def get_code(self, fullname):
        return self._get_code

    def get_source(self, fullname):
        return self._get_source

    def get_file(self, fullname):
        return self._get_file

    def get_path(self, fullname):
        return self._get_path

    def accept_find_module_request_hook(self, fullname, path):
        self._accept_find_module_request_hook(fullname=fullname, path=path)

    def pre_load_module_hook(self, fullname, module):
        self._pre_load_module_hook(fullname=fullname, module=module)

    def post_load_module_hook(self, fullname, module):
        self._post_load_module_hook(fullname=fullname, module=module)

    def import_error_hook(self, fullname):
        self._import_error_hook(fullname=fullname)


class NonstandardModuleImporterTestCase(TestCase):
    def setUp(self):
        self.imp_acquire_lock_patcher = patch(IMP_ACQUIRE_LOCK, MagicMock())
        self.imp_release_lock_patcher = patch(IMP_RELEASE_LOCK, MagicMock())
        self.importer_exec_src_code_patcher = patch(UTILS_IMPORTER_BASE_EXECUTE_SRC_CODE, MagicMock())

        self.imp_acquire_lock_patcher.start()
        self.imp_release_lock_patcher.start()
        self.importer_exec_src_code_patcher.start()

    def tearDown(self):
        self.imp_acquire_lock_patcher.stop()
        self.imp_release_lock_patcher.stop()
        self.importer_exec_src_code_patcher.stop()

    def test_find_module__module_not_in_self_modules(self):
        importer = DummyImporter()

        self.assertIsNone(importer.find_module("django"))
        importer._accept_find_module_request_hook.assert_not_called()

        self.assertIsNone(importer.find_module("django.test"))
        importer._accept_find_module_request_hook.assert_not_called()

        self.assertIsNone(importer.find_module("django.test.utils"))
        importer._accept_find_module_request_hook.assert_not_called()

    def test_find_module__module_in_built_in(self):
        importer = DummyImporter()

        self.assertIsNone(importer.find_module("math"))
        importer._accept_find_module_request_hook.assert_not_called()

    def test_find_module__module_has_name_repetition(self):
        importer = DummyImporter(modules=["magic_module"])

        self.assertIsNone(importer.find_module("magic_module.magic_sub_module.magic_module"))
        importer._accept_find_module_request_hook.assert_not_called()

    def test_find_module__accept(self):
        importer = DummyImporter(modules=["magic_module"])

        fullname = "magic_module"
        self.assertIs(importer, importer.find_module(fullname))
        importer._accept_find_module_request_hook.assert_called_once_with(fullname=fullname, path=None)
        importer._accept_find_module_request_hook.reset_mock()

        fullname = "magic_module.magic_sub_module_1"
        self.assertIs(importer, importer.find_module(fullname))
        importer._accept_find_module_request_hook.assert_called_once_with(fullname=fullname, path=None)
        importer._accept_find_module_request_hook.reset_mock()

        fullname = "magic_module.magic_sub_module_1.magic_sub_module_2"
        self.assertIs(importer, importer.find_module(fullname))
        importer._accept_find_module_request_hook.assert_called_once_with(fullname=fullname, path=None)
        importer._accept_find_module_request_hook.reset_mock()

    def test_load_module__module_already_in_sys_modules(self):
        fullname = "exist_module"
        mod = Object()
        importer = DummyImporter()

        with patch(SYS_MODULES, {fullname: mod}):
            self.assertEqual(importer.load_module(fullname=fullname), mod)
            imp.acquire_lock.assert_called_once()
            imp.release_lock.assert_called_once()

    def test_load_module__get_source_raise_import_error(self):
        sub_module = "sub_module"
        fullname = "exist_module.sub_module"
        mod = Object()
        importer = DummyImporter()
        importer.get_source = MagicMock(side_effect=ImportError)

        with patch(SYS_MODULES, {sub_module: mod}):
            self.assertIsNone(importer.load_module(fullname=fullname))
            imp.acquire_lock.assert_called_once()
            imp.release_lock.assert_called_once()

    def test_load_module__is_package(self):
        src_code = "src_code"
        fullname = "magic_module"
        _file = "file"
        path = "path"
        importer = DummyImporter(is_package=True, get_source=src_code, get_file=_file, get_path=path)

        with patch(SYS_MODULES, {}):
            mod = importer.load_module(fullname=fullname)

            self.assertIs(sys.modules[fullname], mod)
            self.assertEqual(mod.__file__, _file)
            self.assertIs(mod.__loader__, importer)
            self.assertEqual(mod.__path__, path)
            self.assertEqual(mod.__package__, fullname)

            imp.acquire_lock.assert_called_once()
            importer._pre_load_module_hook.assert_called_once_with(fullname=fullname, module=mod)
            importer._execute_src_code.assert_called_once_with(src_code=src_code, module=mod)
            importer._post_load_module_hook.assert_called_once_with(fullname=fullname, module=mod)
            imp.release_lock.assert_called_once()

    def test_load_module__is_not_package(self):
        src_code = "src_code"
        fullname = "magic_module.sub_module"
        _file = "file"
        importer = DummyImporter(is_package=False, get_source=src_code, get_file=_file)

        with patch(SYS_MODULES, {}):
            mod = importer.load_module(fullname=fullname)

            self.assertIs(sys.modules[fullname], mod)
            self.assertEqual(mod.__file__, _file)
            self.assertIs(mod.__loader__, importer)
            self.assertEqual(mod.__package__, fullname.rpartition(".")[0])

            imp.acquire_lock.assert_called_once()
            importer._pre_load_module_hook.assert_called_once_with(fullname=fullname, module=mod)
            importer._execute_src_code.assert_called_once_with(src_code=src_code, module=mod)
            importer._post_load_module_hook.assert_called_once_with(fullname=fullname, module=mod)
            imp.release_lock.assert_called_once()

    def test_load_module__raise_exception_before_add_module(self):
        fullname = "magic_module.sub_module"
        importer = DummyImporter(is_package=False)
        importer.get_source = MagicMock(side_effect=Exception())
        importer._import_error_hook = MagicMock(side_effect=Exception())

        with patch(SYS_MODULES, {}):
            self.assertRaises(ImportError, importer.load_module, fullname)
            self.assertNotIn(fullname, sys.modules)

            importer._import_error_hook.assert_called_once()
            imp.release_lock.assert_called_once()

    def test_load_module__raise_exception_after_add_module(self):
        fullname = "magic_module.sub_module"
        importer = DummyImporter(is_package=False)
        importer.get_file = MagicMock(side_effect=Exception())

        with patch(SYS_MODULES, {}):
            self.assertRaises(ImportError, importer.load_module, fullname)
            self.assertNotIn(fullname, sys.modules)

            importer._import_error_hook.assert_called_once()
            imp.release_lock.assert_called_once()
