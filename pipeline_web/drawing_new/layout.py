# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


from itertools import permutations

"""
BK-SOPS 流程画布自动排版算法（块结构）

将 pipeline_tree 解析为层级块结构（网关 → 分支 → 汇聚），
递归计算尺寸，并以块为最小换行单位进行画布排版。

算法流程:
    1. 构建图: 解析 pipeline_tree，构建节点与边的邻接关系
    2. 构建段树: 将流程解析为 NodeSegment / BlockSegment 的层级结构
    3. 计算尺寸: 递归计算每个段的宽度（列数）和高度（行数）
    4. 优化分支顺序: 自底向上重排每个网关块的分支，最小化连线交叉
    5. 放置段: 从左到右排列，以块为单位做换行判断，块不会被拆分
    6. 计算连线: 根据节点相对位置决定箭头方向（Left/Right/Top/Bottom）

使用方式:
    from pipeline_web.drawing_new.layout import layout_pipeline_tree
    layout_pipeline_tree(pipeline_tree, canvas_width=1300)
"""

NODE_TYPE_START = "EmptyStartEvent"
NODE_TYPE_END = "EmptyEndEvent"
NODE_TYPE_SERVICE = "ServiceActivity"
NODE_TYPE_SUBPROCESS = "SubProcess"
NODE_TYPE_EXCLUSIVE_GW = "ExclusiveGateway"
NODE_TYPE_PARALLEL_GW = "ParallelGateway"
NODE_TYPE_CONDITIONAL_PARALLEL_GW = "ConditionalParallelGateway"
NODE_TYPE_CONVERGE_GW = "ConvergeGateway"

BRANCH_GATEWAY_TYPES = frozenset({NODE_TYPE_EXCLUSIVE_GW, NODE_TYPE_PARALLEL_GW, NODE_TYPE_CONDITIONAL_PARALLEL_GW})

TYPE_TO_WEB = {
    NODE_TYPE_START: "startpoint",
    NODE_TYPE_END: "endpoint",
    NODE_TYPE_SERVICE: "tasknode",
    NODE_TYPE_SUBPROCESS: "subflow",
    NODE_TYPE_EXCLUSIVE_GW: "branchgateway",
    NODE_TYPE_PARALLEL_GW: "parallelgateway",
    NODE_TYPE_CONDITIONAL_PARALLEL_GW: "conditionalparallelgateway",
    NODE_TYPE_CONVERGE_GW: "convergegateway",
}

DEFAULT_CONFIG = {
    "activity_size": (154, 54),
    "event_size": (34, 34),
    "gateway_size": (34, 34),
    "start": (60, 100),
    "horizontal_gap": 230,
    "vertical_gap": 80,
    "canvas_width": 1300,
}


class PipelineGraph:
    """从 pipeline_tree 构建的有向图"""

    def __init__(self, pipeline_tree):
        self.nodes = {}
        self.edges = {}
        self.start_id = pipeline_tree["start_event"]["id"]
        self.end_id = pipeline_tree["end_event"]["id"]
        self._build(pipeline_tree)

    def _build(self, tree):
        for key in ("start_event", "end_event"):
            ev = tree[key]
            self.nodes[ev["id"]] = {
                "id": ev["id"],
                "type": ev["type"],
                "name": ev.get("name", ""),
                "incoming": _to_list(ev.get("incoming", [])),
                "outgoing": _to_list(ev.get("outgoing", [])),
            }
        for nid, node in tree.get("activities", {}).items():
            self.nodes[nid] = {
                "id": nid,
                "type": node["type"],
                "name": node.get("name", ""),
                "stage_name": node.get("stage_name", ""),
                "incoming": _to_list(node.get("incoming", [])),
                "outgoing": _to_list(node.get("outgoing", [])),
            }
        for nid, node in tree.get("gateways", {}).items():
            self.nodes[nid] = {
                "id": nid,
                "type": node["type"],
                "name": node.get("name", ""),
                "incoming": _to_list(node.get("incoming", [])),
                "outgoing": _to_list(node.get("outgoing", [])),
                "converge_gateway_id": node.get("converge_gateway_id"),
            }
        for fid, flow in tree.get("flows", {}).items():
            self.edges[fid] = {"id": fid, "source": flow["source"], "target": flow["target"]}

    def get_outgoing_targets(self, node_id):
        """按 outgoing 顺序返回 [(flow_id, target_id), ...]"""
        node = self.nodes.get(node_id)
        if not node:
            return []
        result = []
        for fid in node["outgoing"]:
            edge = self.edges.get(fid)
            if edge:
                result.append((fid, edge["target"]))
        return result


def _to_list(value):
    if isinstance(value, list):
        return value
    return [value] if value else []


class NodeSegment:
    """单节点段"""

    __slots__ = ("node_id",)

    def __init__(self, node_id):
        self.node_id = node_id

    def width(self):
        return 1

    def height(self):
        return 1


class BlockSegment:
    """网关 → 分支 → 汇聚 块段"""

    __slots__ = ("gateway_id", "converge_id", "branches")

    def __init__(self, gateway_id, converge_id, branches):
        self.gateway_id = gateway_id
        self.converge_id = converge_id
        self.branches = branches  # list of [Segment, ...]

    def width(self):
        if not self.branches:
            return 2
        max_branch_w = max(_seq_width(b) for b in self.branches)
        return 1 + max_branch_w + 1  # 网关 + 最长分支 + 汇聚

    def height(self):
        if not self.branches:
            return 1
        return sum(_seq_height(b) for b in self.branches)


def _seq_width(segments):
    """序列的总宽度（rank 列数之和）"""
    return sum(s.width() for s in segments) if segments else 0


def _seq_height(segments):
    """序列的高度（取最高段的高度，空分支占 1 行）"""
    if not segments:
        return 1
    return max(s.height() for s in segments)


def _build_segment_tree(graph):
    """
    将流程图解析为段树：
    - 顺序节点 → NodeSegment
    - 分支网关 → BlockSegment（递归解析每条分支直到汇聚网关）
    """
    visited = set()

    def _parse(start_id, stop_at=None):
        segments = []
        cur = start_id
        while cur and cur not in visited:
            if cur == stop_at:
                break
            node = graph.nodes.get(cur)
            if not node:
                break

            if node["type"] in BRANCH_GATEWAY_TYPES:
                visited.add(cur)
                conv_id = node.get("converge_gateway_id")
                branches = []
                for _, tgt in graph.get_outgoing_targets(cur):
                    branches.append(_parse(tgt, stop_at=conv_id))
                if not branches:
                    branches = [[]]
                segments.append(BlockSegment(cur, conv_id, branches))
                if conv_id:
                    visited.add(conv_id)
                    targets = graph.get_outgoing_targets(conv_id)
                    cur = targets[0][1] if targets else None
                else:
                    cur = None
            elif node["type"] == NODE_TYPE_CONVERGE_GW:
                break
            else:
                visited.add(cur)
                segments.append(NodeSegment(cur))
                targets = graph.get_outgoing_targets(cur)
                cur = targets[0][1] if targets else None

        return segments

    return _parse(graph.start_id)


MAX_PERMUTATION_BRANCHES = 4


def _cross_product(ox, oy, ax, ay, bx, by):
    return (ax - ox) * (by - oy) - (ay - oy) * (bx - ox)


def _overlap_1d(a1, a2, b1, b2):
    """判断一维区间 [min(a1,a2), max(a1,a2)] 与 [min(b1,b2), max(b1,b2)] 是否有重叠"""
    lo_a, hi_a = (a1, a2) if a1 <= a2 else (a2, a1)
    lo_b, hi_b = (b1, b2) if b1 <= b2 else (b2, b1)
    return lo_a < hi_b and lo_b < hi_a


def _segments_cross(x1, y1, x2, y2, x3, y3, x4, y4):
    """
    判断线段 (x1,y1)-(x2,y2) 与 (x3,y3)-(x4,y4) 是否交叉。
    同时检测严格相交和正交线段的重叠（折线路由中常见）。
    """
    d1 = _cross_product(x3, y3, x4, y4, x1, y1)
    d2 = _cross_product(x3, y3, x4, y4, x2, y2)
    d3 = _cross_product(x1, y1, x2, y2, x3, y3)
    d4 = _cross_product(x1, y1, x2, y2, x4, y4)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    if d1 == 0 and d2 == 0:
        return _overlap_1d(x1, x2, x3, x4) or _overlap_1d(y1, y2, y3, y4)
    return False


STUB = 14
MIDPOINT = 0.5

_DIR = {"Right": (1, 0), "Left": (-1, 0), "Top": (0, -1), "Bottom": (0, 1)}


def _flowchart_route(sx, sy, s_arrow, tx, ty, t_arrow):
    """
    模拟 jsPlumb Flowchart connector 的折线路由。
    返回折线顶点列表 [(x,y), ...], 用于交叉检测。

    路由策略:
      1. 从源端口沿 anchor 方向走 STUB 像素
      2. 在 midpoint 位置做直角拐弯
      3. 到达目标端口前 STUB 像素处再拐弯
      4. 沿 anchor 方向进入目标端口
    """
    sdx, sdy = _DIR[s_arrow]
    tdx, tdy = _DIR[t_arrow]

    s_stub = (sx + sdx * STUB, sy + sdy * STUB)
    t_stub = (tx + tdx * STUB, ty + tdy * STUB)

    s_horiz = sdx != 0
    t_horiz = tdx != 0

    if s_horiz and t_horiz:
        mid_x = s_stub[0] + (t_stub[0] - s_stub[0]) * MIDPOINT
        return [(sx, sy), s_stub, (mid_x, s_stub[1]), (mid_x, t_stub[1]), t_stub, (tx, ty)]

    if not s_horiz and not t_horiz:
        mid_y = s_stub[1] + (t_stub[1] - s_stub[1]) * MIDPOINT
        return [(sx, sy), s_stub, (s_stub[0], mid_y), (t_stub[0], mid_y), t_stub, (tx, ty)]

    if s_horiz and not t_horiz:
        return [(sx, sy), s_stub, (t_stub[0], s_stub[1]), t_stub, (tx, ty)]

    return [(sx, sy), s_stub, (s_stub[0], t_stub[1]), t_stub, (tx, ty)]


def _polylines_cross(poly_a, poly_b):
    """两条折线之间是否存在线段交叉"""
    for i in range(len(poly_a) - 1):
        ax1, ay1 = poly_a[i]
        ax2, ay2 = poly_a[i + 1]
        for j in range(len(poly_b) - 1):
            bx1, by1 = poly_b[j]
            bx2, by2 = poly_b[j + 1]
            if _segments_cross(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
                return True
    return False


def _count_crossings(graph, positions, config):
    """基于 Flowchart 折线路径的交叉检测，模拟前端 jsPlumb 实际渲染路径"""
    polylines = []
    for edge in graph.edges.values():
        src_id, tgt_id = edge["source"], edge["target"]
        sp, tp = positions.get(src_id), positions.get(tgt_id)
        if not sp or not tp:
            continue
        st = graph.nodes.get(src_id, {}).get("type", "")
        tt = graph.nodes.get(tgt_id, {}).get("type", "")
        sa, ta = _arrows(sp, tp, st, tt, config)
        sx, sy = _port_pos(sp, st, sa, config)
        tx, ty = _port_pos(tp, tt, ta, config)
        polylines.append(_flowchart_route(sx, sy, sa, tx, ty, ta))

    count = 0
    n = len(polylines)
    for i in range(n):
        for j in range(i + 1, n):
            if _polylines_cross(polylines[i], polylines[j]):
                count += 1
    return count


def _optimize_branch_order(top_segments, graph, config):
    """递归优化每个 BlockSegment 的分支顺序，使全局交叉最小化"""
    _optimize_recursive(top_segments, top_segments, graph, config)


def _optimize_recursive(segments, top_segments, graph, config):
    for seg in segments:
        if not isinstance(seg, BlockSegment):
            continue
        for branch in seg.branches:
            _optimize_recursive(branch, top_segments, graph, config)
        if len(seg.branches) <= 1:
            continue
        if len(seg.branches) <= MAX_PERMUTATION_BRANCHES:
            _best_permutation(seg, top_segments, graph, config)
        else:
            _barycenter_sort(seg)


def _best_permutation(block, top_segments, graph, config):
    """尝试所有分支排列组合，保留交叉数最少的排列"""
    original = list(block.branches)
    best_order = original
    best_crossings = float("inf")

    for perm in permutations(range(len(original))):
        block.branches = [original[i] for i in perm]
        positions = _place_segments(top_segments, graph, config)
        crossings = _count_crossings(graph, positions, config)
        if crossings < best_crossings:
            best_crossings = crossings
            best_order = list(block.branches)

    block.branches = best_order


def _barycenter_sort(block):
    """对 5+ 分支的块，按分支高度升序排列（短分支在上，减少长连线交叉）"""
    block.branches.sort(key=lambda branch: sum(s.height() for s in branch))


def _compute_y_offset(node_type, config):
    """不同类型节点的 y 轴偏移，使其与 activity 节点垂直居中"""
    ah = config["activity_size"][1]
    eh = config["event_size"][1]
    gh = config["gateway_size"][1]
    if node_type in (NODE_TYPE_START, NODE_TYPE_END):
        return int((ah - eh) * 0.5)
    if node_type in BRANCH_GATEWAY_TYPES or node_type == NODE_TYPE_CONVERGE_GW:
        return int((ah - gh) * 0.5)
    return 0


def _node_size(node_type, config):
    if node_type in (NODE_TYPE_START, NODE_TYPE_END):
        return config["event_size"]
    if node_type in BRANCH_GATEWAY_TYPES or node_type == NODE_TYPE_CONVERGE_GW:
        return config["gateway_size"]
    return config["activity_size"]


def _port_pos(pos, node_type, arrow, config):
    """根据箭头方向计算节点连接端口的实际像素坐标（节点 pos 为左上角）"""
    x, y = pos["x"], pos["y"]
    w, h = _node_size(node_type, config)
    if arrow == "Left":
        return x, y + h * 0.5
    if arrow == "Right":
        return x + w, y + h * 0.5
    if arrow == "Top":
        return x + w * 0.5, y
    if arrow == "Bottom":
        return x + w * 0.5, y + h
    return x + w * 0.5, y + h * 0.5


def _place_segments(top_segments, graph, config):
    """
    放置顶层段序列，以块为最小单位做换行判断。
    返回 {node_id: {"x": int, "y": int}}
    """
    start_x, start_y = config["start"]
    h_gap = config["horizontal_gap"]
    v_gap = config["vertical_gap"]
    canvas_width = config["canvas_width"]

    positions = {}

    def _node_pos(node_id, col, slot, y_base):
        ntype = graph.nodes[node_id]["type"]
        x = start_x + col * h_gap
        y = start_y + y_base + slot * v_gap + _compute_y_offset(ntype, config)
        positions[node_id] = {"x": round(x), "y": round(y)}

    def _place_block(block, col, slot, y_base):
        total_h = block.height()
        center_slot = slot + (total_h - 1) / 2.0
        _node_pos(block.gateway_id, col, center_slot, y_base)
        max_bw = max(_seq_width(b) for b in block.branches) if block.branches else 0
        branch_slot = slot
        for branch in block.branches:
            bcol = col + 1
            for seg in branch:
                _place(seg, bcol, branch_slot, y_base)
                bcol += seg.width()
            branch_slot += _seq_height(branch)
        if block.converge_id:
            _node_pos(block.converge_id, col + 1 + max_bw, center_slot, y_base)

    def _place(seg, col, slot, y_base):
        if isinstance(seg, NodeSegment):
            _node_pos(seg.node_id, col, slot, y_base)
        else:
            _place_block(seg, col, slot, y_base)

    # 顶层序列：从左到右，块感知换行
    cur_col = 0
    row_y = 0
    row_h = 0

    for i, seg in enumerate(top_segments):
        sw = seg.width()
        sh = seg.height()

        pixel_right = start_x + (cur_col + sw) * h_gap
        remaining_w = sum(s.width() for s in top_segments[i:])
        can_wrap = cur_col > 0 and remaining_w > 2

        if pixel_right > canvas_width and can_wrap:
            row_y += (row_h + 1) * v_gap
            cur_col = 0
            row_h = 0

        _place(seg, cur_col, 0, row_y)
        cur_col += sw
        row_h = max(row_h, sh)

    return positions


def _compute_lines(graph, positions, config):
    """根据节点坐标计算每条连线的箭头方向和折线 midpoint"""
    lines = []
    v_gap = config["vertical_gap"]

    for fid, edge in graph.edges.items():
        src_id, tgt_id = edge["source"], edge["target"]
        sp, tp = positions.get(src_id), positions.get(tgt_id)
        if not sp or not tp:
            continue

        st = graph.nodes.get(src_id, {}).get("type", "")
        tt = graph.nodes.get(tgt_id, {}).get("type", "")
        sa, ta = _arrows(sp, tp, st, tt, config)
        line = {"id": fid, "source": {"arrow": sa, "id": src_id}, "target": {"arrow": ta, "id": tgt_id}}

        # 换行连线需要 midpoint 控制折线弯折位置
        if tp["x"] < sp["x"] and tp["y"] > sp["y"]:
            dy = tp["y"] - sp["y"]
            if dy > 0:
                line["midpoint"] = round(1 - v_gap * 0.5 / dy, 3)

        lines.append(line)

    return lines


def _arrows(sp, tp, st, tt, config):
    """
    根据源/目标节点的类型和相对位置决定箭头方向。
    使用"基准 y"（去掉节点类型的对齐偏移）来判断上下关系，
    避免不同类型节点的 y 微调导致误判。

    对网关扇出和汇聚扇入做特殊处理，形成对称扇形路径，避免连线交叉：
    - 网关扇出：按分支方向从 Top/Right/Bottom 出，统一入 Left
    - 汇聚扇入：统一从 Right 出，按分支方向入 Top/Left/Bottom
    """
    sx, tx = sp["x"], tp["x"]
    sby = sp["y"] - _compute_y_offset(st, config)
    tby = tp["y"] - _compute_y_offset(tt, config)

    if sx < tx:
        if st in BRANCH_GATEWAY_TYPES:
            if sby < tby:
                return "Bottom", "Left"
            elif sby > tby:
                return "Top", "Left"
            else:
                return "Right", "Left"
        if tt == NODE_TYPE_CONVERGE_GW:
            if sby < tby:
                return "Right", "Top"
            elif sby > tby:
                return "Right", "Bottom"
            else:
                return "Right", "Left"
        return "Right", "Left"
    elif sx > tx:
        if sby < tby:
            return "Right", "Left"
        else:
            return "Bottom", "Bottom"
    else:
        if sby < tby:
            return "Bottom", "Top"
        elif sby > tby:
            return "Top", "Bottom"
        else:
            return "Right", "Left"


def _build_locations(graph, positions):
    """构建前端 location 数组"""
    locations = []
    for nid, node in graph.nodes.items():
        pos = positions.get(nid)
        if not pos:
            continue
        loc = {
            "id": nid,
            "type": TYPE_TO_WEB.get(node["type"], node["type"]),
            "x": pos["x"],
            "y": pos["y"],
            "status": "",
        }
        if node["type"] not in (NODE_TYPE_START, NODE_TYPE_END):
            loc["name"] = node.get("name", "")
        if node.get("stage_name"):
            loc["stage_name"] = node["stage_name"]
        locations.append(loc)
    return locations


def layout_pipeline_tree(pipeline_tree, **kwargs):
    """
    对 pipeline_tree 进行自动排版，原地修改 location 和 line 字段。

    :param pipeline_tree: BK-SOPS pipeline_tree 字典
    :param kwargs: 可选布局参数覆盖:
        - activity_size: tuple, 活动节点尺寸, 默认 (154, 54)
        - event_size: tuple, 事件节点尺寸, 默认 (34, 34)
        - gateway_size: tuple, 网关节点尺寸, 默认 (34, 34)
        - start: tuple, 起始坐标, 默认 (60, 100)
        - horizontal_gap: int, 水平间距, 默认 230
        - vertical_gap: int, 垂直间距, 默认 80
        - canvas_width: int, 画布最大宽度, 默认 1300
    """
    config = dict(DEFAULT_CONFIG)
    config.update(kwargs)

    # 解析 pipeline_tree，构建节点与边的有向图
    graph = PipelineGraph(pipeline_tree)
    # 将有向图转换为层级段树（顺序节点 → NodeSegment，网关分支 → BlockSegment）
    segments = _build_segment_tree(graph)
    # 重排每个网关块的分支顺序，最小化连线交叉
    _optimize_branch_order(segments, graph, config)
    # 按段树从左到右放置节点坐标，以块为单位做换行
    positions = _place_segments(segments, graph, config)
    # 根据节点坐标计算每条连线的箭头方向和折线控制点
    lines = _compute_lines(graph, positions, config)
    # 构建前端所需的 location 数组
    locations = _build_locations(graph, positions)

    pipeline_tree["location"] = locations
    pipeline_tree["line"] = lines
    return pipeline_tree
