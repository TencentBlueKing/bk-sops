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

- 已发布版本：`bamboo-pipeline==3.24.16`（依赖 `bamboo-engine==2.6.5`，含 `engine.py` 热路径钩子），均已在 PyPI。
- 标准运维 `requirements.txt` 已指向 `bamboo-pipeline==3.24.16`；装此一个包即拉齐 runtime 诊断 + core 钩子，不要指向未发布的未来版本。
- 3.24.14 相对 3.24.13 的增量：`child_process_finish` 重复 ACK 幂等修复；M2 可靠事件 `pipeline.contrib.reliable_events` 随包提供但未注册进 `INSTALLED_APPS`，不建表不生效，M1 灰度不受影响。
- 3.24.15 / 3.24.16 的增量都是判据降噪，见下方「判据为什么会误判」。开 `SCAN` 前务必先到 3.24.16，否则设计内停车（人工暂停 / 失败等人工 / 并行网关等失败分支）会被兜底判据报成卡住。
- 发布后先在 stage 验证 `/admin/diagnostics/task/`、`/admin/diagnostics/cases/` 页面、证据包导出命令和 dry-run 操作。
- 观察 `[pipeline_diagnostics_alert]` 与 `[bk_sops_task_diagnostic_alert]` 日志是否符合预期。

## 灰度上线 checklist（M1 检测打底）

M1 只做“检测立案”，只读为主、执行热路径不变。按下述顺序灰度，任意步骤可秒级熔断。

**Step 0 前置（已就绪）**

- [ ] `requirements.txt` 已指向 `bamboo-pipeline==3.24.16`。
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
- [ ] 代码回滚：整体回退诊断能力 `requirements.txt` pin 回 `bamboo-pipeline==3.24.11`；只回退 3.24.16 的兜底降噪则 pin 回 `3.24.15`，连 3.24.15 的判据降噪一起回退则 pin 回 `3.24.14`（两者都会重新产生设计内停车的噪音案例）。残留空表无害、无需清理。

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
| `BKAPP_DIAGNOSTICS_SCAN_MAX_SILENT_SECONDS` | `604800` | Layer0 取样池静默上界（秒，7 天；`0` 表示不设上界） |
| `BKAPP_DIAGNOSTICS_SUPPLEMENT_BATCH` | `200` | 补充检测单轮候选上限 |
| `BKAPP_DIAGNOSTICS_SUPPLEMENT_MIN_RUNNING_SECONDS` | `3600` | 补充检测治理窗口下界（秒） |
| `BKAPP_DIAGNOSTICS_SUPPLEMENT_MAX_RUNNING_SECONDS` | `604800` | 补充检测治理窗口上界（秒，7 天） |
| `BKAPP_DIAGNOSTICS_SUPPLEMENT_CLOSE_BATCH` | `500` | 单轮案例收敛的扫描上限 |

## 补充检测（任务视角兜底）

Layer0 从 `eri_process.last_heartbeat` 找停滞 root，进程已经消失的场景没有 heartbeat 可比，覆盖不到。补充检测从任务视角兜底：bk-sops 侧任务还是“运行中”（v2 引擎、pipeline 已启动、未完成、未撤销、运行时数据未过期、任务未删除），但引擎侧一个存活进程都没有。

注意这个检测跟 Layer0 是两条独立通路：**它不受 `BKAPP_DIAGNOSTICS_SCAN_ENABLED` 控制**，只要周期任务在跑就会立案。要停它只能停 `scan_stuck_diagnostics` 这个周期任务本身，或把配置里的 `PIPELINE_DIAGNOSTICS_CASE_ENABLED` 置 `False`（这项没有对应的 env 开关，需要改配置重新发布，且 Layer0 也会一起不再立案）。

### 治理窗口

只看启动时间落在 `[now - MAX, now - MIN]` 之间的任务，默认 1 小时 ~ 7 天。两个边界挡的是两类完全不同的问题：

**下界挡误判。** 引擎正常收尾时先写 `is_finished` 再把进程置 `dead`，这两步之间任务看起来就是“运行中且无存活进程”。短命任务（几十秒级的周期任务等）会在扫描过程中大量踩到这个窗口。调低下界会更快发现问题，但误判也更多；真实卡住的流程通常已经卡了很久，1 小时不影响发现。

**上界挡历史僵尸。** 现网存在大量启动于一两年前、`is_expired` 仍为 `False`、引擎侧 `eri_state` 已查不到任何记录的任务。这类任务永远不会 `is_finished`，也永远不会有进程，既治不了也关不掉，而候选批次只有 200，它们会长期占满取样窗口让新问题排不进来。上界把它们挡在候选池外。

另两道误判防线：

- **批量进程判定**：整批候选只查一次 `eri_process`，判定窗口不再随候选数放大（旧实现逐个查，200 个候选耗时接近一分钟，期间跑完的任务全被判成卡住）；
- **立案前二次确认**：进程判定之后重新读一次任务态，扫描期间跑完的任务不立案。

### Layer0 的同类风险（3.24.15 已收敛）

`stalled_root_candidates` 的候选是 `eri_process` 按 root 取 `MAX(last_heartbeat)`。3.24.15 之前是 `order by latest` 升序取 200——**最久静默优先**，而现网有近两千个心跳停在两年前的 `dead=False` 僵尸进程（实测队头静默 1771 天），当时直接打开 `BKAPP_DIAGNOSTICS_SCAN_ENABLED` 会稳定地每轮只看这批历史垃圾，新问题一条都排不进窗口。

3.24.15 起取样加了静默上界（`BKAPP_DIAGNOSTICS_SCAN_MAX_SILENT_SECONDS`，默认 7 天）并改为**最近静默优先**，窗口外的历史积压交给一次性回扫，不占用周期任务名额。

另外注意 `beat()` 只在执行推进循环和 schedule 时被调用，等回调的休眠进程心跳不刷新，所以“心跳老旧”不等于卡住——bk-sops 的主力 JOB 插件和 `remote_plugin` 都是回调型，一个跑 3 小时的作业必然被判静默 3 小时。Layer0 对此有两道防护：候选只是入场券，真正立案要求 `diagnose_snapshot` 命中规则；3.24.15 起判据本身也会识别设计内停车（等待外部回调、人工暂停 / 失败停车、并行网关等子进程收敛），不再判为卡住。

### 兜底判据的补漏（3.24.16）

3.24.15 只让专属判据认识了设计内停车，但 `stalled_no_progress` 这条兜底（root 长期无推进即报 warning）漏了同一层豁免，同一批流程仍会以 warning 立案。3.24.16 给兜底补齐，其中一处值得单独说明：

**等 ACK 收敛的父进程算中性。** 并行网关下若有分支失败停车，父进程会永远收不齐 ACK：

```
父进程  ack=2/4  停在自己那个 FINISHED 的网关节点上
子进程  停在 FAILED 节点 + 沉睡   <- 等人工重试或跳过
子进程  停在 FAILED 节点 + 沉睡   <- 等人工重试或跳过
```

父进程既没有被用户暂停、也不在失败节点上，按 3.24.16 之前的写法它会被当成「还有进程在正常推进」，一票否决整个豁免。但它能否往下走完全取决于子进程，而子进程已各自被判定为失败停车，所以它在这个判断里应当中性。现网 `task 138970299`（SRE 稳定性巡检，挂 56 天）就是这个形态。

这不会放过真问题：子进程若停在 RUNNING 却没有对应 version 的调度记录，由 `schedule_missing_for_running_node` 报出；子进程全死却仍未收敛，由 `parallel_ack_not_converged` 报出。

需要注意「长期有失败节点无人处理」这类任务从此不再进卡住看板——它确实该有人管，但属于任务治理，和「引擎推不动」是两回事，混在一起正是早期看板噪音的成因，后续用独立报表覆盖。

### 案例收敛

补充检测的案例由 `close_recovered_cases` 随扫描同轮收敛，分两种终态：

- `resolved`：任务已完成 / 已撤销 / 已过期 / 已删除 / 记录已不存在，或进程已恢复 —— 问题没了；
- `ignored`：任务确实还卡着，但已经超出治理窗口上界 —— 治不了了，不该继续占看板。

窗口上界同时作用在立案和收敛两侧，这一点很关键：只加在立案侧的话，窗口外的历史僵尸案例会永远留在 `open`（任务永远不完成、进程永远不出现，`resolved` 的判据一条都不满足）。

代价要清楚：一个卡了 6 天没人处理的流程，第 8 天会被自动收敛成 `ignored` 并从待治理列表消失，之后也不会再立案。告警在立案那一刻就已经发出，看板不承担长期待办的职责；如果 7 天不够，调大 `BKAPP_DIAGNOSTICS_SUPPLEMENT_MAX_RUNNING_SECONDS`。

引擎侧的 `close_stale_cases` 以 heartbeat 恢复为判据，覆盖不到这个检测（这里的 root 根本没有进程），而且它被 Layer0 扫描开关挡住，所以单独实现。

看板列表和详情都带“任务当前状态”，用来区分“还卡着”和“立案之后任务已经跑完”。

清算存量案例（比如修复上线前积累的误判）用命令，先 dry-run 看量：

```bash
python manage.py close_recovered_diagnostic_cases --dry-run
python manage.py close_recovered_diagnostic_cases
```

命令按 id 游标翻页扫全量 `open` 案例，周期任务只看最近未更新的一批，两者判据一致。输出形如 `scanned=N resolved=X ignored=Y`，`--dry-run` 时前缀 `would_`。
