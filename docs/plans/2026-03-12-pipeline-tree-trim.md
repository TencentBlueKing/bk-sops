# pipeline_tree MCP 响应裁剪 — 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** MCP 请求默认仍不返回 `pipeline_tree`（向后兼容），需要的 Skill 通过 `include_pipeline_tree=true` 参数显式请求裁剪后版本；同时将 `get_task_node_detail` 的 `histories` 从完全移除改为限制最近 3 条。

**Architecture:** 新增 `pipeline_tree_trimmer.py` 纯函数模块，扩展 `@mcp_apigw` 装饰器支持 `trim_responses` 参数（默认移除，opt-in 时裁剪返回），修改 4 个视图函数的装饰器配置，在 `get_task_node_detail` 视图内部实现 histories 限制。

**Tech Stack:** Python 3, Django, ujson

**TAPD:** --story=132544238

**行为矩阵：**

| 场景 | pipeline_tree 行为 |
|------|-------------------|
| MCP 请求，未传 `include_pipeline_tree` | 移除（向后兼容） |
| MCP 请求，`include_pipeline_tree=true` | 返回裁剪后版本 |
| 非 MCP 请求 | 返回完整版本（不变） |

---

### Task 1: 创建 pipeline_tree_trimmer 模块

**Files:**
- Create: `gcloud/apigw/pipeline_tree_trimmer.py`
- Test: `gcloud/tests/apigw/test_pipeline_tree_trimmer.py`

**Step 1: 创建裁剪模块**

在 `gcloud/apigw/pipeline_tree_trimmer.py` 中实现以下纯函数（无外部依赖，仅需标准库）：

```python
"""pipeline_tree MCP 响应裁剪模块

对 pipeline_tree 执行结构化裁剪：移除前端渲染、画布布局、冗余元数据等字段，
保留 Skill 所需的全部语义信息。

裁剪规则：
- Activities: 白名单保留核心字段，SubProcess 递归裁剪
- Component.data: hook 解包 + 空值移除 + 黑名单过滤
- Gateways: 白名单保留
- Flows: 仅保留 source/target/is_default
- Events: 仅保留 id/type/name
- Constants: 白名单保留 + 空值过滤
- 顶层 line/location: 移除
"""

_ACTIVITY_KEEP = {
    "id", "type", "name", "component", "pipeline",
    "stage_name", "retryable", "skippable", "error_ignorable", "auto_retry",
    "source_info",
}
_SUBPROCESS_EXTRA = {"template_id", "template_source", "version", "hooked_constants"}

_GATEWAY_KEEP = {"id", "type", "name", "conditions", "default_condition", "converge_gateway_id"}

_CONSTANT_KEEP = {"key", "name", "desc", "source_type", "custom_type", "value", "source_tag", "source_info"}

_DATA_FIELD_BLACKLIST = {
    "button_refresh", "button_refresh_2", "button_refresh_3",
    "ip_is_exist", "is_tagged_ip",
    "need_log_outputs_even_fail",
    "job_rolling_config",
    "\u00a9",
}


def trim_pipeline_tree(pipeline_tree):
    if not isinstance(pipeline_tree, dict):
        return pipeline_tree
    return _trim_tree(pipeline_tree)


def _trim_tree(tree):
    result = {}
    for key, val in tree.items():
        if key in ("line", "location"):
            continue
        if key == "activities" and isinstance(val, dict):
            result[key] = _trim_activities(val)
        elif key == "gateways" and isinstance(val, dict):
            result[key] = _trim_gateways(val)
        elif key == "flows" and isinstance(val, dict):
            result[key] = _trim_flows(val)
        elif key in ("start_event", "end_event") and isinstance(val, dict):
            result[key] = _trim_event(val)
        elif key == "constants" and isinstance(val, dict):
            result[key] = _trim_constants(val)
        else:
            result[key] = val
    return result


def _trim_activities(activities):
    trimmed = {}
    for act_id, act in activities.items():
        is_subprocess = act.get("type") == "SubProcess"
        keep = _ACTIVITY_KEEP | _SUBPROCESS_EXTRA if is_subprocess else _ACTIVITY_KEEP
        node = {}
        for field, val in act.items():
            if field not in keep:
                continue
            if field == "pipeline" and isinstance(val, dict):
                val = _trim_tree(val)
            elif field == "component" and isinstance(val, dict):
                val = _trim_component(val)
            node[field] = val
        trimmed[act_id] = node
    return trimmed


def _trim_component(component):
    result = {"code": component.get("code", "")}
    if "version" in component:
        result["version"] = component["version"]
    if "data" in component and isinstance(component["data"], dict):
        result["data"] = _trim_component_data(component["data"])
    return result


def _trim_component_data(data):
    result = {}
    for field_name, field_val in data.items():
        if field_name in _DATA_FIELD_BLACKLIST:
            continue
        val = _unwrap_hook(field_val)
        if _is_empty(val):
            continue
        result[field_name] = val
    return result


def _unwrap_hook(val):
    if isinstance(val, dict) and "value" in val and "hook" in val:
        return val["value"]
    return val


def _is_empty(val):
    return val == "" or val == [] or val == {} or val is None


def _trim_gateways(gateways):
    return {
        gw_id: {k: v for k, v in gw.items() if k in _GATEWAY_KEEP}
        for gw_id, gw in gateways.items()
    }


def _trim_flows(flows):
    trimmed = {}
    for fl_id, fl in flows.items():
        if "source" not in fl or "target" not in fl:
            continue
        entry = {"source": fl["source"], "target": fl["target"]}
        if fl.get("is_default"):
            entry["is_default"] = True
        trimmed[fl_id] = entry
    return trimmed


def _trim_event(event):
    return {
        "id": event.get("id", ""),
        "type": event.get("type", ""),
        "name": event.get("name", ""),
    }


def _trim_constants(constants):
    trimmed = {}
    for key, const in constants.items():
        if isinstance(const, dict):
            entry = {}
            for field, val in const.items():
                if field not in _CONSTANT_KEEP:
                    continue
                if field == "value":
                    val = _unwrap_hook(val)
                if _is_empty(val):
                    continue
                entry[field] = val
            trimmed[key] = entry
        else:
            trimmed[key] = const
    return trimmed
```

**Step 2: 编写单元测试**

在 `gcloud/tests/apigw/test_pipeline_tree_trimmer.py` 中编写测试：

```python
from django.test import TestCase

from gcloud.apigw.pipeline_tree_trimmer import trim_pipeline_tree


def _make_sample_tree():
    """构造一个包含所有典型字段的 pipeline_tree"""
    return {
        "id": "root_pipeline",
        "name": "测试流程",
        "start_event": {
            "id": "start_node",
            "type": "EmptyStartEvent",
            "name": "开始",
            "incoming": "",
            "outgoing": "flow1",
        },
        "end_event": {
            "id": "end_node",
            "type": "EmptyEndEvent",
            "name": "结束",
            "incoming": "flow2",
            "outgoing": "",
        },
        "activities": {
            "node1": {
                "id": "node1",
                "type": "ServiceActivity",
                "name": "执行脚本",
                "incoming": "flow1",
                "outgoing": "flow2",
                "optional": True,
                "loop": None,
                "labels": [],
                "stage_name": "步骤1",
                "retryable": True,
                "skippable": True,
                "error_ignorable": False,
                "auto_retry": {"enabled": False},
                "timeout_config": {"enabled": False},
                "component": {
                    "code": "job_fast_execute_script",
                    "version": "v1.0",
                    "data": {
                        "job_script_source": {"hook": False, "need_render": True, "value": "manual"},
                        "job_content": {"hook": False, "need_render": True, "value": "echo hello"},
                        "ip_list": {"hook": True, "need_render": True, "value": "${ip_list}"},
                        "button_refresh": {"hook": False, "value": ""},
                        "empty_field": {"hook": False, "value": ""},
                    },
                },
            },
        },
        "gateways": {
            "gw1": {
                "id": "gw1",
                "type": "ExclusiveGateway",
                "name": "判断",
                "incoming": "f1",
                "outgoing": ["f2", "f3"],
                "conditions": {"f2": {"evaluate": "${result} == True"}},
                "default_condition": {"flow_id": "f3"},
                "labels": [],
            },
        },
        "flows": {
            "flow1": {
                "id": "flow1",
                "source": "start_node",
                "target": "node1",
                "is_default": False,
                "line": {"x": 1, "y": 2},
            },
            "flow2": {
                "id": "flow2",
                "source": "node1",
                "target": "end_node",
                "is_default": True,
            },
        },
        "constants": {
            "${ip_list}": {
                "key": "${ip_list}",
                "name": "IP列表",
                "desc": "目标IP",
                "source_type": "custom",
                "custom_type": "textarea",
                "value": {"hook": True, "value": ""},
                "source_tag": "",
                "source_info": {},
                "index": 1,
                "version": "legacy",
                "show_type": "show",
                "form_schema": {},
                "validation": "",
            },
        },
        "line": {"l1": {"source": {"id": "n1"}, "target": {"id": "n2"}}},
        "location": [{"id": "n1", "x": 100, "y": 200}],
    }


class TrimPipelineTreeTest(TestCase):
    def test_preserves_top_level_structure(self):
        result = trim_pipeline_tree(_make_sample_tree())
        for key in ("activities", "flows", "gateways", "constants", "start_event", "end_event"):
            self.assertIn(key, result)
        self.assertIn("id", result)
        self.assertIn("name", result)

    def test_removes_line_and_location(self):
        result = trim_pipeline_tree(_make_sample_tree())
        self.assertNotIn("line", result)
        self.assertNotIn("location", result)

    def test_activity_whitelist(self):
        result = trim_pipeline_tree(_make_sample_tree())
        node = result["activities"]["node1"]
        self.assertEqual(node["id"], "node1")
        self.assertEqual(node["type"], "ServiceActivity")
        self.assertEqual(node["name"], "执行脚本")
        self.assertEqual(node["stage_name"], "步骤1")
        self.assertTrue(node["retryable"])
        self.assertNotIn("incoming", node)
        self.assertNotIn("outgoing", node)
        self.assertNotIn("optional", node)
        self.assertNotIn("loop", node)
        self.assertNotIn("labels", node)
        self.assertNotIn("timeout_config", node)

    def test_component_data_hook_unwrap(self):
        result = trim_pipeline_tree(_make_sample_tree())
        data = result["activities"]["node1"]["component"]["data"]
        self.assertEqual(data["job_script_source"], "manual")
        self.assertEqual(data["ip_list"], "${ip_list}")

    def test_component_data_removes_blacklist(self):
        result = trim_pipeline_tree(_make_sample_tree())
        data = result["activities"]["node1"]["component"]["data"]
        self.assertNotIn("button_refresh", data)

    def test_component_data_removes_empty(self):
        result = trim_pipeline_tree(_make_sample_tree())
        data = result["activities"]["node1"]["component"]["data"]
        self.assertNotIn("empty_field", data)

    def test_gateway_whitelist(self):
        result = trim_pipeline_tree(_make_sample_tree())
        gw = result["gateways"]["gw1"]
        self.assertEqual(gw["id"], "gw1")
        self.assertEqual(gw["type"], "ExclusiveGateway")
        self.assertIn("conditions", gw)
        self.assertIn("default_condition", gw)
        self.assertNotIn("incoming", gw)
        self.assertNotIn("outgoing", gw)
        self.assertNotIn("labels", gw)

    def test_flow_preserves_source_target(self):
        result = trim_pipeline_tree(_make_sample_tree())
        f1 = result["flows"]["flow1"]
        self.assertEqual(f1["source"], "start_node")
        self.assertEqual(f1["target"], "node1")
        self.assertNotIn("line", f1)
        self.assertNotIn("id", f1)

    def test_flow_preserves_is_default(self):
        result = trim_pipeline_tree(_make_sample_tree())
        f2 = result["flows"]["flow2"]
        self.assertTrue(f2["is_default"])

    def test_event_keeps_only_id_type_name(self):
        result = trim_pipeline_tree(_make_sample_tree())
        start = result["start_event"]
        self.assertEqual(set(start.keys()), {"id", "type", "name"})

    def test_constants_whitelist(self):
        result = trim_pipeline_tree(_make_sample_tree())
        const = result["constants"]["${ip_list}"]
        self.assertEqual(const["key"], "${ip_list}")
        self.assertEqual(const["name"], "IP列表")
        self.assertNotIn("index", const)
        self.assertNotIn("version", const)
        self.assertNotIn("show_type", const)
        self.assertNotIn("form_schema", const)

    def test_constants_value_hook_unwrap(self):
        result = trim_pipeline_tree(_make_sample_tree())
        const = result["constants"]["${ip_list}"]
        self.assertNotIn("value", const)  # unwrapped value is "" which is empty, so removed

    def test_subprocess_recursion(self):
        tree = {
            "id": "root",
            "activities": {
                "sub1": {
                    "id": "sub1",
                    "type": "SubProcess",
                    "name": "子流程",
                    "template_id": 100,
                    "template_source": "project",
                    "version": "v1",
                    "pipeline": {
                        "id": "sub_pipeline",
                        "activities": {},
                        "gateways": {},
                        "flows": {},
                        "constants": {},
                        "start_event": {"id": "s1", "type": "EmptyStartEvent", "name": ""},
                        "end_event": {"id": "e1", "type": "EmptyEndEvent", "name": ""},
                        "line": {"should": "be removed"},
                        "location": [{"should": "be removed"}],
                    },
                },
            },
            "gateways": {},
            "flows": {},
            "constants": {},
            "start_event": {"id": "s0", "type": "EmptyStartEvent", "name": ""},
            "end_event": {"id": "e0", "type": "EmptyEndEvent", "name": ""},
        }
        result = trim_pipeline_tree(tree)
        sub = result["activities"]["sub1"]
        self.assertEqual(sub["template_id"], 100)
        self.assertNotIn("line", sub["pipeline"])
        self.assertNotIn("location", sub["pipeline"])

    def test_preserves_converge_gateway_id(self):
        tree = {
            "id": "root",
            "activities": {},
            "gateways": {
                "pg1": {
                    "id": "pg1",
                    "type": "ParallelGateway",
                    "name": "",
                    "converge_gateway_id": "cg1",
                    "incoming": "f1",
                    "outgoing": ["f2", "f3"],
                },
            },
            "flows": {},
            "constants": {},
            "start_event": {"id": "s", "type": "EmptyStartEvent", "name": ""},
            "end_event": {"id": "e", "type": "EmptyEndEvent", "name": ""},
        }
        result = trim_pipeline_tree(tree)
        self.assertEqual(result["gateways"]["pg1"]["converge_gateway_id"], "cg1")

    def test_non_dict_input_returns_as_is(self):
        self.assertIsNone(trim_pipeline_tree(None))
        self.assertEqual(trim_pipeline_tree("string"), "string")
        self.assertEqual(trim_pipeline_tree([1, 2]), [1, 2])
```

**Step 3: 运行测试**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/apigw/test_pipeline_tree_trimmer.py -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add gcloud/apigw/pipeline_tree_trimmer.py gcloud/tests/apigw/test_pipeline_tree_trimmer.py
git commit -m "feat: 新增 pipeline_tree MCP 响应裁剪模块 --story=132544238"
```

---

### Task 2: 扩展 @mcp_apigw 装饰器

**Files:**
- Modify: `gcloud/apigw/decorators.py:281-338`

**Step 1: 修改 `mcp_apigw` 函数**

在 `gcloud/apigw/decorators.py` 中，将 `mcp_apigw` 函数替换为以下实现：

将当前的 `mcp_apigw` 函数（第 281-338 行）替换为：

```python
def mcp_apigw(exclude_responses=None, trim_responses=None):
    """
    装饰器：MCP 请求响应处理

    @param exclude_responses: 要无条件移除的键列表，支持 "xx.yy.zz" 格式
    @param trim_responses: 可选裁剪字段映射 {字段名: 裁剪函数}。
        字段名为 data 下的直接键名（如 "pipeline_tree"）。
        MCP 请求默认移除这些字段；客户端传入 include_{字段名}=true 时，
        调用裁剪函数处理后返回。非 MCP 请求不受影响。
    """
    if exclude_responses is None:
        exclude_responses = []
    if trim_responses is None:
        trim_responses = {}

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            request.is_mcp_request = is_mcp_request(request)
            result = view_func(request, *args, **kwargs)

            if request.is_mcp_request and (exclude_responses or trim_responses):
                if isinstance(result, JsonResponse):
                    result_data = json.loads(result.content.decode("utf-8"))
                    _apply_mcp_transforms(request, result_data, exclude_responses, trim_responses)
                    result = JsonResponse(result_data)
                elif isinstance(result, dict):
                    _apply_mcp_transforms(request, result, exclude_responses, trim_responses)

            return result

        return wrapper

    return decorator


def _apply_mcp_transforms(request, result_data, exclude_responses, trim_responses):
    """对 MCP 响应数据执行裁剪/移除操作（原地修改）"""
    data = result_data.get("data") if isinstance(result_data, dict) else None

    if trim_responses and isinstance(data, dict):
        for field, trimmer in trim_responses.items():
            if field not in data:
                continue
            include_param = "include_{}".format(field)
            if _is_param_true(request, include_param):
                data[field] = trimmer(data[field])
            else:
                del data[field]

    if exclude_responses:
        cleaned = _remove_keys_from_dict(result_data, exclude_responses)
        result_data.clear()
        result_data.update(cleaned)


def _is_param_true(request, param_name):
    """检查请求参数（GET 或 POST body）中指定参数是否为 true"""
    val = request.GET.get(param_name)
    if val is None and request.method == "POST" and request.body:
        try:
            body = json.loads(request.body)
            val = body.get(param_name)
        except Exception:
            pass
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes")
```

**Step 2: 运行现有装饰器测试确保不回退**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/apigw/ -v -k "not trimmer"`
Expected: All existing tests PASS

**Step 3: Commit**

```bash
git add gcloud/apigw/decorators.py
git commit -m "feat: @mcp_apigw 装饰器新增 trim_responses 参数支持 opt-in 裁剪 --story=132544238"
```

---

### Task 3: 修改 get_template_info 视图

**Files:**
- Modify: `gcloud/apigw/views/get_template_info.py`

**Step 1: 修改装饰器参数**

1. 在文件顶部 import 区域添加：
```python
from gcloud.apigw.pipeline_tree_trimmer import trim_pipeline_tree
```

2. 将第 37 行从：
```python
@mcp_apigw(exclude_responses=["data.pipeline_tree"])
```
改为：
```python
@mcp_apigw(trim_responses={"pipeline_tree": trim_pipeline_tree})
```

**Step 2: 运行现有测试**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/apigw/views/test_get_template_info.py -v`
Expected: All tests PASS（现有测试不会传 include_pipeline_tree，所以行为与之前一致——pipeline_tree 被移除）

**Step 3: Commit**

```bash
git add gcloud/apigw/views/get_template_info.py
git commit -m "feat: get_template_info 支持 include_pipeline_tree 参数 opt-in 裁剪返回 --story=132544238"
```

---

### Task 4: 修改 get_task_detail 视图

**Files:**
- Modify: `gcloud/apigw/views/get_task_detail.py`

**Step 1: 修改装饰器参数**

1. 在文件顶部添加 import：
```python
from gcloud.apigw.pipeline_tree_trimmer import trim_pipeline_tree
```

2. 将第 32 行从：
```python
@mcp_apigw(exclude_responses=["data.pipeline_tree", "data.task_webhook_history"])
```
改为：
```python
@mcp_apigw(
    exclude_responses=["data.task_webhook_history"],
    trim_responses={"pipeline_tree": trim_pipeline_tree},
)
```

**Step 2: 运行现有测试**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/apigw/views/test_get_task_detail.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add gcloud/apigw/views/get_task_detail.py
git commit -m "feat: get_task_detail 支持 include_pipeline_tree 参数 opt-in 裁剪返回 --story=132544238"
```

---

### Task 5: 修改 get_common_template_info 视图

**Files:**
- Modify: `gcloud/apigw/views/get_common_template_info.py`

**Step 1: 修改装饰器参数**

1. 在文件顶部添加 import：
```python
from gcloud.apigw.pipeline_tree_trimmer import trim_pipeline_tree
```

2. 将第 31 行从：
```python
@mcp_apigw(exclude_responses=["data.pipeline_tree", "data.template_constants"])
```
改为：
```python
@mcp_apigw(
    exclude_responses=["data.template_constants"],
    trim_responses={"pipeline_tree": trim_pipeline_tree},
)
```

**Step 2: 运行现有测试**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/apigw/views/test_get_common_template_info.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add gcloud/apigw/views/get_common_template_info.py
git commit -m "feat: get_common_template_info 支持 include_pipeline_tree 参数 opt-in 裁剪返回 --story=132544238"
```

---

### Task 6: 修改 get_task_node_detail 视图（histories 限制）

**Files:**
- Modify: `gcloud/apigw/views/get_task_node_detail.py`

**Step 1: 修改装饰器和视图函数**

1. 将装饰器从 `@mcp_apigw(exclude_responses=["data.histories"])` 改为 `@mcp_apigw()`
2. 在视图函数末尾、`return result` 之前，添加 MCP histories 限制逻辑
3. 在文件末尾添加 `_get_max_histories` 辅助函数

修改后的完整视图函数：

```python
@login_exempt
@require_GET
@apigw_require
@mcp_apigw()
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
def get_task_node_detail(request, task_id, project_id):
    """
    @summary: 获取节点输入输出
    @param request:
    @param task_id:
    @param project_id:
    @return:
    """
    project = request.project
    try:
        task = TaskFlowInstance.objects.get(id=task_id, project_id=project.id)
    except TaskFlowInstance.DoesNotExist:
        message = (
            "[API] get_task_node_detail task[id={task_id}] "
            "of project[project_id={project_id}, biz_id{biz_id}] does not exist".format(
                task_id=task_id, project_id=project.id, biz_id=project.bk_biz_id
            )
        )
        logger.exception(message)
        return {"result": False, "message": message, "code": err_code.CONTENT_NOT_EXIST.code}

    node_id = request.GET.get("node_id")
    component_code = request.GET.get("component_code")
    loop = request.GET.get("loop")

    try:
        subprocess_stack = json.loads(request.GET.get("subprocess_stack", "[]"))
    except Exception:
        return {
            "result": False,
            "message": "subprocess_stack is not a valid array json",
            "code": err_code.UNKNOWN_ERROR.code,
        }
    result = task.get_node_detail(
        node_id=node_id,
        username=request.user.username,
        component_code=component_code,
        subprocess_stack=subprocess_stack,
        project_id=project_id,
        loop=loop,
    )

    if getattr(request, "is_mcp_request", False) and result.get("result"):
        max_histories = _get_max_histories(request)
        histories = result.get("data", {}).get("histories")
        if histories is not None and len(histories) > max_histories:
            result["data"]["histories"] = histories[-max_histories:]

    return result


def _get_max_histories(request):
    try:
        val = int(request.GET.get("max_histories", 3))
        return max(val, 0)
    except (ValueError, TypeError):
        return 3
```

注意：需要在文件顶部添加 `from gcloud import err_code` 的 import（检查是否已有）。

**Step 2: 运行现有测试**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/apigw/views/test_get_task_node_detail.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add gcloud/apigw/views/get_task_node_detail.py
git commit -m "feat: get_task_node_detail 的 histories 从完全移除改为限制最近 N 条 --story=132544238"
```

---

### Task 7: 更新文档

**Files:**
- Modify: `docs/design/mcp-response-field-exclusions.md`
- Modify: `docs/apidoc/zh_hans/get_task_node_detail.md`（添加 max_histories 参数说明）

**Step 1: 更新 mcp-response-field-exclusions.md**

更新以下接口的裁剪说明：

1. `get_template_info`：
   - `pipeline_tree` 从"完全移除"改为"默认移除，传入 `include_pipeline_tree=true` 时返回裁剪后版本"
   
2. `get_task_detail`：同上说明，`task_webhook_history` 保持无条件移除

3. `get_common_template_info`：`pipeline_tree` 同上，`template_constants` 保持无条件移除

4. `get_task_node_detail`：`histories` 从"完全移除"改为"返回最近 3 条，可通过 `max_histories` 参数调整"

**Step 2: 更新 get_task_node_detail API 文档**

在 `docs/apidoc/zh_hans/get_task_node_detail.md` 的参数表中添加：

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| max_histories | int | 否 | MCP 请求时，返回最近 N 条重试记录，默认 3。0 表示不返回。非 MCP 请求忽略此参数 |

同时为 `get_template_info`、`get_task_detail`、`get_common_template_info` 的 API 文档中添加 `include_pipeline_tree` 参数说明。

**Step 3: Commit**

```bash
git add docs/design/mcp-response-field-exclusions.md docs/apidoc/zh_hans/get_task_node_detail.md
git commit -m "docs: 更新 MCP 响应裁剪策略文档，新增 opt-in 参数说明 --story=132544238"
```

---

### Task 8: 更新 YAML 资源定义

**Files:**
- Modify: `apigw/bk_apigw_resources_bk-sops_mcp_supplement.yaml`

**Step 1: 为 3 个接口补充 include_pipeline_tree 参数**

在 YAML 中为 `get_template_info`、`get_task_detail`、`get_common_template_info` 添加 `include_pipeline_tree` query 参数定义：

```yaml
- in: query
  name: include_pipeline_tree
  schema:
    type: boolean
    default: false
  description: >-
    仅 MCP 请求有效。设置为 true 时返回裁剪后的 pipeline_tree（移除画布坐标、
    前端渲染字段等冗余数据，保留流程结构语义信息）。默认不返回 pipeline_tree。
```

同时为 `get_task_node_detail` 添加 `max_histories` 参数定义：

```yaml
- in: query
  name: max_histories
  schema:
    type: integer
    default: 3
  description: >-
    仅 MCP 请求有效。限制返回的节点重试历史记录条数，默认 3 条。
    设置为 0 表示不返回历史记录。非 MCP 请求忽略此参数。
```

如果这些接口尚未在 supplement YAML 中定义，则新增对应的路径定义。

**Step 2: 验证 YAML 语法**

Run: `python3 -c "import yaml; yaml.safe_load(open('apigw/bk_apigw_resources_bk-sops_mcp_supplement.yaml')); print('YAML is valid')"`
Expected: "YAML is valid"

**Step 3: Commit**

```bash
git add apigw/bk_apigw_resources_bk-sops_mcp_supplement.yaml
git commit -m "docs: YAML 资源定义补充 include_pipeline_tree 和 max_histories 参数 --story=132544238"
```

---

### Task 9: 全量测试验证

**Step 1: 运行所有 apigw 测试**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/apigw/ -v`
Expected: All tests PASS

**Step 2: 确认无遗漏**

检查所有修改文件的 lint 状态，确保无语法错误。
