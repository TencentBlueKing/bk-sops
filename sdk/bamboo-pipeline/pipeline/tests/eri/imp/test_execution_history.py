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

from django.utils import timezone
from django.test import TransactionTestCase

from bamboo_engine.eri import ExecutionHistory, ExecutionShortHistory

from pipeline.eri.imp.execution_history import ExecutionHistoryMixin
from pipeline.eri.models import ExecutionHistory as DBExecutionHistory
from bamboo_engine.utils.string import unique_id


class Obj:
    def __init__(self, attr1, attr2):
        self.attr1 = attr1
        self.attr2 = attr2

    def __eq__(self, other):
        return self.attr1 == other.attr1 and self.attr2 == other.attr2


class ExecutionHistoryMixinTestCase(TransactionTestCase):
    def setUp(self):
        self.mixin = ExecutionHistoryMixin()
        self.node_id = unique_id("n")
        self.version = unique_id("v")
        self.started_time = timezone.now()
        self.archived_time = timezone.now()
        self.json_data = {"a": 1, "b": 2}
        self.pickle_data = {"c": 3, "d": Obj(4, Obj(5, 6))}

    def test_add_history(self):
        self.mixin.add_history(
            node_id=self.node_id,
            started_time=self.started_time,
            archived_time=self.archived_time,
            loop=1,
            skip=True,
            retry=3,
            version=self.version,
            inputs=self.json_data,
            outputs=self.pickle_data,
        )
        self.mixin.add_history(
            node_id=self.node_id,
            started_time=self.started_time,
            archived_time=self.archived_time,
            loop=2,
            skip=False,
            retry=0,
            version=self.version,
            inputs=self.json_data,
            outputs=self.json_data,
        )
        qs = DBExecutionHistory.objects.filter(node_id=self.node_id)

        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0].node_id, self.node_id)
        self.assertEqual(qs[0].started_time, self.started_time)
        self.assertEqual(qs[0].archived_time, self.archived_time)
        self.assertEqual(qs[0].loop, 1)
        self.assertTrue(qs[0].skip)
        self.assertEqual(qs[0].retry, 3)
        self.assertEqual(qs[0].version, self.version)
        self.assertEqual(qs[0].inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(qs[0].inputs, qs[0].inputs_serializer), self.json_data)
        self.assertEqual(qs[0].outputs_serializer, self.mixin.PICKLE_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(qs[0].outputs, qs[0].outputs_serializer), self.pickle_data)

        self.assertEqual(qs[1].node_id, self.node_id)
        self.assertEqual(qs[1].started_time, self.started_time)
        self.assertEqual(qs[1].archived_time, self.archived_time)
        self.assertEqual(qs[1].loop, 2)
        self.assertFalse(qs[1].skip)
        self.assertEqual(qs[1].retry, 0)
        self.assertEqual(qs[1].version, self.version)
        self.assertEqual(qs[1].inputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(qs[1].inputs, qs[1].inputs_serializer), self.json_data)
        self.assertEqual(qs[1].outputs_serializer, self.mixin.JSON_SERIALIZER)
        self.assertEqual(self.mixin._deserialize(qs[1].outputs, qs[1].outputs_serializer), self.json_data)

    def test_get_histories(self):
        self.mixin.add_history(
            node_id=self.node_id,
            started_time=self.started_time,
            archived_time=self.archived_time,
            loop=1,
            skip=True,
            retry=3,
            version=self.version,
            inputs=self.json_data,
            outputs=self.pickle_data,
        )
        self.mixin.add_history(
            node_id=self.node_id,
            started_time=self.started_time,
            archived_time=self.archived_time,
            loop=2,
            skip=False,
            retry=0,
            version=self.version,
            inputs=self.json_data,
            outputs=self.json_data,
        )

        histories = self.mixin.get_histories(node_id=self.node_id)
        self.assertEqual(len(histories), 2)
        self.assertTrue(isinstance(histories[0], ExecutionHistory))
        self.assertEqual(histories[0].node_id, self.node_id)
        self.assertEqual(histories[0].started_time, self.started_time)
        self.assertEqual(histories[0].archived_time, self.archived_time)
        self.assertEqual(histories[0].loop, 1)
        self.assertTrue(histories[0].skip)
        self.assertEqual(histories[0].retry, 3)
        self.assertEqual(histories[0].version, self.version)
        self.assertEqual(histories[0].inputs, self.json_data)
        self.assertEqual(histories[0].outputs, self.pickle_data)

        self.assertTrue(isinstance(histories[1], ExecutionHistory))
        self.assertEqual(histories[1].node_id, self.node_id)
        self.assertEqual(histories[1].started_time, self.started_time)
        self.assertEqual(histories[1].archived_time, self.archived_time)
        self.assertEqual(histories[1].loop, 2)
        self.assertFalse(histories[1].skip)
        self.assertEqual(histories[1].retry, 0)
        self.assertEqual(histories[1].version, self.version)
        self.assertEqual(histories[1].inputs, self.json_data)
        self.assertEqual(histories[1].outputs, self.json_data)

    def test_get_histories__with_loop(self):
        self.mixin.add_history(
            node_id=self.node_id,
            started_time=self.started_time,
            archived_time=self.archived_time,
            loop=1,
            skip=True,
            retry=3,
            version=self.version,
            inputs=self.json_data,
            outputs=self.pickle_data,
        )
        self.mixin.add_history(
            node_id=self.node_id,
            started_time=self.started_time,
            archived_time=self.archived_time,
            loop=2,
            skip=False,
            retry=0,
            version=self.version,
            inputs=self.json_data,
            outputs=self.json_data,
        )

        histories = self.mixin.get_histories(node_id=self.node_id, loop=1)
        self.assertEqual(len(histories), 1)
        self.assertTrue(isinstance(histories[0], ExecutionHistory))
        self.assertEqual(histories[0].node_id, self.node_id)
        self.assertEqual(histories[0].started_time, self.started_time)
        self.assertEqual(histories[0].archived_time, self.archived_time)
        self.assertEqual(histories[0].loop, 1)
        self.assertTrue(histories[0].skip)
        self.assertEqual(histories[0].retry, 3)
        self.assertEqual(histories[0].version, self.version)
        self.assertEqual(histories[0].inputs, self.json_data)
        self.assertEqual(histories[0].outputs, self.pickle_data)

    def test_get_short_histories(self):
        self.mixin.add_history(
            node_id=self.node_id,
            started_time=self.started_time,
            archived_time=self.archived_time,
            loop=1,
            skip=True,
            retry=3,
            version=self.version,
            inputs=self.json_data,
            outputs=self.pickle_data,
        )
        self.mixin.add_history(
            node_id=self.node_id,
            started_time=self.started_time,
            archived_time=self.archived_time,
            loop=2,
            skip=False,
            retry=0,
            version=self.version,
            inputs=self.json_data,
            outputs=self.json_data,
        )

        histories = self.mixin.get_short_histories(node_id=self.node_id)
        self.assertEqual(len(histories), 2)
        self.assertTrue(isinstance(histories[0], ExecutionShortHistory))
        self.assertEqual(histories[0].node_id, self.node_id)
        self.assertEqual(histories[0].started_time, self.started_time)
        self.assertEqual(histories[0].archived_time, self.archived_time)
        self.assertEqual(histories[0].loop, 1)
        self.assertTrue(histories[0].skip)
        self.assertEqual(histories[0].retry, 3)
        self.assertEqual(histories[0].version, self.version)

        self.assertTrue(isinstance(histories[1], ExecutionShortHistory))
        self.assertEqual(histories[1].node_id, self.node_id)
        self.assertEqual(histories[1].started_time, self.started_time)
        self.assertEqual(histories[1].archived_time, self.archived_time)
        self.assertEqual(histories[1].loop, 2)
        self.assertFalse(histories[1].skip)
        self.assertEqual(histories[1].retry, 0)
        self.assertEqual(histories[1].version, self.version)

    def test_get_short_histories__with_loop(self):
        self.mixin.add_history(
            node_id=self.node_id,
            started_time=self.started_time,
            archived_time=self.archived_time,
            loop=1,
            skip=True,
            retry=3,
            version=self.version,
            inputs=self.json_data,
            outputs=self.pickle_data,
        )
        self.mixin.add_history(
            node_id=self.node_id,
            started_time=self.started_time,
            archived_time=self.archived_time,
            loop=2,
            skip=False,
            retry=0,
            version=self.version,
            inputs=self.json_data,
            outputs=self.json_data,
        )

        histories = self.mixin.get_short_histories(node_id=self.node_id, loop=1)
        self.assertEqual(len(histories), 1)
        self.assertTrue(isinstance(histories[0], ExecutionShortHistory))
        self.assertEqual(histories[0].node_id, self.node_id)
        self.assertEqual(histories[0].started_time, self.started_time)
        self.assertEqual(histories[0].archived_time, self.archived_time)
        self.assertEqual(histories[0].loop, 1)
        self.assertTrue(histories[0].skip)
        self.assertEqual(histories[0].retry, 3)
        self.assertEqual(histories[0].version, self.version)
