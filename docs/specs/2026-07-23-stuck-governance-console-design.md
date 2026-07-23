# 卡住流程治理控制台（bk-sops 侧）设计

- 状态: Draft
- 日期: 2026-07-23
- 作者: dengyh (+ AI 协作)
- 关联:
  - 总体设计: `docs/specs/2026-07-20-stuck-governance-design.md`
  - M1 检测打底: PR TencentBlueKing/bk-sops#8424（已合入 master）
  - 引擎侧诊断能力: `bamboo-pipeline 3.24.13` / `bamboo-engine 2.6.5`（`pipeline.contrib.diagnostics`）

## 1. 背景与问题

M1 检测打底已上线：bamboo-engine 侧的 `pipeline.contrib.diagnostics` 会把"卡住的流程"沉淀为
三张底层表（`DiagnosticEvent` / `DiagnosticCase` / `DiagnosticOperationAudit`），bk-sops 侧提供了
只读 JSON 端点（`/admin/diagnostics/cases/`、`/admin/diagnostics/cases/detail/`）和一个按 task_id
诊断单任务的极简页面（`/admin/diagnostics/task/`）。

现状的管理面存在两个问题：

1. **底层表难以直接管理**：`DiagnosticCase` 里是 bamboo-engine 的底层标识（`root_pipeline_id` /
   `node_id`），管理员在 Django admin 里看到的是裸 ID，无法直接对应到"哪个业务、哪个任务、哪个模板、
   哪个节点"，需要人工反查关联，效率低。
2. **只有数据、没有运营入口**：目前只能通过 Django admin（需要 Django `is_staff` + admin 登录，SSO
   环境不便）或裸 JSON 接口查看，没有一个"能筛选、能点进任务、能改状态、能跑恢复动作"的运营页面。

**为什么放在 bk-sops 侧**：把 `root_pipeline_id` / `node_id` 反向映射回任务 / 模板 / 业务 / 执行人 /
可点击链接 / 节点名，这层映射只有标准运维（bk-sops）的代码清楚。bamboo-engine 是通用引擎，不该也无法
感知 bk-sops 的任务模型。

## 2. 目标与非目标

### 目标
- 在 bk-sops `/admin/` 下新增一个**超管专用的「卡住流程治理控制台」**（单页）。
- 把底层 `DiagnosticCase` 关联回**具体任务 / 模板 / 业务 / 执行人 + 可点击跳转 + 节点名**。
- 支持**病历状态管理**（待治理 ↔ 已解决 / 已忽略）。
- 支持**按 case 直接跑诊断 / 恢复动作**（dry-run 出结果；apply 受 `APPLY_ENABLED` 开关约束）。
- 仅平台超管、全局可见。

### 非目标（YAGNI）
- 不做业务 / 项目级隔离权限（M1 只需超管全局）。
- 不接入 bk-sops 主 Vue SPA（`frontend/desktop`）；保持与现有 admin 诊断页一致的独立模板形态。
- 不新增数据库字段 / 迁移；复用现有 `pipeline.contrib.diagnostics` 模型。
- 不改动 bamboo-engine（全部改动落在 bk-sops 侧；引擎侧只被调用）。

## 3. 约束与既有事实（已核实）

- `DiagnosticCase` 状态只有三态：`open`(待治理) / `resolved`(已解决) / `ignored`(已忽略)。
- `DiagnosticCase.Meta.unique_together = (("root_pipeline_id", "node_id", "stuck_type", "status"),)`。
  - **含义**：手动把某个 case 从 `open` 改成 `resolved`/`ignored` 时，若已存在同
    `(root_pipeline_id, node_id, stuck_type, 目标状态)` 的"孪生 case"，裸 `update(status=...)` 会触发
    `IntegrityError`。**状态写必须走"合并 + 删重复"逻辑**（复用引擎 `pipeline.contrib.diagnostics.cases`
    中 `_resolve_one` 的思路：把命中/时间并入孪生 case，删除本行）。
- `DiagnosticOperationAudit`：有 `case`(FK) / `operation_type` / `operator` / `mode`(dry_run/apply) /
  `risk_level` 等字段，用于记录每一次动作。状态变更也应写审计。
- 恢复动作可复用 bk-sops 侧现有 `gcloud/contrib/admin/diagnostics/actions.py::run_task_action`：
  - `inspect_ack_converge` / `inspect_node_runtime_readiness`（只读诊断，需 `root_pipeline_id`+`node_id`）；
  - `replay_callback_data`（需 `callback_data_id`）；
  - `resend_schedule` / `expire_stale_schedule`（需 `schedule_id`）。
  - 这些参数可从 `case.root_pipeline_id` / `case.node_id` / `case.evidence` / `case.related_objects` 取到。
- 反向映射数据源：`TaskFlowInstance.objects.filter(pipeline_instance__instance_id__in=[...])`
  （`pipeline_instance.instance_id == root_pipeline_id`）。
- 节点名：从任务的 pipeline tree（`pipeline_instance.execution_data` / `execution_snapshot`）按
  `node_id` 解析，开销较大，**仅在详情视图做**，列表页不做。

## 4. 架构与数据流

```
浏览器（超管）
   │  GET /admin/diagnostics/board/            → 渲染页面壳 cases.html
   │  GET /admin/diagnostics/cases/            → 列表 JSON（已有，增强：批量反向映射）
   │  GET /admin/diagnostics/cases/detail/     → 详情 JSON（已有，增强：任务上下文+节点名+审计历史）
   │  POST /admin/diagnostics/cases/status/    → 改状态（新增，合并+删重复+写审计）
   │  POST /admin/diagnostics/cases/action/    → 按 case 跑诊断/恢复（新增，复用 run_task_action）
   ▼
gcloud/contrib/admin（views + diagnostics 适配层）
   │  反向映射: root_pipeline_id → TaskFlowInstance（批量）
   │  节点名:   node_id → pipeline tree（仅详情）
   ▼
pipeline.contrib.diagnostics（bamboo-engine，只被调用，不改）
   DiagnosticCase / DiagnosticOperationAudit / operations / cases
```

所有跨层调用 **fail-safe**：映射 / 节点名解析 / 诊断能力不可用时降级（显示原始 ID、返回可读错误），
不阻塞页面主流程。

## 5. 后端设计（gcloud/contrib/admin）

### 5.1 端点清单

| 方法 | 路径 | 说明 | 状态 |
| --- | --- | --- | --- |
| GET | `/admin/diagnostics/board/` | 渲染控制台页面壳 `cases.html` | 新增 |
| GET | `/admin/diagnostics/cases/` | 病历列表 JSON（分页 + 筛选 + **批量任务上下文**） | 增强 |
| GET | `/admin/diagnostics/cases/detail/` | 病历详情 JSON（**任务上下文 + 节点名 + 审计历史**） | 增强 |
| POST | `/admin/diagnostics/cases/status/` | 改 case 状态（合并+删重复+写审计） | 新增 |
| POST | `/admin/diagnostics/cases/action/` | 按 case_id 跑诊断/恢复动作 | 新增 |

- 页面壳与 JSON 列表端点**分开路由**（`board/` vs `cases/`），避免"同一路径既返回 HTML 又返回 JSON"。
- 权限：读端点用 `@check_is_superuser()` + `@iam_intercept(AdminViewViewInterceptor())`；
  写 / 动作端点用 `@check_is_superuser()` + `@iam_intercept(AdminEditViewInterceptor())`；
  GET/POST 用 `@require_GET` / `@require_POST`。与现有诊断视图完全一致。

### 5.2 列表增强（批量反向映射，避免 N+1）

- 现有 `diagnostic_case_list` 拉到当前页的 `DiagnosticCase` 后：
  1. 收集本页所有 `root_pipeline_id`；
  2. 一次查询 `TaskFlowInstance.objects.filter(pipeline_instance__instance_id__in=ids)
     .select_related("pipeline_instance", "project")`，构建 `root_pipeline_id -> task 摘要` 字典；
  3. 序列化时为每行补充 `task`(id/name/url) / `project`(id/name) / `template_id` / `executor` /
     `create_time`；查不到则该行 `task=None`，仅显示 `root_pipeline_id`。
- 任务链接：用现有任务执行页路由构造（实现阶段确认确切 URL 形态，例如
  `/taskflow/execute/{project_id}/?instance_id={task_id}`，以 `SITE_URL` 前缀拼接）。

### 5.3 详情增强

- 在现有 `diagnostic_case_detail` 返回基础上补：
  - `task` / `project` / `template` / `executor` / `create_time`（同上反向映射，单条）；
  - `node_name`：加载该任务 pipeline tree，按 `case.node_id` 解析节点名（fail-safe）；
  - `audit_history`：`DiagnosticOperationAudit.objects.filter(case_id=case.id).order_by("-created_at")`
    序列化最近 N 条。

### 5.4 状态写（关键：处理 unique_together 冲突）

- 新增 bk-sops 适配层函数 `set_case_status(case_id, target_status, operator)`，落在新文件
  `gcloud/contrib/admin/diagnostics/cases_admin.py`（合并逻辑参考引擎 `cases._resolve_one` 思路，
  但不改引擎代码）：
  1. 校验 `target_status ∈ {open, resolved, ignored}`；
  2. 加载 case；若当前状态 == 目标状态 → no-op；
  3. 在 `transaction.atomic()` 内查是否存在孪生
     `(root_pipeline_id, node_id, stuck_type, status=target_status)`：
     - 存在 → 把本 case 的 `hit_count` / `last_seen_at`（取较大/较新）并入孪生 case，`save`，
       然后删除本 case；审计记录挂到**孪生 case**；
     - 不存在 → `case.status = target_status; case.save(update_fields=[...])`；审计挂本 case；
  4. 写一条 `DiagnosticOperationAudit`（`operation_type="set_status:<target>"`, `mode=apply`,
     `risk_level=low`, `operator`）。
- 视图 `diagnostic_case_status(request)`：`@require_POST` + 超管 + `AdminEditViewInterceptor`，
  解析 body(`case_id`, `status`)，调用 `set_case_status`，返回 `{result, data/ message}`。

### 5.5 按 case 跑动作

- 新增视图 `diagnostic_case_action(request)`：`@require_POST` + 超管 + `AdminEditViewInterceptor`。
- 解析 body：`case_id`, `action`, `mode`(默认 dry_run), 及可选 `schedule_id` / `callback_data_id`。
- 加载 case → 组装参数：`root_pipeline_id=case.root_pipeline_id`, `node_id=case.node_id`,
  `schedule_id`/`callback_data_id` 优先取 body，其次从 `case.evidence`/`case.related_objects` 兜底。
- 复用 `run_task_action(task_id=<可选/None>, node_id, action, operator, mode, **参数)`；apply 模式下
  引擎 operations 内部已受 `APPLY_ENABLED` 约束，未开启时返回 blocked。
- 返回 operation result（含 dry-run 预览 / blockers）。

## 6. 前端设计（方案 A：独立模板 + 原生 JS）

- 新增 `gcloud/contrib/admin/templates/diagnostics/cases.html`：
  - 顶部筛选栏：`status` / `stuck_type` / `severity` / 关键字（root_pipeline_id、task_id、任务名）/ 刷新。
  - 列表表格列：任务名（→ 可点跳任务执行页）| 业务 | 模板 | `stuck_type` | `severity` | `status` |
    卡住时长(`evidence.stall_seconds`) | 命中次数 | 最近出现 | 详情。
  - 详情抽屉 / 弹层：关联信息 + 诊断信息（`message` / `confidence` / `evidence` 格式化 JSON /
    推荐 & 禁止动作）+ 操作审计历史 + 动作区：
    - 状态切换：待治理 → 已解决 / 已忽略（含二次确认）；
    - 诊断 / 恢复：`inspect_*`（只读）、`resend_schedule` / `expire_stale_schedule` /
      `replay_callback_data`；先 dry-run 显示结果，`apply` 按钮在环境未开启时**禁用并提示**。
  - 交互：原生 `fetch`；写请求带 `X-CSRFToken`（从 cookie 读取）；少量内联 CSS，无需前端构建。
- 在现有 `task_diagnostic.html` 增加到控制台的互链，反之亦然。

## 7. 测试

沿用 `gcloud/tests/contrib/admin/diagnostics/` 测试范式（`RequestFactory` + mock `iam_intercept`，
诊断能力不可用时 `skip`）：

- **列表增强**：批量反向映射正确、命中/未命中降级、分页 & 筛选保持。
- **详情增强**：任务上下文 + 节点名（含解析失败降级）+ 审计历史。
- **状态写**：`open→resolved` 正常；**目标状态存在孪生 case 时合并、不报 `IntegrityError`**；
  写入审计；`open→open` no-op；非法状态被拒。
- **按 case 动作**：dry-run 参数组装正确并调用；`apply` 在 `APPLY_ENABLED=False` 时被拦（blocked）。
- **权限**：非超管 403；`require_GET`/`require_POST` 生效。

## 8. 兼容性、风险与回滚

- **无 DB 迁移**：复用现有模型，零 schema 变更。
- **诊断能力缺失兼容**：所有对 `pipeline.contrib.diagnostics` 的引用 `try/except ImportError` 降级，
  引擎包未安装时页面返回可读提示而非 500。
- **读多写少**：列表 / 详情为读操作；批量映射把额外 DB 查询压到"每页一次"。节点名解析仅详情触发。
- **写操作风险**：状态变更是低风险（仅改本插件表）；恢复动作 apply 受 `APPLY_ENABLED` 全局开关约束，
  M1 环境默认关闭，页面按钮禁用兜底。
- **回滚**：本功能是纯新增页面 + 端点，回滚只需下线路由 / 回退分支，不影响 M1 检测与引擎。

## 8.1 已知限制 (M1)

按 case 执行诊断/恢复动作时,审计记录 `DiagnosticOperationAudit` 由引擎 `operations._audit` 写入且**不带
`case` 外键**(受"不改 bamboo-engine"约束,M1 不修改引擎)。因此这类动作审计会出现在 Django admin / 全局
审计表中,但**不会**出现在控制台案例详情的"操作审计(audit_history)"列表里(该列表按 `case_id` 过滤)。
而案例状态变更(set_case_status)的审计**会**正确关联到 case。后续迭代可在引擎侧补 `case` 外键,或在
bk-sops 详情侧按 `root_pipeline_id`+`node_id`/`target_object` 匹配补齐。

## 9. 落地约定

- 分支：`feat/stuck-governance-console`（基于 `upstream/master`，已含 M1）；单独出 PR，push 到 `origin`(fork)。
- 提交信息遵循 `.ai/rules/commit-message-convention.mdc`（含 TAPD 单号）。
- 本设计文档随分支提交；实现计划由 writing-plans 产出到 `docs/plans/`。
