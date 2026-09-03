# -*- coding: utf-8 -*-
"""
Mako 表达式全量盘点：从 pipeline_tree 抽出 ${...}，并按 bamboo-engine
PR #269（3.24 LTS RCE hardening）打标。

本模块不依赖新版 bamboo-engine 的 WhitelistNameVisitor，以便在当前
bamboo-pipeline==3.24.11 上直接跑。
"""

from __future__ import unicode_literals

import ast
import json
import logging
import re

logger = logging.getLogger("root")

# 与 bamboo-engine 新引擎一致：${} 内不能再出现 $ / #。
# 比 v2 的 [^${}#] 更宽，能抓住 {"{}"}.format(...) 这类字面量花括号表达式。
TEMPLATE_PATTERN = re.compile(r"\${[^$#]+}")
# v2 引擎实际用来切模板的正则，含花括号的表达式在新引擎上今天就不会被渲染。
V2_TEMPLATE_PATTERN = re.compile(r"\${[^${}#]+}")

SAFE_FILTERS = {"n", "h", "x", "u", "trim", "entity", "unicode", "str"}
SAFE_DECODE_FILTER_PATTERN = re.compile(r"^decode\.[A-Za-z0-9][A-Za-z0-9_.-]*$")
FORBIDDEN_TEMPLATE_METHODS = {"format", "format_map"}
MAKO_RESERVED_NAMESPACES = frozenset(
    {
        "self",
        "context",
        "local",
        "parent",
        "next",
        "caller",
        "pageargs",
        "UNDEFINED",
        "STOP_RENDERING",
    }
)
DANGEROUS_ATTR_NAMES = frozenset(
    {
        "os",
        "sys",
        "subprocess",
        "shutil",
        "ctypes",
        "socket",
        "_thread",
        "threading",
        "builtins",
        "__builtins__",
        "modules",
        "popen",
        "popen2",
        "popen3",
        "popen4",
        "system",
        "spawnl",
        "spawnle",
        "spawnlp",
        "spawnlpe",
        "spawnv",
        "spawnve",
        "spawnvp",
        "spawnvpe",
        "execl",
        "execle",
        "execlp",
        "execlpe",
        "execv",
        "execve",
        "execvp",
        "execvpe",
        "fork",
        "forkpty",
        "kill",
    }
)
SAFE_BUILTIN_NAMES = frozenset(
    {
        "True",
        "False",
        "None",
        "bool",
        "int",
        "float",
        "str",
        "list",
        "tuple",
        "dict",
        "set",
        "abs",
        "round",
        "pow",
        "sum",
        "min",
        "max",
        "len",
        "range",
        "slice",
        "enumerate",
        "zip",
        "sorted",
        "reversed",
        "all",
        "any",
    }
)
DEFAULT_IMPORT_MODULES = {
    "datetime": "datetime",
    "datetime.datetime": "datetime.datetime",
    "re": "re",
    "hashlib": "hashlib",
    "random": "random",
    "time": "time",
    "os.path": "os.path",
    "config.mock.mock_json": "json",
}
DEFAULT_EXTRA_WHITELIST = frozenset({"_system", "_loop"})
DEEP_ATTR_THRESHOLD = 2


def yes_no(value):
    return "是" if value else "否"


def load_import_modules():
    try:
        from django.conf import settings

        modules = getattr(settings, "MAKO_SANDBOX_IMPORT_MODULES", None)
        if modules:
            return dict(modules)
    except Exception:
        pass
    return dict(DEFAULT_IMPORT_MODULES)


def load_extra_whitelist():
    try:
        from bamboo_engine.config import Settings as BambooSettings

        extra = getattr(BambooSettings, "MAKO_TEMPLATE_NAME_EXTRA_WHITELIST", None)
        if extra:
            return frozenset(extra)
    except Exception:
        pass
    try:
        from django.conf import settings

        extra = getattr(settings, "MAKO_TEMPLATE_NAME_EXTRA_WHITELIST", None)
        if extra:
            return frozenset(extra)
    except Exception:
        pass
    return DEFAULT_EXTRA_WHITELIST


def import_module_roots(import_modules=None):
    modules = import_modules if import_modules is not None else load_import_modules()
    roots = set()
    for alias in modules.values():
        if alias:
            roots.add(alias.split(".", 1)[0])
    return roots


def resolve_attr_chain(node):
    """Walk Attribute nodes only; stop at Call so return-value methods are ignored."""
    attrs = [node.attr]
    cur = node.value
    while isinstance(cur, ast.Attribute):
        attrs.append(cur.attr)
        cur = cur.value
    attrs.reverse()
    if isinstance(cur, ast.Name):
        return "name", cur.id, attrs
    if isinstance(cur, ast.Call):
        return "call_result", None, attrs
    return "other", None, attrs


def import_chain_violation(root, attrs, aliases):
    """Copy of bamboo-engine Task 1 helper. Python 3.6 compatible; no engine import."""
    if not root:
        return None
    roots = set(alias.split(".", 1)[0] for alias in aliases)
    if root not in roots:
        return None
    best_len = -1
    for index in range(len(attrs) + 1):
        candidate = root if index == 0 else "{}.{}".format(root, ".".join(attrs[:index]))
        if candidate in aliases:
            best_len = index
    if best_len < 0:
        return "import path not configured"
    if len(attrs[best_len:]) > 1:
        return "import attr deeper than one level"
    return None


def extract_expressions(text):
    if not isinstance(text, str):
        return []
    return TEMPLATE_PATTERN.findall(text)


def _split_top_level_filters(inner):
    """按 Mako `${expr | filter, filter}` 规则切出表达式和 filter 列表。"""
    parts = []
    buf = []
    depth = 0
    in_single = False
    in_double = False
    escape = False
    for ch in inner:
        if escape:
            buf.append(ch)
            escape = False
            continue
        if ch == "\\":
            buf.append(ch)
            escape = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
            continue
        if in_single or in_double:
            buf.append(ch)
            continue
        if ch in "([{":
            depth += 1
            buf.append(ch)
            continue
        if ch in ")]}":
            depth = max(depth - 1, 0)
            buf.append(ch)
            continue
        if ch == "|" and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    parts.append("".join(buf).strip())
    if not parts:
        return "", []
    return parts[0], [item for item in parts[1:] if item]


def _split_filter_args(filter_text):
    args = []
    buf = []
    depth = 0
    in_single = False
    in_double = False
    for ch in filter_text:
        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
            continue
        if in_single or in_double:
            buf.append(ch)
            continue
        if ch in "([{":
            depth += 1
            buf.append(ch)
            continue
        if ch in ")]}":
            depth = max(depth - 1, 0)
            buf.append(ch)
            continue
        if ch == "," and depth == 0:
            item = "".join(buf).strip()
            if item:
                args.append(item)
            buf = []
            continue
        buf.append(ch)
    item = "".join(buf).strip()
    if item:
        args.append(item)
    return args


def _validate_filter_args(filter_args, reasons):
    for filter_arg in filter_args:
        normalized = filter_arg.strip()
        if not normalized:
            continue
        if normalized in SAFE_FILTERS:
            continue
        decode_parts = normalized.split(".")
        if (
            SAFE_DECODE_FILTER_PATTERN.match(normalized)
            and "__" not in normalized
            and not any(part.startswith("_") for part in decode_parts[1:])
        ):
            continue
        reasons.append("unsupported_filter:{}".format(normalized))


class _PolicyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.reasons = []
        self.root_names = []
        self.attr_chains = []
        self.import_chains = []
        self.max_attr_depth = 0
        self.scope_stack = []

    def _in_scope(self, name):
        for scope in self.scope_stack:
            if name in scope:
                return True
        return False

    @staticmethod
    def _collect_targets(target, into):
        if isinstance(target, ast.Name):
            into.add(target.id)
        elif isinstance(target, ast.Starred):
            _PolicyVisitor._collect_targets(target.value, into)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                _PolicyVisitor._collect_targets(elt, into)

    def _attr_chain(self, node):
        parts = []
        cur = node
        depth = 0
        while True:
            if isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                depth += 1
                cur = cur.value
            elif isinstance(cur, ast.Call):
                cur = cur.func
            elif isinstance(cur, ast.Subscript):
                cur = cur.value
            else:
                break
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        parts.reverse()
        return ".".join(parts), depth

    def _get_subscript_key(self, node):
        slice_node = node.slice
        constant_node = getattr(ast, "Constant", None)
        if constant_node is not None and isinstance(slice_node, constant_node) and isinstance(slice_node.value, str):
            return slice_node.value
        if hasattr(ast, "Str") and isinstance(slice_node, ast.Str):
            return slice_node.s
        # Python 3.8 及更早：Index(value=Str/Constant)
        if hasattr(ast, "Index") and isinstance(slice_node, ast.Index):
            value = slice_node.value
            if constant_node is not None and isinstance(value, constant_node) and isinstance(value.value, str):
                return value.value
            if hasattr(ast, "Str") and isinstance(value, ast.Str):
                return value.s
        return None

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Load):
            return
        if node.id.startswith("__"):
            self.reasons.append("private_name:{}".format(node.id))
        if self._in_scope(node.id):
            return
        self.root_names.append(node.id)

    def visit_Attribute(self, node):
        chain, depth = self._attr_chain(node)
        self.max_attr_depth = max(self.max_attr_depth, depth)
        if chain:
            self.attr_chains.append(chain)
            root = chain.split(".", 1)[0]
            if root in MAKO_RESERVED_NAMESPACES:
                self.reasons.append("reserved_namespace:{}".format(root))
        kind, import_root, import_attrs = resolve_attr_chain(node)
        if kind == "name" and import_root:
            self.import_chains.append((import_root, import_attrs))
        if node.attr.startswith("__"):
            self.reasons.append("private_attr:{}".format(node.attr))
        if node.attr in FORBIDDEN_TEMPLATE_METHODS:
            self.reasons.append("forbidden_method:{}".format(node.attr))
        if node.attr in DANGEROUS_ATTR_NAMES:
            self.reasons.append("dangerous_attr:{}".format(node.attr))
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_TEMPLATE_METHODS:
            self.reasons.append("forbidden_method:{}".format(node.func.attr))
        self.generic_visit(node)

    def visit_Subscript(self, node):
        key = self._get_subscript_key(node)
        if isinstance(key, str) and key.startswith("__"):
            self.reasons.append("private_key:{}".format(key))
        self.generic_visit(node)

    def visit_Import(self, node):
        self.reasons.append("import_stmt:import")

    def visit_ImportFrom(self, node):
        self.reasons.append("import_stmt:import")

    def _enter_comprehension(self, node):
        local = set()
        for gen in node.generators:
            self._collect_targets(gen.target, local)
        self.scope_stack.append(local)
        try:
            self.generic_visit(node)
        finally:
            self.scope_stack.pop()

    def visit_ListComp(self, node):
        self._enter_comprehension(node)

    def visit_SetComp(self, node):
        self._enter_comprehension(node)

    def visit_DictComp(self, node):
        self._enter_comprehension(node)

    def visit_GeneratorExp(self, node):
        self._enter_comprehension(node)

    def visit_Lambda(self, node):
        local = set()
        args = node.args
        local.update(arg.arg for arg in args.args)
        local.update(arg.arg for arg in args.kwonlyargs)
        local.update(arg.arg for arg in getattr(args, "posonlyargs", ()) or ())
        if args.vararg:
            local.add(args.vararg.arg)
        if args.kwarg:
            local.add(args.kwarg.arg)
        self.scope_stack.append(local)
        try:
            self.generic_visit(node)
        finally:
            self.scope_stack.pop()


def _parse_python(code):
    try:
        return ast.parse(code, "<unknown>", "eval")
    except SyntaxError:
        return ast.parse(code, "<unknown>", "exec")


def analyze_expression(expr, import_modules=None, extra_whitelist=None):
    """分析单条 `${...}`。返回打标字典。"""
    import_modules = import_modules if import_modules is not None else load_import_modules()
    extra_whitelist = extra_whitelist if extra_whitelist is not None else load_extra_whitelist()
    module_roots = import_module_roots(import_modules)

    inner = expr[2:-1] if expr.startswith("${") and expr.endswith("}") else expr
    python_code, raw_filters = _split_top_level_filters(inner)
    filter_args = []
    for item in raw_filters:
        filter_args.extend(_split_filter_args(item))

    reasons = []
    _validate_filter_args(filter_args, reasons)

    visitor = _PolicyVisitor()
    parse_error = ""
    if python_code:
        try:
            tree = _parse_python(python_code)
            visitor.visit(tree)
        except SyntaxError as exc:
            parse_error = "python_parse_error:{}".format(exc.msg or exc)
            reasons.append(parse_error)
        except Exception as exc:
            parse_error = "python_parse_error:{}".format(type(exc).__name__)
            reasons.append(parse_error)

    reasons.extend(visitor.reasons)
    aliases = frozenset(alias for alias in import_modules.values() if alias)
    for root, attrs in visitor.import_chains:
        if import_chain_violation(root, attrs, aliases):
            reasons.append("import_attr_depth:{}.{}".format(root, ".".join(attrs)))
    # 保序去重
    seen = set()
    unique_reasons = []
    for reason in reasons:
        if reason not in seen:
            seen.add(reason)
            unique_reasons.append(reason)

    root_names = []
    for name in visitor.root_names:
        if name not in root_names:
            root_names.append(name)

    used_modules = [name for name in root_names if name in module_roots]
    unknown_roots = [
        name
        for name in root_names
        if name not in module_roots
        and name not in SAFE_BUILTIN_NAMES
        and name not in extra_whitelist
        and name not in MAKO_RESERVED_NAMESPACES
        and not name.startswith("__")
    ]
    for name in unknown_roots:
        unique_reasons.append("unknown_root:{}".format(name))

    unconditional_prefixes = (
        "forbidden_method:",
        "unsupported_filter:",
        "private_name:",
        "private_key:",
        "private_attr:",
        "import_stmt:",
    )
    whitelist_prefixes = ("reserved_namespace:", "dangerous_attr:", "import_attr_depth:")
    hits_unconditional = any(reason.startswith(unconditional_prefixes) for reason in unique_reasons)
    hits_whitelist = any(reason.startswith(whitelist_prefixes) for reason in unique_reasons)
    hits_policy = hits_unconditional or hits_whitelist

    if hits_unconditional:
        risk_level = "无条件阻断"
    elif hits_whitelist:
        risk_level = "仅enforce阻断"
    elif unknown_roots:
        risk_level = "潜在unknown_root"
    elif parse_error:
        risk_level = "解析失败"
    else:
        risk_level = "无"

    attr_chains = []
    for chain in visitor.attr_chains:
        if chain not in attr_chains:
            attr_chains.append(chain)

    return {
        "expr": expr,
        "root_names": root_names,
        "used_modules": used_modules,
        "uses_injected_module": bool(used_modules),
        "unknown_roots": unknown_roots,
        "attr_chains": attr_chains,
        "attr_depth": visitor.max_attr_depth,
        "has_deep_attr": visitor.max_attr_depth >= DEEP_ATTR_THRESHOLD,
        "filters": filter_args,
        "v2_matchable": bool(V2_TEMPLATE_PATTERN.fullmatch(expr)),
        "hits_unconditional": hits_unconditional,
        "hits_whitelist": hits_whitelist,
        "hits_policy": hits_policy,
        "reasons": unique_reasons,
        "risk_level": risk_level,
        "parse_error": parse_error,
    }


def classify_location(path, node_type=""):
    if ".gateways." in path and "evaluate" in path:
        return "网关条件"
    if path.startswith("$.constants.") or path == "$.constants":
        return "全局变量"
    if ".activities." in path and ".component." in path:
        return "节点输入"
    if ".activities." in path and ".constants." in path:
        return "子流程入参"
    if ".outputs" in path:
        return "输出"
    if node_type == "SubProcess":
        return "子流程节点"
    if ".activities." in path:
        return "节点字段"
    return "其他"


def _json_path_escape(key):
    text = str(key)
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", text):
        return text
    return json.dumps(text, ensure_ascii=False)


def iter_tree_strings(tree, path="$", node_ctx=None):
    """深度遍历 pipeline_tree，产出 (path, text, node_ctx)。"""
    if node_ctx is None:
        node_ctx = {}

    if isinstance(tree, str):
        if "${" in tree:
            yield path, tree, node_ctx
        return

    if isinstance(tree, dict):
        next_ctx = dict(node_ctx)
        if path.endswith(".activities") or path.split(".")[-1] == "activities":
            # 由上层对每个 activity 单独处理
            pass
        for key, value in tree.items():
            child_path = "{}.{}".format(path, _json_path_escape(key))
            if path.endswith(".activities") and isinstance(value, dict):
                child_ctx = {
                    "node_id": value.get("id") or key,
                    "node_name": value.get("name") or "",
                    "node_type": value.get("type") or "",
                    "plugin_code": ((value.get("component") or {}).get("code") or value.get("code") or ""),
                }
                yield from iter_tree_strings(value, child_path, child_ctx)
            else:
                yield from iter_tree_strings(value, child_path, next_ctx)
        return

    if isinstance(tree, (list, tuple)):
        for index, item in enumerate(tree):
            yield from iter_tree_strings(item, "{}[{}]".format(path, index), node_ctx)


def iter_template_expressions(tree, import_modules=None, extra_whitelist=None):
    """逐条产出一棵 pipeline_tree 里的表达式分析结果，避免整树结果落内存。"""
    if not isinstance(tree, dict):
        return
    import_modules = import_modules if import_modules is not None else load_import_modules()
    extra_whitelist = extra_whitelist if extra_whitelist is not None else load_extra_whitelist()
    for path, text, node_ctx in iter_tree_strings(tree):
        for expr in extract_expressions(text):
            analysis = analyze_expression(expr, import_modules=import_modules, extra_whitelist=extra_whitelist)
            analysis.update(
                {
                    "path": path,
                    "location_type": classify_location(path, node_ctx.get("node_type") or ""),
                    "node_id": node_ctx.get("node_id") or "",
                    "node_name": node_ctx.get("node_name") or "",
                    "node_type": node_ctx.get("node_type") or "",
                    "plugin_code": node_ctx.get("plugin_code") or "",
                }
            )
            yield analysis


def collect_template_expressions(tree, import_modules=None, extra_whitelist=None):
    """从一棵 pipeline_tree 收集全部表达式分析结果。"""
    return list(iter_template_expressions(tree, import_modules=import_modules, extra_whitelist=extra_whitelist))


def parse_tree(value):
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return {}
    return value


def find_subprocess_refs(tree, target_pipeline_ids):
    found = []

    def walk(sub_tree, stack):
        activities = (sub_tree or {}).get("activities") or {}
        for node_id, act in activities.items():
            if not isinstance(act, dict):
                continue
            next_stack = stack + [node_id]
            if act.get("type") == "SubProcess":
                template_id = str(act.get("template_id") or "")
                if template_id in target_pipeline_ids:
                    found.append(
                        {
                            "target_pipeline_id": template_id,
                            "node_id": node_id,
                            "node_name": act.get("name") or "",
                        }
                    )
                walk(act.get("pipeline") or {}, next_stack)

    walk(parse_tree(tree), [])
    return found


def chunked(seq, size):
    chunk = []
    for item in seq:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def collect_target_ancestors(target_pipeline_ids):
    """只对给定目标做向上闭包，返回 target -> 祖先 pipeline_template_id 集合。"""
    from pipeline.models import TemplateRelationship

    targets = set(target_pipeline_ids)
    target_to_ancestors = {pipeline_id: set() for pipeline_id in targets}
    descendant_to_targets = {pipeline_id: set([pipeline_id]) for pipeline_id in targets}
    frontier = set(targets)
    seen_pairs = set()

    while frontier:
        next_frontier = set()
        rels = TemplateRelationship.objects.filter(descendant_template_id__in=list(frontier)).values(
            "ancestor_template_id",
            "descendant_template_id",
        )
        for rel in rels.iterator(chunk_size=500):
            ancestor = str(rel["ancestor_template_id"])
            descendant = str(rel["descendant_template_id"])
            pair = (ancestor, descendant)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            mapped_targets = descendant_to_targets.get(descendant)
            if not mapped_targets:
                continue
            ancestor_targets = descendant_to_targets.setdefault(ancestor, set())
            for target in mapped_targets:
                target_to_ancestors.setdefault(target, set()).add(ancestor)
                ancestor_targets.add(target)
            next_frontier.add(ancestor)
        frontier = next_frontier

    return target_to_ancestors
