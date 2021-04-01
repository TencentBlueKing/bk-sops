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

from django.test import TestCase
from mock import MagicMock, patch

from pipeline.core import flow
from pipeline.core.flow import EndEvent, FlowNodeClsFactory


class FlowNodeClsFactoryTestCase(TestCase):
    @patch("pipeline.core.flow.post_new_end_event_register", MagicMock())
    def test_register_node__is_not_end_event(self):
        node_cls = MagicMock()

        FlowNodeClsFactory.register_node("key", node_cls)

        self.assertEqual(FlowNodeClsFactory.get_node_cls("key"), node_cls)
        flow.post_new_end_event_register.send.assert_not_called()

        FlowNodeClsFactory.nodes_cls.pop("key")

    @patch("pipeline.core.flow.post_new_end_event_register", MagicMock())
    def test_register_node__with_end_event(self):
        class TestEnd(EndEvent):
            pass

        FlowNodeClsFactory.register_node("key", TestEnd)
        self.assertEqual(FlowNodeClsFactory.get_node_cls("key"), TestEnd)
        flow.post_new_end_event_register.send.assert_called_once_with(
            sender=EndEvent, node_type="key", node_cls=TestEnd
        )

        FlowNodeClsFactory.nodes_cls.pop("key")

    def test_register_node__with_exist_type(self):
        self.assertRaises(KeyError, FlowNodeClsFactory.register_node, "ServiceActivity", MagicMock())
