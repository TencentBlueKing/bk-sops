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

from mock import patch, MagicMock

from django.test import TransactionTestCase
from django.utils import timezone

from bamboo_engine.eri.models import State
from bamboo_engine.exceptions import StateVersionNotMatchError

from pipeline.eri.models import State as DBState
from pipeline.eri.imp.state import StateMixin, states
from bamboo_engine.utils.string import unique_id


class StateMixinTestCase(TransactionTestCase):
    def setUp(self):
        self.mixin = StateMixin()
        self.started_time = timezone.now()
        self.archived_time = timezone.now()
        self.state = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=unique_id("n"),
            parent_id=unique_id("n"),
            name=states.RUNNING,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )

    def test_get_state(self):
        state = self.mixin.get_state(self.state.node_id)
        self.assertTrue(isinstance(state, State))
        self.assertEqual(state.node_id, self.state.node_id)
        self.assertEqual(state.root_id, self.state.root_id)
        self.assertEqual(state.parent_id, self.state.parent_id)
        self.assertEqual(state.name, self.state.name)
        self.assertEqual(state.version, self.state.version)
        self.assertEqual(state.loop, self.state.loop)
        self.assertEqual(state.retry, self.state.retry)
        self.assertEqual(state.skip, self.state.skip)
        self.assertEqual(state.created_time, self.state.created_time)
        self.assertEqual(state.started_time, self.state.started_time)
        self.assertEqual(state.archived_time, self.state.archived_time)

    def test_get_state__not_exist(self):
        self.assertRaises(DBState.DoesNotExist, self.mixin.get_state, "not_exist")

    def test_get_state_or_none(self):
        state = self.mixin.get_state_or_none(self.state.node_id)
        self.assertTrue(isinstance(state, State))
        self.assertEqual(state.node_id, self.state.node_id)
        self.assertEqual(state.root_id, self.state.root_id)
        self.assertEqual(state.parent_id, self.state.parent_id)
        self.assertEqual(state.name, self.state.name)
        self.assertEqual(state.version, self.state.version)
        self.assertEqual(state.loop, self.state.loop)
        self.assertEqual(state.retry, self.state.retry)
        self.assertEqual(state.skip, self.state.skip)
        self.assertEqual(state.created_time, self.state.created_time)
        self.assertEqual(state.started_time, self.state.started_time)
        self.assertEqual(state.archived_time, self.state.archived_time)

    def test_get_state_or_none__not_exist(self):
        self.assertIsNone(self.mixin.get_state_or_none("not_exist"))

    def test_get_state_by_root(self):
        s1 = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=unique_id("n"),
            parent_id="",
            name=states.RUNNING,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )
        s2 = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=s1.root_id,
            parent_id="",
            name=states.RUNNING,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )
        s3 = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=s1.root_id,
            parent_id="",
            name=states.RUNNING,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )

        state_list = self.mixin.get_state_by_root(s1.root_id)
        self.assertEqual(len(state_list), 3)

        self.assertTrue(isinstance(state_list[0], State))
        self.assertEqual(state_list[0].node_id, s1.node_id)
        self.assertEqual(state_list[0].root_id, s1.root_id)
        self.assertEqual(state_list[0].parent_id, s1.parent_id)
        self.assertEqual(state_list[0].name, s1.name)
        self.assertEqual(state_list[0].version, s1.version)
        self.assertEqual(state_list[0].loop, s1.loop)
        self.assertEqual(state_list[0].retry, s1.retry)
        self.assertEqual(state_list[0].skip, s1.skip)
        self.assertEqual(state_list[0].created_time, s1.created_time)
        self.assertEqual(state_list[0].started_time, s1.started_time)
        self.assertEqual(state_list[0].archived_time, s1.archived_time)

        self.assertTrue(isinstance(state_list[1], State))
        self.assertEqual(state_list[1].node_id, s2.node_id)
        self.assertEqual(state_list[1].root_id, s2.root_id)
        self.assertEqual(state_list[1].parent_id, s2.parent_id)
        self.assertEqual(state_list[1].name, s2.name)
        self.assertEqual(state_list[1].version, s2.version)
        self.assertEqual(state_list[1].loop, s2.loop)
        self.assertEqual(state_list[1].retry, s2.retry)
        self.assertEqual(state_list[1].skip, s2.skip)
        self.assertEqual(state_list[1].created_time, s2.created_time)
        self.assertEqual(state_list[1].started_time, s2.started_time)
        self.assertEqual(state_list[1].archived_time, s2.archived_time)

        self.assertTrue(isinstance(state_list[2], State))
        self.assertEqual(state_list[2].node_id, s3.node_id)
        self.assertEqual(state_list[2].root_id, s3.root_id)
        self.assertEqual(state_list[2].parent_id, s3.parent_id)
        self.assertEqual(state_list[2].name, s3.name)
        self.assertEqual(state_list[2].version, s3.version)
        self.assertEqual(state_list[2].loop, s3.loop)
        self.assertEqual(state_list[2].retry, s3.retry)
        self.assertEqual(state_list[2].skip, s3.skip)
        self.assertEqual(state_list[2].created_time, s3.created_time)
        self.assertEqual(state_list[2].started_time, s3.started_time)
        self.assertEqual(state_list[2].archived_time, s3.archived_time)

    def test_get_state_by_root__not_exist(self):
        state_list = self.mixin.get_state_by_root("not_exist")
        self.assertEqual(state_list, [])

    def test_get_state_by_parent(self):
        s1 = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=unique_id("n"),
            parent_id=unique_id("n"),
            name=states.RUNNING,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )
        s2 = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=s1.root_id,
            parent_id=s1.parent_id,
            name=states.RUNNING,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )
        s3 = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=s1.root_id,
            parent_id=s1.parent_id,
            name=states.RUNNING,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )

        state_list = self.mixin.get_state_by_root(s1.root_id)
        self.assertEqual(len(state_list), 3)

        self.assertTrue(isinstance(state_list[0], State))
        self.assertEqual(state_list[0].node_id, s1.node_id)
        self.assertEqual(state_list[0].root_id, s1.root_id)
        self.assertEqual(state_list[0].parent_id, s1.parent_id)
        self.assertEqual(state_list[0].name, s1.name)
        self.assertEqual(state_list[0].version, s1.version)
        self.assertEqual(state_list[0].loop, s1.loop)
        self.assertEqual(state_list[0].retry, s1.retry)
        self.assertEqual(state_list[0].skip, s1.skip)
        self.assertEqual(state_list[0].created_time, s1.created_time)
        self.assertEqual(state_list[0].started_time, s1.started_time)
        self.assertEqual(state_list[0].archived_time, s1.archived_time)

        self.assertTrue(isinstance(state_list[1], State))
        self.assertEqual(state_list[1].node_id, s2.node_id)
        self.assertEqual(state_list[1].root_id, s2.root_id)
        self.assertEqual(state_list[1].parent_id, s2.parent_id)
        self.assertEqual(state_list[1].name, s2.name)
        self.assertEqual(state_list[1].version, s2.version)
        self.assertEqual(state_list[1].loop, s2.loop)
        self.assertEqual(state_list[1].retry, s2.retry)
        self.assertEqual(state_list[1].skip, s2.skip)
        self.assertEqual(state_list[1].created_time, s2.created_time)
        self.assertEqual(state_list[1].started_time, s2.started_time)
        self.assertEqual(state_list[1].archived_time, s2.archived_time)

        self.assertTrue(isinstance(state_list[2], State))
        self.assertEqual(state_list[2].node_id, s3.node_id)
        self.assertEqual(state_list[2].root_id, s3.root_id)
        self.assertEqual(state_list[2].parent_id, s3.parent_id)
        self.assertEqual(state_list[2].name, s3.name)
        self.assertEqual(state_list[2].version, s3.version)
        self.assertEqual(state_list[2].loop, s3.loop)
        self.assertEqual(state_list[2].retry, s3.retry)
        self.assertEqual(state_list[2].skip, s3.skip)
        self.assertEqual(state_list[2].created_time, s3.created_time)
        self.assertEqual(state_list[2].started_time, s3.started_time)
        self.assertEqual(state_list[2].archived_time, s3.archived_time)

    def test_get_state_by_parent__not_exist(self):
        state_list = self.mixin.get_state_by_parent("not_exist")
        self.assertEqual(state_list, [])

    def test_batch_get_state_name(self):
        s1 = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=unique_id("n"),
            parent_id=unique_id("n"),
            name=states.RUNNING,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )
        s2 = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=s1.root_id,
            parent_id=s1.parent_id,
            name=states.READY,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )
        s3 = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=s1.root_id,
            parent_id=s1.parent_id,
            name=states.FINISHED,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )
        s4 = DBState.objects.create(
            node_id=unique_id("n"),
            root_id=s1.root_id,
            parent_id=s1.parent_id,
            name=states.RUNNING,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )

        state_names = self.mixin.batch_get_state_name([s1.node_id, s2.node_id, s3.node_id, s4.node_id])
        self.assertEqual(
            state_names, {s1.node_id: s1.name, s2.node_id: s2.name, s3.node_id: s3.name, s4.node_id: s4.name}
        )

    def test_has_state(self):
        self.assertTrue(self.mixin.has_state(self.state.node_id))

    def test_has_state__not_exist(self):
        self.assertFalse(self.mixin.has_state("not_exist"))

    def test_set_state_root_and_parent(self):
        s = DBState.objects.create(
            node_id=unique_id("n"),
            name=states.RUNNING,
            version=unique_id("v"),
            started_time=self.started_time,
            archived_time=self.archived_time,
        )
        self.assertEqual(s.root_id, "")
        self.assertEqual(s.parent_id, "")

        self.mixin.set_state_root_and_parent(s.node_id, self.state.root_id, self.state.parent_id)
        s.refresh_from_db()
        self.assertEqual(s.root_id, self.state.root_id)
        self.assertEqual(s.parent_id, self.state.parent_id)

    def test_set_state__not_exist(self):
        node_id = unique_id("n")
        root_id = unique_id("n")
        parent_id = root_id
        to_state = states.RUNNING

        post_set_state = MagicMock()
        with patch("pipeline.eri.imp.state.post_set_state", post_set_state):
            version = self.mixin.set_state(
                node_id=node_id,
                to_state=to_state,
                loop=-1,
                root_id=root_id,
                parent_id=parent_id,
                is_retry=True,
                is_skip=True,
                reset_retry=True,
                reset_skip=True,
                error_ignored=True,
                reset_error_ignored=True,
                refresh_version=False,
                clear_started_time=True,
                set_started_time=True,
                clear_archived_time=True,
                set_archive_time=False,
            )

        state = DBState.objects.get(node_id=node_id)
        self.assertEqual(len(version), 33)
        self.assertEqual(state.node_id, node_id)
        self.assertEqual(state.root_id, root_id)
        self.assertEqual(state.parent_id, parent_id)
        self.assertEqual(state.name, to_state)
        self.assertEqual(len(state.version), 33)
        self.assertEqual(state.loop, 1)
        self.assertEqual(state.retry, 0)
        self.assertEqual(state.skip, False)
        self.assertEqual(state.error_ignored, False)
        self.assertIsNotNone(state.created_time)
        self.assertIsNotNone(state.started_time)
        self.assertIsNone(state.archived_time)
        post_set_state.send.assert_called_once_with(
            sender=DBState,
            node_id=node_id,
            to_state=to_state,
            version=state.version,
            root_id=state.root_id,
            parent_id=state.parent_id,
            loop=-1,
        )

    def test_set_state__exist(self):
        to_state = states.FINISHED

        post_set_state = MagicMock()
        with patch("pipeline.eri.imp.state.post_set_state", post_set_state):
            version = self.mixin.set_state(
                node_id=self.state.node_id,
                to_state=to_state,
                loop=2,
                is_retry=True,
                is_skip=True,
                reset_retry=False,
                reset_skip=False,
                error_ignored=True,
                reset_error_ignored=False,
                refresh_version=True,
                clear_started_time=True,
                set_started_time=True,
                clear_archived_time=True,
                set_archive_time=True,
            )

        state = DBState.objects.get(node_id=self.state.node_id)
        self.assertEqual(len(version), 33)
        self.assertNotEqual(version, self.state.version)
        self.assertEqual(version, state.version)
        self.assertEqual(state.node_id, self.state.node_id)
        self.assertEqual(state.root_id, self.state.root_id)
        self.assertEqual(state.parent_id, self.state.parent_id)
        self.assertEqual(state.name, to_state)
        self.assertEqual(len(state.version), 33)
        self.assertNotEqual(state.version, self.state.version)
        self.assertEqual(state.loop, 2)
        self.assertEqual(state.retry, 1)
        self.assertEqual(state.skip, True)
        self.assertEqual(state.error_ignored, True)
        self.assertIsNotNone(state.created_time)
        self.assertNotEqual(state.started_time, self.started_time)
        self.assertIsNotNone(state.archived_time)
        self.assertNotEqual(state.archived_time, self.archived_time)
        post_set_state.send.assert_called_once_with(
            sender=DBState,
            node_id=state.node_id,
            to_state=to_state,
            version=state.version,
            root_id=state.root_id,
            parent_id=state.parent_id,
            loop=state.loop,
        )

    def test_set_state__raise(self):
        post_set_state = MagicMock()
        with patch("pipeline.eri.imp.state.post_set_state", post_set_state):
            self.assertRaises(
                RuntimeError,
                self.mixin.set_state,
                node_id=self.state.node_id,
                to_state=states.READY,
                loop=2,
                is_retry=True,
                is_skip=True,
                reset_retry=True,
                reset_skip=True,
                reset_error_ignored=False,
                error_ignored=True,
                refresh_version=False,
                clear_started_time=True,
                set_started_time=True,
                clear_archived_time=True,
                set_archive_time=True,
            )
        post_set_state.send.assert_not_called()

    def test_set_state__raise_version_not_match(self):
        post_set_state = MagicMock()
        with patch("pipeline.eri.imp.state.post_set_state", post_set_state):
            self.assertRaises(
                StateVersionNotMatchError,
                self.mixin.set_state,
                node_id=self.state.node_id,
                version=unique_id("v"),
                to_state=states.SUSPENDED,
                loop=2,
                is_retry=True,
                is_skip=True,
                reset_retry=True,
                reset_skip=True,
                reset_error_ignored=False,
                error_ignored=True,
                refresh_version=False,
                clear_started_time=True,
                set_started_time=True,
                clear_archived_time=True,
                set_archive_time=True,
            )
        post_set_state.send.assert_not_called()
