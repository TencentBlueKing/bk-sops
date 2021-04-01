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

from bamboo_engine.builder import *  # noqa
from bamboo_engine.validator.gateway import *  # noqa

from .utils import *  # noqa


def flow_valid_case():
    def _(num):
        return num - 1

    def out_assert_case(length, out_set):
        return {"len": length, "outgoing": out_set}

    outgoing_assert = {
        start_event_id: out_assert_case(1, {act_id(1)}),
        act_id(1): out_assert_case(1, {parallel_gw_id(1)}),
        parallel_gw_id(1): out_assert_case(
            3, {parallel_gw_id(2), act_id(5), act_id(6)}
        ),
        parallel_gw_id(2): out_assert_case(3, {act_id(2), act_id(3), act_id(4)}),
        act_id(2): out_assert_case(1, {converge_gw_id(1)}),
        act_id(3): out_assert_case(1, {converge_gw_id(1)}),
        act_id(4): out_assert_case(1, {converge_gw_id(1)}),
        converge_gw_id(1): out_assert_case(1, {act_id(7)}),
        act_id(7): out_assert_case(1, {exclusive_gw_id(1)}),
        exclusive_gw_id(1): out_assert_case(2, {parallel_gw_id(2), converge_gw_id(3)}),
        act_id(5): out_assert_case(1, {exclusive_gw_id(7)}),
        exclusive_gw_id(7): out_assert_case(2, {act_id(8), converge_gw_id(3)}),
        act_id(8): out_assert_case(1, {exclusive_gw_id(8)}),
        exclusive_gw_id(8): out_assert_case(2, {act_id(8), act_id(11)}),
        act_id(11): out_assert_case(1, {converge_gw_id(3)}),
        act_id(6): out_assert_case(1, {exclusive_gw_id(2)}),
        exclusive_gw_id(2): out_assert_case(3, {act_id(6), act_id(9), act_id(10)}),
        act_id(9): out_assert_case(1, {converge_gw_id(2)}),
        act_id(10): out_assert_case(1, {converge_gw_id(2)}),
        converge_gw_id(2): out_assert_case(1, {act_id(12)}),
        act_id(12): out_assert_case(1, {exclusive_gw_id(6)}),
        exclusive_gw_id(6): out_assert_case(
            3, {act_id(6), converge_gw_id(3), converge_gw_id(2)}
        ),
        converge_gw_id(3): out_assert_case(1, {act_id(13)}),
        act_id(13): out_assert_case(1, {exclusive_gw_id(3)}),
        exclusive_gw_id(3): out_assert_case(
            4, {end_event_id, act_id(14), parallel_gw_id(3), act_id(1)}
        ),
        act_id(14): out_assert_case(1, {exclusive_gw_id(4)}),
        exclusive_gw_id(4): out_assert_case(2, {act_id(13), converge_gw_id(4)}),
        parallel_gw_id(3): out_assert_case(3, {act_id(15), act_id(16), act_id(17)}),
        act_id(15): out_assert_case(1, {act_id(18)}),
        act_id(18): out_assert_case(1, {converge_gw_id(4)}),
        act_id(16): out_assert_case(1, {converge_gw_id(4)}),
        act_id(17): out_assert_case(1, {exclusive_gw_id(5)}),
        exclusive_gw_id(5): out_assert_case(2, {act_id(19), act_id(20)}),
        act_id(19): out_assert_case(1, {converge_gw_id(4)}),
        act_id(20): out_assert_case(1, {converge_gw_id(4)}),
        converge_gw_id(4): out_assert_case(1, {end_event_id}),
        end_event_id: out_assert_case(0, set()),
    }

    stream_assert = {
        start_event_id: MAIN_STREAM,
        act_id(1): MAIN_STREAM,
        parallel_gw_id(1): MAIN_STREAM,
        parallel_gw_id(2): "pg_1_0",
        act_id(2): "pg_2_0",
        act_id(3): "pg_2_1",
        act_id(4): "pg_2_2",
        converge_gw_id(1): "pg_1_0",
        act_id(7): "pg_1_0",
        exclusive_gw_id(1): "pg_1_0",
        act_id(5): "pg_1_1",
        exclusive_gw_id(7): "pg_1_1",
        act_id(8): "pg_1_1",
        exclusive_gw_id(8): "pg_1_1",
        act_id(11): "pg_1_1",
        act_id(6): "pg_1_2",
        exclusive_gw_id(2): "pg_1_2",
        act_id(9): "pg_1_2",
        act_id(10): "pg_1_2",
        converge_gw_id(2): "pg_1_2",
        act_id(12): "pg_1_2",
        exclusive_gw_id(6): "pg_1_2",
        converge_gw_id(3): MAIN_STREAM,
        act_id(13): MAIN_STREAM,
        exclusive_gw_id(3): MAIN_STREAM,
        act_id(14): MAIN_STREAM,
        exclusive_gw_id(4): MAIN_STREAM,
        parallel_gw_id(3): MAIN_STREAM,
        act_id(15): "pg_3_0",
        act_id(18): "pg_3_0",
        act_id(16): "pg_3_1",
        act_id(17): "pg_3_2",
        exclusive_gw_id(5): "pg_3_2",
        act_id(19): "pg_3_2",
        act_id(20): "pg_3_2",
        converge_gw_id(4): MAIN_STREAM,
        end_event_id: MAIN_STREAM,
    }

    gateway_validation_assert = {
        converge_gw_id(1): {
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": None,
            "converged_len": 1,
            "converged": {parallel_gw_id(2)},
            "distance": 5,
        },
        converge_gw_id(2): {
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": None,
            "converged_len": 1,
            "converged": {exclusive_gw_id(2)},
            "distance": 6,
        },
        converge_gw_id(3): {
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": None,
            "converged_len": 5,
            "converged": {
                parallel_gw_id(1),
                exclusive_gw_id(1),
                exclusive_gw_id(7),
                exclusive_gw_id(8),
                exclusive_gw_id(6),
            },
            "distance": 9,
        },
        converge_gw_id(4): {
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": None,
            "converged_len": 4,
            "converged": {
                parallel_gw_id(3),
                exclusive_gw_id(3),
                exclusive_gw_id(4),
                exclusive_gw_id(5),
            },
            "distance": 16,
        },
        exclusive_gw_id(1): {
            "match": None,
            "match_assert": converge_gw_id(3),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 7,
        },
        exclusive_gw_id(2): {
            "match": None,
            "match_assert": converge_gw_id(2),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 4,
        },
        exclusive_gw_id(3): {
            "match": None,
            "match_assert": converge_gw_id(4),
            "converge_end": None,
            "converge_end_assert": True,
            "distance": 11,
        },
        exclusive_gw_id(4): {
            "match": None,
            "match_assert": converge_gw_id(4),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 13,
        },
        exclusive_gw_id(5): {
            "match": None,
            "match_assert": converge_gw_id(4),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 14,
        },
        exclusive_gw_id(6): {
            "match": None,
            "match_assert": converge_gw_id(3),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 8,
        },
        exclusive_gw_id(7): {
            "match": None,
            "match_assert": converge_gw_id(3),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 4,
        },
        exclusive_gw_id(8): {
            "match": None,
            "match_assert": converge_gw_id(3),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 6,
        },
        parallel_gw_id(1): {
            "match": None,
            "match_assert": converge_gw_id(3),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 2,
        },
        parallel_gw_id(2): {
            "match": None,
            "match_assert": converge_gw_id(1),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 3,
        },
        parallel_gw_id(3): {
            "match": None,
            "match_assert": converge_gw_id(4),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 12,
        },
    }

    start = EmptyStartEvent(id=start_event_id)
    acts = [ServiceActivity(id=act_id(i)) for i in range(1, 21)]
    pgs = [ParallelGateway(id=parallel_gw_id(i)) for i in range(1, 3)]
    pgs.append(
        ConditionalParallelGateway(
            id=parallel_gw_id(3), conditions={0: "123", 1: "456", 2: "789"}
        )
    )
    egs = [
        ExclusiveGateway(
            id=exclusive_gw_id(i),
            conditions={0: "123", 1: "456", 2: "789", 3: "101112"},
        )
        for i in range(1, 9)
    ]
    cgs = [ConvergeGateway(id=converge_gw_id(i)) for i in range(1, 5)]
    end = EmptyEndEvent(id=end_event_id)

    nodes = [start, end]
    nodes.extend(acts)
    nodes.extend(pgs)
    nodes.extend(egs)
    nodes.extend(cgs)

    start.extend(acts[_(1)]).extend(pgs[_(1)]).connect(
        pgs[_(2)], acts[_(5)], acts[_(6)]
    )

    pgs[_(2)].connect(acts[_(2)], acts[_(3)], acts[_(4)]).converge(cgs[_(1)]).extend(
        acts[_(7)]
    ).extend(egs[_(1)]).connect(pgs[_(2)], cgs[_(3)])
    acts[_(5)].extend(egs[_(7)]).connect(cgs[_(3)], acts[_(8)]).to(acts[_(8)]).extend(
        egs[_(8)]
    ).connect(acts[_(8)], acts[_(11)]).to(acts[_(11)]).extend(cgs[_(3)])
    acts[_(6)].extend(egs[_(2)]).connect(acts[_(9)], acts[_(10)],).converge(
        cgs[_(2)]
    ).extend(acts[_(12)]).extend(egs[_(6)]).connect(
        acts[_(6)], cgs[_(3)], cgs[_(2)]
    ).to(
        egs[_(2)]
    ).connect(
        acts[_(6)]
    )

    cgs[_(3)].extend(acts[_(13)]).extend(egs[_(3)]).connect(
        end, acts[_(14)], pgs[_(3)], acts[_(1)]
    )

    acts[_(14)].extend(egs[_(4)]).connect(acts[_(13)], cgs[_(4)])
    pgs[_(3)].connect(acts[_(15)], acts[_(16)], acts[_(17)]).to(acts[_(15)]).extend(
        acts[_(18)]
    ).extend(cgs[_(4)]).to(acts[_(17)]).extend(egs[_(5)]).connect(
        acts[_(19)], acts[_(20)]
    ).to(
        acts[_(19)]
    ).extend(
        cgs[_(4)]
    ).to(
        acts[_(20)]
    ).extend(
        cgs[_(4)]
    ).to(
        acts[_(16)]
    ).extend(
        cgs[_(4)]
    ).extend(
        end
    )

    for node in nodes:
        a = outgoing_assert[node.id]
        out = {out.id for out in node.outgoing}
        assert a["len"] == len(node.outgoing), "{id} actual: {a}, expect: {e}".format(
            id=node.id, a=len(node.outgoing), e=a["len"]
        )
        assert a["outgoing"] == out, "{id} actual: {a}, expect: {e}".format(
            id=node.id, a=out, e=a["outgoing"]
        )

    return build_tree(start), gateway_validation_assert, stream_assert


def flow_valid_edge_case_1():
    start = EmptyStartEvent(id=start_event_id)
    act_1 = ServiceActivity(id=act_id(1))
    act_2 = ServiceActivity(id=act_id(2))
    eg = ExclusiveGateway(
        id=exclusive_gw_id(1), conditions={0: "123", 1: "456", 2: "789"}
    )
    act_3 = ServiceActivity(id=act_id(3))
    end = EmptyEndEvent(id=end_event_id)

    start.extend(act_1).extend(act_2).extend(eg).connect(act_1, act_2, act_3).to(
        act_3
    ).extend(end)

    return build_tree(start)


def flow_valid_edge_case_2():
    return {
        "activities": {
            "act_1": {
                "component": {"inputs": {}, "code": None},
                "outgoing": "82b12b6aae533e55bdcc5bccfb014c2d",
                "incoming": ["3fc89273786a36b8a6e7beac8301274d"],
                "name": None,
                "error_ignorable": False,
                "type": "ServiceActivity",
                "id": "act_1",
                "optional": False,
            },
            "act_2": {
                "component": {"inputs": {}, "code": None},
                "outgoing": "3368add44347310eaef1f26f25909026",
                "incoming": ["76caeed0e6053fea9db84a89f56a74a8"],
                "name": None,
                "error_ignorable": False,
                "type": "ServiceActivity",
                "id": "act_2",
                "optional": False,
            },
        },
        "end_event": {
            "type": "EmptyEndEvent",
            "outgoing": "",
            "incoming": ["05f91b45a15b37d7b0c96d3ff94bff80"],
            "id": "end_event_id",
            "name": None,
        },
        "flows": {
            "27a9cdeaef623d37834ac6917d05eac5": {
                "is_default": False,
                "source": "start_event_id",
                "target": "pg_1",
                "id": "27a9cdeaef623d37834ac6917d05eac5",
            },
            "82b12b6aae533e55bdcc5bccfb014c2d": {
                "is_default": False,
                "source": "act_1",
                "target": "cg_1",
                "id": "82b12b6aae533e55bdcc5bccfb014c2d",
            },
            "3368add44347310eaef1f26f25909026": {
                "is_default": False,
                "source": "act_2",
                "target": "cg_1",
                "id": "3368add44347310eaef1f26f25909026",
            },
            "05f91b45a15b37d7b0c96d3ff94bff80": {
                "is_default": False,
                "source": "cg_1",
                "target": "end_event_id",
                "id": "05f91b45a15b37d7b0c96d3ff94bff80",
            },
            "3fc89273786a36b8a6e7beac8301274d": {
                "is_default": False,
                "source": "pg_1",
                "target": "act_1",
                "id": "3fc89273786a36b8a6e7beac8301274d",
            },
            "76caeed0e6053fea9db84a89f56a74a8": {
                "is_default": False,
                "source": "pg_1",
                "target": "act_2",
                "id": "76caeed0e6053fea9db84a89f56a74a8",
            },
            "76casdgd0e6053ea9db84a89f56a1234": {
                "is_default": False,
                "source": "pg_1",
                "target": "cg_1",
                "id": "76caeed0e6053fea9db84a89f56a74a8",
            },
        },
        "gateways": {
            "cg_1": {
                "type": "ConvergeGateway",
                "outgoing": "05f91b45a15b37d7b0c96d3ff94bff80",
                "incoming": [
                    "82b12b6aae533e55bdcc5bccfb014c2d",
                    "3368add44347310eaef1f26f25909026",
                    "76casdgd0e6053ea9db84a89f56a1234",
                ],
                "id": "cg_1",
                "name": None,
            },
            "pg_1": {
                "outgoing": [
                    "3fc89273786a36b8a6e7beac8301274d",
                    "76caeed0e6053fea9db84a89f56a74a8",
                    "76casdgd0e6053ea9db84a89f56a1234",
                ],
                "incoming": ["27a9cdeaef623d37834ac6917d05eac5"],
                "name": None,
                "converge_gateway_id": "cg_1",
                "type": "ParallelGateway",
                "id": "pg_1",
            },
        },
        "start_event": {
            "type": "EmptyStartEvent",
            "outgoing": "27a9cdeaef623d37834ac6917d05eac5",
            "incoming": "",
            "id": "start_event_id",
            "name": None,
        },
        "data": {"inputs": {}, "outputs": {}},
        "id": "c986802cd1e23a5f920c85b005f16dc3",
    }


def flow_valid_edge_case_3():

    start = EmptyStartEvent()
    end = EmptyEndEvent()
    eg_1 = ExclusiveGateway(id=exclusive_gw_id(1), conditions={0: "123", 1: "456"})
    eg_2 = ExclusiveGateway(id=exclusive_gw_id(2), conditions={0: "123", 1: "456"})
    eg_3 = ExclusiveGateway(id=exclusive_gw_id(3), conditions={0: "123", 1: "456"})
    eg_4 = ExclusiveGateway(id=exclusive_gw_id(4), conditions={0: "123", 1: "456"})
    pg_1 = ParallelGateway(id=parallel_gw_id(1))
    cg = ConvergeGateway(id=converge_gw_id(1))

    start.connect(eg_1)
    eg_1.connect(pg_1, end)
    pg_1.connect(eg_2, eg_3)
    eg_2.connect(eg_2, cg)
    eg_3.connect(eg_4, eg_4)
    eg_4.connect(eg_4, cg)
    cg.connect(end)

    return build_tree(start)


def flow_valid_edge_case_4():
    start = EmptyStartEvent(id=start_event_id)
    pg = ParallelGateway(id=parallel_gw_id(1))
    eg = ExclusiveGateway(
        id=exclusive_gw_id(1), conditions={0: "123", 1: "456", 2: "789"}
    )
    cg = ConvergeGateway(id=converge_gw_id(1))
    end = EmptyEndEvent(id=end_event_id)

    start.extend(pg).connect(cg, eg)
    eg.connect(eg, cg)
    cg.connect(end)

    return build_tree(start)


def flow_valid_edge_case_5():
    start = EmptyStartEvent(id=start_event_id)
    eg = ExclusiveGateway(
        id=exclusive_gw_id(1), conditions={0: "123", 1: "456", 2: "789"}
    )
    cg = ConvergeGateway(id=converge_gw_id(1))
    end = EmptyEndEvent(id=end_event_id)

    start.extend(eg).connect(cg, cg, end)
    cg.connect(eg)

    return build_tree(start)


def flow_invalid_case_1():
    start = EmptyStartEvent(id=start_event_id)
    act_1 = ServiceActivity(id=act_id(1))
    pg = ParallelGateway(id=parallel_gw_id(1))
    act_2 = ServiceActivity(id=act_id(2))
    act_3 = ServiceActivity(id=act_id(3))
    eg = ExclusiveGateway(id=exclusive_gw_id(1), conditions={0: "123", 1: "456"})
    act_4 = ServiceActivity(id=act_id(4))
    cg = ConvergeGateway(id=converge_gw_id(1))
    end = EmptyEndEvent(id=end_event_id)

    start.extend(act_1).extend(pg).connect(act_2, act_3, eg).to(eg).connect(
        act_3, act_4
    )

    act_2.connect(cg)
    act_3.connect(cg)
    act_4.connect(cg)
    cg.extend(end)

    return build_tree(start)


def flow_invalid_case_2():
    start = EmptyStartEvent(id=start_event_id)
    act_1 = ServiceActivity(id=act_id(1))
    eg = ExclusiveGateway(id=exclusive_gw_id(1), conditions={0: "123", 1: "456"})
    act_2 = ServiceActivity(id=act_id(2))
    pg = ParallelGateway(id=parallel_gw_id(1))
    act_3 = ServiceActivity(id=act_id(3))
    act_4 = ServiceActivity(id=act_id(4))
    cg = ConvergeGateway(id=converge_gw_id(1))
    end = EmptyEndEvent(id=end_event_id)

    start.extend(act_1).extend(eg).connect(act_3, act_2).to(act_2).extend(pg).connect(
        act_3, act_4
    ).converge(cg).extend(end)

    return build_tree(start)


flow_valid_edge_cases = [
    {"case": flow_valid_edge_case_1},
    {"case": flow_valid_edge_case_2},
    {"case": flow_valid_edge_case_3},
    {"case": flow_valid_edge_case_4},
    {"case": flow_valid_edge_case_5},
]

flow_invalid_cases = [
    {"case": flow_invalid_case_1, "assert_invalid": act_id(3)},
    {"case": flow_invalid_case_2, "assert_invalid": act_id(3)},
]


def gateway_valid_case():
    converge = {
        converge_gw_id(1): {
            "incoming": [1, 2, 3],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [exclusive_gw_id(1)],
            "id": converge_gw_id(1),
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": None,
            "distance": 5,
            "in_len": 3,
        },
        converge_gw_id(2): {
            "incoming": [1, 2, 3],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [exclusive_gw_id(6)],
            "id": converge_gw_id(2),
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": None,
            "distance": 5,
            "in_len": 1,
        },
        converge_gw_id(3): {
            "incoming": [1, 2, 3, 4],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [exclusive_gw_id(3)],
            "id": converge_gw_id(3),
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": None,
            "distance": 7,
            "in_len": 4,
        },
        converge_gw_id(4): {
            "incoming": [1, 2, 3, 4, 5],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [end_event_id],
            "id": converge_gw_id(4),
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": None,
            "distance": 9,
            "in_len": 5,
        },
        converge_gw_id(5): {
            "incoming": [1, 2, 3],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [parallel_gw_id(1)],
            "id": converge_gw_id(5),
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": None,
            "distance": 2,
            "in_len": 3,
        },
    }
    gateway = {
        exclusive_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [parallel_gw_id(2), converge_gw_id(3)],
            "id": exclusive_gw_id(1),
            "match": None,
            "match_assert": converge_gw_id(3),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 6,
        },
        exclusive_gw_id(2): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [exclusive_gw_id(2), converge_gw_id(2), converge_gw_id(2)],
            "id": exclusive_gw_id(2),
            "match": None,
            "match_assert": converge_gw_id(2),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 4,
        },
        exclusive_gw_id(3): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [
                parallel_gw_id(4),
                end_event_id,
                exclusive_gw_id(4),
                parallel_gw_id(3),
                parallel_gw_id(1),
            ],
            "id": exclusive_gw_id(3),
            "match": None,
            "match_assert": converge_gw_id(4),
            "converge_end": None,
            "converge_end_assert": True,
            "distance": 8,
        },
        exclusive_gw_id(4): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [exclusive_gw_id(3), converge_gw_id(4)],
            "id": exclusive_gw_id(4),
            "match": None,
            "match_assert": converge_gw_id(4),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 8,
        },
        exclusive_gw_id(5): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [converge_gw_id(4), converge_gw_id(4)],
            "id": exclusive_gw_id(5),
            "match": None,
            "match_assert": converge_gw_id(4),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 9,
        },
        exclusive_gw_id(6): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [converge_gw_id(2), converge_gw_id(3)],
            "id": exclusive_gw_id(6),
            "match": None,
            "match_assert": converge_gw_id(3),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 6,
        },
        exclusive_gw_id(7): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [converge_gw_id(3), exclusive_gw_id(8)],
            "id": exclusive_gw_id(7),
            "match": None,
            "match_assert": converge_gw_id(3),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 4,
        },
        exclusive_gw_id(8): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [exclusive_gw_id(7), converge_gw_id(3)],
            "id": exclusive_gw_id(8),
            "match": None,
            "match_assert": converge_gw_id(3),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 5,
        },
        parallel_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ConditionalParallelGateway",
            "target": [parallel_gw_id(2), exclusive_gw_id(7), exclusive_gw_id(2)],
            "id": parallel_gw_id(1),
            "match": None,
            "match_assert": converge_gw_id(3),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 3,
        },
        parallel_gw_id(2): {
            "incoming": [],
            "outgoing": [],
            "type": "ParallelGateway",
            "target": [converge_gw_id(1), converge_gw_id(1), converge_gw_id(1)],
            "id": parallel_gw_id(2),
            "match": None,
            "match_assert": converge_gw_id(1),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 4,
        },
        parallel_gw_id(3): {
            "incoming": [],
            "outgoing": [],
            "type": "ConditionalParallelGateway",
            "target": [converge_gw_id(4), converge_gw_id(4), exclusive_gw_id(5)],
            "id": parallel_gw_id(3),
            "match": None,
            "match_assert": converge_gw_id(4),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 9,
        },
        parallel_gw_id(4): {
            "incoming": [],
            "outgoing": [],
            "type": "ParallelGateway",
            "target": [converge_gw_id(5), converge_gw_id(5), converge_gw_id(5)],
            "id": parallel_gw_id(4),
            "match": None,
            "match_assert": converge_gw_id(5),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 1,
        },
    }
    stack = []
    converge_in = {}
    distances = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        parallel_gw_id(4),
        distances,
        converge_in,
    )


def gateway_valid_edge_case_1():
    converge = {}
    gateway = {
        exclusive_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [exclusive_gw_id(1), exclusive_gw_id(1), end_event_id],
            "id": exclusive_gw_id(1),
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": True,
            "distance": 2,
        }
    }

    stack = []
    distances = {}
    converge_in = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        exclusive_gw_id(1),
        distances,
        converge_in,
    )


def gateway_valid_edge_case_2():
    converge = {
        converge_gw_id(1): {
            "incoming": [1, 2],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [end_event_id],
            "id": converge_gw_id(1),
            "match": None,
            "match_assert": None,
            "converge_end": None,
            "converge_end_assert": None,
            "distance": 3,
            "in_len": 2,
        },
    }
    gateway = {
        exclusive_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [exclusive_gw_id(1), converge_gw_id(1)],
            "id": exclusive_gw_id(1),
            "match": None,
            "match_assert": converge_gw_id(1),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 2,
        },
        parallel_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ParallelGateway",
            "target": [converge_gw_id(1), exclusive_gw_id(1)],
            "id": parallel_gw_id(1),
            "match": None,
            "match_assert": converge_gw_id(1),
            "converge_end": None,
            "converge_end_assert": False,
            "distance": 1,
        },
    }

    stack = []
    distances = {}
    converge_in = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        parallel_gw_id(1),
        distances,
        converge_in,
    )


def gateway_invalid_case_1():
    converge = {
        converge_gw_id(1): {
            "incoming": [1, 2, 3],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [],
            "id": converge_gw_id(1),
            "match": None,
            "distance": 2,
            "in_len": 3,
        },
    }
    gateway = {
        exclusive_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ConditionalParallelGateway",
            "target": [converge_gw_id(1), end_event_id],
            "id": exclusive_gw_id(1),
            "match": None,
            "distance": 2,
        },
        parallel_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ParallelGateway",
            "target": [converge_gw_id(1), converge_gw_id(1), exclusive_gw_id(1)],
            "id": parallel_gw_id(1),
            "match": None,
            "distance": 1,
        },
    }

    stack = []
    distances = {}
    converge_in = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        parallel_gw_id(1),
        distances,
        converge_in,
    )


def gateway_invalid_case_2():
    converge = {
        converge_gw_id(1): {
            "incoming": [1, 2, 3, 4],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [],
            "id": converge_gw_id(1),
            "match": None,
            "distance": 3,
            "in_len": 4,
        },
    }
    gateway = {
        parallel_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ConditionalParallelGateway",
            "target": [converge_gw_id(1), converge_gw_id(1), parallel_gw_id(2)],
            "id": parallel_gw_id(1),
            "match": None,
            "distance": 1,
        },
        parallel_gw_id(2): {
            "incoming": [],
            "outgoing": [],
            "type": "ParallelGateway",
            "target": [converge_gw_id(1), converge_gw_id(1)],
            "id": parallel_gw_id(1),
            "match": None,
            "distance": 2,
        },
    }

    stack = []
    distances = {}
    converge_in = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        parallel_gw_id(1),
        distances,
        converge_in,
    )


def gateway_invalid_case_3():
    converge = {
        converge_gw_id(1): {
            "incoming": [1, 2, 3],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [],
            "id": converge_gw_id(1),
            "match": None,
            "distance": 3,
            "in_len": 4,
        }
    }
    gateway = {
        exclusive_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [parallel_gw_id(1), converge_gw_id(1)],
            "id": exclusive_gw_id(1),
            "match": None,
            "distance": 2,
        },
        parallel_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ConditionalParallelGateway",
            "target": [converge_gw_id(1), converge_gw_id(1), exclusive_gw_id(1)],
            "id": parallel_gw_id(1),
            "match": None,
            "distance": 1,
        },
    }

    stack = []

    distances = {}
    converge_in = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        parallel_gw_id(1),
        distances,
        converge_in,
    )


def gateway_invalid_case_4():
    converge = {}
    gateway = {
        parallel_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ParallelGateway",
            "target": [end_event_id, end_event_id, end_event_id],
            "id": parallel_gw_id(1),
            "match": None,
            "distance": 1,
        },
    }

    stack = []
    distances = {}
    converge_in = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        parallel_gw_id(1),
        distances,
        converge_in,
    )


def gateway_invalid_case_5():
    converge = {
        converge_gw_id(1): {
            "incoming": [1, 2],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [],
            "id": converge_gw_id(1),
            "match": None,
            "distance": 2,
            "in_len": 2,
        },
        converge_gw_id(2): {
            "incoming": [3, 4],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [],
            "id": converge_gw_id(2),
            "match": None,
            "distance": 2,
            "in_len": 2,
        },
    }
    gateway = {
        parallel_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ConditionalParallelGateway",
            "target": [
                converge_gw_id(1),
                converge_gw_id(1),
                converge_gw_id(2),
                converge_gw_id(2),
            ],
            "id": parallel_gw_id(1),
            "match": None,
            "distance": 1,
        },
    }

    stack = []
    distances = {}
    converge_in = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        parallel_gw_id(1),
        distances,
        converge_in,
    )


def gateway_invalid_case_6():
    converge = {
        converge_gw_id(1): {
            "incoming": [1, 2],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [],
            "id": converge_gw_id(1),
            "match": None,
            "distance": 2,
            "in_len": 2,
        },
        converge_gw_id(2): {
            "incoming": [3, 4],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [],
            "id": converge_gw_id(2),
            "match": None,
            "distance": 2,
            "in_len": 2,
        },
    }
    gateway = {
        exclusive_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ExclusiveGateway",
            "target": [
                converge_gw_id(1),
                converge_gw_id(1),
                converge_gw_id(2),
                converge_gw_id(2),
            ],
            "id": exclusive_gw_id(1),
            "match": None,
            "distance": 1,
        },
    }

    stack = []
    distances = {}
    converge_in = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        exclusive_gw_id(1),
        distances,
        converge_in,
    )


def gateway_invalid_case_7():
    converge = {
        converge_gw_id(1): {
            "incoming": [1, 2],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [],
            "id": converge_gw_id(1),
            "match": None,
            "distance": 3,
            "in_len": 2,
        },
        converge_gw_id(2): {
            "incoming": [1, 2, 3],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [],
            "id": converge_gw_id(2),
            "match": None,
            "distance": 4,
            "in_len": 3,
        },
    }
    gateway = {
        parallel_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ParallelGateway",
            "target": [converge_gw_id(2), converge_gw_id(2), parallel_gw_id(2)],
            "id": parallel_gw_id(1),
            "match": None,
            "distance": 1,
        },
        parallel_gw_id(2): {
            "incoming": [],
            "outgoing": [],
            "type": "ParallelGateway",
            "target": [converge_gw_id(1), converge_gw_id(1), parallel_gw_id(1)],
            "id": parallel_gw_id(2),
            "match": None,
            "distance": 2,
        },
    }

    stack = []
    distances = {}
    converge_in = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        parallel_gw_id(1),
        distances,
        converge_in,
    )


def gateway_invalid_case_8():
    converge = {
        converge_gw_id(1): {
            "incoming": [1],
            "outgoing": [],
            "type": "ConvergeGateway",
            "target": [],
            "id": converge_gw_id(1),
            "match": None,
            "distance": 3,
            "in_len": 1,
        },
    }
    gateway = {
        parallel_gw_id(1): {
            "incoming": [],
            "outgoing": [],
            "type": "ParallelGateway",
            "target": [converge_gw_id(1), converge_gw_id(1), parallel_gw_id(1)],
            "id": parallel_gw_id(1),
            "match": None,
            "distance": 1,
        },
    }

    stack = []
    distances = {}
    converge_in = {}
    for gid, g in list(gateway.items()):
        distances[gid] = g["distance"]
    for cid, c in list(converge.items()):
        distances[cid] = c["distance"]
        converge_in[cid] = c["in_len"]

    return (
        converge,
        gateway,
        stack,
        end_event_id,
        parallel_gw_id(1),
        distances,
        converge_in,
    )


gateway_valid_cases = [
    {"case": gateway_valid_case},
    {"case": gateway_valid_edge_case_1},
    {"case": gateway_valid_edge_case_2},
]

gateway_invalid_cases = [
    {"case": gateway_invalid_case_1, "invalid_assert": exclusive_gw_id(1)},
    {"case": gateway_invalid_case_2, "invalid_assert": converge_gw_id(1)},
    {"case": gateway_invalid_case_3, "invalid_assert": exclusive_gw_id(1)},
    {"case": gateway_invalid_case_4, "invalid_assert": parallel_gw_id(1)},
    {"case": gateway_invalid_case_5, "invalid_assert": parallel_gw_id(1)},
    {"case": gateway_invalid_case_6, "invalid_assert": exclusive_gw_id(1)},
    {"case": gateway_invalid_case_7, "invalid_assert": parallel_gw_id(2)},
    {"case": gateway_invalid_case_8, "invalid_assert": parallel_gw_id(1)},
]
