# AI 平台调用埋点 Implementation Plan

**Goal:** 让 SOPS 后端能识别来自 AI 平台（如 OpenClaw）的 API 调用，并通过 OTel Span 和 create_method 进行埋点统计。

**Architecture:** Skill 在调用 API 时注入 `X-Bkapi-Ai-Platform` Header → 后端 `mark_ai_platform` 装饰器检测并标记 request → `trace_view` 将标记写入 OTel Span 属性 → `create_task` 设置 `create_method=openclaw`。

**Tech Stack:** Django, OpenTelemetry, Python 3

**Design doc:** `docs/plans/2026-03-09-ai-platform-call-tracking-design.md`

---

## Phase 1：后端识别 + create_method 扩展 + 规范文档

### Task 1: Settings 配置项

**Files:**
- Modify: `config/default.py`

**Step 1: 添加配置项**

在 `config/default.py` 中现有的 `APIGW_MCP_APP_CODE_PREFIX` 附近添加两个新配置项：

```
APIGW_AI_PLATFORM_HEADER = "HTTP_X_BKAPI_AI_PLATFORM"
APIGW_AI_SKILL_HEADER = "HTTP_X_BKAPI_AI_SKILL"
```

**Step 2: Commit**

```
git add config/default.py
git commit -m "feat: 新增 AI 平台 Header 配置项"
```

---

### Task 2: 检测函数与装饰器

**Files:**
- Modify: `gcloud/apigw/decorators.py`
- Create: `gcloud/tests/apigw/views/test_decorators.py`

**Step 1: 编写测试**

新建 `gcloud/tests/apigw/views/test_decorators.py`，包含以下测试类和方法：

- `IsAiPlatformRequestTest`
  - `test_returns_platform_when_header_present`: request.META 设置 `HTTP_X_BKAPI_AI_PLATFORM = "openclaw"`，断言返回 `"openclaw"`
  - `test_returns_empty_string_when_header_absent`: 无 Header，断言返回 `""`
  - `test_returns_empty_string_when_header_is_whitespace`: Header 值为空格，断言返回 `""`
  - `test_strips_whitespace`: Header 值 `"  openclaw  "`，断言返回 `"openclaw"`

- `MarkAiPlatformDecoratorTest`
  - `test_injects_ai_platform_and_skill`: 同时设置 Platform 和 Skill Header，断言 `request.ai_platform` 和 `request.ai_skill` 正确
  - `test_empty_when_no_headers`: 无 Header，断言两个属性均为空字符串

**Step 2: 运行测试，确认失败**

```
python -m pytest gcloud/tests/apigw/views/test_decorators.py -v
```

Expected: FAIL（`is_ai_platform_request` 和 `mark_ai_platform` 尚不存在）

**Step 3: 实现检测函数和装饰器**

在 `gcloud/apigw/decorators.py` 中 `is_mcp_request` 函数后面添加：

`is_ai_platform_request(request)`:
- 从 `settings.APIGW_AI_PLATFORM_HEADER`（默认 `HTTP_X_BKAPI_AI_PLATFORM`）读取 Header
- strip 后返回，空则返回空字符串

`mark_ai_platform` 装饰器:
- 调用 `is_ai_platform_request()` 结果赋给 `request.ai_platform`
- 从 `settings.APIGW_AI_SKILL_HEADER`（默认 `HTTP_X_BKAPI_AI_SKILL`）读取 Header，strip 后赋给 `request.ai_skill`

**Step 4: 运行测试，确认通过**

```
python -m pytest gcloud/tests/apigw/views/test_decorators.py -v
```

Expected: PASS

**Step 5: Commit**

```
git add gcloud/apigw/decorators.py gcloud/tests/apigw/views/test_decorators.py
git commit -m "feat: 新增 AI 平台请求检测函数和装饰器"
```

---

### Task 3: TaskCreateMethod 枚举扩展

**Files:**
- Modify: `gcloud/constants.py`

**Step 1: 添加枚举值**

在 `TaskCreateMethod` 枚举中 `MCP = "mcp"` 之后添加 `OPENCLAW = "openclaw"`。

在 `TASK_CREATE_METHOD` 列表中 `MCP` 条目之后添加 `(TaskCreateMethod.OPENCLAW.value, _("OpenClaw"))`。

**Step 2: Commit**

```
git add gcloud/constants.py
git commit -m "feat: TaskCreateMethod 枚举新增 OPENCLAW"
```

---

### Task 4: create_task 视图 create_method 优先级

**Files:**
- Modify: `gcloud/apigw/views/create_task.py:62-74`（装饰器链）
- Modify: `gcloud/apigw/views/create_task.py:196-200`（create_method 判断）
- Modify: `gcloud/tests/apigw/views/test_create_task.py`

**Step 1: 编写测试**

在 `CreateTaskAPITest` 类中新增 `test_create_task__openclaw_create_method` 方法：
- 发送 POST 请求时附带 `HTTP_X_BKAPI_AI_PLATFORM="openclaw"` 和 `HTTP_X_BKAPI_AI_SKILL="sops-task-execution"`
- 断言 `TaskFlowInstance.objects.create` 调用时 `create_method` 参数为 `TaskCreateMethod.OPENCLAW.value`

**Step 2: 运行测试，确认失败**

```
python -m pytest gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task__openclaw_create_method -v
```

Expected: FAIL（create_method 仍为 api）

**Step 3: 修改装饰器链**

在 `create_task.py` 的装饰器链中，`@mark_request_whether_is_trust` 之后添加 `@mark_ai_platform`。

在文件头部添加 import: `from gcloud.apigw.decorators import mark_ai_platform`

**Step 4: 修改 create_method 判断逻辑**

将 create_task.py 第 196-200 行的判断改为三级优先级：

```python
if getattr(request, "ai_platform", ""):
    create_method = TaskCreateMethod.OPENCLAW.value
elif getattr(request, "is_mcp_request", False):
    create_method = TaskCreateMethod.MCP.value
else:
    create_method = TaskCreateMethod.API.value
```

**Step 5: 运行测试，确认通过**

```
python -m pytest gcloud/tests/apigw/views/test_create_task.py -v
```

Expected: ALL PASS

**Step 6: Commit**

```
git add gcloud/apigw/views/create_task.py gcloud/tests/apigw/views/test_create_task.py
git commit -m "feat: create_task 支持 OpenClaw 来源识别"
```

---

### Task 5: 其他写操作视图添加 mark_ai_platform

**Files:**
- Modify: `gcloud/apigw/views/start_task.py`
- Modify: `gcloud/apigw/views/operate_task.py`
- Modify: `gcloud/apigw/views/operate_node.py`
- Modify: `gcloud/apigw/views/node_callback.py`
- Modify: `gcloud/apigw/views/create_and_start_task.py`

**Step 1:** 为每个视图文件添加 import 和 `@mark_ai_platform` 装饰器，位于 `@mark_request_whether_is_trust` 之后。

对于 `create_and_start_task.py`（如包含 create_method 判断），同样应用 Task 4 Step 4 的三级优先级逻辑。

**Step 2: 运行现有测试**

```
python -m pytest gcloud/tests/apigw/views/ -v
```

Expected: ALL PASS

**Step 3: Commit**

```
git add gcloud/apigw/views/
git commit -m "feat: 所有写操作 apigw view 添加 mark_ai_platform 装饰器"
```

---

### Task 6: Skill 编写规范文档

**Files:**
- Create: `docs/specs/openclaw-sops-skill-convention.md`

**Step 1:** 编写规范文档，内容包含：

- 标题：OpenClaw SOPS Skill 编写规范
- AI 来源标识章节（标注为"必须"）：
  - Header 表格：`X-Bkapi-Ai-Platform`（值 `openclaw`，必传）和 `X-Bkapi-Ai-Skill`（值为 skill 名称，必传）
  - HTTP 请求示例
  - 说明：不传不影响功能但无法统计、值固定为 openclaw

**Step 2: Commit**

```
mkdir -p docs/specs
git add docs/specs/openclaw-sops-skill-convention.md
git commit -m "docs: 新增 OpenClaw SOPS Skill 编写规范"
```

---

## Phase 2：OTel Span 属性注入 + 查询 API trace 覆盖

### Task 7: trace_view 扩展

**Files:**
- Modify: `gcloud/core/trace.py:131-160`

**Step 1:** 在 `trace_view` 的 `_wrapped_view` 内部，attr_keys 循环之后、`start_trace` 之前，添加 AI 来源属性注入：

- 检查 `request.ai_platform` 非空时，向 attributes 添加：`ai_platform`、`ai_skill`、`ai_username`（来自 request.user.username）、`ai_app_code`（来自 request.app）

**Step 2: 运行现有测试**

```
python -m pytest gcloud/tests/ -v -k "trace or apigw"
```

Expected: ALL PASS

**Step 3: Commit**

```
git add gcloud/core/trace.py
git commit -m "feat: trace_view 自动注入 AI 平台来源属性到 OTel Span"
```

---

### Task 8: 查询类 API 添加 mark_ai_platform + trace_view

**Files:**
- Modify: `gcloud/apigw/views/get_template_list.py`
- Modify: `gcloud/apigw/views/get_template_info.py`
- Modify: `gcloud/apigw/views/get_task_status.py`
- Modify: `gcloud/apigw/views/get_task_detail.py`
- Modify: `gcloud/apigw/views/get_task_list.py`
- Modify: `gcloud/apigw/views/get_task_node_detail.py`

**Step 1:** 在每个文件装饰器链中 `@project_inject` 之后添加 `@mark_ai_platform` 和 `@trace_view(attr_keys=["project_id"], call_from=CallFrom.APIGW.value)`，以及对应 import。

**Step 2: 运行现有测试**

```
python -m pytest gcloud/tests/apigw/views/ -v
```

Expected: ALL PASS

**Step 3: Commit**

```
git add gcloud/apigw/views/
git commit -m "feat: 查询类 apigw view 添加 AI 平台识别和 trace 覆盖"
```

---

## 验证检查清单

1. `python -m pytest gcloud/tests/apigw/ -v` 全部通过
2. `is_ai_platform_request()` 在无 Header 时返回空字符串
3. `create_task` 传入 `X-Bkapi-Ai-Platform: openclaw` 后 `create_method` 为 `openclaw`
4. 不传 AI Header 时，所有现有行为不受影响
5. `docs/specs/openclaw-sops-skill-convention.md` 内容完整
