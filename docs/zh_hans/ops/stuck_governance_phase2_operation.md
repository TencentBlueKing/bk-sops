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

- 已发布版本：`bamboo-pipeline==3.24.13`（依赖 `bamboo-engine==2.6.5`，含 `engine.py` 热路径钩子），均已在 PyPI。
- 标准运维 `requirements.txt` 已指向 `bamboo-pipeline==3.24.13`；装此一个包即拉齐 runtime 诊断 + core 钩子，不要指向未发布的未来版本。
- 发布后先在 stage 验证 `/admin/diagnostics/task/`、`/admin/diagnostics/cases/` 页面、证据包导出命令和 dry-run 操作。
- 观察 `[pipeline_diagnostics_alert]` 与 `[bk_sops_task_diagnostic_alert]` 日志是否符合预期。

## 灰度上线 checklist（M1 检测打底）

M1 只做“检测立案”，只读为主、执行热路径不变。按下述顺序灰度，任意步骤可秒级熔断。

**Step 0 前置（已就绪）**

- [ ] `requirements.txt` 已指向 `bamboo-pipeline==3.24.13`。
- [ ] 默认安全配置：`SCAN` 开、`EVENT`/`ALERT`/`APPLY` 关（见下方 env 速查）。

**Step 1 休眠部署（先关扫描，验证启动/迁移）**

- [ ] 部署前设 `BKAPP_DIAGNOSTICS_SCAN_ENABLED=0`，其余保持默认关。
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
| `BKAPP_DIAGNOSTICS_SCAN_ENABLED` | `1` | Layer0 周期扫描（检测立案） |
| `BKAPP_DIAGNOSTICS_EVENT_ENABLED` | `0` | 引擎热路径事件采集 |
| `BKAPP_DIAGNOSTICS_ALERT_ENABLED` | `0` | 告警 |
| `BKAPP_DIAGNOSTICS_APPLY_ENABLED` | `0` | 写 / 恢复操作（dry-run 之外） |
| `BKAPP_DIAGNOSTICS_SCAN_CRON` | `*/10 * * * *` | 扫描间隔 |
| `BKAPP_DIAGNOSTICS_CLEANUP_CRON` | `30 3 * * *` | 清理间隔 |
| `BKAPP_DIAGNOSTICS_STALL_THRESHOLD_SECONDS` | `3600` | 判定停滞的静默阈值（秒） |
| `BKAPP_DIAGNOSTICS_SCAN_BATCH` | `200` | 单轮扫描批量上限 |
