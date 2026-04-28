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

- 确认 `bamboo-engine` 二期代码已发布为新的 `bamboo-pipeline` 包。
- 确认标准运维 `requirements.txt` 使用同一个已发布版本，不要指向未发布的未来版本。
- 发布后先在 stage 验证 `/admin/diagnostics/task/` 页面、证据包导出命令和 dry-run 操作。
- 观察 `[pipeline_diagnostics_alert]` 与 `[bk_sops_task_diagnostic_alert]` 日志是否符合预期。
