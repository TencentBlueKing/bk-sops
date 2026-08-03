# 流程卡住治理二期运维说明

## 目标

流程卡住治理二期用于把“流程为什么卡住、证据在哪里、哪些操作可以安全尝试”沉淀成通用能力。底层诊断能力优先放在 `bamboo-engine`，标准运维只补充 `task_id`、子任务关系、callback 记录等业务侧证据。

## 入口

- Engine 通用入口：使用 `root_pipeline_id`、`process_id`、`node_id` 诊断引擎运行时。
- 标准运维入口：访问 `/admin/diagnostics/task/`，按 `task_id` 和可选 `node_id` 查询。
- 命令行证据包：执行 `python manage.py export_task_diagnostic_evidence <task_id> --node-id <node_id> --output evidence.json`。

## 诊断类型

第一版覆盖以下通用卡住类型：

- `callback_lock_conflict`
- `schedule_lock_stuck`
- `missing_state_for_live_process`
- `process_alive_but_terminal_state`
- `parallel_ack_not_converged`
- `multiple_sleep_process_for_node`
- `schedule_finished_but_process_not_exited`

诊断结果会包含严重级别、置信度、证据、关联对象、推荐动作和禁止动作。排查时优先看证据中的 `process_id`、`schedule_id`、`callback_data_id`、`root_pipeline_id`、`node_id`。

## 操作原则

所有写操作必须先 `dry_run`，确认预检查通过后才能 `apply`。`apply` 需要重新校验并写入审计记录。

允许的一期低风险动作：

- `inspect_ack_converge`
- `inspect_node_runtime_readiness`
- `replay_callback_data`
- `resend_schedule`
- `expire_stale_schedule`

禁止直接操作：

- 不要直接修改 state/process。
- 不要手工补 ACK。
- 不要强制唤醒父进程。
- 不要强推后继节点。
- 不要批量 apply。

## 熔断

如果诊断事件入库、扫描任务、告警或写操作对现网有影响，优先关闭对应开关：

- `PIPELINE_DIAGNOSTICS_EVENT_ENABLED`
- `PIPELINE_DIAGNOSTICS_SCAN_ENABLED`
- `PIPELINE_DIAGNOSTICS_CASE_ENABLED`
- `PIPELINE_DIAGNOSTICS_ALERT_ENABLED`
- `PIPELINE_DIAGNOSTICS_APPLY_ENABLED`
- `PIPELINE_DIAGNOSTICS_BATCH_OPERATION_ENABLED`

## 发布检查

- 已发布版本：`bamboo-pipeline==3.24.14`（依赖 `bamboo-engine==2.6.5`，含 `engine.py` 热路径钩子），均已在 PyPI。
- 标准运维 `requirements.txt` 已指向 `bamboo-pipeline==3.24.14`；装此一个包即拉齐 runtime 诊断 + core 钩子，不要指向未发布的未来版本。
- 3.24.14 相对 3.24.13 的增量：`child_process_finish` 重复 ACK 幂等修复；M2 可靠事件 `pipeline.contrib.reliable_events` 随包提供但未注册进 `INSTALLED_APPS`，不建表不生效，M1 灰度不受影响。
- 发布后先在 stage 验证 `/admin/diagnostics/task/`、`/admin/diagnostics/cases/` 页面、证据包导出命令和 dry-run 操作。
- 观察 `[pipeline_diagnostics_alert]` 与 `[bk_sops_task_diagnostic_alert]` 日志是否符合预期。

## 灰度上线 checklist（M1 检测打底）

M1 只做“检测立案”，只读为主、执行热路径不变。按下述顺序灰度，任意步骤可秒级熔断。

**Step 0 前置（已就绪）**

- [ ] `requirements.txt` 已指向 `bamboo-pipeline==3.24.14`。
- [ ] 默认安全配置：`SCAN`/`EVENT`/`ALERT`/`APPLY` 全关（见下方 env 速查）。

**Step 1 休眠部署（先关扫描，验证启动/迁移）**

- [ ] 保持默认即可（四个开关默认均为 `0`），无需额外设置环境变量。
- [ ] 部署 → 确认 `migrate` 正常新建 3 张 `pipeline_diagnostics_*` 表（纯 `CREATE TABLE`，不动存量表）。
- [ ] 确认 web / celery worker / beat 正常启动，无 `pipeline.contrib.diagnostics` import 报错（app 为条件注册）。
- [ ] 确认引擎执行热路径行为不变（`EVENT` 关，2.6.5 钩子处于“装好但睡眠”态）。

**Step 2 灰度开扫描（盯 DB）**

- [ ] 设 `BKAPP_DIAGNOSTICS_SCAN_ENABLED=1`；可先把 `BKAPP_DIAGNOSTICS_SCAN_CRON` 调保守（如 `*/30 * * * *`）。
- [ ] 盯 `eri_process` 上 Layer0 分组查询（`SELECT root_pipeline_id, MAX(last_heartbeat) ... WHERE dead=0 GROUP BY root_pipeline_id`）的慢查询 / DB 负载 1–2 天。
- [ ] 在 `/admin/diagnostics/cases/` 查看是否正常产出“病历”；核对 `[pipeline_diagnostics_alert]` 日志。
- [ ] 超大实例若有压力：扫描指向只读从库 / 调大间隔 / 或 `SCAN_ENABLED=0` 熔断。

**Step 3 全量**

- [ ] 负载可控后恢复默认间隔 `*/10 * * * *`，全量开 `SCAN`。
- [ ] 确认 `cleanup` 每日 `30 3 * * *` 正常清理过期数据（保留：event 30d / case 365d / audit 365d）。

**（可选，后续）开热路径事件采集**

- [ ] 需要 schedule-lock 冲突等热路径事件时，设 `BKAPP_DIAGNOSTICS_EVENT_ENABLED=1`（2.6.5 钩子已在，无需重新发包）；先小范围观察 `DiagnosticEvent` 写入量。

**熔断 / 回滚（任意步骤）**

- [ ] 秒级：把对应 `BKAPP_DIAGNOSTICS_*_ENABLED` 置 `0`，无需重新部署。
- [ ] 代码回滚：`requirements.txt` pin 回 `bamboo-pipeline==3.24.11`；残留空表无害、无需清理。

### env 开关速查

| 环境变量 | 默认 | 作用 |
| --- | --- | --- |
| `BKAPP_DIAGNOSTICS_SCAN_ENABLED` | `0` | Layer0 周期扫描（检测立案） |
| `BKAPP_DIAGNOSTICS_EVENT_ENABLED` | `0` | 引擎热路径事件采集 |
| `BKAPP_DIAGNOSTICS_ALERT_ENABLED` | `0` | 告警 |
| `BKAPP_DIAGNOSTICS_APPLY_ENABLED` | `0` | 写 / 恢复操作（dry-run 之外） |
| `BKAPP_DIAGNOSTICS_SCAN_CRON` | `*/10 * * * *` | 扫描间隔 |
| `BKAPP_DIAGNOSTICS_CLEANUP_CRON` | `30 3 * * *` | 清理间隔 |
| `BKAPP_DIAGNOSTICS_STALL_THRESHOLD_SECONDS` | `3600` | 判定停滞的静默阈值（秒） |
| `BKAPP_DIAGNOSTICS_SCAN_BATCH` | `200` | 单轮扫描批量上限 |

---

## 灰度上线 checklist（M2 可靠事件 / callback 兜底接管）

M1 只“立案”，卡住了能看见但救不回来。M2 在此之上加一条**可靠事件**旁路：callback 落库时同时记一条
`EngineEventInbox` 事件，消费者作为**幂等兜底**在直接驱动没成功时重放 schedule。
能力随 `bamboo-pipeline>=3.24.14` 提供，bk-sops 侧负责「哪些流程允许被接管」的白名单判定。

**四个开关的关系（先理解再操作）**

- `SHADOW`：只记录、只比对，**不改引擎状态**。用于铺底观测。
- `ACTIVE`：允许兜底重放。它是**总闸**，且必须叠加白名单——两者同时满足才会接管。
- `DISPATCH`：callback 落库后立即投递消费任务。关掉则只靠 `COMPENSATION` 的周期补偿兜底。
- `COMPENSATION`：周期补偿扫描 + 保留期清理（`purge_scan` 同样受它管）。

`SHADOW` / `ACTIVE` 至少开一个，collector 才会写事件；全关则 collector 首行 return，**零写入**。

**Step 0 前置（已就绪）**

- [ ] `requirements.txt` 已指向 `bamboo-pipeline==3.24.14`。
- [ ] `pipeline.contrib.reliable_events` 已条件注册进 `INSTALLED_APPS`。
- [ ] 默认安全配置：四个 `BKAPP_RELIABLE_EVENTS_*` 开关全关（见下方 env 速查）。

**Step 1 休眠部署（先不开任何开关）**

- [ ] 保持默认即可，无需设置环境变量。
- [ ] 部署 → 确认 `migrate` 正常新建 2 张 `pipeline_reliable_events_*` 表（纯 `CREATE TABLE`，不动存量表）。
- [ ] 确认 `compensation_scan` / `purge_scan` 已被 beat 自动排程（由 `@periodic_task` 自注册，
      **不要**再往 `CELERYBEAT_SCHEDULE` 手工登记，否则同一任务会被排两次）。
- [ ] 确认引擎执行热路径行为不变（开关全关 = collector 不写、callback 响应不变）。

**Step 2 G2 影子铺底（只观测，不改引擎状态）**

- [ ] 设 `BKAPP_RELIABLE_EVENTS_SHADOW_ENABLED=1` + `BKAPP_RELIABLE_EVENTS_COMPENSATION_ENABLED=1`，
      `ACTIVE` 保持 `0`。
- [ ] 采 1~2 周，看：Inbox 覆盖率、`idempotency_key` 冲突率、`SHADOW_MISMATCH` 率（≈ 一期竞态命中）、DB 写放大。
- [ ] **注意**：`SHADOW` 是全局的，不受白名单约束，开启即全量流量都会写事件。
      Inbox 增长速度约等于 callback 速率，需同步关注表体积与 `purge_scan` 是否在正常回收。

**Step 3 G3 白名单 ACTIVE 兜底（开始真正救流程）**

- [ ] 先给 1~2 个内部 / 低敏业务或模板配白名单（见下方配置方法）。
- [ ] 再设 `BKAPP_RELIABLE_EVENTS_ACTIVE_ENABLED=1` + `BKAPP_RELIABLE_EVENTS_DISPATCH_ENABLED=1`。
      顺序很重要：**先配白名单再开总闸**，避免开闸瞬间范围失控。
- [ ] 观测：`APPLIED` 比例、兜底真正触发重放（`attempts>=1` 后 `APPLIED`）的数量 = 实际救回的卡住数、
      `MANUAL_REQUIRED` 数量与原因（应极少且都是真需人工）、与直接驱动的锁竞争噪声（`LEASE_BUSY`）、
      有无重复业务副作用（对比 `Schedule.schedule_times` 与组件输出）。
- [ ] 逐步扩白名单。

### ACTIVE 白名单配置方法

白名单存在 `TaskConfig` 表，`config_type=3`（`CONFIG_TYPE_ACTIVE_CALLBACK`），**模板级优先于项目级**。

```python
# python manage.py shell
from gcloud.taskflow3.models import TaskConfig

# 按项目整体开启（该项目下所有流程）
TaskConfig.objects.create(
    scope=TaskConfig.SCOPE_TYPE_PROJECT, scope_id=<project_id>,
    config_type=TaskConfig.CONFIG_TYPE_ACTIVE_CALLBACK,
    config_value=TaskConfig.ENABLE_ACTIVE_CALLBACK,
)

# 按业务流程模板开启
TaskConfig.objects.create(
    scope=TaskConfig.SCOPE_TYPE_TEMPLATE, scope_id=<template_id>,
    config_type=TaskConfig.CONFIG_TYPE_ACTIVE_CALLBACK,
    config_value=TaskConfig.ENABLE_ACTIVE_CALLBACK,
)

# 在已开启的项目里单独排除某个模板：用 DISABLE 覆盖（模板级优先）
TaskConfig.objects.create(
    scope=TaskConfig.SCOPE_TYPE_TEMPLATE, scope_id=<template_id>,
    config_type=TaskConfig.CONFIG_TYPE_ACTIVE_CALLBACK,
    config_value=TaskConfig.DISABLE_ACTIVE_CALLBACK,
)
```

**公共流程（CommonTemplate）**沿用仓内既有约定，模板级配置的 `scope_id` 记为**负的** template_id：

```python
TaskConfig.objects.create(
    scope=TaskConfig.SCOPE_TYPE_TEMPLATE, scope_id=-<common_template_id>,
    config_type=TaskConfig.CONFIG_TYPE_ACTIVE_CALLBACK,
    config_value=TaskConfig.ENABLE_ACTIVE_CALLBACK,
)
```

公共流程创建的任务同时也能回落到它**真实所属项目**的项目级配置，所以“按项目整体开启”对公共流程任务同样生效。

**熔断 / 回滚（任意步骤，均无需重新部署）**

- [ ] 最快回滚：`BKAPP_RELIABLE_EVENTS_ACTIVE_ENABLED=0` → 所有事件降级为 SHADOW，引擎行为等价于 M2 之前。
- [ ] 完全停用：`SHADOW` 与 `ACTIVE` 都置 `0` → collector 首行 return，零写入。
- [ ] 紧急停消费：`COMPENSATION=0` + `DISPATCH=0` → 事件留在 Inbox（`PENDING`），不消费也不清理，处理完再开。
- [ ] 代码回滚：因全默认关且 ACTIVE 是 additive 兜底，相关变更可长期休眠，一般无需回退版本。

### env 开关速查（M2）

| 环境变量 | 默认 | 作用 |
| --- | --- | --- |
| `BKAPP_RELIABLE_EVENTS_SHADOW_ENABLED` | `0` | 影子记录（全局生效，不受白名单约束） |
| `BKAPP_RELIABLE_EVENTS_ACTIVE_ENABLED` | `0` | 兜底接管总闸（须叠加白名单才实际接管） |
| `BKAPP_RELIABLE_EVENTS_DISPATCH_ENABLED` | `0` | callback 落库后立即投递消费任务 |
| `BKAPP_RELIABLE_EVENTS_COMPENSATION_ENABLED` | `0` | 周期补偿扫描 + 保留期清理 |

引擎侧还有一批调优项（`CONVERGE_SECONDS` / `LEASE_SECONDS` / `MAX_ATTEMPTS` / `BACKOFF_*` /
`COMPENSATION_BATCH` / `EVENT_RETENTION_DAYS` / `ACTIVE_INITIAL_DELAY_SECONDS`），
bk-sops 未透出为环境变量，取包内默认值；确有调优需要时再按 `PIPELINE_RELIABLE_EVENTS_<NAME>` 补到 settings。

### 已知运维考量

- **队列归属**：`compensation_scan` / `purge_scan` / `dispatch_event` 均走 default 队列（`dworker`），
  未单独路由。开启 `DISPATCH` 后该队列会新增约等于 callback 速率的任务量，需关注队列堆积。
- **Inbox 查询索引**：v4 callback 响应里的 `accepted` / `event_id` 依赖
  `(root_pipeline_id, node_id, version)` 联合索引的最左前缀。当前引擎写入时 `root_pipeline_id` 为空串，
  查询已按此适配；若后续引擎改为回填真实 root id，该查询仍然正确。
  Inbox / Lane 两张新表的索引会在 M2 全部落地后统一 review。
- **表体积**：`purge_scan` 只回收 `APPLIED` / `OBSOLETE` 的终态事件（默认保留 30 天），
  `MANUAL_REQUIRED` 与异常明细会保留，需定期人工消化。
