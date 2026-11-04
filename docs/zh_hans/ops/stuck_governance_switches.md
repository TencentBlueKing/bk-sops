# 流程卡住治理：统一开关与旧配置迁移

本说明适用于包含统一开关改动的 bk-sops 版本，运行时依赖仍为 `bamboo-pipeline==3.24.22`。只升级运行时包不会增加这些应用侧配置。

## 三个统一入口

| 环境变量 | 可选值 | 作用 |
| --- | --- | --- |
| `BKAPP_DIAGNOSTICS_DETECTION_ENABLED` | `0` / `1` | 关闭 / 开启定时检测，包含无动静兜底扫描、丢失类型扫描、回调扫描和“任务运行中但没有存活进程”的补充检测 |
| `BKAPP_PIPELINE_FENCE_MODE` | `off` / `observe` / `enforce` | 防重复检查：关闭 / 消息带上预期状态但只观察 / 消息带上预期状态并拦截不匹配消息 |
| `BKAPP_DIAGNOSTICS_RECOVERY_POLICY` | `off` / `preview` / `auto` | 周期恢复：停止新增恢复计划 / 只预览 / 在允许的项目和类型范围内自动恢复 |

**三个新入口都不设置时，继续使用旧配置，原有行为不变。** 这包括原先不受扫描开关控制的补充检测，以及旧 `RECOVERY_ENABLED=0` 同时停止回查的行为。不要把“不设置新配置”等同于新配置设为 `off`。

新恢复入口使用 `RECOVERY_POLICY`，避免重新解释旧 `BKAPP_DIAGNOSTICS_RECOVERY_MODE=preview/apply`。新 `auto` 对应引擎的 `apply`，旧变量仍只接受其原有语义。

## 检测范围

`BKAPP_DIAGNOSTICS_DETECTION_ENABLED=1` 默认启用四种定时扫描，使用窗口扫描替代旧取样扫描。需要分批开启时，可额外设置 `BKAPP_DIAGNOSTICS_SCANNERS`：

| 值 | 扫描内容 |
| --- | --- |
| `window` | 无动静兜底扫描 |
| `signature` | 丢失类型扫描；S7 是否参与仍由 S7 开关决定 |
| `callback` | 回调扫描 |
| `supplement` | 补充检测，以及这类案例恢复后的关闭检查 |

多个值用逗号分隔；不设置表示四种全选，显式空字符串表示全不选。只配置 `SCANNERS` 而不配置检测总开关会在启动时报错。

总开关为 `0` 时，上述定时任务在获取 Redis 锁或查询数据库前返回，也不会继续复核并关闭这些扫描器负责的案例。周期任务仍保留注册，不需要删除定时任务记录。

检测总开关不影响人工诊断、显式执行的补扫命令、事件记录、告警、历史数据清理或已有案例的恢复。已有恢复记录的回查由恢复模式控制。

## 防重复检查与恢复

| 新配置 | 兼容到原有配置 |
| --- | --- |
| `FENCE_MODE=off` | `FENCE_EMIT_ENABLED=0`、`FENCE_ENFORCE=0` |
| `FENCE_MODE=observe` | `FENCE_EMIT_ENABLED=1`、`FENCE_ENFORCE=0` |
| `FENCE_MODE=enforce` | `FENCE_EMIT_ENABLED=1`、`FENCE_ENFORCE=1` |
| `RECOVERY_POLICY=off` | 停止新增预览和自动恢复，只回查已创建的恢复记录 |
| `RECOVERY_POLICY=preview` | `RECOVERY_ENABLED=1`、`RECOVERY_MODE=preview` |
| `RECOVERY_POLICY=auto` | `RECOVERY_ENABLED=1`、`RECOVERY_MODE=apply` |

`off` 的回查沿用原来的等待时间、批量上限和恢复任务锁；已发出的记录会更新为 `applied`、`ineffective` 或 `obsolete`，已有预览或不能重放的记录会记下回查结果。它不会补发消息，也不会撤回已经发出的消息。旧配置保持 `RECOVERY_ENABLED=0` 时仍完全不运行恢复任务。

自动恢复仍受 `BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES`、`BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS`、限次、间隔、每轮上限和自动暂停规则约束。范围为空时不会自动恢复；范围外的案例仍只预览。执行和轮询类恢复还要求 `FENCE_MODE=enforce`，回调类沿用原有调度检查。

`BKAPP_DIAGNOSTICS_APPLY_ENABLED` 继续单独控制人工写操作。`RECOVERY_POLICY=auto` 不会开启人工操作，`off` 也不会关闭已单独开启的人工操作。要停止所有新增恢复，应同时设置 `RECOVERY_POLICY=off` 和 `BKAPP_DIAGNOSTICS_APPLY_ENABLED=0`。

S7 的 `BKAPP_PIPELINE_SYNC_ADVANCE_CHECKPOINT_ENABLED`、`BKAPP_DIAGNOSTICS_SYNC_ADVANCE_ENABLED` 保持独立；事件和告警开关也保持独立。关闭恢复时不要同时关闭 S7 检查点或防重复检查，须按 [S7 操作说明](sync_advance_governance.md) 处理完在途任务后再回退。

## 从旧配置迁移

每组配置可以独立迁移。新旧同时存在时，只有含义一致才允许启动；明确冲突会抛出 `ValueError`，提示冲突的变量名。新布尔值支持 `1/0`、`true/false`、`yes/no`、`on/off`，模式值和扫描器名称会校验；旧配置独立使用时保留原解析方式。

建议在同一次配置变更中移除被替代的旧变量，避免后续切换新模式时留下冲突：

| 新入口 | 对应旧变量（以下均带 `BKAPP_` 前缀） |
| --- | --- |
| `DIAGNOSTICS_DETECTION_ENABLED` + 可选 `DIAGNOSTICS_SCANNERS` | `DIAGNOSTICS_SCAN_ENABLED`、`DIAGNOSTICS_WINDOW_SCAN_ENABLED`、`DIAGNOSTICS_SIGNATURE_SCAN_ENABLED`、`DIAGNOSTICS_CALLBACK_SCAN_ENABLED` |
| `PIPELINE_FENCE_MODE` | `PIPELINE_FENCE_EMIT_ENABLED`、`PIPELINE_FENCE_ENFORCE` |
| `DIAGNOSTICS_RECOVERY_POLICY` | `DIAGNOSTICS_RECOVERY_ENABLED`、`DIAGNOSTICS_RECOVERY_MODE` |

例如，迁移后打开检测总开关，但仍显式保留旧 `WINDOW_SCAN_ENABLED=0`，会因默认选中了 `window` 而报错。应删除旧变量，或用 `SCANNERS` 明确排除 `window`。新模式下旧取样扫描固定关闭，原来使用 `SCAN_ENABLED=1` 的环境应移除它并使用 `window`。

新 `RECOVERY_POLICY=off` 的内部兼容值是 `RECOVERY_ENABLED=0`、`RECOVERY_MODE=preview`；如果保留旧 `RECOVERY_MODE=apply`，也会报冲突。不要在回退时只新增一个 `off` 而保留不一致的旧值。

完成代码升级、相关迁移及所有 worker 版本核对后，可先按以下配置只开回调检测和恢复预览：

```text
BKAPP_DIAGNOSTICS_DETECTION_ENABLED=1
BKAPP_DIAGNOSTICS_SCANNERS=callback
BKAPP_PIPELINE_FENCE_MODE=observe
BKAPP_DIAGNOSTICS_RECOVERY_POLICY=preview
```

扩大检测范围时调整 `SCANNERS`，移除该变量会选择全部四种扫描。启用自动恢复前，再验证防重复检查、配置项目和类型范围，并切换到 `enforce` / `auto`。这些操作不会自动开启 S7。

环境变量在进程启动时读取。建议应用级配置保持一致，并重启实际消费 `task_data_clean` 的 worker、引擎 worker 和提供诊断操作的 web/API 进程；定时周期变化还需重启 beat。部署中队列可能由 cleaner 或 pipeline 模块消费，以实际进程配置为准。仅改配置而不重启，旧进程会继续使用旧值。

若回退到尚不支持新入口的应用版本，须先恢复匹配的旧环境变量；旧版本会忽略这些新变量。新 `off` 下继续回查的能力无法由旧 `RECOVERY_ENABLED=0` 表达。
