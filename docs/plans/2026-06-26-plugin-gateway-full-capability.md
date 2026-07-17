# 插件网关全量插件能力 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让标准运维插件网关把**内置 + 第三方全部插件**通过 `uniform_api v4.0.0` 暴露给 BKFlow，并用「组件运行壳（方案 B）」以真实 operator + 业务上下文真实执行（同步 / 轮询 / 回调），收敛 MVP 仅第三方同步的缺口。

**Architecture:** 目录层统一内置（遍历 `ComponentLibrary`）与第三方（`PluginServiceApiClient`）输出 v4 目录；执行层在 `gcloud/plugin_gateway/services/runner.py` 内直接实例化组件 `bound_service` 并驱动 `execute/schedule`，不创建 `PipelineModel` 引擎实例；`context` 解析 sops `Project` 与 operator 写入 `parent_data`；状态机 `CREATED→RUNNING→(WAITING_CALLBACK)→SUCCEEDED/FAILED/CANCELLED`，配 3 个独立 Celery 队列与现有回调桥接。

**Tech Stack:** Django, DRF, Celery, bamboo-pipeline（`ComponentLibrary` / `Service` / `DataObject` / `FancyDict`）, API Gateway, pytest / Django TestCase

**Spec:** `docs/specs/2026-06-26-plugin-gateway-full-capability-design.md`（MVP 基线见 `docs/specs/2026-04-21-plugin-gateway-design.md`）

**TAPD:** 沿用本特性 story `--story=133649781`（提交前若有更精确单据请替换；规则见 `.ai/rules/commit-message-convention.mdc`）

---

## 关键约束（执行者必读）

1. **运行壳 ≠ 引擎实例**：内置组件继承 `BasePluginService`（`pipeline_plugins/base/core.py`），其 `execute/schedule` 会调用 `BambooDjangoRuntime().get_data/get_state(self.id)`。运行壳里没有真实引擎节点，因此：
   - `_get_raw_password_map()` 已用 `try/except` 兜底返回 `{}`，**不会崩**，但「全局密码变量解密」能力在运行壳内不可用 → 强依赖全局密码变量的插件应进 `do_not_open_list`。
   - 个别组件（如 `RemotePluginService.plugin_schedule` 里的 `_get_node_start_time()` → `runtime.get_state(self.id)`）在没有节点状态时会抛异常。运行壳必须捕获并转 `FAILED`，第三方切换运行壳时要专门回归（spec §10）。
2. **跨进程持久化**：方案 B 的轮询/回调发生在不同 Celery 任务（不同进程），`service` 对象与 `data.outputs` 不能跨进程保留。必须把 `data.outputs`、`inputs`、`__need_schedule__`/`__schedule_finish__`、`schedule_times` 持久化到 `PluginGatewayRun`，每个 tick 重建 `service` 与 `data`。
3. **向后兼容**：不传 `context` → `default_project_id` 兜底；第三方 `plugin_id` 保持裸 `code`（无 `__` 分隔符）兼容存量；内置用 `builtin__{code}`。
4. **TDD**：每个 Task 先写失败测试再实现。运行环境变量与既有 plugin_gateway 测试一致（`DJANGO_SETTINGS_MODULE=settings`，依赖 `gcloud/tests/mock_settings`）。

---

## File Structure

| 文件 | 操作 | 责任 |
|------|------|------|
| `gcloud/plugin_gateway/models.py` | Modify | `PluginGatewaySourceConfig` 增 `scope_project_map / do_not_open_list / execution_timeout_seconds`；`PluginGatewayRun` 增 `CREATED/RUNNING` 状态、`runtime_outputs / schedule_times / execution_expire_at` |
| `gcloud/plugin_gateway/migrations/0003_full_capability_fields.py` | Create | 上述字段迁移 |
| `gcloud/plugin_gateway/constants.py` | Modify | `plugin_id` 编解码 `encode_plugin_id/decode_plugin_id`；轮询 `RUNNING_STATUS_VALUE` 改回 `RUNNING` |
| `gcloud/plugin_gateway/services/builtin_catalog.py` | Create | 内置组件元数据适配器（遍历 `ComponentLibrary` → v4 字段、schema 转换） |
| `gcloud/plugin_gateway/services/catalog.py` | Modify | 合并内置 + 第三方目录；`group/category` 透传；`do_not_open_list` 三处一致拦截；`running_tag=RUNNING` |
| `gcloud/plugin_gateway/services/context.py` | Modify | 新增 `resolve_run_context`（scope→Project 混合映射 + operator） |
| `gcloud/plugin_gateway/services/runner.py` | Create | 组件运行壳：构造 `data/parent_data`、实例化组件、`run_execute / run_schedule`、结果落库 |
| `gcloud/plugin_gateway/services/execution.py` | Modify | `create_run` 读取并校验 `context`、命中黑名单同步 4xx、登记 `execution_expire_at` |
| `gcloud/plugin_gateway/serializers.py` | Modify | `create_run` body 增可选 `context` 对象 |
| `gcloud/plugin_gateway/tasks.py` | Modify | `dispatch` 改走 runner；新增 `poll_plugin_gateway_run`；队列路由 |
| `gcloud/apigw/views/plugin_gateway.py` | Modify | 新增内部回调入口 `plugin_gateway_run_internal_callback`；错误映射 |
| `gcloud/apigw/urls.py` | Modify | 注册内部回调路由 |
| `config/default.py` | Modify | 注册 `open_plugin_dispatch / open_plugin_polling / open_plugin_callback` 队列与路由 |
| `docs/zh_hans/apidoc/*.md` / `docs/en/apidoc/*.md` | Modify | 更新 v4 目录 / execute `context` / 回调文档 |
| `gcloud/apigw/management/commands/data/api-resources.yml` | Modify | 注册内部回调资源 |
| `gcloud/apigw/docs/apigw-docs.tgz` | Modify | 重新打包 |
| `gcloud/tests/plugin_gateway/test_builtin_catalog.py` | Create | 内置目录适配测试 |
| `gcloud/tests/plugin_gateway/test_runner.py` | Create | 运行壳同步 / 轮询 / 回调测试 |
| `gcloud/tests/plugin_gateway/test_context_resolve.py` | Create | scope→Project 解析测试 |
| `gcloud/tests/plugin_gateway/test_catalog.py` | Modify | 内置 + 第三方合并、黑名单、`running_tag` |
| `gcloud/tests/plugin_gateway/test_execution.py` | Modify | `context` 读取、黑名单 4xx、timeout 登记 |
| `gcloud/tests/plugin_gateway/test_dispatch.py` | Modify | dispatch 走 runner、轮询/回调状态流转 |
| `gcloud/tests/apigw/views/test_plugin_gateway.py` | Modify | 内部回调入口、错误码 |

**Files NOT changed:** `pipeline_plugins/base/core.py`、`pipeline_plugins/components/collections/remote_plugin/v1_0_0.py`、引擎本身。

---

### Task 1: 模型与迁移扩展（来源治理字段 + 运行态持久化）

**Files:**
- Modify: `gcloud/plugin_gateway/models.py`
- Create: `gcloud/plugin_gateway/migrations/0003_full_capability_fields.py`
- Test: `gcloud/tests/plugin_gateway/test_models.py`

- [ ] **Step 1: 写失败测试**

在 `gcloud/tests/plugin_gateway/test_models.py` 追加：

```python
def test_source_config_full_capability_fields(self):
    cfg = PluginGatewaySourceConfig.objects.create(
        source_key="sops",
        display_name="标准运维",
        callback_domain_allow_list=["bkflow.example.com"],
        scope_project_map={"biz:2": 10},
        do_not_open_list=["builtin__pause_node"],
        execution_timeout_seconds=7200,
    )
    self.assertEqual(cfg.scope_project_map["biz:2"], 10)
    self.assertEqual(cfg.do_not_open_list, ["builtin__pause_node"])
    self.assertEqual(cfg.execution_timeout_seconds, 7200)

def test_run_has_running_state_and_runtime_fields(self):
    self.assertEqual(PluginGatewayRun.Status.CREATED, "CREATED")
    self.assertEqual(PluginGatewayRun.Status.RUNNING, "RUNNING")
    self.assertNotIn(PluginGatewayRun.Status.RUNNING, PluginGatewayRun.Status.TERMINAL)
    run = PluginGatewayRun.objects.create(
        source_key="sops",
        plugin_id="builtin__job_execute_task",
        plugin_version="legacy",
        client_request_id="req-1",
        open_plugin_run_id="a" * 32,
        callback_url="https://bkflow.example.com/cb",
        callback_token="tok",
        run_status=PluginGatewayRun.Status.CREATED,
        caller_app_code="bkflow",
    )
    self.assertEqual(run.runtime_outputs, {})
    self.assertEqual(run.schedule_times, 0)
    self.assertIsNone(run.execution_expire_at)
```

- [ ] **Step 2: 运行失败测试**

Run: `python manage.py test gcloud.tests.plugin_gateway.test_models -v 2`
Expected: FAIL，提示 `scope_project_map` 等字段或 `Status.RUNNING` 不存在

- [ ] **Step 3: 扩展模型**

在 `gcloud/plugin_gateway/models.py`，`PluginGatewaySourceConfig` 增加：

```python
    scope_project_map = models.JSONField(default=dict, blank=True)  # {"biz:2": 10, "space:88": 12}
    do_not_open_list = models.JSONField(default=list, blank=True)   # 不开放黑名单(plugin_id)
    execution_timeout_seconds = models.IntegerField(default=7200)   # 运行壳执行超时窗口
```

`PluginGatewayRun.Status` 增加 `CREATED = "CREATED"` 与 `RUNNING = "RUNNING"`（`TERMINAL` 不变），并新增字段：

```python
    runtime_outputs = models.JSONField(default=dict, blank=True)        # 跨 tick 持久化 data.outputs
    schedule_times = models.IntegerField(default=0)                    # 轮询次数(保护上限)
    execution_expire_at = models.DateTimeField(null=True, blank=True)  # 超时兜底时刻
```

- [ ] **Step 4: 生成迁移**

Run: `python manage.py makemigrations plugin_gateway -n full_capability_fields`
Expected: 生成 `gcloud/plugin_gateway/migrations/0003_full_capability_fields.py`，仅含 `AddField`（不得手改 schema 操作）。

- [ ] **Step 5: 运行测试至通过**

Run: `python manage.py test gcloud.tests.plugin_gateway.test_models -v 2`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add gcloud/plugin_gateway/models.py \
  gcloud/plugin_gateway/migrations/0003_full_capability_fields.py \
  gcloud/tests/plugin_gateway/test_models.py
git commit -m "feat: 插件网关补齐来源治理与运行态持久化字段 --story=133649781"
```

---

### Task 2: 目录统一（内置 + 第三方、plugin_id 编解码、黑名单、running_tag）

**Files:**
- Modify: `gcloud/plugin_gateway/constants.py`
- Create: `gcloud/plugin_gateway/services/builtin_catalog.py`
- Modify: `gcloud/plugin_gateway/services/catalog.py`
- Create: `gcloud/tests/plugin_gateway/test_builtin_catalog.py`
- Modify: `gcloud/tests/plugin_gateway/test_catalog.py`

- [ ] **Step 1: 写 plugin_id 编解码失败测试**

在 `gcloud/tests/plugin_gateway/test_builtin_catalog.py`：

```python
from gcloud.plugin_gateway.constants import (
    PLUGIN_SOURCE_BUILTIN,
    PLUGIN_SOURCE_THIRD_PARTY,
    decode_plugin_id,
    encode_plugin_id,
)


class TestPluginIdCodec(TestCase):
    def test_encode_builtin(self):
        self.assertEqual(encode_plugin_id(PLUGIN_SOURCE_BUILTIN, "job_execute_task"), "builtin__job_execute_task")

    def test_decode_builtin(self):
        self.assertEqual(decode_plugin_id("builtin__job_execute_task"), (PLUGIN_SOURCE_BUILTIN, "job_execute_task"))

    def test_decode_legacy_third_party_is_bare_code(self):
        # 存量第三方 plugin_id == code，无分隔符，按 third_party 兼容
        self.assertEqual(decode_plugin_id("bk_plugin_demo"), (PLUGIN_SOURCE_THIRD_PARTY, "bk_plugin_demo"))
```

- [ ] **Step 2: 运行失败测试**

Run: `python manage.py test gcloud.tests.plugin_gateway.test_builtin_catalog -v 2`
Expected: FAIL，`encode_plugin_id` / `decode_plugin_id` 不存在

- [ ] **Step 3: 实现编解码与 running_tag 常量**

在 `gcloud/plugin_gateway/constants.py`：

```python
PLUGIN_ID_SEP = "__"


def encode_plugin_id(plugin_source, plugin_code):
    if plugin_source == PLUGIN_SOURCE_THIRD_PARTY:
        # 第三方保持裸 code，兼容存量 BKFlow 引用
        return plugin_code
    return "{}{}{}".format(plugin_source, PLUGIN_ID_SEP, plugin_code)


def decode_plugin_id(plugin_id):
    if PLUGIN_ID_SEP in plugin_id:
        source, _, code = plugin_id.partition(PLUGIN_ID_SEP)
        return source, code
    return PLUGIN_SOURCE_THIRD_PARTY, plugin_id
```

并把轮询常量改回 `RUNNING`（spec §5）：

```python
RUNNING_STATUS_VALUE = "RUNNING"  # 恢复轮询语义(MVP 曾改为 WAITING_CALLBACK)
```

- [ ] **Step 4: 写内置目录适配失败测试**

在 `test_builtin_catalog.py` 追加（mock `ComponentLibrary` 避免依赖真实组件集）：

```python
from unittest.mock import patch
from gcloud.plugin_gateway.services.builtin_catalog import BuiltinCatalogService


class FakeService:
    def inputs_format(self):
        return []

    def outputs_format(self):
        return []


class FakeComponent:
    code = "job_execute_task"
    name = "执行作业"
    group_name = "JOB"
    version = "legacy"
    bound_service = FakeService

    @classmethod
    def outputs_format(cls):
        return []


class TestBuiltinCatalog(TestCase):
    @patch("gcloud.plugin_gateway.services.builtin_catalog.ComponentLibrary")
    def test_list_builtin_plugins(self, mock_lib):
        mock_lib.component_list.return_value = [FakeComponent]
        plugins = BuiltinCatalogService.list_plugins()
        self.assertEqual(plugins[0]["plugin_source"], "builtin")
        self.assertEqual(plugins[0]["id"], "builtin__job_execute_task")
        self.assertEqual(plugins[0]["plugin_code"], "job_execute_task")
        self.assertEqual(plugins[0]["category"], "JOB")  # 透传内置 group
        self.assertIn("legacy", plugins[0]["versions"])
```

- [ ] **Step 5: 实现 `BuiltinCatalogService`**

`gcloud/plugin_gateway/services/builtin_catalog.py`：

```python
# -*- coding: utf-8 -*-
from pipeline.component_framework.library import ComponentLibrary

from gcloud.plugin_gateway.constants import PLUGIN_SOURCE_BUILTIN, encode_plugin_id


class BuiltinCatalogService:
    """遍历内置组件注册表，输出 uniform_api v4 目录字段。"""

    @classmethod
    def list_plugins(cls):
        plugins = []
        seen = {}
        for component_cls in ComponentLibrary.component_list():
            code = component_cls.code
            version = getattr(component_cls, "version", "legacy")
            seen.setdefault(code, []).append(version)
        for code, versions in seen.items():
            component_cls = ComponentLibrary.get_component_class(code)
            plugins.append(cls._build_meta(component_cls, code, versions))
        return plugins

    @classmethod
    def get_plugin_detail(cls, code, version=None):
        component_cls = ComponentLibrary.get_component_class(code, version)
        meta = cls._build_meta(component_cls, code, [getattr(component_cls, "version", "legacy")])
        service = component_cls.bound_service()
        meta["inputs"] = cls._convert_io(service.inputs_format())
        meta["outputs"] = cls._convert_io(service.outputs_format())
        return meta

    @classmethod
    def _build_meta(cls, component_cls, code, versions):
        versions = sorted(set(versions))
        return {
            "id": encode_plugin_id(PLUGIN_SOURCE_BUILTIN, code),
            "plugin_source": PLUGIN_SOURCE_BUILTIN,
            "plugin_code": code,
            "name": str(getattr(component_cls, "name", code)),
            "group": str(getattr(component_cls, "group_name", "") or ""),
            "category": str(getattr(component_cls, "group_name", "") or PLUGIN_SOURCE_BUILTIN),
            "versions": versions,
            "default_version": getattr(component_cls, "version", versions[-1]),
            "latest_version": versions[-1],
        }

    @staticmethod
    def _convert_io(io_format):
        fields = []
        for item in io_format or []:
            schema = getattr(item, "schema", None)
            fields.append(
                {
                    "key": item["key"] if isinstance(item, dict) else getattr(item, "key", ""),
                    "name": item["name"] if isinstance(item, dict) else getattr(item, "name", ""),
                    "type": getattr(schema, "type", "string") if schema else "string",
                }
            )
        return fields
```

> 注：`inputs_format()/outputs_format()` 返回的 item 形态各组件略有差异（`InputItem`/`OutputItem` 对象或 dict）。本任务以「能列出 + 取 key/name/type」为最小目标；复杂 `form` 转换在 §1.3 视联调反馈再细化，先不阻塞主链路。

- [ ] **Step 6: 合并目录 + 黑名单 + group/category 透传**

在 `gcloud/plugin_gateway/services/catalog.py`：

- `get_plugin_list`：合并 `BuiltinCatalogService.list_plugins()` 与现有 `_list_plugins()`（第三方），统一注入 `meta_url_template`；过滤掉命中来源 `do_not_open_list` 的 `plugin_id`。
- `get_plugin_detail`：先 `decode_plugin_id(plugin_id)`，`builtin` 走 `BuiltinCatalogService.get_plugin_detail`，`third_party` 走原路径；命中黑名单抛 `PluginGatewayPluginNotFoundError`（对外 404）。
- `_list_plugins()`（第三方）：把硬编码的 `category=PLUGIN_SOURCE_THIRD_PARTY` 改为透传插件 `group/tag`（取不到再回退 `third_party`），并修复 categories 一致性（list 现在确实会返回 `builtin` 项）。
- 详情 `polling.running_tag.value` 引用 `RUNNING_STATUS_VALUE`（已为 `RUNNING`）。

黑名单过滤辅助（catalog.py 内）：

```python
@staticmethod
def _filter_blacklist(plugins):
    from gcloud.plugin_gateway.models import PluginGatewaySourceConfig
    blacklist = set()
    for cfg in PluginGatewaySourceConfig.objects.filter(is_enabled=True):
        blacklist.update(cfg.do_not_open_list or [])
    return [p for p in plugins if p["id"] not in blacklist]
```

- [ ] **Step 7: 更新 `test_catalog.py`**

- 合并后列表既含 `plugin_source=builtin` 也含 `third_party`。
- `do_not_open_list` 命中项不出现在 list、detail 抛 404。
- `running_tag.value == "RUNNING"`（修正 MVP 阶段断言的 `WAITING_CALLBACK`）。

- [ ] **Step 8: 运行测试至通过**

Run:
- `python manage.py test gcloud.tests.plugin_gateway.test_builtin_catalog -v 2`
- `python manage.py test gcloud.tests.plugin_gateway.test_catalog -v 2`

Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add gcloud/plugin_gateway/constants.py \
  gcloud/plugin_gateway/services/builtin_catalog.py \
  gcloud/plugin_gateway/services/catalog.py \
  gcloud/tests/plugin_gateway/test_builtin_catalog.py \
  gcloud/tests/plugin_gateway/test_catalog.py
git commit -m "feat: 插件网关统一暴露内置与第三方插件目录 --story=133649781"
```

---

### Task 3: project / identity 解析（混合映射 + 真实 operator）

**Files:**
- Modify: `gcloud/plugin_gateway/services/context.py`
- Modify: `gcloud/plugin_gateway/exceptions.py`
- Create: `gcloud/tests/plugin_gateway/test_context_resolve.py`

- [ ] **Step 1: 写解析失败测试**

`gcloud/tests/plugin_gateway/test_context_resolve.py`：

```python
from unittest.mock import patch

from django.test import TestCase

from gcloud.core.models import Project
from gcloud.plugin_gateway.exceptions import PluginGatewayContextResolveError
from gcloud.plugin_gateway.models import PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.context import PluginGatewayContextService


class TestResolveRunContext(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="biz2", bk_biz_id=2, from_cmdb=True)
        self.cfg = PluginGatewaySourceConfig.objects.create(
            source_key="sops", display_name="标准运维", default_project_id=None,
            scope_project_map={"space:88": self.project.id},
        )

    def test_biz_scope_resolves_project(self):
        ctx = {"scope_type": "biz", "scope_value": "2", "operator": "zhangsan"}
        resolved = PluginGatewayContextService.resolve_run_context(self.cfg, ctx)
        self.assertEqual(resolved["project_id"], self.project.id)
        self.assertEqual(resolved["bk_biz_id"], 2)
        self.assertEqual(resolved["operator"], "zhangsan")

    def test_map_table_fallback(self):
        ctx = {"scope_type": "space", "scope_value": "88", "operator": "lisi"}
        resolved = PluginGatewayContextService.resolve_run_context(self.cfg, ctx)
        self.assertEqual(resolved["project_id"], self.project.id)

    def test_default_project_fallback(self):
        self.cfg.default_project_id = self.project.id
        self.cfg.scope_project_map = {}
        self.cfg.save()
        resolved = PluginGatewayContextService.resolve_run_context(self.cfg, None)
        self.assertEqual(resolved["project_id"], self.project.id)

    def test_no_resolution_raises(self):
        self.cfg.scope_project_map = {}
        self.cfg.default_project_id = None
        self.cfg.save()
        with self.assertRaises(PluginGatewayContextResolveError):
            PluginGatewayContextService.resolve_run_context(self.cfg, {"scope_type": "other", "scope_value": "x"})
```

- [ ] **Step 2: 运行失败测试**

Run: `python manage.py test gcloud.tests.plugin_gateway.test_context_resolve -v 2`
Expected: FAIL，`resolve_run_context` / `PluginGatewayContextResolveError` 不存在

- [ ] **Step 3: 新增异常**

`gcloud/plugin_gateway/exceptions.py`：

```python
class PluginGatewayContextResolveError(ValueError):
    """无法从 context 解析出可执行的 sops Project / operator。"""
```

- [ ] **Step 4: 实现 `resolve_run_context`**

在 `gcloud/plugin_gateway/services/context.py` 的 `PluginGatewayContextService` 增加（spec §3 混合映射）：

```python
@classmethod
def resolve_run_context(cls, source_config, context):
    context = context or {}
    scope_type = context.get("scope_type")
    scope_value = context.get("scope_value")
    project_id = cls._resolve_project_id(source_config, scope_type, scope_value)
    if project_id is None:
        raise PluginGatewayContextResolveError(
            "cannot resolve sops project from scope_type=%s scope_value=%s" % (scope_type, scope_value)
        )
    from gcloud.core.models import Project
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        raise PluginGatewayContextResolveError("resolved project_id=%s not found" % project_id)
    return {
        "project_id": project.id,
        "bk_biz_id": project.bk_biz_id,
        "operator": context.get("operator") or "",
        "scope_type": scope_type,
        "scope_value": scope_value,
        "space_id": context.get("space_id"),
        "task_id": context.get("task_id"),
        "node_id": context.get("node_id"),
        "task_name": context.get("task_name"),
    }

@staticmethod
def _resolve_project_id(source_config, scope_type, scope_value):
    # 1) biz scope → bk_biz_id → Project
    if scope_type in ("biz", "cmdb_biz") and scope_value:
        from gcloud.core.models import Project
        project = Project.objects.filter(bk_biz_id=int(scope_value), from_cmdb=True).first()
        if project:
            return project.id
    # 2) 来源映射表 {"<scope_type>:<scope_value>": project_id}
    mapping = source_config.scope_project_map or {}
    if scope_type and scope_value:
        mapped = mapping.get("%s:%s" % (scope_type, scope_value))
        if mapped:
            return int(mapped)
    # 3) default_project_id 兜底
    if source_config.default_project_id:
        return int(source_config.default_project_id)
    return None
```

> biz scope 若 `Project` 尚未同步，可按需调用 `gcloud.core.project.sync_projects_from_cmdb(operator)` 后重试一次（联调阶段视命中率决定是否启用，先不默认拉 CMDB，避免登记期阻塞）。

- [ ] **Step 5: 运行测试至通过**

Run: `python manage.py test gcloud.tests.plugin_gateway.test_context_resolve -v 2`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add gcloud/plugin_gateway/services/context.py \
  gcloud/plugin_gateway/exceptions.py \
  gcloud/tests/plugin_gateway/test_context_resolve.py
git commit -m "feat: 插件网关按 context 混合解析 project 与 operator --story=133649781"
```

---

### Task 4: 组件运行壳核心（同步 execute）

**Files:**
- Create: `gcloud/plugin_gateway/services/runner.py`
- Create: `gcloud/tests/plugin_gateway/test_runner.py`

- [ ] **Step 1: 写同步执行失败测试**

`gcloud/tests/plugin_gateway/test_runner.py`：

```python
from unittest.mock import patch

from django.test import TestCase

from gcloud.plugin_gateway.models import PluginGatewayRun
from gcloud.plugin_gateway.services.runner import PluginGatewayRunner


class _SyncService:
    interval = None

    def execute(self, data, parent_data):
        data.set_outputs("echo_operator", parent_data.get_one_of_inputs("operator"))
        data.set_outputs("done", True)
        return True

    def need_schedule(self):
        return False


class _SyncComponent:
    code = "demo_sync"
    version = "legacy"
    bound_service = _SyncService


class TestRunnerExecute(TestCase):
    def _run(self):
        return PluginGatewayRun.objects.create(
            plugin_id="builtin__demo_sync", plugin_version="legacy", client_request_id="r1",
            open_plugin_run_id="a" * 32, callback_url="https://x/cb", callback_token="t",
            run_status=PluginGatewayRun.Status.CREATED, caller_app_code="bkflow",
            trigger_payload={"inputs": {"k": "v"}},
        )

    @patch("gcloud.plugin_gateway.services.runner.ComponentLibrary")
    def test_sync_success(self, mock_lib):
        mock_lib.get_component_class.return_value = _SyncComponent
        result = PluginGatewayRunner.run_execute(self._run(), {"operator": "zhangsan", "project_id": 10, "bk_biz_id": 2})
        self.assertTrue(result["ok"])
        self.assertFalse(result["need_schedule"])
        self.assertEqual(result["mode"], "sync")
        self.assertEqual(result["outputs"]["echo_operator"], "zhangsan")
        self.assertTrue(result["outputs"]["done"])

    @patch("gcloud.plugin_gateway.services.runner.ComponentLibrary")
    def test_execute_exception_maps_failed(self, mock_lib):
        class _Boom(_SyncService):
            def execute(self, data, parent_data):
                raise RuntimeError("boom")

        class _BoomComponent(_SyncComponent):
            bound_service = _Boom

        mock_lib.get_component_class.return_value = _BoomComponent
        result = PluginGatewayRunner.run_execute(self._run(), {"operator": "x", "project_id": 10, "bk_biz_id": 2})
        self.assertFalse(result["ok"])
        self.assertIn("boom", result["error_message"])
```

- [ ] **Step 2: 运行失败测试**

Run: `python manage.py test gcloud.tests.plugin_gateway.test_runner -v 2`
Expected: FAIL，`runner` 模块或 `run_execute` 不存在

- [ ] **Step 3: 实现运行壳**

`gcloud/plugin_gateway/services/runner.py`：

```python
# -*- coding: utf-8 -*-
import logging

from pipeline.component_framework.library import ComponentLibrary
from pipeline.core.data.base import DataObject
from pipeline.utils.collections import FancyDict

from gcloud.plugin_gateway.constants import PLUGIN_SOURCE_BUILTIN, decode_plugin_id

logger = logging.getLogger("root")

THIRD_PARTY_COMPONENT_CODE = "remote_plugin"
THIRD_PARTY_COMPONENT_VERSION = "1.0.0"


class PluginGatewayRunner:
    """组件运行壳（方案 B）：直接驱动组件 Service，不创建引擎实例。"""

    @classmethod
    def build_service(cls, run):
        source, code = decode_plugin_id(run.plugin_id)
        if source == PLUGIN_SOURCE_BUILTIN:
            version = None if run.plugin_version in ("", "legacy") else run.plugin_version
            component_cls = ComponentLibrary.get_component_class(code, version)
        else:
            component_cls = ComponentLibrary.get_component_class(
                THIRD_PARTY_COMPONENT_CODE, THIRD_PARTY_COMPONENT_VERSION
            )
        service = component_cls.bound_service()
        # 运行壳没有真实引擎节点，用 run_id 充当节点/根流程标识
        service.id = run.open_plugin_run_id
        service.root_pipeline_id = run.open_plugin_run_id
        setattr(service, "version", run.plugin_version)
        return source, code, service

    @classmethod
    def build_data(cls, run, run_context, source, code):
        inputs = dict(run.trigger_payload.get("inputs", {}))
        if source != PLUGIN_SOURCE_BUILTIN:
            inputs.setdefault("plugin_code", code)
            inputs.setdefault("plugin_version", run.plugin_version)
        data = DataObject(inputs=FancyDict(inputs), outputs=FancyDict(dict(run.runtime_outputs or {})))
        parent_data = DataObject(
            inputs=FancyDict(
                {
                    "operator": run_context.get("operator") or "",
                    "executor": run_context.get("operator") or "",
                    "project_id": run_context.get("project_id"),
                    "bk_biz_id": run_context.get("bk_biz_id"),
                    "task_id": run_context.get("task_id"),
                    "task_name": run_context.get("task_name"),
                    "task_start_time": None,
                }
            )
        )
        return data, parent_data

    @classmethod
    def run_execute(cls, run, run_context):
        source, code, service = cls.build_service(run)
        data, parent_data = cls.build_data(run, run_context, source, code)
        try:
            ok = bool(service.execute(data, parent_data))
        except Exception as e:  # 运行壳上下文不完备/组件异常 → 统一转 FAILED
            logger.exception("[plugin_gateway] runner execute error run=%s", run.open_plugin_run_id)
            return cls._result(False, cls._outputs(data), str(e), False)
        try:
            need_schedule = bool(service.need_schedule())
        except Exception:
            need_schedule = False
        if not ok:
            mode = "sync"
        elif not need_schedule:
            mode = "sync"
        elif getattr(service, "interval", None) is None:
            mode = "callback"  # interval 被组件置 None → 回调型
        else:
            mode = "poll"
        return cls._result(ok, cls._outputs(data), cls._ex_data(data), need_schedule, mode)

    @staticmethod
    def _outputs(data):
        try:
            return dict(data.get_outputs())
        except Exception:
            return {}

    @staticmethod
    def _ex_data(data):
        try:
            return str(data.get_one_of_outputs("ex_data") or "")
        except Exception:
            return ""

    @staticmethod
    def _result(ok, outputs, error_message, need_schedule, mode="sync", finished=False):
        return {
            "ok": ok,
            "outputs": outputs,
            "error_message": error_message,
            "need_schedule": need_schedule,
            "mode": mode,
            "finished": finished,
        }
```

- [ ] **Step 4: 运行测试至通过**

Run: `python manage.py test gcloud.tests.plugin_gateway.test_runner -v 2`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add gcloud/plugin_gateway/services/runner.py gcloud/tests/plugin_gateway/test_runner.py
git commit -m "feat: 新增插件网关组件运行壳同步执行能力 --story=133649781"
```

---

### Task 5: dispatch 接线 + 协议 context 读取 + 独立队列

**Files:**
- Modify: `gcloud/plugin_gateway/serializers.py`
- Modify: `gcloud/plugin_gateway/services/execution.py`
- Modify: `gcloud/plugin_gateway/services/context.py`（`build_trigger_payload` 携带 `context`）
- Modify: `gcloud/plugin_gateway/tasks.py`
- Modify: `config/default.py`
- Modify: `gcloud/tests/plugin_gateway/test_execution.py`
- Modify: `gcloud/tests/plugin_gateway/test_dispatch.py`

- [ ] **Step 1: 写 context 读取 + dispatch 失败测试**

在 `gcloud/tests/plugin_gateway/test_execution.py` 追加：

```python
def test_create_run_persists_context(self):
    payload = self._base_payload()  # 含 source_key/plugin_id/plugin_version/client_request_id/callback_*
    payload["context"] = {"scope_type": "biz", "scope_value": "2", "operator": "zhangsan"}
    run, created = PluginGatewayExecutionService.create_run("bkflow", payload)
    self.assertTrue(created)
    self.assertEqual(run.trigger_payload["context"]["operator"], "zhangsan")

def test_create_run_blacklist_rejected(self):
    self.source_config.do_not_open_list = [self.plugin_id]
    self.source_config.save()
    payload = self._base_payload()
    with self.assertRaises(PluginGatewayPluginNotEnabledError):
        PluginGatewayExecutionService.create_run("bkflow", payload)
```

在 `gcloud/tests/plugin_gateway/test_dispatch.py` 追加（dispatch 走 runner，同步成功）。前置：`_create_run` 需同时创建匹配 `run.source_key` 的 `PluginGatewaySourceConfig`，否则 dispatch/poll/callback 任务 `PluginGatewaySourceConfig.objects.get(source_key=run.source_key)` 会抛 `DoesNotExist`：

```python
@patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
@patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_execute")
@patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
def test_dispatch_sync_success_calls_callback(self, mock_ctx, mock_exec, mock_cb):
    mock_ctx.return_value = {"operator": "x", "project_id": 10, "bk_biz_id": 2}
    mock_exec.return_value = {"ok": True, "need_schedule": False, "mode": "sync",
                              "outputs": {"a": 1}, "error_message": ""}
    run = self._create_run(status=PluginGatewayRun.Status.CREATED)
    dispatch_plugin_gateway_run(run.open_plugin_run_id)
    run.refresh_from_db()
    mock_cb.assert_called_once()
    self.assertEqual(mock_cb.call_args[1]["run_status"], PluginGatewayRun.Status.SUCCEEDED)
```

- [ ] **Step 2: 运行失败测试**

Run:
- `python manage.py test gcloud.tests.plugin_gateway.test_execution -v 2`
- `python manage.py test gcloud.tests.plugin_gateway.test_dispatch -v 2`

Expected: FAIL，`context` 未持久化 / dispatch 仍直连 `PluginServiceApiClient`

- [ ] **Step 3: serializer 增加可选 `context`**

`gcloud/plugin_gateway/serializers.py` 的 `PluginGatewayRunCreateSerializer` 增加：

```python
    context = serializers.DictField(required=False, default=dict)
```

- [ ] **Step 4: `create_run` 读取 context + 黑名单拦截**

在 `gcloud/plugin_gateway/services/execution.py`：

- `_get_plugin_reference` 前增加黑名单校验：命中 `source_config.do_not_open_list` → `raise PluginGatewayPluginNotEnabledError`。
- `build_trigger_payload`（context.py）把 `payload.get("context")` 原样并入 `trigger_payload["context"]`（不传则 `{}`）。dispatch / poll / callback 任务通过模型已有的 `run.source_key` 字段取 `PluginGatewaySourceConfig`，无需额外塞 source_key 进 trigger_payload。
- 登记 `execution_expire_at = now + timedelta(seconds=source_config.execution_timeout_seconds)`，写入 `defaults`。
- 初始 `run_status = PluginGatewayRun.Status.CREATED`。

- [ ] **Step 5: dispatch 改走运行壳**

重写 `gcloud/plugin_gateway/tasks.py` 的 `dispatch_plugin_gateway_run`（去掉「非 third_party 直接失败」与「异步状态 fast-fail」）：

```python
@task(queue="open_plugin_dispatch")
def dispatch_plugin_gateway_run(open_plugin_run_id):
    run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id)
    if run.run_status in PluginGatewayRun.Status.TERMINAL:
        return
    source_config = PluginGatewaySourceConfig.objects.get(source_key=run.source_key)
    try:
        run_context = PluginGatewayContextService.resolve_run_context(
            source_config, run.trigger_payload.get("context")
        )
    except PluginGatewayContextResolveError as e:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.FAILED, error_message=str(e)
        )
        return

    run.run_status = PluginGatewayRun.Status.RUNNING
    run.save(update_fields=["run_status", "update_time"])

    result = PluginGatewayRunner.run_execute(run, run_context)
    if not result["ok"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.FAILED,
            error_message=result["error_message"] or "plugin execute failed",
        )
        return
    if not result["need_schedule"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.SUCCEEDED, outputs=result["outputs"]
        )
        return
    # 异步：持久化运行态，转 polling / callback
    run.runtime_outputs = result["outputs"]
    run.schedule_times = 0
    if result["mode"] == "callback":
        run.run_status = PluginGatewayRun.Status.WAITING_CALLBACK
        run.save(update_fields=["run_status", "runtime_outputs", "schedule_times", "update_time"])
    else:
        run.save(update_fields=["runtime_outputs", "schedule_times", "update_time"])
        poll_plugin_gateway_run.apply_async(
            kwargs={"open_plugin_run_id": open_plugin_run_id}, countdown=10, queue="open_plugin_polling"
        )
```

> `poll_plugin_gateway_run` 在 Task 6 实现；本任务先 import 占位（Task 6 补全实现并解开轮询测试）。

- [ ] **Step 6: 注册独立队列**

在 `config/default.py` 队列装配处追加（与存量任务队列物理隔离，spec §6）：

```python
ScalableQueues.add(name="open_plugin_dispatch")
ScalableQueues.add(name="open_plugin_polling")
ScalableQueues.add(name="open_plugin_callback")
CELERY_QUEUES.extend(QueueResolver("open_plugin_dispatch").queues())
CELERY_QUEUES.extend(QueueResolver("open_plugin_polling").queues())
CELERY_QUEUES.extend(QueueResolver("open_plugin_callback").queues())
```

> 按仓库现有 `ScalableQueues` / `QueueResolver` 实际 API 对齐（参考 `API_TASK_QUEUE_NAME_V2` 装配方式）；目标是让三类任务路由到独立 worker，不与 `pipeline_*` 队列混跑。部署侧补 worker 命令在 Task 9 文档同步。

- [ ] **Step 7: 运行测试至通过**

Run:
- `python manage.py test gcloud.tests.plugin_gateway.test_execution -v 2`
- `python manage.py test gcloud.tests.plugin_gateway.test_dispatch -v 2`

Expected: PASS（轮询分支用 mock 占位，Task 6 落地真实轮询）

- [ ] **Step 8: Commit**

```bash
git add gcloud/plugin_gateway/serializers.py \
  gcloud/plugin_gateway/services/execution.py \
  gcloud/plugin_gateway/services/context.py \
  gcloud/plugin_gateway/tasks.py \
  config/default.py \
  gcloud/tests/plugin_gateway/test_execution.py \
  gcloud/tests/plugin_gateway/test_dispatch.py
git commit -m "feat: 插件网关 dispatch 走运行壳并读取业务 context --story=133649781"
```

---

### Task 6: 轮询模式（run_schedule + poll 任务 + 超时/次数保护）

**Files:**
- Modify: `gcloud/plugin_gateway/services/runner.py`（新增 `run_schedule`）
- Modify: `gcloud/plugin_gateway/tasks.py`（新增 `poll_plugin_gateway_run`）
- Modify: `gcloud/plugin_gateway/constants.py`（`MAX_SCHEDULE_TIMES`、轮询 backoff）
- Modify: `gcloud/tests/plugin_gateway/test_runner.py`
- Modify: `gcloud/tests/plugin_gateway/test_dispatch.py`

- [ ] **Step 1: 写轮询失败测试**

在 `test_runner.py` 追加（一个组件先 need_schedule，再 finish）：

```python
class _PollService:
    interval = object()  # 非 None → 轮询型

    def execute(self, data, parent_data):
        setattr(self, "__need_schedule__", True)
        return True

    def need_schedule(self):
        return getattr(self, "__need_schedule__", False)

    def schedule(self, data, parent_data, callback_data=None):
        data.set_outputs("polled", True)
        setattr(self, "__schedule_finish__", True)
        return True

    def is_schedule_finished(self):
        return getattr(self, "__schedule_finish__", False)


class _PollComponent:
    code = "demo_poll"
    version = "legacy"
    bound_service = _PollService


class TestRunnerSchedule(TestCase):
    @patch("gcloud.plugin_gateway.services.runner.ComponentLibrary")
    def test_schedule_finishes(self, mock_lib):
        mock_lib.get_component_class.return_value = _PollComponent
        run = PluginGatewayRun.objects.create(
            plugin_id="builtin__demo_poll", plugin_version="legacy", client_request_id="rp",
            open_plugin_run_id="b" * 32, callback_url="https://x/cb", callback_token="t",
            run_status=PluginGatewayRun.Status.RUNNING, caller_app_code="bkflow",
            trigger_payload={"inputs": {}}, runtime_outputs={},
        )
        result = PluginGatewayRunner.run_schedule(run, {"operator": "x", "project_id": 10, "bk_biz_id": 2})
        self.assertTrue(result["ok"])
        self.assertTrue(result["finished"])
        self.assertTrue(result["outputs"]["polled"])
```

在 `test_dispatch.py` 追加 poll 任务测试：

```python
@patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
@patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_schedule")
@patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
def test_poll_finished_calls_success_callback(self, mock_ctx, mock_sched, mock_cb):
    mock_ctx.return_value = {"operator": "x", "project_id": 10, "bk_biz_id": 2}
    mock_sched.return_value = {"ok": True, "finished": True, "outputs": {"r": 1}, "error_message": "", "mode": "poll"}
    run = self._create_run(status=PluginGatewayRun.Status.RUNNING)
    poll_plugin_gateway_run(run.open_plugin_run_id)
    self.assertEqual(mock_cb.call_args[1]["run_status"], PluginGatewayRun.Status.SUCCEEDED)
```

- [ ] **Step 2: 运行失败测试**

Run:
- `python manage.py test gcloud.tests.plugin_gateway.test_runner -v 2`
- `python manage.py test gcloud.tests.plugin_gateway.test_dispatch -v 2`

Expected: FAIL，`run_schedule` / `poll_plugin_gateway_run` 不存在

- [ ] **Step 3: 实现 `run_schedule`**

在 `gcloud/plugin_gateway/services/runner.py`：

```python
    @classmethod
    def run_schedule(cls, run, run_context, callback_data=None):
        source, code, service = cls.build_service(run)
        data, parent_data = cls.build_data(run, run_context, source, code)
        setattr(service, "__need_schedule__", True)  # 处于 schedule 阶段
        try:
            ok = bool(service.schedule(data, parent_data, callback_data=callback_data))
        except Exception as e:
            logger.exception("[plugin_gateway] runner schedule error run=%s", run.open_plugin_run_id)
            return cls._result(False, cls._outputs(data), str(e), False, "poll", finished=False)
        try:
            finished = bool(service.is_schedule_finished())
        except Exception:
            finished = False
        return cls._result(ok, cls._outputs(data), cls._ex_data(data), not finished, "poll", finished=finished)
```

- [ ] **Step 4: 常量与 poll 任务**

`gcloud/plugin_gateway/constants.py`：

```python
MAX_SCHEDULE_TIMES = 1000  # 轮询次数保护上限


def poll_countdown(schedule_times):
    # 最小 10s，逐步退避，最大 600s
    return 10 if schedule_times < 30 else min((schedule_times - 25) ** 2, 600)
```

`gcloud/plugin_gateway/tasks.py` 新增：

```python
@task(queue="open_plugin_polling")
def poll_plugin_gateway_run(open_plugin_run_id):
    run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id)
    if run.run_status in PluginGatewayRun.Status.TERMINAL:
        return
    if run.execution_expire_at and timezone.now() >= run.execution_expire_at:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.FAILED, error_message="execution timeout"
        )
        return
    if run.schedule_times >= MAX_SCHEDULE_TIMES:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.FAILED, error_message="exceed max schedule times"
        )
        return
    source_config = PluginGatewaySourceConfig.objects.get(source_key=run.source_key)
    try:
        run_context = PluginGatewayContextService.resolve_run_context(source_config, run.trigger_payload.get("context"))
    except PluginGatewayContextResolveError as e:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.FAILED, error_message=str(e)
        )
        return

    result = PluginGatewayRunner.run_schedule(run, run_context)
    run.schedule_times += 1
    run.runtime_outputs = result["outputs"]
    run.save(update_fields=["schedule_times", "runtime_outputs", "update_time"])

    if not result["ok"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.FAILED,
            error_message=result["error_message"] or "plugin schedule failed",
        )
    elif result["finished"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.SUCCEEDED, outputs=result["outputs"]
        )
    else:
        poll_plugin_gateway_run.apply_async(
            kwargs={"open_plugin_run_id": open_plugin_run_id},
            countdown=poll_countdown(run.schedule_times),
            queue="open_plugin_polling",
        )
```

补 import：`from django.utils import timezone`、`from gcloud.plugin_gateway.constants import MAX_SCHEDULE_TIMES, poll_countdown`。

- [ ] **Step 5: 运行测试至通过**

Run:
- `python manage.py test gcloud.tests.plugin_gateway.test_runner -v 2`
- `python manage.py test gcloud.tests.plugin_gateway.test_dispatch -v 2`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add gcloud/plugin_gateway/services/runner.py \
  gcloud/plugin_gateway/tasks.py \
  gcloud/plugin_gateway/constants.py \
  gcloud/tests/plugin_gateway/test_runner.py \
  gcloud/tests/plugin_gateway/test_dispatch.py
git commit -m "feat: 插件网关支持轮询型插件异步执行 --story=133649781"
```

---

### Task 7: 回调模式（内部回调入口 + callback 任务）

> **风险标记（spec §2.4 / §11）**：回调型组件常用 `get_node_callback_url(root_pipeline_id, id, version)` 自行拼装回调地址，指向标准运维节点回调端点。运行壳没有引擎节点，需让该 run_id 的回调被路由到网关回调处理而非引擎。本任务交付网关侧回调入口与 `service.schedule(callback_data=...)` 闭环；「下游回调地址正确指向网关」这一路由缝隙在联调中确认；无法重定向回调的组件进 `do_not_open_list`。

**Files:**
- Modify: `gcloud/apigw/views/plugin_gateway.py`（新增内部回调入口）
- Modify: `gcloud/apigw/urls.py`
- Modify: `gcloud/plugin_gateway/tasks.py`（新增 `callback_plugin_gateway_run`）
- Modify: `gcloud/tests/apigw/views/test_plugin_gateway.py`
- Modify: `gcloud/tests/plugin_gateway/test_dispatch.py`

- [ ] **Step 1: 写回调入口失败测试**

在 `gcloud/tests/apigw/views/test_plugin_gateway.py`：

```python
@patch("gcloud.apigw.views.plugin_gateway.callback_plugin_gateway_run.apply_async")
def test_internal_callback_enqueues_schedule(self, mock_async):
    run = self._create_waiting_callback_run()  # status=WAITING_CALLBACK, caller_app_code 与请求一致
    resp = self.client.post(
        "/apigw/plugin-gateway/runs/{}/internal-callback/".format(run.open_plugin_run_id),
        data=json.dumps({"callback_data": {"result": "ok"}}),
        content_type="application/json",
    )
    self.assertTrue(resp.json()["result"])
    mock_async.assert_called_once()
```

在 `test_dispatch.py`：

```python
@patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run")
@patch("gcloud.plugin_gateway.tasks.PluginGatewayRunner.run_schedule")
@patch("gcloud.plugin_gateway.tasks.PluginGatewayContextService.resolve_run_context")
def test_callback_task_finishes(self, mock_ctx, mock_sched, mock_cb):
    mock_ctx.return_value = {"operator": "x", "project_id": 10, "bk_biz_id": 2}
    mock_sched.return_value = {"ok": True, "finished": True, "outputs": {"r": 9}, "error_message": "", "mode": "callback"}
    run = self._create_run(status=PluginGatewayRun.Status.WAITING_CALLBACK)
    callback_plugin_gateway_run(run.open_plugin_run_id, {"result": "ok"})
    self.assertEqual(mock_cb.call_args[1]["run_status"], PluginGatewayRun.Status.SUCCEEDED)
    mock_sched.assert_called_once()
```

- [ ] **Step 2: 运行失败测试**

Run:
- `python manage.py test gcloud.tests.apigw.views.test_plugin_gateway -v 2`
- `python manage.py test gcloud.tests.plugin_gateway.test_dispatch -v 2`

Expected: FAIL，回调入口 / `callback_plugin_gateway_run` 不存在

- [ ] **Step 3: 实现 callback 任务**

`gcloud/plugin_gateway/tasks.py`：

```python
@task(queue="open_plugin_callback")
def callback_plugin_gateway_run(open_plugin_run_id, callback_data=None):
    run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id)
    if run.run_status in PluginGatewayRun.Status.TERMINAL:
        return  # 已终态幂等
    source_config = PluginGatewaySourceConfig.objects.get(source_key=run.source_key)
    try:
        run_context = PluginGatewayContextService.resolve_run_context(source_config, run.trigger_payload.get("context"))
    except PluginGatewayContextResolveError as e:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.FAILED, error_message=str(e)
        )
        return
    result = PluginGatewayRunner.run_schedule(run, run_context, callback_data=callback_data)
    run.runtime_outputs = result["outputs"]
    run.save(update_fields=["runtime_outputs", "update_time"])
    if not result["ok"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.FAILED,
            error_message=result["error_message"] or "plugin callback schedule failed",
        )
    elif result["finished"]:
        PluginGatewayCallbackService.callback_run(
            open_plugin_run_id, run_status=PluginGatewayRun.Status.SUCCEEDED, outputs=result["outputs"]
        )
    # 未完成则继续等待下一次回调
```

- [ ] **Step 4: 实现网关内部回调入口**

`gcloud/apigw/views/plugin_gateway.py` 新增（沿用本文件既有装饰器组合与 `caller_app_code` 归属校验）：

```python
@login_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
def plugin_gateway_run_internal_callback(request, run_id):
    caller_app_code = getattr(request, "app", None) and request.app.bk_app_code
    body = _load_request_body(request)  # 已有的窄异常解析
    try:
        run = PluginGatewayExecutionService.get_run_detail(run_id, caller_app_code)
    except PluginGatewayRun.DoesNotExist:
        return {"result": False, "data": None, "code": err_code.CONTENT_NOT_EXIST.code}
    if run["status"] in PluginGatewayRun.Status.TERMINAL:
        return {"result": True, "data": {"status": run["status"]}}  # 终态幂等
    callback_plugin_gateway_run.apply_async(
        kwargs={"open_plugin_run_id": run_id, "callback_data": body.get("callback_data")},
        queue="open_plugin_callback",
    )
    return {"result": True, "data": {"open_plugin_run_id": run_id}}
```

在 `gcloud/apigw/urls.py` 注册：

```python
re_path(
    r"^plugin-gateway/runs/(?P<run_id>[0-9a-f]{32})/internal-callback/$",
    plugin_gateway.plugin_gateway_run_internal_callback,
    name="apigw_plugin_gateway_run_internal_callback",
),
```

- [ ] **Step 5: 运行测试至通过**

Run:
- `python manage.py test gcloud.tests.apigw.views.test_plugin_gateway -v 2`
- `python manage.py test gcloud.tests.plugin_gateway.test_dispatch -v 2`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add gcloud/apigw/views/plugin_gateway.py \
  gcloud/apigw/urls.py \
  gcloud/plugin_gateway/tasks.py \
  gcloud/tests/apigw/views/test_plugin_gateway.py \
  gcloud/tests/plugin_gateway/test_dispatch.py
git commit -m "feat: 插件网关支持回调型插件异步执行 --story=133649781"
```

---

### Task 8: 超时兜底 + 取消 best-effort + 错误映射

**Files:**
- Modify: `gcloud/plugin_gateway/tasks.py`（新增 `sweep_expired_plugin_gateway_runs` 周期任务）
- Modify: `gcloud/plugin_gateway/services/execution.py`（`cancel_run` best-effort）
- Modify: `gcloud/apigw/views/plugin_gateway.py`（登记期错误映射）
- Modify: `config/default.py`（注册 beat 周期任务）
- Modify: `gcloud/tests/plugin_gateway/test_execution.py`
- Modify: `gcloud/tests/apigw/views/test_plugin_gateway.py`

- [ ] **Step 1: 写超时/取消/错误映射失败测试**

`test_execution.py`：

```python
def test_sweep_marks_expired_running_failed(self):
    run = self._create_run(status=PluginGatewayRun.Status.RUNNING)
    run.execution_expire_at = timezone.now() - timedelta(seconds=1)
    run.save()
    with patch("gcloud.plugin_gateway.tasks.PluginGatewayCallbackService.callback_run") as mock_cb:
        sweep_expired_plugin_gateway_runs()
        self.assertEqual(mock_cb.call_args[1]["run_status"], PluginGatewayRun.Status.FAILED)

def test_cancel_already_terminal_is_idempotent(self):
    run = self._create_run(status=PluginGatewayRun.Status.SUCCEEDED)
    result = PluginGatewayExecutionService.cancel_run(run.open_plugin_run_id, "bkflow")
    self.assertEqual(result.run_status, PluginGatewayRun.Status.SUCCEEDED)  # 不回退终态
```

`test_plugin_gateway.py`（登记期错误 → 同步 4xx）：

```python
@patch("gcloud.apigw.views.plugin_gateway.PluginGatewayExecutionService.create_run")
def test_create_run_context_resolve_error_returns_400(self, mock_create):
    mock_create.side_effect = PluginGatewayContextResolveError("no project")
    resp = self.client.post("/apigw/plugin-gateway/runs/", data=json.dumps(self._valid_create_body()),
                            content_type="application/json")
    self.assertFalse(resp.json()["result"])
    self.assertEqual(resp.json()["code"], err_code.REQUEST_PARAM_INVALID.code)
```

- [ ] **Step 2: 运行失败测试**

Run:
- `python manage.py test gcloud.tests.plugin_gateway.test_execution -v 2`
- `python manage.py test gcloud.tests.apigw.views.test_plugin_gateway -v 2`

Expected: FAIL

- [ ] **Step 3: 超时兜底周期任务**

`gcloud/plugin_gateway/tasks.py`：

```python
@task(queue="open_plugin_polling")
def sweep_expired_plugin_gateway_runs():
    now = timezone.now()
    expired = PluginGatewayRun.objects.filter(
        execution_expire_at__lt=now
    ).exclude(run_status__in=list(PluginGatewayRun.Status.TERMINAL))
    for run in expired.iterator():
        PluginGatewayCallbackService.callback_run(
            run.open_plugin_run_id, run_status=PluginGatewayRun.Status.FAILED, error_message="execution timeout"
        )
```

在 `config/default.py` 的 `CELERYBEAT_SCHEDULE`（或等价 beat 配置）注册，建议每 60s 执行一次，路由到 `open_plugin_polling` 队列。

> `callback_token` TTL 不在 bk-sops 侧硬过期；以执行超时窗口 + BKFlow 节点 timeout 为兜底（spec §7）。

- [ ] **Step 4: `cancel_run` best-effort**

`gcloud/plugin_gateway/services/execution.py` 的 `cancel_run`：

- 已终态 → 原样返回（幂等，不回退）。
- 非终态 → best-effort 调底层取消（运行壳目前无统一取消原语，先记审计日志并置 `CANCELLED`），失败只记日志不抛错，然后回调 BKFlow。

```python
@classmethod
def cancel_run(cls, open_plugin_run_id, caller_app_code):
    run = PluginGatewayRun.objects.get(open_plugin_run_id=open_plugin_run_id, caller_app_code=caller_app_code)
    if run.run_status in PluginGatewayRun.Status.TERMINAL:
        return run
    try:
        # best-effort：运行壳暂无统一底层取消，记审计；后续按组件补 cancel 钩子
        logger.info("[plugin_gateway] best-effort cancel run=%s", open_plugin_run_id)
    except Exception:
        logger.exception("[plugin_gateway] cancel underlying failed run=%s", open_plugin_run_id)
    run.run_status = PluginGatewayRun.Status.CANCELLED
    run.save(update_fields=["run_status", "update_time"])
    PluginGatewayCallbackService.callback_run(open_plugin_run_id, run_status=PluginGatewayRun.Status.CANCELLED)
    return run
```

- [ ] **Step 5: 视图错误映射**

`gcloud/apigw/views/plugin_gateway.py` 的 `create_plugin_gateway_run`：捕获 `PluginGatewayContextResolveError`、`PluginGatewayPluginNotEnabledError`（黑名单/未开放）→ `REQUEST_PARAM_INVALID`（400）；`PluginGatewayConflictError` → 409（沿用现状）；运行期失败统一走异步回调 `FAILED`（不在同步响应内）。

- [ ] **Step 6: 运行测试至通过**

Run:
- `python manage.py test gcloud.tests.plugin_gateway.test_execution -v 2`
- `python manage.py test gcloud.tests.apigw.views.test_plugin_gateway -v 2`

Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add gcloud/plugin_gateway/tasks.py \
  gcloud/plugin_gateway/services/execution.py \
  gcloud/apigw/views/plugin_gateway.py \
  config/default.py \
  gcloud/tests/plugin_gateway/test_execution.py \
  gcloud/tests/apigw/views/test_plugin_gateway.py
git commit -m "feat: 插件网关补齐超时兜底取消与错误映射 --story=133649781"
```

---

### Task 9: APIGW 资源 / 中英文文档 / 部署说明同步

**Files:**
- Modify: `docs/zh_hans/apidoc/*.md`、`docs/en/apidoc/*.md`（v4 目录字段、execute `context`、内部回调）
- Modify: `gcloud/apigw/management/commands/data/api-resources.yml`（注册 internal-callback 资源）
- Modify: `gcloud/apigw/docs/apigw-docs.tgz`（重新打包）
- Modify: `docs/zh_hans/deploy/plugin_gateway_deploy.md`、`docs/en/deploy/plugin_gateway_deploy.md`（worker 队列、内置+异步已支持）
- Modify: `docs/specs/2026-04-21-plugin-gateway-design.md`（「实现现状与缺口」回写为已收敛）

- [ ] **Step 1: 更新中英文 apidoc**

- 目录接口补 `plugin_source / group / category / versions / default_version / latest_version`，明确 `builtin` 也会返回。
- execute 接口补可选 `context` 对象（字段 + 不传时 `default_project_id` 兜底）。
- 新增 `internal-callback` 接口文档。
- `polling.running_tag` 标注为 `RUNNING`。

- [ ] **Step 2: 注册资源并重打包**

按 `.ai/rules/api-change-checklist.mdc` 在 `api-resources.yml` 注册 internal-callback，然后按 `commit-message-convention.mdc` 的打包脚本重生成 tgz：

```bash
tmpdir=$(mktemp -d)
mkdir -p "$tmpdir/zh" "$tmpdir/en"
cp docs/zh_hans/apidoc/*.md "$tmpdir/zh/"
cp docs/en/apidoc/*.md "$tmpdir/en/"
tar -czf gcloud/apigw/docs/apigw-docs.tgz -C "$tmpdir" zh en
rm -rf "$tmpdir"
```

- [ ] **Step 3: 更新部署/设计文档**

- 部署指南补：`open_plugin_dispatch / open_plugin_polling / open_plugin_callback` 三个 worker 的启动命令与隔离说明、beat 超时兜底任务。
- 把 MVP 设计 `2026-04-21-plugin-gateway-design.md` 的「实现现状与缺口」更新为「已收敛（内置+第三方、同步/轮询/回调）」，并交叉引用本设计与本计划。

- [ ] **Step 4: Commit**

```bash
git add docs/zh_hans/apidoc docs/en/apidoc \
  gcloud/apigw/management/commands/data/api-resources.yml \
  gcloud/apigw/docs/apigw-docs.tgz \
  docs/zh_hans/deploy/plugin_gateway_deploy.md \
  docs/en/deploy/plugin_gateway_deploy.md \
  docs/specs/2026-04-21-plugin-gateway-design.md
git commit -m "docs: 同步插件网关全量能力接口与部署文档 --story=133649781"
```

---

### Task 10: 自检与回归

**Files:**
- Verify: 上述全部改动

- [ ] **Step 1: 全量插件网关测试**

Run: `python manage.py test gcloud.tests.plugin_gateway -v 2`
Expected: PASS

- [ ] **Step 2: APIGW 视图测试**

Run: `python manage.py test gcloud.tests.apigw.views.test_plugin_gateway -v 2`
Expected: PASS

- [ ] **Step 3: 第三方运行壳回归（重点）**

确认第三方插件从「直连 `PluginServiceApiClient.invoke`」切到「`remote_plugin` 运行壳」后行为等价；重点回归 `RemotePluginService.plugin_schedule` 中 `_get_node_start_time()`（`runtime.get_state(self.id)`）在无引擎节点时不崩（已被运行壳 try/except 兜底为 `FAILED` 或需对该路径打补丁）。必要时把无法在运行壳跑通的第三方插件临时进 `do_not_open_list`，并回写设计。

Run: `python manage.py test gcloud.tests.external_plugins -v 2`（若存在）
Expected: PASS 或明确记录已知限制

- [ ] **Step 4: 格式检查**

Run: `pre-commit run --files $(git diff --name-only HEAD~9)`（黑名单/格式/迁移检查）
Expected: PASS

- [ ] **Step 5: 自检清单（见文末 Verification Checklist）逐条确认**

- [ ] **Step 6: Commit（如有修补）**

```bash
git add -A
git commit -m "test: 插件网关全量能力回归与修补 --story=133649781"
```

---

## 当前交付边界（实事求是）

- ✅ 目录统一暴露内置 + 第三方，`group/category` 透传，`do_not_open_list` 三处一致拦截
- ✅ 组件运行壳（方案 B）真实执行：同步 / 轮询 / 回调
- ✅ `context` 混合解析 `project` + 真实 operator；不传 `context` → `default_project_id` 兜底
- ✅ 独立 worker 队列、超时兜底、取消 best-effort、错误映射
- ⏳ 已知限制（spec §11）：
  1. 运行壳上下文不完备的组件（强依赖全局密码变量 / 引擎节点状态 / 特殊 `parent_data`）需进黑名单
  2. 回调型组件「回调地址指向网关」的路由缝隙待联调确认
  3. 多版本插件不做进程级隔离
  4. 用户级凭证透传/代理身份不在本期

---

## Self-Review（spec 覆盖核对）

| spec 章节 | 对应 Task |
|---|---|
| §1 目录统一（内置适配/分类/schema/黑名单） | Task 2 |
| §2 组件运行壳（dispatch/polling/callback/约束） | Task 4 / 6 / 7 |
| §3 project/identity 解析 | Task 3 |
| §4 协议 `context` 读取与兜底 | Task 5 |
| §5 状态机与回调桥接（RUNNING/running_tag） | Task 1 / 2 / 5 / 6 / 7 |
| §6 worker 隔离 | Task 5 |
| §7 异步/取消/超时/错误/截断 | Task 6 / 8（截断沿用现有 `MAX_OUTPUT_BYTES`） |
| §8 安全边界（黑名单/白名单/跨应用/operator） | Task 2 / 5 / 8 |
| §9 测试与验收 | 各 Task TDD + Task 10 |
| §10 迁移与兼容 | Task 1 / 2 / 9 / 10 |
| §11 风险与后续 | 交付边界 + Task 7/10 风险标记 |

---

## Verification Checklist

- 目录返回内置 + 第三方，且 `categories` 与 `plugins` 的 `builtin` 一致
- `do_not_open_list` 命中项在 list 不可见、detail 404、execute 登记 4xx
- 内置插件经运行壳真实执行：同步成功、轮询完成、回调完成
- `context` 为 biz scope 时自动解析 `bk_biz_id → Project`；映射表与 `default_project_id` 兜底生效；都拿不到时 run 明确 `FAILED`
- operator 写入 `parent_data`，无权限时底层系统拒绝并回调 `FAILED`
- 三个 `open_plugin_*` 队列与存量 `pipeline_*` 队列隔离
- 超时兜底周期任务把过期 `RUNNING/WAITING_CALLBACK` 置 `FAILED` 并回调
- 不传 `context` 的老第三方来源零改造仍可执行（兼容回归）
- `apigw-docs.tgz` 与 apidoc 同步；`pre-commit` 全绿

---

## Notes For Executor

- 推荐顺序：Task 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10。先把模型/目录/解析/运行壳打通（同步可端到端），再叠加轮询、回调、治理与文档。
- 运行测试统一用 `python manage.py test <dotted.path> -v 2`（`DJANGO_SETTINGS_MODULE=settings`，依赖 `gcloud/tests/mock_settings`）；首次需确保 worktree 有可用 `local_settings.py` 与必要环境变量（参考 `docs/zh_hans/develop/dev_deploy.md`）。
- 任何改 `bkflow`/`apigw` 文档的 Task，提交前务必重打包 `apigw-docs.tgz`（见 `commit-message-convention.mdc` / `api-change-checklist.mdc`）。
- 运行壳是最大风险点：优先用 fake service 跑通契约，再用一个真实内置组件（如简单同步插件）做端到端联调，最后再放开依赖复杂 `parent_data` 的组件。
