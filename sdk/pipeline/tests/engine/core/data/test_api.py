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

import sys

from django.test import TestCase
from django.utils.module_loading import import_string

from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa


class EngineDataAPITestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_settings = MagicMock()
        cls.settings_patch = patch(ENGINE_DATA_API_SETTINGS, cls.mock_settings)
        cls.import_backend_patch = patch(ENGINE_DATA_API_IMPORT_BACKEND, MagicMock())
        cls.settings_patch.start()
        cls.import_backend_patch.start()

        cls.api = import_string("pipeline.engine.core.data.api")
        cls.write_methods = ["set_object", "del_object", "expire_cache"]
        cls.read_methods = ["get_object", "cache_for"]
        cls.method_params = {
            "set_object": ["key", "obj"],
            "del_object": ["key"],
            "expire_cache": ["key", "obj", "expires"],
            "cache_for": ["key"],
            "get_object": ["key"],
        }

    @classmethod
    def tearDownClass(cls):
        cls.settings_patch.stop()
        cls.import_backend_patch.stop()

    def setUp(self):
        self.backend = MagicMock()
        self.candidate_backend = MagicMock()
        self.mock_settings.PIPELINE_DATA_BACKEND_AUTO_EXPIRE = False

    def test_write__without_candidate(self):
        for method in self.write_methods:

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, None):
                    getattr(self.api, method)(*self.method_params[method])
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_not_called()

            sys.stdout.write("{} pass test_write__without_candidate test\n".format(method))

    def test_write__without_candiate_raise_err(self):
        for method in self.write_methods:

            setattr(self.backend, method, MagicMock(side_effect=Exception))

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, None):
                    self.assertRaises(Exception, getattr(self.api, method), *self.method_params[method])
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_not_called()

            sys.stdout.write("{} pass test_write__without_candiate_raise_err test\n".format(method))

    def test_write__with_candidate(self):
        for method in self.write_methods:

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                    getattr(self.api, method)(*self.method_params[method])
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_called_once_with(*self.method_params[method])

            sys.stdout.write("{} pass test_write__with_candidate test\n".format(method))

    def test_write__with_candidate_main_raise_err(self):
        for method in self.write_methods:

            setattr(self.backend, method, MagicMock(side_effect=Exception))

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                    getattr(self.api, method)(*self.method_params[method])
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_called_once_with(*self.method_params[method])

            sys.stdout.write("{} pass test_write__with_candidate_main_raise_err test\n".format(method))

    def test_write__with_candidate_raise_err(self):
        for method in self.write_methods:

            setattr(self.candidate_backend, method, MagicMock(side_effect=Exception))

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                    getattr(self.api, method)(*self.method_params[method])
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_called_once_with(*self.method_params[method])

            sys.stdout.write("{} pass test_write__with_candidate_raise_err test\n".format(method))

    def test_write__with_candidate_both_raise_err(self):
        for method in self.write_methods:

            setattr(self.backend, method, MagicMock(side_effect=Exception))
            setattr(self.candidate_backend, method, MagicMock(side_effect=Exception))

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                    self.assertRaises(Exception, getattr(self.api, method), *self.method_params[method])
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_called_once_with(*self.method_params[method])

            sys.stdout.write("{} pass test_write__with_candidate_both_raise_err test\n".format(method))

    def test_write__with_auto_expire(self):
        self.mock_settings.PIPELINE_DATA_BACKEND_AUTO_EXPIRE = True
        self.mock_settings.PIPELINE_DATA_BACKEND_AUTO_EXPIRE_SECONDS = 30

        for method in self.write_methods:

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                    getattr(self.api, method)(*self.method_params[method])
                    if method == "set_object":
                        getattr(self.backend, "expire_cache").assert_called_once_with(
                            *self.method_params[method], expires=30
                        )
                        self.backend.expire_cache.reset_mock()
                    else:
                        getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_called_once_with(*self.method_params[method])

            sys.stdout.write("{} pass test_write__with_candidate_both_raise_err test\n".format(method))

    def test_read__without_candidate(self):
        for method in self.read_methods:

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, None):
                    data = getattr(self.api, method)(*self.method_params[method])
                    self.assertIsNotNone(data)
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_not_called()

            sys.stdout.write("{} pass test_read__without_candidate test\n".format(method))

    def test_read__without_candidate_raise_err(self):
        for method in self.read_methods:

            setattr(self.backend, method, MagicMock(side_effect=Exception))

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, None):
                    self.assertRaises(Exception, getattr(self.api, method), *self.method_params[method])
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_not_called()

            sys.stdout.write("{} pass test_read__without_candidate_raise_err test\n".format(method))

    def test_read__with_candidate_not_use(self):
        for method in self.read_methods:

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                    data = getattr(self.api, method)(*self.method_params[method])
                    self.assertIsNotNone(data)
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_not_called()

            sys.stdout.write("{} pass test_read__with_candidate_not_use test\n".format(method))

    def test_read__with_candidate_use(self):
        for method in self.read_methods:

            setattr(self.backend, method, MagicMock(return_value=None))

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                    data = getattr(self.api, method)(*self.method_params[method])
                    self.assertIsNotNone(data)
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_called_once_with(*self.method_params[method])

            sys.stdout.write("{} pass test_read__with_candidate_use test\n".format(method))

    def test_read__with_candidate_err(self):
        for method in self.read_methods:

            setattr(self.backend, method, MagicMock(return_value=None))
            setattr(self.candidate_backend, method, MagicMock(side_effect=Exception))

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                    data = getattr(self.api, method)(*self.method_params[method])
                    self.assertIsNone(data)
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_called_once_with(*self.method_params[method])

            sys.stdout.write("{} pass test_read__with_candidate_err test\n".format(method))

    def test_read__with_candidate_main_raise_err(self):
        for method in self.read_methods:

            setattr(self.backend, method, MagicMock(side_effect=Exception))

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                    data = getattr(self.api, method)(*self.method_params[method])
                    self.assertIsNotNone(data)
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_called_once_with(*self.method_params[method])

            sys.stdout.write("{} pass test_read__with_candidate_main_raise_err test\n".format(method))

    def test_read__with_candidate_both_raise_err(self):
        for method in self.read_methods:

            setattr(self.backend, method, MagicMock(side_effect=Exception))
            setattr(self.candidate_backend, method, MagicMock(side_effect=Exception))

            with patch(ENGINE_DATA_API_BACKEND, self.backend):
                with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                    self.assertRaises(Exception, getattr(self.api, method), *self.method_params[method])
                    getattr(self.backend, method).assert_called_once_with(*self.method_params[method])
                    getattr(self.candidate_backend, method).assert_called_once_with(*self.method_params[method])

            sys.stdout.write("{} pass test_read__with_candidate_both_raise_err test\n".format(method))

    def test_set_schedule_data(self):
        with patch(ENGINE_DATA_API_BACKEND, self.backend):
            with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                self.api.set_schedule_data("key", "data")
                self.backend.set_object.assert_called_once_with("key_schedule_parent_data", "data")
                self.candidate_backend.set_object.assert_called_once_with("key_schedule_parent_data", "data")

    def test_delete_parent_data(self):
        with patch(ENGINE_DATA_API_BACKEND, self.backend):
            with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                self.api.delete_parent_data("key")
                self.backend.del_object.assert_called_once_with("key_schedule_parent_data")
                self.candidate_backend.del_object.assert_called_once_with("key_schedule_parent_data")

    def test_get_schedule_parent_data(self):
        with patch(ENGINE_DATA_API_BACKEND, self.backend):
            with patch(ENGINE_DATA_API_CANDIDATE_BACKEND, self.candidate_backend):
                data = self.api.get_schedule_parent_data("key")
                self.assertIsNotNone(data)
                self.backend.get_object.assert_called_once_with("key_schedule_parent_data")
                self.candidate_backend.get_object.assert_not_called()
