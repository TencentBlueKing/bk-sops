# 创建任务复用上次执行参数 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在创建任务的填参步骤中，支持一键导入同模板上次执行的参数值。

**Architecture:** 在 `preview_task_tree` 和 `preview_task_tree_with_schemes` 两个视图层附带查询 `last_execution_id`，新增一个轻量 API `last_execution_constants` 返回上次执行的 constants。前端部分仅描述交互改造点，不包含具体代码实现。

**Tech Stack:** Django, DRF, Python 3, pipeline engine (PipelineInstance)

**Spec:** `docs/superpowers/specs/2026-03-25-task-create-reuse-last-execution-params-design.md`

---

## File Structure

| 文件 | 操作 | 职责 |
|------|------|------|
| `gcloud/taskflow3/apis/django/api.py` | 修改 | 修改 `preview_task_tree` 视图，新增 `last_execution_constants` 视图 |
| `gcloud/taskflow3/apis/django/validators.py` | 修改 | 新增 `LastExecutionConstantsValidator` |
| `gcloud/taskflow3/apis/drf/viewsets/preview_task_tree.py` | 修改 | 修改 `PreviewTaskTreeWithSchemesView` 附带 `last_execution_id` |
| `gcloud/taskflow3/urls.py` | 修改 | 注册新 URL |
| `gcloud/tests/taskflow3/test_api.py` | 修改 | 新增测试 |

**注意：** `TaskFlowInstance` 在 `gcloud/taskflow3/apis/django/api.py:73` 中已有 import（`from gcloud.taskflow3.models import TaskFlowInstance, TimeoutNodeConfig`），无需重复添加。

**关于权限控制：** 现有的 `preview_task_tree` 视图不使用 `@iam_intercept` 装饰器，新增的 `last_execution_constants` API 与之保持一致，因为这些都是只读的预览/查询接口，权限由上层页面入口控制。

---

### Task 1: 在 `preview_task_tree` 视图中附带 `last_execution_id`

**Files:**
- Modify: `gcloud/taskflow3/apis/django/api.py:404-427`
- Test: `gcloud/tests/taskflow3/test_api.py`

- [ ] **Step 1: 写失败测试 — `preview_task_tree` 返回 `last_execution_id`**

在 `gcloud/tests/taskflow3/test_api.py` 的 `APITest` 类中新增两个测试方法：

```python
@mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
@mock.patch("gcloud.taskflow3.apis.django.api.TaskFlowInstance.objects.filter")
def test_preview_task_tree__last_execution_id_exists(self, mock_filter):
    mock_task = MagicMock()
    mock_task.id = 999
    mock_filter.return_value.order_by.return_value.only.return_value.first.return_value = mock_task

    with mock.patch(
        TASKTEMPLATE_GET, MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))
    ):
        data = {
            "template_source": "project",
            "template_id": "1",
            "version": "test_version",
            "exclude_task_nodes_id": [],
        }
        result = api.preview_task_tree(MockJsonBodyRequest("POST", data), TEST_PROJECT_ID)
        self.assertTrue(result["result"])
        self.assertEqual(result["data"]["last_execution_id"], 999)

@mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
@mock.patch("gcloud.taskflow3.apis.django.api.TaskFlowInstance.objects.filter")
def test_preview_task_tree__last_execution_id_none(self, mock_filter):
    mock_filter.return_value.order_by.return_value.only.return_value.first.return_value = None

    with mock.patch(
        TASKTEMPLATE_GET, MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))
    ):
        data = {
            "template_source": "project",
            "template_id": "1",
            "version": "test_version",
            "exclude_task_nodes_id": [],
        }
        result = api.preview_task_tree(MockJsonBodyRequest("POST", data), TEST_PROJECT_ID)
        self.assertTrue(result["result"])
        self.assertIsNone(result["data"]["last_execution_id"])
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/taskflow3/test_api.py::APITest::test_preview_task_tree__last_execution_id_exists gcloud/tests/taskflow3/test_api.py::APITest::test_preview_task_tree__last_execution_id_none -v`
Expected: FAIL — `last_execution_id` key not in response data

- [ ] **Step 3: 实现 — 修改 `preview_task_tree` 视图**

在 `gcloud/taskflow3/apis/django/api.py` 中，修改 `preview_task_tree` 函数。`TaskFlowInstance` 已在 line 73 导入，无需添加 import。

在 `data = preview_template_tree(...)` 之后、`return JsonResponse(...)` 之前插入：

```python
    last_task = TaskFlowInstance.objects.filter(
        project_id=project_id,
        template_id=str(template_id),
        template_source=template_source,
        is_deleted=False,
        is_child_taskflow=False,
        pipeline_instance__is_started=True,
        pipeline_instance__isnull=False,
    ).order_by("-id").only("id").first()

    data["last_execution_id"] = last_task.id if last_task else None
```

- [ ] **Step 4: 修复已有测试 — 补充 mock**

已有的 `test_preview_task_tree__constants_not_referred` 测试会因为新增的 `TaskFlowInstance.objects.filter` 调用而失败（缺少 mock）。需要给该测试方法添加 mock 装饰器：

将：
```python
@mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
def test_preview_task_tree__constants_not_referred(self):
```

改为：
```python
@mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
@mock.patch("gcloud.taskflow3.apis.django.api.TaskFlowInstance.objects.filter")
def test_preview_task_tree__constants_not_referred(self, mock_filter):
    mock_filter.return_value.order_by.return_value.only.return_value.first.return_value = None
```

注意：`mock_filter` 参数需要加在方法签名中，且在方法体第一行设置返回值。原有测试逻辑不变。

- [ ] **Step 5: 运行全部测试确认通过**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/taskflow3/test_api.py::APITest -v`
Expected: ALL PASS

- [ ] **Step 6: 提交**

```bash
git add gcloud/taskflow3/apis/django/api.py gcloud/tests/taskflow3/test_api.py
git commit -m "feat: preview_task_tree 附带返回 last_execution_id"
```

---

### Task 2: 在 `PreviewTaskTreeWithSchemesView` 中附带 `last_execution_id`

**Files:**
- Modify: `gcloud/taskflow3/apis/drf/viewsets/preview_task_tree.py:52-94`
- Create: `gcloud/tests/taskflow3/test_preview_task_tree_with_schemes.py`

- [ ] **Step 1: 写测试**

创建 `gcloud/tests/taskflow3/test_preview_task_tree_with_schemes.py`：

```python
# -*- coding: utf-8 -*-
from unittest import mock

from django.test import TestCase

from gcloud.taskflow3.apis.drf.viewsets.preview_task_tree import PreviewTaskTreeWithSchemesView


class PreviewTaskTreeWithSchemesLastExecutionTest(TestCase):

    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.preview_template_tree_with_schemes")
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.TaskFlowInstance.objects.filter")
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.TaskTemplate.objects.get")
    def test_last_execution_id_with_project_id(self, mock_tmpl_get, mock_filter, mock_preview):
        mock_preview.return_value = {"pipeline_tree": {}, "constants_not_referred": {}}
        mock_task = mock.MagicMock()
        mock_task.id = 888
        mock_filter.return_value.order_by.return_value.only.return_value.first.return_value = mock_task

        request = mock.MagicMock()
        request.data = {
            "project_id": 1,
            "template_id": "10",
            "version": "v1",
            "template_source": "project",
            "scheme_id_list": [],
        }

        view = PreviewTaskTreeWithSchemesView()
        view.request = request
        view.format_kwarg = None
        response = view.post(request)

        self.assertTrue(response.data["result"])
        self.assertEqual(response.data["data"]["last_execution_id"], 888)

    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.preview_template_tree_with_schemes")
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.preview_task_tree.CommonTemplate.objects.get")
    def test_last_execution_id_none_without_project_id(self, mock_tmpl_get, mock_preview):
        mock_preview.return_value = {"pipeline_tree": {}, "constants_not_referred": {}}

        request = mock.MagicMock()
        request.data = {
            "template_id": "10",
            "version": "v1",
            "template_source": "common",
            "scheme_id_list": [],
        }

        view = PreviewTaskTreeWithSchemesView()
        view.request = request
        view.format_kwarg = None
        response = view.post(request)

        self.assertTrue(response.data["result"])
        self.assertIsNone(response.data["data"]["last_execution_id"])
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/taskflow3/test_preview_task_tree_with_schemes.py -v`
Expected: FAIL — `last_execution_id` key not in response data

- [ ] **Step 3: 实现 — 修改 `PreviewTaskTreeWithSchemesView.post` 方法**

在 `gcloud/taskflow3/apis/drf/viewsets/preview_task_tree.py` 中：

1. 添加 import（在已有 import 区域）：
```python
from gcloud.taskflow3.models import TaskFlowInstance
```

2. 在 `data = preview_template_tree_with_schemes(...)` 调用之后、`return Response(...)` 之前插入：
```python
        if project_id:
            last_task = TaskFlowInstance.objects.filter(
                project_id=project_id,
                template_id=str(template_id),
                template_source=template_source,
                is_deleted=False,
                is_child_taskflow=False,
                pipeline_instance__is_started=True,
                pipeline_instance__isnull=False,
            ).order_by("-id").only("id").first()
            data["last_execution_id"] = last_task.id if last_task else None
        else:
            data["last_execution_id"] = None
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/taskflow3/test_preview_task_tree_with_schemes.py -v`
Expected: ALL PASS

- [ ] **Step 5: 提交**

```bash
git add gcloud/taskflow3/apis/drf/viewsets/preview_task_tree.py gcloud/tests/taskflow3/test_preview_task_tree_with_schemes.py
git commit -m "feat: preview_task_tree_with_schemes 附带返回 last_execution_id"
```

---

### Task 3: 新增 `LastExecutionConstantsValidator`

**Files:**
- Modify: `gcloud/taskflow3/apis/django/validators.py`

- [ ] **Step 1: 在 validators.py 末尾新增验证器类**

```python
class LastExecutionConstantsValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        template_id = request.GET.get("template_id")
        if not template_id:
            return False, "template_id can not be empty"
        return True, ""
```

`RequestValidator` 已在文件顶部 line 16 导入。`template_source` 有默认值 `project`，不需要强制校验。

- [ ] **Step 2: 提交**

```bash
git add gcloud/taskflow3/apis/django/validators.py
git commit -m "feat: 新增 LastExecutionConstantsValidator"
```

---

### Task 4: 新增 `last_execution_constants` API 视图 + URL 注册

**Files:**
- Modify: `gcloud/taskflow3/apis/django/api.py`
- Modify: `gcloud/taskflow3/urls.py`
- Test: `gcloud/tests/taskflow3/test_api.py`

- [ ] **Step 1: 写失败测试**

在 `gcloud/tests/taskflow3/test_api.py` 的 `APITest` 类中新增测试方法：

```python
@mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
@mock.patch("gcloud.taskflow3.apis.django.api.TaskFlowInstance.objects.filter")
def test_last_execution_constants__success(self, mock_filter):
    mock_pipeline_instance = MagicMock()
    mock_pipeline_instance.execution_data = {
        "constants": {
            "${ip}": {
                "key": "${ip}",
                "name": "目标IP",
                "value": "10.0.0.1",
                "custom_type": "input",
                "source_type": "custom",
                "show_type": "show",
            },
            "${hidden_var}": {
                "key": "${hidden_var}",
                "name": "隐藏变量",
                "value": "secret",
                "custom_type": "input",
                "source_type": "custom",
                "show_type": "hide",
            },
        }
    }
    mock_pipeline_instance.name = "测试任务"
    mock_pipeline_instance.creator = "admin"
    mock_pipeline_instance.create_time.strftime.return_value = "2026-03-20 10:30:00"

    mock_task = MagicMock()
    mock_task.id = 123
    mock_task.pipeline_instance = mock_pipeline_instance

    mock_filter.return_value.order_by.return_value.select_related.return_value.first.return_value = mock_task

    request = MockJsonBodyRequest("GET", {})
    request.GET = {"template_id": "1", "template_source": "project"}
    result = api.last_execution_constants(request, TEST_PROJECT_ID)

    self.assertTrue(result["result"])
    self.assertEqual(result["data"]["task_id"], 123)
    self.assertEqual(result["data"]["task_name"], "测试任务")
    self.assertEqual(result["data"]["executor"], "admin")
    self.assertIn("${ip}", result["data"]["constants"])
    self.assertNotIn("${hidden_var}", result["data"]["constants"])
    returned_ip = result["data"]["constants"]["${ip}"]
    self.assertEqual(returned_ip["value"], "10.0.0.1")
    self.assertEqual(returned_ip["name"], "目标IP")
    self.assertEqual(returned_ip["custom_type"], "input")

@mock.patch("gcloud.taskflow3.apis.django.api.JsonResponse", MockJsonResponse())
@mock.patch("gcloud.taskflow3.apis.django.api.TaskFlowInstance.objects.filter")
def test_last_execution_constants__no_history(self, mock_filter):
    mock_filter.return_value.order_by.return_value.select_related.return_value.first.return_value = None

    request = MockJsonBodyRequest("GET", {})
    request.GET = {"template_id": "1", "template_source": "project"}
    result = api.last_execution_constants(request, TEST_PROJECT_ID)

    self.assertFalse(result["result"])
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/taskflow3/test_api.py::APITest::test_last_execution_constants__success gcloud/tests/taskflow3/test_api.py::APITest::test_last_execution_constants__no_history -v`
Expected: FAIL — `api.last_execution_constants` does not exist

- [ ] **Step 3: 实现 `last_execution_constants` 视图**

在 `gcloud/taskflow3/apis/django/api.py` 中：

1. 在文件顶部 import 区域（已有的 validator import 附近）添加：
```python
from gcloud.taskflow3.apis.django.validators import LastExecutionConstantsValidator
```

2. 在 `preview_task_tree` 函数之后，添加新视图函数：

```python
@require_GET
@request_validate(LastExecutionConstantsValidator)
def last_execution_constants(request, project_id):
    template_id = request.GET.get("template_id")
    template_source = request.GET.get("template_source", PROJECT)

    last_task = TaskFlowInstance.objects.filter(
        project_id=project_id,
        template_id=str(template_id),
        template_source=template_source,
        is_deleted=False,
        is_child_taskflow=False,
        pipeline_instance__is_started=True,
        pipeline_instance__isnull=False,
    ).order_by("-id").select_related("pipeline_instance").first()

    if not last_task or not last_task.pipeline_instance:
        return JsonResponse(
            {"result": False, "message": _("没有历史执行记录"), "code": err_code.CONTENT_NOT_EXIST.code, "data": None}
        )

    execution_data = last_task.pipeline_instance.execution_data
    all_constants = execution_data.get("constants", {})

    constants = {}
    for key, val in all_constants.items():
        if val.get("show_type") != "show":
            continue
        constants[key] = {
            "key": val.get("key", key),
            "name": val.get("name", ""),
            "value": val.get("value"),
            "custom_type": val.get("custom_type", ""),
            "source_type": val.get("source_type", ""),
        }

    data = {
        "task_id": last_task.id,
        "task_name": last_task.pipeline_instance.name,
        "executor": last_task.pipeline_instance.creator,
        "create_time": last_task.pipeline_instance.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        "constants": constants,
    }

    return JsonResponse({"result": True, "data": data, "code": err_code.SUCCESS.code, "message": ""})
```

- [ ] **Step 4: 注册 URL**

在 `gcloud/taskflow3/urls.py` 的 `urlpatterns` 列表中，在 `preview_task_tree` URL 行之后添加：

```python
url(r"^api/last_execution_constants/(?P<project_id>\d+)/$", api.last_execution_constants),
```

- [ ] **Step 5: 运行全部测试确认通过**

Run: `cd /root/Projects/bk-sops && python -m pytest gcloud/tests/taskflow3/test_api.py::APITest -v`
Expected: ALL PASS

- [ ] **Step 6: 提交**

```bash
git add gcloud/taskflow3/apis/django/api.py gcloud/taskflow3/apis/django/validators.py gcloud/taskflow3/urls.py gcloud/tests/taskflow3/test_api.py
git commit -m "feat: 新增 last_execution_constants API 获取上次执行参数"
```

---

### Task 5: 前端改造点（描述，不含代码实现）

此 task 无需自动执行，供前端开发者参考。

**涉及文件：**
- `frontend/desktop/src/pages/task/TaskCreate/TaskParamFill.vue`
- `frontend/desktop/src/store/modules/task.js`
- `frontend/desktop/src/pages/task/TaskParamEdit.vue`

**改造要点：**

1. **`task.js` (Vuex store)**：新增 action `getLastExecutionConstants`，调用 `GET /taskflow/api/last_execution_constants/{project_id}/?template_id={id}&template_source={source}`

2. **`TaskParamFill.vue`**：
   - 从 `preview_task_tree` 响应中读取 `last_execution_id`，存入组件 data
   - 当 `last_execution_id` 不为 `null` 时，在"参数信息"标题右侧渲染一个 text 类型按钮"使用上一次参数"
   - 点击按钮后弹出二次确认对话框，确认后调用 `getLastExecutionConstants` action
   - 拿到 constants 后调用 `TaskParamEdit` 暴露的批量设置方法
   - 根据匹配结果显示提示消息

3. **`TaskParamEdit.vue`**：
   - 暴露一个方法（如 `applyHistoryConstants(historyConstants)`）供父组件调用
   - 方法内遍历当前 constants，与 historyConstants 按 key + custom_type 匹配，匹配成功则覆盖 value
   - 返回匹配结果 `{ matched: [...], unmatched: [...] }`，供父组件生成提示文案
   - 匹配逻辑参考现有 `reuseTaskId` 的参数复用实现
