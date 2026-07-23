# 卡住流程治理控制台 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 bk-sops `/admin/` 下新增超管专用的「卡住流程治理控制台」,把 bamboo-engine 的 `DiagnosticCase` 关联回具体任务/模板/业务/节点并支持状态管理与按 case 跑诊断/恢复动作。

**Architecture:** 纯 bk-sops 侧改动(不改 bamboo-engine)。后端在 `gcloud/contrib/admin` 增加反向映射适配层 + 状态写适配层 + 3 个新视图,并增强现有列表/详情视图;前端用一个独立 Django 模板 + 原生 JS(方案 A),调用 JSON 端点。所有对 `pipeline.contrib.diagnostics` 的引用均 `try/except ImportError` 降级。

**Tech Stack:** Django 2.2 (Python 3.6.15)、`pipeline.contrib.diagnostics`(bamboo-pipeline 3.24.13 / bamboo-engine 2.6.5)、原生 JS + fetch,测试用 `django.test.TestCase` + `RequestFactory` + `unittest.mock`。

## Global Constraints

- 设计依据:`docs/specs/2026-07-23-stuck-governance-console-design.md`。
- 仅平台超管、全局可见:读端点 `@check_is_superuser()` + `@iam_intercept(AdminViewViewInterceptor())`;写/动作端点 `@check_is_superuser()` + `@iam_intercept(AdminEditViewInterceptor())`。
- 病历状态只有三态:`DiagnosticCase.STATUS_OPEN="open"` / `STATUS_RESOLVED="resolved"` / `STATUS_IGNORED="ignored"`。
- `DiagnosticCase` 有 `unique_together=(("root_pipeline_id","node_id","stuck_type","status"),)`:改状态**必须走"合并+删重复"**,禁止裸 `update(status=...)`。
- 不新增 DB 字段/迁移;不改 bamboo-engine;不接主 Vue SPA。
- 所有对 `pipeline.contrib.diagnostics` 的引用必须 `try/except ImportError` 降级,引擎包缺失时返回可读错误而非 500。
- 反向映射数据源:`TaskFlowInstance.objects.filter(pipeline_instance__instance_id__in=ids)`(`pipeline_instance.instance_id == root_pipeline_id`)。
- 任务 URL 形态:`settings.BK_SOPS_HOST.rstrip("/") + "/taskflow/execute/{project_id}/?instance_id={task_id}"`。
- 提交信息遵循 `.ai/rules/commit-message-convention.mdc`,统一带 `--bug=1010131351157180998`。分支 `feat/stuck-governance-console`,push 到 `origin`(fork)。

---

## File Structure

- Create `gcloud/contrib/admin/diagnostics/task_mapping.py` — 反向映射:`root_pipeline_id → 任务摘要`(批量/单条)、`node_id → 节点名`。
- Create `gcloud/contrib/admin/diagnostics/cases_admin.py` — `set_case_status()`:状态写 + 合并去重 + 审计。
- Modify `gcloud/contrib/admin/views/diagnostics.py` — 增强 `diagnostic_case_list`/`diagnostic_case_detail`;新增 `diagnostic_case_status`/`diagnostic_case_action`/`diagnostic_board`。
- Modify `gcloud/contrib/admin/urls.py` — 新增 `board/`、`cases/status/`、`cases/action/` 路由。
- Create `gcloud/contrib/admin/templates/diagnostics/cases.html` — 控制台页面。
- Modify `gcloud/contrib/admin/templates/diagnostics/task_diagnostic.html` — 加控制台互链。
- Create `gcloud/tests/contrib/admin/diagnostics/test_task_mapping.py`
- Create `gcloud/tests/contrib/admin/diagnostics/test_cases_admin.py`
- Create `gcloud/tests/contrib/admin/diagnostics/test_case_admin_views.py`

测试运行环境(每个测试步骤统一前缀,worktree 根目录已备好 `local_settings.py`(SQLite + `BK_IAM_SKIP=1`)与 `pytest.ini`):

```bash
# 在 worktree 根目录 /Users/dengyh/Projects/bk-sops/.worktrees/stuck-governance-console 下
export PYTHONPATH=/tmp/rc-pkg          # 提供 pipeline.contrib.diagnostics(bamboo-pipeline 3.24.13rc0)
export BK_ENV=development              # 使 settings 走 config.dev(会 from local_settings import *)
python manage.py test gcloud.tests.contrib.admin.diagnostics.<模块> -v 2
```

> 注:默认 `DJANGO_SETTINGS_MODULE=settings` → `config.dev` → `from local_settings import *`(SQLite)。
> 运行时出现的 `near "show": syntax error` 来自 data_migration 工具在 SQLite 上执行 MySQL 语句,属**无害告警**,
> 不影响测试结果。若诊断包不可用,相关测试通过 `skipUnless` 自动跳过。

---

## Task 1: 反向映射适配层 `task_mapping.py`

**Files:**
- Create: `gcloud/contrib/admin/diagnostics/task_mapping.py`
- Test: `gcloud/tests/contrib/admin/diagnostics/test_task_mapping.py`

**Interfaces:**
- Produces:
  - `resolve_task_summaries(root_pipeline_ids: Iterable[str]) -> Dict[str, dict]`
    返回 `{root_pipeline_id: summary}`,summary 形如
    `{"task_id": int, "task_name": str, "project_id": int|None, "project_name": str|None,
      "template_id": str, "executor": str, "create_time": str|None, "task_url": str}`。
    查不到的 root_pipeline_id 不出现在返回字典里。
  - `resolve_task_summary(root_pipeline_id: str) -> Optional[dict]`(单条,复用批量)。
  - `resolve_node_name(root_pipeline_id: str, node_id: str) -> str`(找不到返回 `""`,失败降级 `""`)。

- [ ] **Step 1: 写失败测试**

Create `gcloud/tests/contrib/admin/diagnostics/test_task_mapping.py`:

```python
# -*- coding: utf-8 -*-
from datetime import datetime
from unittest import mock

from django.test import TestCase

from gcloud.contrib.admin.diagnostics import task_mapping


def _fake_task(root_id, task_id, name, proj_id, proj_name, executor, template_id):
    task = mock.MagicMock()
    task.id = task_id
    task.template_id = template_id
    task.pipeline_instance.instance_id = root_id
    task.pipeline_instance.name = name
    task.pipeline_instance.executor = executor
    task.pipeline_instance.create_time = datetime(2026, 7, 23, 10, 0, 0)
    task.project.id = proj_id
    task.project.name = proj_name
    return task


class ResolveTaskSummariesTest(TestCase):
    def test_batch_maps_hits_and_skips_misses(self):
        fake = _fake_task("root-1", 101, "任务A", 7, "业务X", "neo", "55")
        qs = mock.MagicMock()
        qs.select_related.return_value = [fake]
        with mock.patch.object(task_mapping, "TaskFlowInstance") as m_tf, mock.patch.object(
            task_mapping, "settings"
        ) as m_settings:
            m_settings.BK_SOPS_HOST = "https://sops.example.com/"
            m_tf.objects.filter.return_value = qs
            result = task_mapping.resolve_task_summaries(["root-1", "root-miss", ""])

        m_tf.objects.filter.assert_called_once_with(pipeline_instance__instance_id__in=mock.ANY)
        self.assertIn("root-1", result)
        self.assertNotIn("root-miss", result)
        summary = result["root-1"]
        self.assertEqual(summary["task_id"], 101)
        self.assertEqual(summary["task_name"], "任务A")
        self.assertEqual(summary["project_id"], 7)
        self.assertEqual(summary["project_name"], "业务X")
        self.assertEqual(summary["executor"], "neo")
        self.assertEqual(summary["template_id"], "55")
        self.assertEqual(summary["task_url"], "https://sops.example.com/taskflow/execute/7/?instance_id=101")

    def test_empty_input_returns_empty(self):
        self.assertEqual(task_mapping.resolve_task_summaries([]), {})

    def test_query_failure_degrades_to_empty(self):
        with mock.patch.object(task_mapping, "TaskFlowInstance") as m_tf:
            m_tf.objects.filter.side_effect = RuntimeError("db down")
            self.assertEqual(task_mapping.resolve_task_summaries(["root-1"]), {})

    def test_single_summary_uses_batch(self):
        with mock.patch.object(task_mapping, "resolve_task_summaries", return_value={"root-1": {"task_id": 1}}):
            self.assertEqual(task_mapping.resolve_task_summary("root-1"), {"task_id": 1})
            self.assertIsNone(task_mapping.resolve_task_summary("root-x"))


class ResolveNodeNameTest(TestCase):
    def _patch_tree(self, tree):
        pi = mock.MagicMock()
        pi.execution_data = tree
        m = mock.MagicMock()
        m.objects.filter.return_value.first.return_value = pi
        return mock.patch.object(task_mapping, "PipelineInstance", m)

    def test_finds_top_level_activity_name(self):
        tree = {"activities": {"act-1": {"name": "HTTP 请求", "type": "ServiceActivity"}}}
        with self._patch_tree(tree):
            self.assertEqual(task_mapping.resolve_node_name("root-1", "act-1"), "HTTP 请求")

    def test_finds_name_in_subprocess(self):
        tree = {
            "activities": {
                "sub-1": {
                    "name": "子流程",
                    "type": "SubProcess",
                    "pipeline": {"activities": {"act-2": {"name": "内层节点", "type": "ServiceActivity"}}},
                }
            }
        }
        with self._patch_tree(tree):
            self.assertEqual(task_mapping.resolve_node_name("root-1", "act-2"), "内层节点")

    def test_missing_node_returns_empty(self):
        tree = {"activities": {"act-1": {"name": "X", "type": "ServiceActivity"}}}
        with self._patch_tree(tree):
            self.assertEqual(task_mapping.resolve_node_name("root-1", "nope"), "")

    def test_no_instance_returns_empty(self):
        m = mock.MagicMock()
        m.objects.filter.return_value.first.return_value = None
        with mock.patch.object(task_mapping, "PipelineInstance", m):
            self.assertEqual(task_mapping.resolve_node_name("root-x", "act-1"), "")
```

- [ ] **Step 2: 运行确认失败**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_task_mapping -v 2`
Expected: FAIL(`ImportError`/`AttributeError`,`task_mapping` 尚未实现)。

- [ ] **Step 3: 实现 `task_mapping.py`**

Create `gcloud/contrib/admin/diagnostics/task_mapping.py`:

```python
# -*- coding: utf-8 -*-
"""
Reverse-mapping helpers: turn bamboo-engine ids (root_pipeline_id / node_id)
back into bk-sops task context that admins can understand.
"""

import logging

from django.conf import settings

from pipeline.models import PipelineInstance

from gcloud.taskflow3.models import TaskFlowInstance

logger = logging.getLogger("root")


def _format_dt(dt):
    try:
        return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None
    except Exception:  # noqa
        return None


def _task_url(project_id, task_id):
    host = getattr(settings, "BK_SOPS_HOST", "") or ""
    return "{}/taskflow/execute/{}/?instance_id={}".format(host.rstrip("/"), project_id, task_id)


def _summarize_task(task):
    pi = task.pipeline_instance
    project = getattr(task, "project", None)
    project_id = getattr(project, "id", None)
    project_name = getattr(project, "name", None)
    return {
        "task_id": task.id,
        "task_name": pi.name,
        "project_id": project_id,
        "project_name": project_name,
        "template_id": task.template_id,
        "executor": pi.executor,
        "create_time": _format_dt(pi.create_time),
        "task_url": _task_url(project_id, task.id) if project_id is not None else "",
    }


def resolve_task_summaries(root_pipeline_ids):
    """Batch map root_pipeline_id -> bk-sops task summary. Missing ids are omitted."""
    ids = [rid for rid in set(root_pipeline_ids or []) if rid]
    result = {}
    if not ids:
        return result
    try:
        qs = TaskFlowInstance.objects.filter(pipeline_instance__instance_id__in=ids).select_related(
            "pipeline_instance", "project"
        )
        for task in qs:
            pi = task.pipeline_instance
            if pi is None:
                continue
            try:
                result[pi.instance_id] = _summarize_task(task)
            except Exception:  # noqa - one bad row must not break the whole page
                logger.exception("[diagnostics] summarize task failed: task_id=%s", getattr(task, "id", None))
    except Exception:  # noqa - mapping is best-effort, never block the page
        logger.exception("[diagnostics] resolve_task_summaries failed")
        return result
    return result


def resolve_task_summary(root_pipeline_id):
    return resolve_task_summaries([root_pipeline_id]).get(root_pipeline_id)


def _find_node_name(tree, node_id):
    if not isinstance(tree, dict):
        return ""
    activities = tree.get("activities") or {}
    for nid, info in activities.items():
        if not isinstance(info, dict):
            continue
        if nid == node_id:
            return info.get("name") or ""
        if info.get("type") == "SubProcess":
            name = _find_node_name(info.get("pipeline"), node_id)
            if name:
                return name
    return ""


def resolve_node_name(root_pipeline_id, node_id):
    if not root_pipeline_id or not node_id:
        return ""
    try:
        pi = PipelineInstance.objects.filter(instance_id=root_pipeline_id).first()
        if pi is None:
            return ""
        return _find_node_name(pi.execution_data, node_id)
    except Exception:  # noqa - best-effort
        logger.exception("[diagnostics] resolve_node_name failed: root=%s node=%s", root_pipeline_id, node_id)
        return ""
```

- [ ] **Step 4: 运行确认通过**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_task_mapping -v 2`
Expected: PASS(8 项)。

- [ ] **Step 5: 提交**

```bash
git add gcloud/contrib/admin/diagnostics/task_mapping.py gcloud/tests/contrib/admin/diagnostics/test_task_mapping.py
git commit -m "feat: 诊断控制台反向映射适配层(任务上下文+节点名) --bug=1010131351157180998"
```

---

## Task 2: 列表视图批量反向映射增强

**Files:**
- Modify: `gcloud/contrib/admin/views/diagnostics.py`(`diagnostic_case_list`)
- Test: `gcloud/tests/contrib/admin/diagnostics/test_case_admin_views.py`(新建,本任务先加列表增强用例)

**Interfaces:**
- Consumes: `task_mapping.resolve_task_summaries`(Task 1)。
- Produces: `GET /admin/diagnostics/cases/` 每个 item 新增键 `task`(dict 或 `None`)。

- [ ] **Step 1: 写失败测试**

Create `gcloud/tests/contrib/admin/diagnostics/test_case_admin_views.py`:

```python
# -*- coding: utf-8 -*-
import json
from unittest import mock, skipUnless

from django.test import RequestFactory, TestCase

try:
    import pipeline.contrib.diagnostics  # noqa: F401

    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False

_VIEW_INTERCEPTOR = "gcloud.iam_auth.view_interceptors.admin.AdminViewViewInterceptor.process"
_EDIT_INTERCEPTOR = "gcloud.iam_auth.view_interceptors.admin.AdminEditViewInterceptor.process"


def _superuser_get(path, **params):
    request = RequestFactory().get(path, data=params)
    request.user = mock.MagicMock(is_superuser=True, username="admin")
    return request


def _superuser_post(path, body):
    request = RequestFactory().post(path, data=json.dumps(body), content_type="application/json")
    request.user = mock.MagicMock(is_superuser=True, username="admin")
    return request


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.13)")
class CaseListEnrichmentTest(TestCase):
    def setUp(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        self.DiagnosticCase = DiagnosticCase
        self.case = DiagnosticCase.objects.create(
            root_pipeline_id="root-1",
            node_id="n1",
            stuck_type="stalled_no_progress",
            severity=DiagnosticCase.SEVERITY_WARNING,
            status=DiagnosticCase.STATUS_OPEN,
            evidence={"stall_seconds": 120},
        )

    def test_list_items_carry_task_summary(self):
        from gcloud.contrib.admin.views import diagnostics

        summaries = {"root-1": {"task_id": 9, "task_name": "任务A", "task_url": "u", "project_name": "业务X"}}
        with mock.patch(_VIEW_INTERCEPTOR), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.resolve_task_summaries", return_value=summaries
        ):
            resp = diagnostics.diagnostic_case_list(_superuser_get("/admin/diagnostics/cases/"))

        item = json.loads(resp.content)["data"]["items"][0]
        self.assertEqual(item["task"]["task_id"], 9)
        self.assertEqual(item["task"]["task_name"], "任务A")

    def test_list_item_task_none_when_unmapped(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_VIEW_INTERCEPTOR), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.resolve_task_summaries", return_value={}
        ):
            resp = diagnostics.diagnostic_case_list(_superuser_get("/admin/diagnostics/cases/"))

        item = json.loads(resp.content)["data"]["items"][0]
        self.assertIsNone(item["task"])
```

- [ ] **Step 2: 运行确认失败**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_case_admin_views.CaseListEnrichmentTest -v 2`
Expected: FAIL(item 无 `task` 键 / `resolve_task_summaries` 未导入)。

- [ ] **Step 3: 修改 `diagnostic_case_list`**

在 `gcloud/contrib/admin/views/diagnostics.py` 顶部 import 区加入:

```python
from gcloud.contrib.admin.diagnostics.task_mapping import (
    resolve_node_name,
    resolve_task_summaries,
    resolve_task_summary,
)
```

把 `diagnostic_case_list` 里构造 `data` 的部分改为(在 `page_obj` 之后):

```python
    cases = list(page_obj.object_list)
    summaries = resolve_task_summaries([c.root_pipeline_id for c in cases])
    items = []
    for case in cases:
        item = _serialize_case(case)
        item["task"] = summaries.get(case.root_pipeline_id)
        items.append(item)
    data = {
        "total": paginator.count,
        "page": page_obj.number,
        "page_size": page_size,
        "items": items,
    }
    return JsonResponse({"result": True, "data": data})
```

- [ ] **Step 4: 运行确认通过**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_case_admin_views.CaseListEnrichmentTest gcloud.tests.contrib.admin.diagnostics.test_case_list_view -v 2`
Expected: PASS(新用例 + 原 `test_case_list_view` 回归全过)。

- [ ] **Step 5: 提交**

```bash
git add gcloud/contrib/admin/views/diagnostics.py gcloud/tests/contrib/admin/diagnostics/test_case_admin_views.py
git commit -m "feat: 诊断案例列表补充任务上下文(批量反向映射) --bug=1010131351157180998"
```

---

## Task 3: 详情视图增强(任务上下文 + 节点名 + 审计历史)

**Files:**
- Modify: `gcloud/contrib/admin/views/diagnostics.py`(`diagnostic_case_detail`)
- Test: `gcloud/tests/contrib/admin/diagnostics/test_case_admin_views.py`(追加)

**Interfaces:**
- Consumes: `task_mapping.resolve_task_summary` / `resolve_node_name`(Task 1);`DiagnosticOperationAudit`。
- Produces: 详情 JSON 新增键 `task`(dict|None)、`node_name`(str)、`audit_history`(list)。

- [ ] **Step 1: 写失败测试**

在 `test_case_admin_views.py` 追加:

```python
@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.13)")
class CaseDetailEnrichmentTest(TestCase):
    def setUp(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase, DiagnosticOperationAudit

        self.DiagnosticCase = DiagnosticCase
        self.case = DiagnosticCase.objects.create(
            root_pipeline_id="root-1",
            node_id="n1",
            stuck_type="stalled_no_progress",
            severity=DiagnosticCase.SEVERITY_WARNING,
            status=DiagnosticCase.STATUS_OPEN,
            evidence={"stall_seconds": 120},
        )
        DiagnosticOperationAudit.objects.create(
            case=self.case, operation_type="set_status:resolved", operator="admin"
        )

    def test_detail_has_task_node_name_and_audit(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_VIEW_INTERCEPTOR), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.resolve_task_summary",
            return_value={"task_id": 9, "task_name": "任务A"},
        ), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.resolve_node_name", return_value="HTTP 请求"
        ):
            resp = diagnostics.diagnostic_case_detail(
                _superuser_get("/admin/diagnostics/cases/detail/", case_id=self.case.id)
            )

        data = json.loads(resp.content)["data"]
        self.assertEqual(data["task"]["task_id"], 9)
        self.assertEqual(data["node_name"], "HTTP 请求")
        self.assertEqual(len(data["audit_history"]), 1)
        self.assertEqual(data["audit_history"][0]["operation_type"], "set_status:resolved")
```

- [ ] **Step 2: 运行确认失败**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_case_admin_views.CaseDetailEnrichmentTest -v 2`
Expected: FAIL(详情缺 `task`/`node_name`/`audit_history`)。

- [ ] **Step 3: 修改 `diagnostic_case_detail`**

在 `gcloud/contrib/admin/views/diagnostics.py` 顶部 import 区补充(与现有 import 合并):

```python
def _audit_model():
    try:
        from pipeline.contrib.diagnostics.models import DiagnosticOperationAudit

        return DiagnosticOperationAudit
    except ImportError:
        return None


def _serialize_audit(audit):
    return {
        "id": audit.id,
        "operation_type": audit.operation_type,
        "operator": audit.operator,
        "mode": audit.mode,
        "risk_level": audit.risk_level,
        "result": audit.result,
        "created_at": audit.created_at.strftime("%Y-%m-%d %H:%M:%S") if audit.created_at else None,
    }
```

把 `diagnostic_case_detail` 里 `detail = _serialize_case(case)` 之后、`return` 之前补充:

```python
    detail["evidence"] = case.evidence
    detail["related_objects"] = case.related_objects
    detail["recommended_actions"] = case.recommended_actions
    detail["forbidden_actions"] = case.forbidden_actions
    detail["task"] = resolve_task_summary(case.root_pipeline_id)
    detail["node_name"] = resolve_node_name(case.root_pipeline_id, case.node_id)
    audit_model = _audit_model()
    if audit_model is not None:
        audits = audit_model.objects.filter(case_id=case.id).order_by("-created_at")[:50]
        detail["audit_history"] = [_serialize_audit(a) for a in audits]
    else:
        detail["audit_history"] = []
    return JsonResponse({"result": True, "data": detail})
```

> 注:上面前四行(`evidence`/`related_objects`/`recommended_actions`/`forbidden_actions`)是**已有代码**,保留不变,仅在其后追加 `task`/`node_name`/`audit_history` 逻辑。

- [ ] **Step 4: 运行确认通过**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_case_admin_views -v 2`
Expected: PASS(列表 + 详情增强全过)。

- [ ] **Step 5: 提交**

```bash
git add gcloud/contrib/admin/views/diagnostics.py gcloud/tests/contrib/admin/diagnostics/test_case_admin_views.py
git commit -m "feat: 诊断案例详情补充任务上下文/节点名/审计历史 --bug=1010131351157180998"
```

---

## Task 4: 状态写适配层 + 视图(合并去重 + 审计)

**Files:**
- Create: `gcloud/contrib/admin/diagnostics/cases_admin.py`
- Modify: `gcloud/contrib/admin/views/diagnostics.py`(新增 `diagnostic_case_status`)
- Modify: `gcloud/contrib/admin/urls.py`
- Test: `gcloud/tests/contrib/admin/diagnostics/test_cases_admin.py`

**Interfaces:**
- Produces:
  - `cases_admin.set_case_status(case_id, target_status, operator) -> dict`
    返回 `{"result": bool, "message"?: str, "data"?: {"id": int, "status": str, "merged": bool}}`。
  - `POST /admin/diagnostics/cases/status/`,body `{"case_id": int, "status": "open|resolved|ignored"}`。

- [ ] **Step 1: 写失败测试**

Create `gcloud/tests/contrib/admin/diagnostics/test_cases_admin.py`:

```python
# -*- coding: utf-8 -*-
from unittest import skipUnless

from django.test import TransactionTestCase

try:
    import pipeline.contrib.diagnostics  # noqa: F401

    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.13)")
class SetCaseStatusTest(TransactionTestCase):
    def setUp(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        self.DiagnosticCase = DiagnosticCase

    def _make(self, status, hit_count=1):
        return self.DiagnosticCase.objects.create(
            root_pipeline_id="root-1",
            node_id="n1",
            stuck_type="stalled_no_progress",
            severity=self.DiagnosticCase.SEVERITY_WARNING,
            status=status,
            hit_count=hit_count,
        )

    def test_open_to_resolved_normal(self):
        from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status
        from pipeline.contrib.diagnostics.models import DiagnosticOperationAudit

        case = self._make(self.DiagnosticCase.STATUS_OPEN)
        res = set_case_status(case.id, self.DiagnosticCase.STATUS_RESOLVED, "admin")

        self.assertTrue(res["result"])
        self.assertFalse(res["data"]["merged"])
        case.refresh_from_db()
        self.assertEqual(case.status, self.DiagnosticCase.STATUS_RESOLVED)
        self.assertEqual(DiagnosticOperationAudit.objects.filter(case_id=case.id).count(), 1)

    def test_merge_when_twin_exists_no_integrity_error(self):
        from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

        twin = self._make(self.DiagnosticCase.STATUS_RESOLVED, hit_count=2)
        open_case = self._make(self.DiagnosticCase.STATUS_OPEN, hit_count=5)

        res = set_case_status(open_case.id, self.DiagnosticCase.STATUS_RESOLVED, "admin")

        self.assertTrue(res["result"])
        self.assertTrue(res["data"]["merged"])
        self.assertEqual(res["data"]["id"], twin.id)
        # 原 open case 已删除,孪生 case 命中数取较大值
        self.assertFalse(self.DiagnosticCase.objects.filter(id=open_case.id).exists())
        twin.refresh_from_db()
        self.assertEqual(twin.hit_count, 5)

    def test_noop_when_same_status(self):
        from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

        case = self._make(self.DiagnosticCase.STATUS_OPEN)
        res = set_case_status(case.id, self.DiagnosticCase.STATUS_OPEN, "admin")
        self.assertTrue(res["result"])
        self.assertFalse(res["data"]["merged"])

    def test_invalid_status_rejected(self):
        from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

        case = self._make(self.DiagnosticCase.STATUS_OPEN)
        res = set_case_status(case.id, "bogus", "admin")
        self.assertFalse(res["result"])

    def test_missing_case(self):
        from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

        res = set_case_status(999999, self.DiagnosticCase.STATUS_RESOLVED, "admin")
        self.assertFalse(res["result"])
```

- [ ] **Step 2: 运行确认失败**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_cases_admin -v 2`
Expected: FAIL(`cases_admin` 未实现)。

- [ ] **Step 3: 实现 `cases_admin.py`**

Create `gcloud/contrib/admin/diagnostics/cases_admin.py`:

```python
# -*- coding: utf-8 -*-
"""
Admin-side write operations for diagnostic cases.

Status change must honor DiagnosticCase.unique_together
(root_pipeline_id, node_id, stuck_type, status): if a twin already holds the
target status, merge the recurrence into it and drop the duplicate row instead
of a naive update() that would raise IntegrityError.
"""

import logging

from django.db import transaction

logger = logging.getLogger("root")


def _models():
    from pipeline.contrib.diagnostics.models import DiagnosticCase, DiagnosticOperationAudit

    return DiagnosticCase, DiagnosticOperationAudit


def set_case_status(case_id, target_status, operator):
    try:
        DiagnosticCase, DiagnosticOperationAudit = _models()
    except ImportError as err:
        return {"result": False, "message": "pipeline diagnostics is unavailable: {}".format(err)}

    valid = {DiagnosticCase.STATUS_OPEN, DiagnosticCase.STATUS_RESOLVED, DiagnosticCase.STATUS_IGNORED}
    if target_status not in valid:
        return {"result": False, "message": "invalid status: {}".format(target_status)}

    with transaction.atomic():
        case = DiagnosticCase.objects.select_for_update().filter(id=case_id).first()
        if case is None:
            return {"result": False, "message": "case not found"}

        if case.status == target_status:
            return {"result": True, "data": {"id": case.id, "status": case.status, "merged": False}}

        twin = (
            DiagnosticCase.objects.select_for_update()
            .filter(
                root_pipeline_id=case.root_pipeline_id,
                node_id=case.node_id,
                stuck_type=case.stuck_type,
                status=target_status,
            )
            .exclude(id=case.id)
            .first()
        )

        if twin is not None:
            twin.hit_count = max(twin.hit_count, case.hit_count)
            if case.last_seen_at and (not twin.last_seen_at or case.last_seen_at > twin.last_seen_at):
                twin.last_seen_at = case.last_seen_at
            twin.save(update_fields=["hit_count", "last_seen_at", "updated_at"])
            surviving = twin
            case.delete()
            merged = True
        else:
            case.status = target_status
            case.save(update_fields=["status", "updated_at"])
            surviving = case
            merged = False

        DiagnosticOperationAudit.objects.create(
            case=surviving,
            operation_type="set_status:{}".format(target_status),
            operator=operator or "",
            mode=DiagnosticOperationAudit.MODE_APPLY,
            risk_level=DiagnosticOperationAudit.RISK_LEVEL_LOW,
            result={"status": target_status, "merged": merged},
        )

    return {"result": True, "data": {"id": surviving.id, "status": surviving.status, "merged": merged}}
```

- [ ] **Step 4: 新增视图 + 路由**

在 `gcloud/contrib/admin/views/diagnostics.py` 追加:

```python
@require_POST
@check_is_superuser()
@iam_intercept(AdminEditViewInterceptor())
def diagnostic_case_status(request):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except ValueError:
        return JsonResponse({"result": False, "message": "invalid json body"})

    case_id = body.get("case_id")
    status = body.get("status")
    if not case_id or not status:
        return JsonResponse({"result": False, "message": "case_id and status are required"})

    from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

    return JsonResponse(set_case_status(case_id, status, request.user.username))
```

在 `gcloud/contrib/admin/urls.py` 的 diagnostics 路由块追加(紧邻 `cases/detail/`):

```python
    url(r"^diagnostics/cases/status/$", diagnostics.diagnostic_case_status),
```

- [ ] **Step 5: 运行确认通过**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_cases_admin -v 2`
Expected: PASS(5 项,含孪生合并不报 IntegrityError)。

- [ ] **Step 6: 提交**

```bash
git add gcloud/contrib/admin/diagnostics/cases_admin.py gcloud/contrib/admin/views/diagnostics.py gcloud/contrib/admin/urls.py gcloud/tests/contrib/admin/diagnostics/test_cases_admin.py
git commit -m "feat: 诊断案例状态管理(合并去重+审计)与写端点 --bug=1010131351157180998"
```

---

## Task 5: 按 case 跑诊断/恢复动作端点

**Files:**
- Modify: `gcloud/contrib/admin/views/diagnostics.py`(新增 `diagnostic_case_action`)
- Modify: `gcloud/contrib/admin/urls.py`
- Test: `gcloud/tests/contrib/admin/diagnostics/test_case_admin_views.py`(追加)

**Interfaces:**
- Consumes: `gcloud.contrib.admin.diagnostics.actions.run_task_action`(已存在,签名
  `run_task_action(task_id, node_id, action, operator, mode="dry_run", **kwargs)`)。
- Produces: `POST /admin/diagnostics/cases/action/`,body
  `{"case_id": int, "action": str, "mode": "dry_run|apply", "schedule_id"?, "callback_data_id"?}`。

- [ ] **Step 1: 写失败测试**

在 `test_case_admin_views.py` 追加:

```python
@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.13)")
class CaseActionViewTest(TestCase):
    def setUp(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        self.case = DiagnosticCase.objects.create(
            root_pipeline_id="root-1",
            node_id="n1",
            stuck_type="ack_not_converged",
            severity=DiagnosticCase.SEVERITY_WARNING,
            status=DiagnosticCase.STATUS_OPEN,
            evidence={"schedule_id": 555},
        )

    def test_action_dispatches_with_case_context(self):
        from gcloud.contrib.admin.views import diagnostics

        captured = {}

        def _fake_run(**kwargs):
            captured.update(kwargs)
            return {"result": True, "data": {"preview": "ok"}}

        with mock.patch(_EDIT_INTERCEPTOR), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.run_task_action", side_effect=_fake_run
        ):
            resp = diagnostics.diagnostic_case_action(
                _superuser_post(
                    "/admin/diagnostics/cases/action/",
                    {"case_id": self.case.id, "action": "resend_schedule", "mode": "dry_run"},
                )
            )

        body = json.loads(resp.content)
        self.assertTrue(body["result"])
        self.assertEqual(captured["action"], "resend_schedule")
        self.assertEqual(captured["node_id"], "n1")
        self.assertEqual(captured["mode"], "dry_run")
        self.assertEqual(captured["operator"], "admin")
        # schedule_id 从 evidence 兜底
        self.assertEqual(captured["schedule_id"], 555)
        self.assertEqual(captured["root_pipeline_id"], "root-1")

    def test_action_missing_case(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_EDIT_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_action(
                _superuser_post("/admin/diagnostics/cases/action/", {"case_id": 999999, "action": "resend_schedule"})
            )
        self.assertFalse(json.loads(resp.content)["result"])

    def test_action_forbidden_for_non_superuser(self):
        from gcloud.contrib.admin.views import diagnostics

        req = _superuser_post("/admin/diagnostics/cases/action/", {"case_id": self.case.id, "action": "resend_schedule"})
        req.user = mock.MagicMock(is_superuser=False, username="normal")
        with mock.patch(_EDIT_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_action(req)
        self.assertEqual(resp.status_code, 403)
```

- [ ] **Step 2: 运行确认失败**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_case_admin_views.CaseActionViewTest -v 2`
Expected: FAIL(`diagnostic_case_action` 未实现)。

- [ ] **Step 3: 实现视图 + 路由**

在 `gcloud/contrib/admin/views/diagnostics.py` 顶部 import 区加入:

```python
from gcloud.contrib.admin.diagnostics.actions import run_task_action
```

追加视图:

```python
@require_POST
@check_is_superuser()
@iam_intercept(AdminEditViewInterceptor())
def diagnostic_case_action(request):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except ValueError:
        return JsonResponse({"result": False, "message": "invalid json body", "blockers": ["invalid json body"]})

    model, message = _diagnostic_case_model()
    if model is None:
        return JsonResponse({"result": False, "message": message, "blockers": [message]})

    case_id = body.get("case_id")
    action = body.get("action")
    mode = body.get("mode", "dry_run")
    if not case_id or not action:
        return JsonResponse({"result": False, "message": "case_id and action are required"})

    case = model.objects.filter(id=case_id).first()
    if case is None:
        return JsonResponse({"result": False, "message": "case not found"})

    evidence = case.evidence or {}
    related = case.related_objects or {}
    action_kwargs = {"root_pipeline_id": case.root_pipeline_id}
    schedule_id = body.get("schedule_id") or evidence.get("schedule_id") or related.get("schedule_id")
    callback_data_id = body.get("callback_data_id") or evidence.get("callback_data_id") or related.get("callback_data_id")
    if schedule_id is not None:
        action_kwargs["schedule_id"] = schedule_id
    if callback_data_id is not None:
        action_kwargs["callback_data_id"] = callback_data_id

    result = run_task_action(
        task_id=None,
        node_id=case.node_id,
        action=action,
        operator=request.user.username,
        mode=mode,
        **action_kwargs,
    )
    return JsonResponse(result)
```

在 `gcloud/contrib/admin/urls.py` 追加:

```python
    url(r"^diagnostics/cases/action/$", diagnostics.diagnostic_case_action),
```

- [ ] **Step 4: 运行确认通过**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_case_admin_views.CaseActionViewTest -v 2`
Expected: PASS(3 项)。

- [ ] **Step 5: 提交**

```bash
git add gcloud/contrib/admin/views/diagnostics.py gcloud/contrib/admin/urls.py gcloud/tests/contrib/admin/diagnostics/test_case_admin_views.py
git commit -m "feat: 诊断案例按 case 跑诊断/恢复动作端点 --bug=1010131351157180998"
```

---

## Task 6: 控制台页面(模板 + 页面视图 + 路由 + 互链)

**Files:**
- Create: `gcloud/contrib/admin/templates/diagnostics/cases.html`
- Modify: `gcloud/contrib/admin/views/diagnostics.py`(新增 `diagnostic_board`)
- Modify: `gcloud/contrib/admin/urls.py`
- Modify: `gcloud/contrib/admin/templates/diagnostics/task_diagnostic.html`(互链)
- Test: `gcloud/tests/contrib/admin/diagnostics/test_case_admin_views.py`(追加 board 用例)

**Interfaces:**
- Produces: `GET /admin/diagnostics/board/` 渲染 `diagnostics/cases.html`(超管 200,非超管 403)。

- [ ] **Step 1: 写失败测试**

在 `test_case_admin_views.py` 追加:

```python
class DiagnosticBoardViewTest(TestCase):
    def test_board_renders_for_superuser(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_VIEW_INTERCEPTOR):
            resp = diagnostics.diagnostic_board(_superuser_get("/admin/diagnostics/board/"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"diagnostics-board", resp.content)

    def test_board_forbidden_for_non_superuser(self):
        from gcloud.contrib.admin.views import diagnostics

        req = _superuser_get("/admin/diagnostics/board/")
        req.user = mock.MagicMock(is_superuser=False, username="normal")
        with mock.patch(_VIEW_INTERCEPTOR):
            resp = diagnostics.diagnostic_board(req)
        self.assertEqual(resp.status_code, 403)
```

- [ ] **Step 2: 运行确认失败**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_case_admin_views.DiagnosticBoardViewTest -v 2`
Expected: FAIL(`diagnostic_board` 未实现 / 模板不存在)。

- [ ] **Step 3: 新增页面视图 + 路由**

在 `gcloud/contrib/admin/views/diagnostics.py` 追加:

```python
@require_GET
@check_is_superuser()
@iam_intercept(AdminViewViewInterceptor())
def diagnostic_board(request):
    return render(request, "diagnostics/cases.html")
```

在 `gcloud/contrib/admin/urls.py` 追加(建议置于 diagnostics 路由块首行):

```python
    url(r"^diagnostics/board/$", diagnostics.diagnostic_board),
```

- [ ] **Step 4: 新增模板 `cases.html`**

Create `gcloud/contrib/admin/templates/diagnostics/cases.html`:

```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>卡住流程治理控制台</title>
  <style>
    body { font-family: -apple-system, "PingFang SC", Arial, sans-serif; margin: 16px; color: #313238; }
    h1 { font-size: 18px; }
    .filters { margin-bottom: 12px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    .filters input, .filters select { padding: 4px 6px; border: 1px solid #c4c6cc; border-radius: 2px; }
    button { padding: 4px 10px; border: 1px solid #c4c6cc; background: #fff; border-radius: 2px; cursor: pointer; }
    button.primary { background: #3a84ff; color: #fff; border-color: #3a84ff; }
    button:disabled { opacity: .5; cursor: not-allowed; }
    table { border-collapse: collapse; width: 100%; font-size: 13px; }
    th, td { border: 1px solid #dcdee5; padding: 6px 8px; text-align: left; vertical-align: top; }
    th { background: #fafbfd; }
    .tag { padding: 1px 6px; border-radius: 2px; font-size: 12px; }
    .sev-fatal, .sev-error { background: #ffe6e6; color: #ea3636; }
    .sev-warning { background: #fff3e1; color: #ff9c01; }
    .sev-info { background: #f0f1f5; color: #63656e; }
    .drawer { position: fixed; top: 0; right: 0; width: 560px; height: 100%; background: #fff;
              box-shadow: -2px 0 8px rgba(0,0,0,.1); padding: 16px; overflow: auto; display: none; }
    .drawer.open { display: block; }
    .drawer .close { float: right; }
    pre { background: #f5f7fa; padding: 8px; overflow: auto; max-height: 240px; }
    .muted { color: #979ba5; }
    .row-actions button { margin-right: 4px; }
    #result-box { margin-top: 8px; }
  </style>
</head>
<body>
  <h1 class="diagnostics-board">卡住流程治理控制台 <span class="muted" style="font-size:12px">(超管专用 · 全局)</span></h1>
  <div class="muted" style="margin-bottom:8px">
    单任务诊断: <a href="/admin/diagnostics/task/">/admin/diagnostics/task/</a>
  </div>

  <div class="filters">
    <select id="f-status">
      <option value="">全部状态</option>
      <option value="open">待治理</option>
      <option value="resolved">已解决</option>
      <option value="ignored">已忽略</option>
    </select>
    <input id="f-stuck_type" placeholder="stuck_type">
    <select id="f-severity">
      <option value="">全部级别</option>
      <option value="fatal">fatal</option>
      <option value="error">error</option>
      <option value="warning">warning</option>
      <option value="info">info</option>
    </select>
    <input id="f-root_pipeline_id" placeholder="root_pipeline_id">
    <button class="primary" onclick="loadList(1)">查询</button>
    <span id="total" class="muted"></span>
  </div>

  <table>
    <thead>
      <tr>
        <th>任务</th><th>业务</th><th>模板</th><th>stuck_type</th><th>级别</th>
        <th>状态</th><th>卡住时长(s)</th><th>命中</th><th>最近出现</th><th>操作</th>
      </tr>
    </thead>
    <tbody id="tbody"></tbody>
  </table>
  <div style="margin-top:10px">
    <button onclick="loadList(state.page-1)" id="prev">上一页</button>
    <span id="page-info" class="muted"></span>
    <button onclick="loadList(state.page+1)" id="next">下一页</button>
  </div>

  <div class="drawer" id="drawer">
    <button class="close" onclick="closeDrawer()">关闭</button>
    <div id="drawer-body"></div>
  </div>

<script>
  var state = { page: 1, page_size: 50, total: 0 };

  function getCookie(name) {
    var m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }
  function esc(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function sevTag(sev) {
    return '<span class="tag sev-' + esc(sev) + '">' + esc(sev) + '</span>';
  }

  function loadList(page) {
    if (page < 1) return;
    var params = new URLSearchParams();
    params.set('page', page);
    params.set('page_size', state.page_size);
    ['status', 'stuck_type', 'severity', 'root_pipeline_id'].forEach(function (k) {
      var v = document.getElementById('f-' + k).value.trim();
      if (v) params.set(k, v);
    });
    fetch('/admin/diagnostics/cases/?' + params.toString(), { credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (body) {
        if (!body.result) { alert(body.message || '加载失败'); return; }
        state.page = body.data.page;
        state.total = body.data.total;
        renderList(body.data.items);
        document.getElementById('total').textContent = '共 ' + body.data.total + ' 条';
        document.getElementById('page-info').textContent = '第 ' + state.page + ' 页';
      });
  }

  function renderList(items) {
    var rows = items.map(function (it) {
      var task = it.task;
      var taskCell = task
        ? '<a href="' + esc(task.task_url) + '" target="_blank">' + esc(task.task_name || task.task_id) + '</a>'
        : '<span class="muted">' + esc(it.root_pipeline_id) + '</span>';
      var bizCell = task ? esc(task.project_name || task.project_id || '') : '';
      var tplCell = task ? esc(task.template_id || '') : '';
      return '<tr>' +
        '<td>' + taskCell + '</td>' +
        '<td>' + bizCell + '</td>' +
        '<td>' + tplCell + '</td>' +
        '<td>' + esc(it.stuck_type) + '</td>' +
        '<td>' + sevTag(it.severity) + '</td>' +
        '<td>' + esc(it.status) + '</td>' +
        '<td>' + esc(it.stall_seconds == null ? '' : it.stall_seconds) + '</td>' +
        '<td>' + esc(it.hit_count) + '</td>' +
        '<td>' + esc(it.last_seen_at || '') + '</td>' +
        '<td class="row-actions"><button onclick="openDetail(' + it.id + ')">详情</button></td>' +
        '</tr>';
    });
    document.getElementById('tbody').innerHTML = rows.join('') || '<tr><td colspan="10" class="muted">无数据</td></tr>';
  }

  function openDetail(caseId) {
    fetch('/admin/diagnostics/cases/detail/?case_id=' + caseId, { credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (body) {
        if (!body.result) { alert(body.message || '加载失败'); return; }
        renderDetail(body.data);
        document.getElementById('drawer').classList.add('open');
      });
  }

  function renderDetail(d) {
    var task = d.task;
    var taskLine = task
      ? '<a href="' + esc(task.task_url) + '" target="_blank">' + esc(task.task_name || task.task_id) + '</a> '
        + '(业务: ' + esc(task.project_name || '') + ' · 执行人: ' + esc(task.executor || '') + ')'
      : '<span class="muted">未关联到任务, root_pipeline_id=' + esc(d.root_pipeline_id) + '</span>';
    var audits = (d.audit_history || []).map(function (a) {
      return '<li>' + esc(a.created_at) + ' · ' + esc(a.operation_type) + ' · ' + esc(a.operator)
        + ' · ' + esc(a.mode) + '</li>';
    }).join('');
    var actionBtns = ['inspect_ack_converge', 'inspect_node_runtime_readiness', 'resend_schedule',
      'expire_stale_schedule', 'replay_callback_data'].map(function (act) {
      return '<button onclick="runAction(' + d.id + ',\'' + act + '\',\'dry_run\')">' + act + ' (dry-run)</button>';
    }).join(' ');

    document.getElementById('drawer-body').innerHTML =
      '<h2>病历 #' + d.id + '</h2>' +
      '<p><b>关联任务:</b> ' + taskLine + '</p>' +
      '<p><b>节点:</b> ' + esc(d.node_name || '') + ' <span class="muted">(' + esc(d.node_id) + ')</span></p>' +
      '<p><b>类型/级别/状态:</b> ' + esc(d.stuck_type) + ' / ' + sevTag(d.severity) + ' / ' + esc(d.status) + '</p>' +
      '<p><b>诊断信息:</b> ' + esc(d.message || '') + '</p>' +
      '<p><b>证据:</b></p><pre>' + esc(JSON.stringify(d.evidence, null, 2)) + '</pre>' +
      '<p><b>推荐动作:</b> ' + esc(JSON.stringify(d.recommended_actions)) + '</p>' +
      '<p><b>禁止动作:</b> ' + esc(JSON.stringify(d.forbidden_actions)) + '</p>' +
      '<hr><p><b>状态管理:</b> ' +
      '<button onclick="setStatus(' + d.id + ',\'resolved\')">标记已解决</button> ' +
      '<button onclick="setStatus(' + d.id + ',\'ignored\')">标记已忽略</button> ' +
      '<button onclick="setStatus(' + d.id + ',\'open\')">重开</button></p>' +
      '<p><b>诊断/恢复(dry-run):</b><br>' + actionBtns + '</p>' +
      '<div id="result-box"></div>' +
      '<hr><p><b>操作审计:</b></p><ul>' + (audits || '<li class="muted">无</li>') + '</ul>';
  }

  function post(url, payload) {
    return fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(payload)
    }).then(function (r) { return r.json(); });
  }

  function setStatus(caseId, status) {
    if (!confirm('确认把病历 #' + caseId + ' 状态改为 ' + status + ' ?')) return;
    post('/admin/diagnostics/cases/status/', { case_id: caseId, status: status }).then(function (body) {
      if (!body.result) { alert(body.message || '操作失败'); return; }
      closeDrawer();
      loadList(state.page);
    });
  }

  function runAction(caseId, action, mode) {
    post('/admin/diagnostics/cases/action/', { case_id: caseId, action: action, mode: mode }).then(function (body) {
      document.getElementById('result-box').innerHTML =
        '<p><b>' + esc(action) + ' 结果:</b></p><pre>' + esc(JSON.stringify(body, null, 2)) + '</pre>';
    });
  }

  function closeDrawer() { document.getElementById('drawer').classList.remove('open'); }

  loadList(1);
</script>
</body>
</html>
```

- [ ] **Step 5: 在 `task_diagnostic.html` 加互链**

在 `gcloud/contrib/admin/templates/diagnostics/task_diagnostic.html` 的 `<h1>Task Diagnostics</h1>` 下一行加入:

```html
  <p><a href="/admin/diagnostics/board/">→ 卡住流程治理控制台(病历列表)</a></p>
```

- [ ] **Step 6: 运行确认通过**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics.test_case_admin_views.DiagnosticBoardViewTest -v 2`
Expected: PASS(2 项)。

- [ ] **Step 7: 全量回归**

Run: `python manage.py test gcloud.tests.contrib.admin.diagnostics -v 2`
Expected: PASS(本插件全部诊断测试,含既有 M1 用例)。

- [ ] **Step 8: 提交**

```bash
git add gcloud/contrib/admin/templates/diagnostics/cases.html gcloud/contrib/admin/templates/diagnostics/task_diagnostic.html gcloud/contrib/admin/views/diagnostics.py gcloud/contrib/admin/urls.py gcloud/tests/contrib/admin/diagnostics/test_case_admin_views.py
git commit -m "feat: 卡住流程治理控制台页面与页面视图 --bug=1010131351157180998"
```

---

## 收尾:PR

- [ ] push 到 fork:`git push -u origin feat/stuck-governance-console`
- [ ] 建 PR(base `TencentBlueKing/bk-sops:master`,head `dengyh:feat/stuck-governance-console`),
      描述引用本 spec/plan,标注:纯 bk-sops 侧、无迁移、依赖 bamboo-pipeline>=3.24.13、超管专用。

---

## Self-Review

**Spec coverage:**
- §5.1 端点清单(board/list 增强/detail 增强/status/action)→ Task 2/3/4/5/6 全覆盖。
- §5.2 列表批量映射避免 N+1 → Task 2(每页一次 `resolve_task_summaries`)。
- §5.3 详情节点名 + 审计历史 → Task 3。
- §5.4 状态写合并去重 + 审计 → Task 4(`set_case_status` + `test_merge_when_twin_exists_no_integrity_error`)。
- §5.5 按 case 动作复用 `run_task_action` → Task 5。
- §6 前端方案 A + 互链 → Task 6。
- §7 测试点(列表映射&降级、详情、状态合并、动作 dry-run、权限 403)→ 各任务测试覆盖。
- §8 fail-safe / 无迁移 → `task_mapping`/`cases_admin`/视图均 `try/except`,无 models 变更。

**Placeholder scan:** 无 TBD/TODO;所有步骤含完整代码与命令。任务 URL、节点名解析、审计字段、状态常量均用已核实的真实签名。

**Type consistency:** `resolve_task_summaries/resolve_task_summary/resolve_node_name`、`set_case_status`、
视图函数名 `diagnostic_case_list/detail/status/action/board`、URL 路径在各任务间一致;summary 字段
(`task_id/task_name/project_id/project_name/template_id/executor/create_time/task_url`)前后一致。

> apply 动作在生产受 `PIPELINE_DIAGNOSTICS_APPLY_ENABLED` 全局开关约束(引擎 operations 内部拦截),
> M1 环境默认关闭;前端仅提供 dry-run 按钮,符合 spec"apply 受开关约束"。
