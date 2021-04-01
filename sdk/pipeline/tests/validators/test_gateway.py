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

from pipeline.tests.validators.cases import *  # noqa


class TestStreamValidation(TestCase):
    def test_distance_from_start(self):
        tree, gateway_validation_assert, _ = flow_valid_case(self)
        distances = {}
        for gid, g in list(tree[PE.gateways].items()):
            distance_from(origin=tree[PE.start_event], node=g, tree=tree, marked=distances)

        for gid, ga in list(gateway_validation_assert.items()):
            actual = distances[gid]
            expect = ga["distance"]
            self.assertEqual(actual, expect, msg="{id} actual: {a}, expect: {e}".format(id=gid, a=actual, e=expect))

        for gid, ga in list(gateway_validation_assert.items()):
            actual = distance_from(origin=tree[PE.start_event], node=tree[PE.gateways][gid], tree=tree, marked={})
            expect = ga["distance"]
            self.assertEqual(actual, expect, msg="{id} actual: {a}, expect: {e}".format(id=gid, a=actual, e=expect))

    def test_match_converge(self):
        for n, i in enumerate(gateway_valid_cases, start=1):
            converge, gateway, stack, eid, start, distances, in_len = i["case"]()
            block_nodes = {start: set()}

            converge_id, _ = match_converge(
                converges=converge,
                gateways=gateway,
                cur_index=start,
                end_event_id=end_event_id,
                converged={},
                block_start=start,
                block_nodes=block_nodes,
                dist_from_start=distances,
                converge_in_len=in_len,
            )
            if converge_id:
                while converge[converge_id][PE.target][0] != eid:
                    start = converge[converge_id][PE.target][0]
                    block_nodes[start] = set()
                    converge_id, _ = match_converge(
                        converges=converge,
                        gateways=gateway,
                        cur_index=start,
                        end_event_id=end_event_id,
                        converged={},
                        block_start=start,
                        block_nodes=block_nodes,
                        dist_from_start=distances,
                        converge_in_len=in_len,
                    )
                    if converge_id is None:
                        break

            for _, c in list(converge.items()):
                actual = c["match"]
                expect = c["match_assert"]
                self.assertEqual(
                    actual, expect, msg="{id} actual: {a}, expect: {e}".format(id=c[PE.id], a=actual, e=expect)
                )

                actual = c["converge_end"]
                expect = c["converge_end_assert"]
                self.assertEqual(
                    actual, expect, msg="{id} actual: {a}, expect: {e}".format(id=c[PE.id], a=actual, e=expect)
                )

            for _, g in list(gateway.items()):
                actual = g["match"]
                expect = g["match_assert"]
                self.assertEqual(
                    actual, expect, msg="{id} actual: {a}, expect: {e}".format(id=g[PE.id], a=actual, e=expect)
                )

                actual = g["converge_end"]
                expect = g["converge_end_assert"]
                self.assertEqual(
                    actual, expect, msg="{id} actual: {a}, expect: {e}".format(id=g[PE.id], a=actual, e=expect)
                )

        for n, i in enumerate(gateway_invalid_cases, start=1):
            converge, gateway, stack, eid, start, distances, in_len = i["case"]()
            invalid = False
            block_nodes = {start: set()}
            try:
                converge_id, _ = match_converge(
                    converges=converge,
                    gateways=gateway,
                    cur_index=start,
                    end_event_id=end_event_id,
                    converged={},
                    block_start=start,
                    block_nodes=block_nodes,
                    dist_from_start=distances,
                    converge_in_len=in_len,
                )
                while converge[converge_id][PE.target][0] != eid:
                    start = converge[converge_id][PE.target][0]
                    block_nodes[start] = set()
                    converge_id, _ = match_converge(
                        converges=converge,
                        gateways=gateway,
                        cur_index=start,
                        end_event_id=end_event_id,
                        converged={},
                        block_start=start,
                        block_nodes=block_nodes,
                        dist_from_start=distances,
                        converge_in_len=in_len,
                    )
            except exceptions.ConvergeMatchError as e:
                invalid = True
                actual = e.gateway_id
                expect = i["invalid_assert"]
                self.assertEqual(
                    actual, expect, msg="invalid assert{id} actual: {a}, expect: {e}".format(id=n, a=actual, e=expect)
                )

            self.assertTrue(invalid, msg="invalid case %s expect raise exception" % n)

    def test_validate_gateway(self):
        tree, gateway_validation_assert, _ = flow_valid_case(self)
        converged = validate_gateways(tree)

        for cid, converge_items in list(converged.items()):
            actual = len(converge_items)
            expect = gateway_validation_assert[cid]["converged_len"]
            self.assertEqual(actual, expect, msg="{id} actual: {a}, expect: {e}".format(id=cid, a=actual, e=expect))

            actual = set(converge_items)
            expect = gateway_validation_assert[cid]["converged"]

            self.assertEqual(actual, expect, msg="{id} actual: {a}, expect: {e}".format(id=cid, a=actual, e=expect))

        for gid, gateway in list(tree[PE.gateways].items()):
            if gateway[PE.type] != PE.ConvergeGateway:
                actual = gateway[PE.converge_gateway_id]
                expect = gateway_validation_assert[gid]["match_assert"]
                self.assertEqual(actual, expect, msg="{id} actual: {a}, expect: {e}".format(id=gid, a=actual, e=expect))

        # edge cases
        for i, c in enumerate(flow_valid_edge_cases):
            tree = c["case"]()
            print(f"test gateway valid edge case {i+1}")
            converged = validate_gateways(tree)

    def test_validate_stream(self):

        tree, gateway_validation_assert, stream_assert = flow_valid_case(self)
        validate_gateways(tree)
        data = validate_stream(tree)

        for nid, expect in list(stream_assert.items()):
            actual = data[nid][STREAM]
            self.assertEqual(actual, expect, msg="{id} actual: {a}, expect: {e}".format(id=nid, a=actual, e=expect))

        for n, c in enumerate(flow_valid_edge_cases):
            tree = c["case"]()
            validate_gateways(tree)
            try:
                validate_stream(tree)
            except Exception as e:
                self.assertTrue(False, msg="valid edge case {} raise exception: {}".format(n, e))

        for n, item in enumerate(flow_invalid_cases, start=1):
            tree = item["case"]()
            invalid = False
            validate_gateways(tree)
            try:
                validate_stream(tree)
            except exceptions.StreamValidateError as e:
                actual = e.node_id
                expect = item["assert_invalid"]
                self.assertEqual(
                    actual, expect, msg="invalid assert{id} actual: {a}, expect: {e}".format(id=n, a=actual, e=expect)
                )
                invalid = True

            self.assertTrue(invalid, msg="invalid case %s expect raise exception" % n)
