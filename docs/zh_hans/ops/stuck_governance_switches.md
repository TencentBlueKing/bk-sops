# 流程卡住治理：统一开关与旧配置迁移

本说明适用于包含统一开关改动的 bk-sops 版本，运行时依赖仍为 `bamboo-pipeline==3.24.22`。只升级运行时包不会增加这些应用侧配置。

## 统一入口与人工操作开关

| 环境变量 | 可选值 | 作用 |
| --- | --- | --- |
| `BKAPP_DIAGNOSTICS_DETECTION_ENABLED` | `0` / `1` | 关闭 / 开启定时检测，包含无动静兜底扫描、丢失类型扫描、回调扫描和“任务运行中但没有存活进程”的补充检测 |
| `BKAPP_PIPELINE_FENCE_MODE` | `off` / `observe` / `enforce` | 防重复检查：关闭 / 消息带上预期状态但只观察 / 消息带上预期状态并拦截不匹配消息 |
| `BKAPP_DIAGNOSTICS_RECOVERY_POLICY` | `off` / `preview` / `auto` | 周期恢复：停止新增恢复计划 / 只预览 / 在允许的项目和类型范围内自动恢复 |
| `BKAPP_DIAGNOSTICS_MANUAL_APPLY_ENABLED` | `0` / `1` | 禁止 / 允许控制台人工写操作，默认关闭，与自动恢复模式独立 |
| `BKAPP_DIAGNOSTICS_S7_ENABLED` | `0` / `1` | 同时关闭 / 开启同步节点输出检查点和 S7 检测能力，默认关闭 |
| `BKAPP_DIAGNOSTICS_OBSERVABILITY_MODE` | `off` / `alerts` / `full` | 关闭事件和告警日志 / 只输出告警日志 / 再记录诊断事件，默认关闭 |

**新配置未设置时继续读取旧配置；旧 `SCAN_ENABLED=1` 现在兼容为开启窗口扫描，不再执行取样扫描。** 其他旧开关的含义保持不变，包括原先不受扫描开关控制的补充检测，以及旧 `RECOVERY_ENABLED=0` 同时停止回查的行为。不要把“不设置新配置”等同于新配置设为 `off`。

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

人工写操作使用 `BKAPP_DIAGNOSTICS_MANUAL_APPLY_ENABLED`，旧名 `BKAPP_DIAGNOSTICS_APPLY_ENABLED` 继续兼容：新名未设置时沿用旧值；同时设置时须一致，否则启动报错。引擎仍读取同一个人工操作配置，因此权限检查、预检查和操作审计不变。`RECOVERY_POLICY=auto` 不会开启人工操作，`off` 也不会关闭已单独开启的人工操作。要停止所有新增恢复，应同时设置 `RECOVERY_POLICY=off` 和 `BKAPP_DIAGNOSTICS_MANUAL_APPLY_ENABLED=0`，并移除或同步旧 `APPLY_ENABLED`。

## S7 与事件、告警

`BKAPP_DIAGNOSTICS_S7_ENABLED=1` 同时启用同步节点输出检查点和 S7 检测能力，替代原来的两个开关；`0` 同时关闭两者。它不自动开启定时检测、防重复检查或任何恢复操作。定时检测仍需检测总开关启用且扫描范围包含 `signature`；恢复仍需 `FENCE_MODE=enforce`、人工操作开关或自动恢复模式及范围。

`BKAPP_DIAGNOSTICS_OBSERVABILITY_MODE` 统一事件记录和告警日志：

| 模式 | 诊断事件落库 | 诊断告警日志 |
| --- | --- | --- |
| `off` | 关闭 | 关闭 |
| `alerts` | 关闭，不访问事件表 | 开启 |
| `full` | 开启 | 开启 |

此模式只控制原有 `EVENT_ENABLED` / `ALERT_ENABLED` 的行为，不控制案例、恢复记录、操作审计或 Prometheus 指标，也不会自动配置通知推送。`full` 会增加事件表写入，正常观察可使用 `alerts`。

**不配置上述新入口及对应旧变量时，S7、事件记录和告警日志均保持关闭。** 未配置新入口但显式配置了旧变量时，完整保留原组合，包括仅开启 S7 检测、仅开启检查点、仅记录事件但不输出告警等情况；不是把旧变量做“或”运算后一起开启。新旧同时配置时须一致，否则启动时报错。

关闭恢复时不要同时关闭 S7 或防重复检查：先设置 `RECOVERY_POLICY=off`、`MANUAL_APPLY_ENABLED=0`，保留 `S7_ENABLED=1` 和 `FENCE_MODE=enforce`，按 [S7 操作说明](sync_advance_governance.md) 处理完在途任务后再回退。

## 从旧配置迁移

每组配置可以独立迁移。新旧同时存在时，只有含义一致才允许启动；明确冲突会抛出 `ValueError`，提示冲突的变量名。新布尔值支持 `1/0`、`true/false`、`yes/no`、`on/off`，模式值和扫描器名称会校验；旧配置独立使用时保留原解析方式。

建议在同一次配置变更中移除被替代的旧变量，避免后续切换新模式时留下冲突：

| 新入口 | 对应旧变量（以下均带 `BKAPP_` 前缀） |
| --- | --- |
| `DIAGNOSTICS_DETECTION_ENABLED` + 可选 `DIAGNOSTICS_SCANNERS` | `DIAGNOSTICS_SCAN_ENABLED`、`DIAGNOSTICS_WINDOW_SCAN_ENABLED`、`DIAGNOSTICS_SIGNATURE_SCAN_ENABLED`、`DIAGNOSTICS_CALLBACK_SCAN_ENABLED` |
| `PIPELINE_FENCE_MODE` | `PIPELINE_FENCE_EMIT_ENABLED`、`PIPELINE_FENCE_ENFORCE` |
| `DIAGNOSTICS_RECOVERY_POLICY` | `DIAGNOSTICS_RECOVERY_ENABLED`、`DIAGNOSTICS_RECOVERY_MODE` |
| `DIAGNOSTICS_MANUAL_APPLY_ENABLED` | `DIAGNOSTICS_APPLY_ENABLED` |
| `DIAGNOSTICS_S7_ENABLED` | `PIPELINE_SYNC_ADVANCE_CHECKPOINT_ENABLED`、`DIAGNOSTICS_SYNC_ADVANCE_ENABLED` |
| `DIAGNOSTICS_OBSERVABILITY_MODE` | `DIAGNOSTICS_EVENT_ENABLED`、`DIAGNOSTICS_ALERT_ENABLED` |

例如，迁移后打开检测总开关，但仍显式保留旧 `WINDOW_SCAN_ENABLED=0`，会因默认选中了 `window` 而报错。应删除旧变量，或用 `SCANNERS` 明确排除 `window`。旧 `SCAN_ENABLED=1` 与新配置选中 `window` 可以同时存在；若新配置关闭检测或排除了 `window`，则报冲突。旧 `SCAN_ENABLED=0` 不会阻止窗口扫描开启，保持它原先不约束窗口扫描的用法。

新 `RECOVERY_POLICY=off` 的内部兼容值是 `RECOVERY_ENABLED=0`、`RECOVERY_MODE=preview`；如果保留旧 `RECOVERY_MODE=apply`，也会报冲突。不要在回退时只新增一个 `off` 而保留不一致的旧值。

完成代码升级、相关迁移及所有 worker 版本核对后，可先按以下配置只开回调检测和恢复预览：

```text
BKAPP_DIAGNOSTICS_DETECTION_ENABLED=1
BKAPP_DIAGNOSTICS_SCANNERS=callback
BKAPP_PIPELINE_FENCE_MODE=observe
BKAPP_DIAGNOSTICS_RECOVERY_POLICY=preview
BKAPP_DIAGNOSTICS_MANUAL_APPLY_ENABLED=0
```

扩大检测范围时调整 `SCANNERS`，移除该变量会选择全部四种扫描。启用自动恢复前，再验证防重复检查、配置项目和类型范围，并切换到 `enforce` / `auto`。这些操作不会自动开启 S7。

环境变量在进程启动时读取。建议应用级配置保持一致，并重启实际消费 `task_data_clean` 的 worker、引擎 worker 和提供诊断操作的 web/API 进程；定时周期变化还需重启 beat。部署中队列可能由 cleaner 或 pipeline 模块消费，以实际进程配置为准。仅改配置而不重启，旧进程会继续使用旧值。

若回退到尚不支持新入口的应用版本，须先恢复匹配的旧环境变量；旧版本会忽略这些新变量。新 `off` 下继续回查的能力无法由旧 `RECOVERY_ENABLED=0` 表达。

## stag 全量配置：按模块复制

以下是显式开启全部治理能力的 stag 示例，**不是代码默认值**。全量配置共 8 个不同变量，包含项目和类型两个范围参数；`SCANNERS` 不配置就全选。配置仅应用于 stag，各模块使用同一版本的 bk-sops 和 `bamboo-pipeline==3.24.22`，完成所需迁移后再启用；保存环境变量后需重启相关进程，包含 beat。

先从应用级及对应模块级配置中移除上表中已被新入口替代的旧变量，避免继承旧值产生冲突；应删除变量，不是设为空字符串。未被替代的阈值和周期参数继续使用原值或默认值。

`default`（web / beat / dworker）：

```dotenv
BKAPP_PIPELINE_FENCE_MODE=enforce
BKAPP_DIAGNOSTICS_S7_ENABLED=1
BKAPP_DIAGNOSTICS_OBSERVABILITY_MODE=full
BKAPP_DIAGNOSTICS_MANUAL_APPLY_ENABLED=1
```

`api-server` / `api`，以及单独部署的 `callback`：

```dotenv
BKAPP_PIPELINE_FENCE_MODE=enforce
BKAPP_DIAGNOSTICS_S7_ENABLED=1
BKAPP_DIAGNOSTICS_OBSERVABILITY_MODE=full
```

`pipeline`（包含普通任务、API 任务和周期任务的全部执行 / 轮询 worker）：

```dotenv
BKAPP_PIPELINE_FENCE_MODE=enforce
BKAPP_DIAGNOSTICS_S7_ENABLED=1
BKAPP_DIAGNOSTICS_OBSERVABILITY_MODE=full
```

独立 `cleaner` 模块（消费 `task_data_clean`）：

```dotenv
BKAPP_DIAGNOSTICS_DETECTION_ENABLED=1
BKAPP_PIPELINE_FENCE_MODE=enforce
BKAPP_DIAGNOSTICS_S7_ENABLED=1
BKAPP_DIAGNOSTICS_OBSERVABILITY_MODE=full
BKAPP_DIAGNOSTICS_RECOVERY_POLICY=auto
BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS=*
BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES=execute_dispatch_lost,poll_dispatch_lost,parent_wakeup_lost,child_start_lost,callback_dispatch_lost,sync_advance_stalled
```

仓库 `app_desc.yaml` 中 cleaner 是 pipeline 下的进程；这种部署直接将 cleaner 整段配置放到 pipeline 模块，替代上一段 pipeline 配置。S7 和防重复检查在扫描 / 恢复端也必须启用，恢复前会检查这些设置。仅运行独立插件执行进程的 `plugin` 模块无需专门增加本组变量。

`RECOVERY_PROJECT_IDS=*` 表示全部 stag 项目，也可以改成指定项目 ID（逗号分隔）。自动类型必须明确列出，不支持 `*`；上述 6 类是当前运行时支持的全部类型，限次、自动暂停和安全检查继续生效。首次验证可将 `RECOVERY_POLICY` 改成 `preview`，确认后再切为 `auto`。本配置不会自动补扫全部历史任务，补扫方式见下文。

## 旧取样扫描的替换

bk-sops 的周期任务已移除旧取样执行路径。未设置新检测总开关时，旧 `SCAN_ENABLED` 和 `WINDOW_SCAN_ENABLED` 任意一个为 `1` 就开启窗口扫描；例如旧组合 `SCAN_ENABLED=1`、`WINDOW_SCAN_ENABLED=0` 仍能启用检测，但实际执行窗口扫描。旧 `SCAN_ENABLED` 不会额外开启回调或丢失类型扫描。

选用了窗口扫描但运行时不支持它时，会记录错误，不再自动回落到取样扫描；补充检测和历史数据清理也不再以旧取样扫描器是否存在来判断能否运行。应用仍要求安装固定的 3.24.22 运行时，没有新增依赖或迁移。

本次兼容的是配置入口，不保留取样算法。切换后统一安排历史补扫，不能把“成功启动扫描”当成“历史任务已覆盖”：

- 旧取样曾按 `SCAN_MAX_SILENT_SECONDS` 限定范围，并按 `SCAN_BATCH` 取样。这两个旧配置继续接受，但不再控制周期检测；窗口扫描使用 `WINDOW_TIERS`、`WINDOW_MAX_ROOTS` 和检查进度。
- 窗口扫描按检查进度继续处理，首次启动时，每档从其阈值对应的时间往前回看 3600 秒；默认档位是 1 小时和 24 小时。这不代表首次开启就能覆盖之前 7 天的任务。
- 窗口扫描不读取旧取样使用的回调明细。迁移时还需启用并验证独立回调扫描，不能只打开 `window` 就宣称覆盖完全相同。

首次启用建议使用新的检测总开关和扫描列表，分别验证窗口、回调及丢失类型扫描。历史补扫按实际治理范围选择起点和批量，不在应用启动时自动执行。

### 历史补扫与回退核对

迁移前先查看当前案例和检查进度，再按需要预览历史区间。以下示例检查最近 7 天、无动静超过 1 小时的任务，最多读 2000 行：

```bash
python manage.py diagnostics_scan --scanner window --tier 3600 --start-seconds 604800 --max-rows 2000 --dry-run
```

`--dry-run` 不写案例或检查进度。确认范围和负载可接受后，去掉 `--dry-run` 才会登记案例；保留 `--start-seconds` 时始终不改定时扫描的检查进度。若输出 `capped=True`，说明本轮未覆盖完整指定范围，应调整范围或上限后重新核验，不能认定历史补扫已经完成。

检测关闭期间检查进度保持原值，重新开启后继续处理。移除新总开关与 `SCANNERS`，恢复旧 `SCAN_ENABLED=1` 或 `WINDOW_SCAN_ENABLED=1`，仍沿用同一份窗口检查进度，不会恢复取样算法，也不会重新回看全部历史。其他扫描、恢复和人工操作开关按原配置分别处理。

若需回退应用代码，同时保留旧配置名并明确配置 `SCAN_ENABLED=0`、`WINDOW_SCAN_ENABLED=1`，避免旧版本重新走取样路径；新旧应用版本的窗口扫描可使用同一份检查进度。仅配置新入口时，旧版本会忽略它们，回退前必须同步旧配置。
