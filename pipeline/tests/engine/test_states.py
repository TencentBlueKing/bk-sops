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

import itertools

from django.test import TestCase

from pipeline.engine import states
from pipeline.engine.states import *  # noqa


class StatesTestCase(TestCase):
    def test_constants(self):
        self.assertEqual(CREATED, "CREATED")
        self.assertEqual(READY, "READY")
        self.assertEqual(RUNNING, "RUNNING")
        self.assertEqual(SUSPENDED, "SUSPENDED")
        self.assertEqual(BLOCKED, "BLOCKED")
        self.assertEqual(FINISHED, "FINISHED")
        self.assertEqual(FAILED, "FAILED")
        self.assertEqual(REVOKED, "REVOKED")
        self.assertEqual(EXPIRED, "EXPIRED")

        self.assertEqual(ALL_STATES, frozenset([READY, RUNNING, SUSPENDED, BLOCKED, FINISHED, FAILED, REVOKED]))
        self.assertEqual(SLEEP_STATES, frozenset([SUSPENDED, REVOKED]))
        self.assertEqual(CHILDREN_IGNORE_STATES, frozenset([BLOCKED]))
        self.assertEqual(
            states._NODE_TRANSITION,
            ConstantDict(
                {
                    READY: frozenset([RUNNING, SUSPENDED]),
                    RUNNING: frozenset([FINISHED, FAILED]),
                    SUSPENDED: frozenset([READY, REVOKED]),
                    BLOCKED: frozenset([]),
                    FINISHED: frozenset([RUNNING, FAILED]),
                    FAILED: frozenset([]),
                    REVOKED: frozenset([]),
                }
            ),
        )
        self.assertEqual(
            states._PIPELINE_TRANSITION,
            ConstantDict(
                {
                    READY: frozenset([RUNNING, SUSPENDED, BLOCKED]),
                    RUNNING: frozenset([SUSPENDED, BLOCKED, FINISHED, FAILED]),
                    SUSPENDED: frozenset([READY, REVOKED, BLOCKED]),
                    BLOCKED: frozenset([READY, REVOKED]),
                    FINISHED: frozenset([RUNNING]),
                    FAILED: frozenset([]),
                    REVOKED: frozenset([]),
                }
            ),
        )
        self.assertEqual(
            states._APPOINT_PIPELINE_TRANSITION,
            ConstantDict(
                {
                    READY: frozenset([SUSPENDED, REVOKED]),
                    RUNNING: frozenset([SUSPENDED, REVOKED]),
                    SUSPENDED: frozenset([READY, REVOKED, RUNNING]),
                    BLOCKED: frozenset([REVOKED]),
                    FINISHED: frozenset([]),
                    FAILED: frozenset([REVOKED]),
                    REVOKED: frozenset([]),
                }
            ),
        )
        self.assertEqual(
            states._APPOINT_NODE_TRANSITION,
            ConstantDict(
                {
                    READY: frozenset([SUSPENDED]),
                    RUNNING: frozenset([]),
                    SUSPENDED: frozenset([READY]),
                    BLOCKED: frozenset([]),
                    FINISHED: frozenset([]),
                    FAILED: frozenset([READY, FINISHED]),
                    REVOKED: frozenset([]),
                }
            ),
        )
        self.assertEqual(
            TRANSITION_MAP,
            {
                # first level: is_pipeline
                True: {
                    # second level: appoint
                    True: states._APPOINT_PIPELINE_TRANSITION,
                    False: states._PIPELINE_TRANSITION,
                },
                False: {True: states._APPOINT_NODE_TRANSITION, False: states._NODE_TRANSITION},
            },
        )

    def test_can_transit(self):

        for is_pipeline, appoint_case in list(TRANSITION_MAP.items()):
            for is_appoint, from_to_map in list(appoint_case.items()):
                for from_, to_set in list(from_to_map.items()):
                    valid_transit = to_set
                    invalid_transit = ALL_STATES.difference(to_set)

                    for valid_to in valid_transit:
                        self.assertTrue(
                            can_transit(
                                from_state=from_, to_state=valid_to, is_pipeline=is_pipeline, appoint=is_appoint
                            )
                        )

                    for invalid_to in invalid_transit:
                        self.assertFalse(
                            can_transit(
                                from_state=from_, to_state=invalid_to, is_pipeline=is_pipeline, appoint=is_appoint
                            )
                        )

    def test_is_rerunning(self):
        for (f, t) in itertools.product(ALL_STATES, ALL_STATES):
            if f == FINISHED and t == RUNNING:
                self.assertTrue(is_rerunning(f, t))
            else:
                self.assertFalse(is_rerunning(f, t))
