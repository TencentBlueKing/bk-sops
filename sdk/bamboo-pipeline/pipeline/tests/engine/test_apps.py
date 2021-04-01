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

import mock
from django.test import TestCase

from pipeline.engine.apps import EngineConfig


class EngineConfigTestCase(TestCase):
    @mock.patch("pipeline.django_signal_valve.valve.set_valve_function", mock.MagicMock())
    @mock.patch("pipeline.engine.models.FunctionSwitch.objects.init_db", mock.MagicMock())
    @mock.patch("pipeline.engine.signals.dispatch.dispatch", mock.MagicMock())
    def test_ready(self):
        from pipeline.engine.signals import dispatch  # noqa
        from pipeline.django_signal_valve import valve  # noqa
        from pipeline.engine.models import FunctionSwitch  # noqa

        EngineConfig.path = "test"

        config = EngineConfig("", "")

        config.ready()

        dispatch.dispatch.assert_called()

        valve.set_valve_function.assert_called_with(FunctionSwitch.objects.is_frozen)

        FunctionSwitch.objects.init_db.assert_called()
