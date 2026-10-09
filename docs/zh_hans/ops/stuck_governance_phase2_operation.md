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

## 三期检测全覆盖（P3-1）

需要 `bamboo-pipeline>=3.24.20`。三个扫描器各有开关，默认全关；只立案，不重放。三个开关互相独立，也不受 M1 的 `BKAPP_DIAGNOSTICS_SCAN_ENABLED` 约束：打开窗口扫描后，即使 M1 开关是关的，也会扫描 root 并立案。

| 扫描器 | 周期 | 发现什么 |
| --- | --- | --- |
| 静默窗口扫描 | 随 `BKAPP_DIAGNOSTICS_SCAN_CRON` | 心跳跨过 1 小时 / 24 小时的 root，判据同 M1；开启后替代 M1 取样扫描，不再受 batch 截断，每轮静默 root 超过上限时停在已读位置、下一轮接着扫 |
| 形态快检 | 每分钟 | 执行、首次轮询、轮询续派、父进程唤醒、子进程启动这五类消息丢失 |
| 回调水位扫描 | 每 30 秒 | 回调数据已落库、调度却没消费（回调锁重试用尽等） |

### 新增诊断类型

| 类型 | 含义 | 证据里的关键字段 |
| --- | --- | --- |
| `execute_dispatch_lost` | 节点已完成，后继节点的执行消息没被消费 | `derived_message`、`next_node_ids` |
| `poll_dispatch_lost` | 轮询消息没被消费；`signature=S2` 是首次轮询，`S3` 是续派 | `schedule_id`、`schedule_times`、`code` |
| `callback_dispatch_lost` | 回调数据已落库，调度没消费 | `callback_data_id`、`schedule_id` |
| `parent_wakeup_lost` | 并行分支全部结束，父进程没被唤醒 | `child_process_id`、`converge_gateway_id` |
| `child_start_lost` | 子进程已创建，启动消息没被消费 | `parent_process_id` |

`derived_message` 是推导出的"应该被消费却丢失的那条消息"。3.24.21 起可以在控制台对这些案例预览重放、人工重放（见"三期恢复台账与人工重放"）；更早的版本只能按证据定位后人工处置：已有的 `replay_callback_data`、`resend_schedule` 动作在 `apply` 模式下只做预检，不会派发消息。

这些案例由各自的扫描器逐条复核：进程往前走了，或者任务被撤销了，下一轮就会关成 `resolved`，不参与按 root 进展关闭。

M1 规则产出的案例（如 `stalled_no_progress`）在 root 恢复进展、没有存活进程或根流程已撤销 / 已结束时关成 `resolved`；补充检测的 `running_task_without_live_process` 只由 bk-sops 自己的收敛逻辑关闭，引擎不再碰它。

### env 开关速查（三期）

| 环境变量 | 默认 | 作用 |
| --- | --- | --- |
| `BKAPP_DIAGNOSTICS_WINDOW_SCAN_ENABLED` | `0` | 静默窗口扫描（开启后替代 M1 取样扫描） |
| `BKAPP_DIAGNOSTICS_WINDOW_TIERS` | `3600,86400` | 窗口档位（秒）；不要设成空值，空值会让窗口扫描没有任何档位 |
| `BKAPP_DIAGNOSTICS_WINDOW_MAX_ROOTS` | `1000` | 窗口扫描每档每轮最多处理的静默 root 数；超出的下一轮接着处理，不会漏 |
| `BKAPP_DIAGNOSTICS_SIGNATURE_SCAN_ENABLED` | `0` | 形态快检 |
| `BKAPP_DIAGNOSTICS_SIGNATURE_FAST_THRESHOLD_SECONDS` | `300` | 快档阈值（执行、首次轮询、父子进程） |
| `BKAPP_DIAGNOSTICS_SIGNATURE_SLOW_THRESHOLD_SECONDS` | `1800` | 慢档阈值（轮询续派，并复查快档） |
| `BKAPP_DIAGNOSTICS_POLL_EXCLUDE_CODES` | `sleep_timer` | 不检查轮询续派的插件 code，逗号分隔 |
| `BKAPP_DIAGNOSTICS_CALLBACK_SCAN_ENABLED` | `0` | 回调水位扫描 |
| `BKAPP_DIAGNOSTICS_CALLBACK_CONFIRM_SECONDS` | `120` | 回调持续未消费多久才立案（要长于回调锁重试的约 19 秒） |
| `BKAPP_DIAGNOSTICS_SIGNATURE_SCAN_CRON` | `* * * * *` | 形态快检周期 |
| `BKAPP_DIAGNOSTICS_CALLBACK_SCAN_INTERVAL` | `30` | 回调扫描间隔（秒） |

### 上线步骤

1. 发版后开关保持全关，先在 webconsole 做只读预演（都带 `--dry-run`，不写任何表）：

   ```bash
   python manage.py diagnostics_scan --scanner signature --dry-run --start-seconds 3600
   python manage.py diagnostics_scan --scanner window --tier 3600 --dry-run --start-seconds 7200
   python manage.py diagnostics_scan --scanner callback --dry-run --from-callback-id <起点 id>
   python manage.py diagnostics_poll_profile --days 7
   ```

2. 依次打开回调、形态、窗口三个开关，每开一个观察一天；`BKAPP_DIAGNOSTICS_ALERT_ENABLED` 保持关闭。
3. 观察日志 `[pipeline_diagnostics_scan]` 和指标 `pipeline_diagnostics_scan_rows`、`pipeline_diagnostics_scan_hits`、`pipeline_diagnostics_scan_cursor_lag`、`pipeline_diagnostics_detect_latency_seconds`：水位滞后应接近 0，`capped=True` 只能偶发。
4. 用 `diagnostics_poll_profile` 的结果调整慢档阈值和排除清单：`silent_*` 是距上次轮询的静默时长分位数，`interval_p50` 是续派间隔中位数。首行 `capped=True` 表示读满了 `--max-rows`，缺的是心跳最新的进程，调大 `--max-rows` 或缩小 `--days` 后再看。

需要真实补扫一段历史区间时，去掉 `--dry-run`、保留 `--start-seconds`：照常立案，但既不读也不写定时扫描的水位，不会让定时扫描跳过任何区间。

回滚：把开关关掉即可；水位表里的记录无害，重新打开时从上次水位继续。

## 三期引擎门禁（P3-2）

需要 `bamboo-pipeline>=3.24.21`（依赖 `bamboo-engine==2.6.9`）。门禁让引擎在执行、调度入口识别并丢弃过期或重复的消息：正常派发的消息在 `headers["fence"]` 里附带令牌，入口按令牌做条件抢占，不符就丢弃。两个开关默认全关，全关时与 3.24.20 行为一致。

| 消息 | 令牌 | 入口校验 |
| --- | --- | --- |
| 调度完成后执行下一节点、唤醒父进程、启动子进程 | `from_node`、`from_version` | 进程仍睡在 `from_node`，且该节点的状态版本没变 |
| 首次轮询、轮询续派 | `schedule_times` | 调度次数没变；锁被占用时沿用原有处理 |

API 触发的执行（启动、继续、重试、跳过等）和回调触发的调度都不带令牌，按原逻辑执行；诊断里原有的 `resend_schedule`、`replay_callback_data` 动作只做预检，不派发消息。P3-3 的案例重放对执行类、轮询类消息附带令牌。

### env 开关速查（P3-2）

| 环境变量 | 默认 | 作用 |
| --- | --- | --- |
| `BKAPP_PIPELINE_FENCE_EMIT_ENABLED` | `0` | 正常派发点附带令牌 |
| `BKAPP_PIPELINE_FENCE_ENFORCE` | `0` | 令牌不符时丢弃消息；关闭时只记日志和指标，照常执行 |

### 上线步骤（P3-2）

1. 发版，两个开关保持关闭。确认**所有**消费引擎队列的 worker 进程都已经是 3.24.21：旧 worker 会把收到的令牌原样传给下一条消息，新旧混跑时会给无关的消息带上错误令牌。
2. 打开 `BKAPP_PIPELINE_FENCE_EMIT_ENABLED=1`，`ENFORCE` 保持关闭，观察 1～2 周：
   - 指标 `engine_fence_drop_total{enforced="false"}`，按 `kind`（`execute` / `schedule`）和 `reason`（`version_mismatch` / `process_moved` / `schedule_times_mismatch`）看；
   - 日志关键字 `[fence]`、`would be dropped`，日志里带 `root_pipeline_id`、`process_id` 或 `schedule_id`、`node_id` 和令牌内容，逐条确认是真的重复或过期消息（同一节点已有另一条消息生效）。
   - 预期会命中的来源：broker 重复投递；运行时派发消息第一次报错后重发一次（`_retry_once`），而第一次其实已经发出；抢占提交后连接报错、从 `ENTRY` 恢复的消息（记为 `process_moved`）；对轮询节点调用回调接口后，回调触发的调度会增加调度次数，队列里原来那条轮询消息记为 `schedule_times_mismatch`。逐条对上这些来源，出现解释不了的命中时不要进入下一步。
   - 同时到达的重复轮询消息走锁被占用的原有处理，只记诊断事件 `schedule_lock_conflict`，不计入 `engine_fence_drop_total`。
   - 日志 `[fence] build fence for process(...) failed, dispatch without fence` 表示唤醒父进程前读库生成令牌失败，这条消息退回不带令牌、照常唤醒，不影响推进；频繁出现时先排查数据库。
3. 打开 `BKAPP_PIPELINE_FENCE_ENFORCE=1`。之后命中的日志变为 `dropped`，指标标签变为 `enforced="true"`。
4. 对比开关前后 `engine_execute_pre_process_duration`、`engine_schedule_pre_process_duration` 的 p99，确认入口耗时的增加可以接受。

### 回滚（P3-2）

先关 `ENFORCE`，立即恢复为只记录、不丢弃；需要时再关 `EMIT`，新消息不再带令牌。需要降级到 3.24.20 时先关两个开关；降级期间旧 worker 会把已经发出的令牌继续往下传，所以之后重新升级要从上线步骤 1 重来，在观察模式下至少跑满一个最长的轮询周期再打开 `ENFORCE`。

### 已知限制（P3-2）

- 引擎 celery 任务目前不开 `acks_late`，消息在执行前确认。将来如果开启，worker 崩溃后重投的消息会被当作重复丢弃，而进程已被第一次投递抢占，会留下"已唤醒但没人推进"的进程；开启前必须重新评估门禁。
- 进程抢占的条件更新已经提交、随后数据库连接才报错时，断点恢复会把同一条消息当作重复丢弃，同样留下已唤醒的空闲进程。这种情况极少见，由三期的静默窗口扫描发现。

## 三期恢复台账与人工重放（P3-3）

需要 `bamboo-pipeline>=3.24.21`（依赖 `bamboo-engine==2.6.9`），新增迁移 `pipeline_diagnostics.0003`（恢复台账表）。

重放针对形态快检和回调水位扫描立的案例：按库内当前状态重新判定形态，推导出丢失的那条消息，附带门禁令牌交给运行时派发。原消息如果只是迟到，两条消息谁先到谁生效，后到的被 P3-2 门禁丢弃。形态已不成立时不重放。

| 类型 | 重放的消息 | 令牌 |
| --- | --- | --- |
| `execute_dispatch_lost` | 执行唯一的后继节点 | 已完成节点和它的状态版本 |
| `parent_wakeup_lost` | 父进程执行汇聚网关 | 父进程当前节点和状态版本 |
| `child_start_lost` | 子进程执行分支首节点 | 首节点和状态版本（还没有状态时为空） |
| `poll_dispatch_lost` | 轮询当前调度 | 当前调度次数 |
| `callback_dispatch_lost` | 按回调数据调度 | 不带，依靠调度入口原有的检查（调度已完成、版本不符、调度锁） |

以下情况不重放，结果里的 `blockers` 给出原因：

| 原因 | 含义 / 处理 |
| --- | --- |
| `fence enforce is off` | 执行类、轮询类重放要求 `BKAPP_PIPELINE_FENCE_ENFORCE=1`，否则迟到的原消息会和重放各执行一次 |
| `fence emit is off, confirm the risk to replay` | `EMIT` 未开时正常派发不带令牌，迟到的原消息会无条件执行；控制台会弹出二次确认，确认已排除队列积压后再重放 |
| `fence emit is off` | 恢复任务自动预演时 `EMIT` 未开的阻断原因；自动预演没有确认风险这一步，控制台人工重放遇到同样情况给出的是 `fence emit is off, confirm the risk to replay` |
| `message came from a skip and carries no fence token, confirm the risk to replay` | `execute_dispatch_lost` 的节点、或 `child_start_lost` 父进程所在的条件并行网关是被跳过的（人工跳过，或节点超时策略"强制失败并跳过"）：跳过接口派发的消息不带令牌，即使开了 `ENFORCE`，迟到的原消息也会无条件执行；控制台会弹出二次确认，确认已排除队列积压后再重放 |
| `message came from a skip and carries no fence token` | 恢复任务自动预演时遇到跳过产生的消息的阻断原因；自动预演没有确认风险这一步，控制台人工重放遇到同样情况给出的是 `message came from a skip and carries no fence token, confirm the risk to replay` |
| `successor node is not unique` | 后继不唯一，按证据人工处置 |
| `callback schedule is running` | 回调对应的调度正在进行，继续观察 |
| `more than one callback was lost on this node` | 同一节点丢失过不止一条回调（按案例命中次数判断，命中超过一次即阻断），按证据人工处置 |
| `a replay is waiting to settle` | 同一案例的同一消息已派发，距今还不到 `BKAPP_DIAGNOSTICS_RECOVERY_SETTLE_SECONDS`（默认 180 秒）；过了这个时间不再阻断 |
| `apply disabled` | 人工重放还受 `BKAPP_DIAGNOSTICS_APPLY_ENABLED` 约束 |
| `dispatch failed` | 运行时派发报错；台账记一行 `blocked`，报错信息在 `detail.error`。先排查报错原因，再决定是否重放 |
| `shape no longer holds` | 形态已不成立，无需重放 |

### 控制台

案例详情展示最近 20 条重放记录。可重放的类型多出"预览重放""重放"两个按钮：预览只返回推导出的消息和阻断原因，不派发；重放派发后在台账记一行 `dispatched`。两者都写操作审计（案例不存在时不写），类型 `replay_case`。重放遇到需要确认风险的阻断（`EMIT` 未开，或节点、条件并行网关是被跳过的）时，控制台弹出二次确认，确认已排除队列积压后才带上确认重新提交。已有的 `replay_callback_data`、`resend_schedule` 等动作保持原样。

控制台返回 `replay_case raised, check recovery history before retrying: …`，或者显示"重放请求失败，请先查看重放记录再决定是否重试："时，重放结果未知：消息可能已经派发，台账或操作审计里却可能没有对应记录。重试前先看案例的重放记录，再看节点是否已经往前走；标准运维日志关键字 `[diagnostics] replay_case raised`。

### 恢复任务

恢复任务每分钟一轮（redis 单例锁，队列 `task_data_clean`），P3-3 只预演、不重放：

1. 复核到期的记录：记录满 `BKAPP_DIAGNOSTICS_RECOVERY_SETTLE_SECONDS`（默认 180 秒）后再判定一次形态，`dispatched` 改为 `applied`（形态已解除、根流程仍在运行）、`obsolete`（形态已解除，但根流程已结束、撤销或暂停；或者案例已被删除）或 `ineffective`（形态仍成立，轮询类还要求调度次数没变；回调类在回调仍待消费或调度仍在进行时都算仍卡着）；预演和阻断记录只把形态是否仍成立写进 `detail.settled_holds`，案例已被删除的不写。复核只由恢复任务做，人工重放的记录也一样：`BKAPP_DIAGNOSTICS_RECOVERY_ENABLED` 关闭时，人工重放的记录会一直停在 `dispatched`。
2. 检查未关闭的可重放案例（每轮最多 200 个，先看最新的）：同一案例同一消息只记一行 `previewed`（可以重放，没有阻断）或 `blocked`（带阻断原因）；形态已不成立的只计数。

台账与操作审计的保留期相同（365 天），由已有的 `cleanup_diagnostics` 周期任务清理。

### env 开关速查（P3-3）

| 环境变量 | 默认 | 作用 |
| --- | --- | --- |
| `BKAPP_DIAGNOSTICS_RECOVERY_ENABLED` | `0` | 恢复任务（复核与预演） |
| `BKAPP_DIAGNOSTICS_RECOVERY_SETTLE_SECONDS` | `180` | 派发后多久复核；要长于执行、调度消息正常排队和处理的时长 |
| `BKAPP_DIAGNOSTICS_RECOVERY_CRON` | `* * * * *` | 恢复任务周期 |

`BKAPP_PIPELINE_FENCE_EMIT_ENABLED`、`BKAPP_PIPELINE_FENCE_ENFORCE`、`BKAPP_DIAGNOSTICS_APPLY_ENABLED`、`BKAPP_DIAGNOSTICS_RECOVERY_SETTLE_SECONDS` 要在 `default` 和 `pipeline` 模块设成一样的值（或者直接设成应用级环境变量）：人工重放在 `default` 模块的 web 进程里检查这些开关和收敛窗口，令牌却由 `pipeline` 模块的引擎 worker 校验，恢复任务也跑在 `pipeline` 模块。恢复任务自己的两个变量则各只在一个模块生效：`BKAPP_DIAGNOSTICS_RECOVERY_ENABLED` 由 `pipeline` 模块消费 `task_data_clean` 队列的 worker 在任务运行时读取，`BKAPP_DIAGNOSTICS_RECOVERY_CRON` 由 `default` 模块的 celery beat 在加载任务时读取、用来排周期；只设在另一个模块上不会报错，但也不会生效，所以这两个也直接设成应用级环境变量。

### 上线步骤（P3-3）

1. 发版并执行迁移，开关保持关闭。
2. 打开 `BKAPP_DIAGNOSTICS_RECOVERY_ENABLED=1`，观察几天。日志关键字 `[pipeline_diagnostics_recovery]`；在 webconsole 查看预演报告（只读）：

   ```bash
   python manage.py diagnostics_recovery_report --hours 24
   ```

   输出的 `types` 下按类型分组：`preview` 是预演结果分布，`blockers` 是阻断原因分布，`settled.healed` / `settled.holds` 是预演后不重放也自愈 / 仍然卡住的条数，`self_heal_ratio` 是自愈比例，`apply` 是人工重放记录的状态分布。`settled` 和 `self_heal_ratio` 只统计推导出了消息、复核时案例还在的预演记录；同一案例同一消息只在第一次看到时记一行，所以 `blockers` 反映的是第一次看到时的阻断原因；预演记录复核前被人工重放修好的也算自愈，开始人工重放后自愈比例只是上限。自愈比例高的类型说明检测阈值偏短，先调对应的检测阈值，再考虑自动重放：`execute_dispatch_lost`、`parent_wakeup_lost`、`child_start_lost` 和 `signature=S2` 的 `poll_dispatch_lost` 看 `BKAPP_DIAGNOSTICS_SIGNATURE_FAST_THRESHOLD_SECONDS`，`signature=S3` 的看 `BKAPP_DIAGNOSTICS_SIGNATURE_SLOW_THRESHOLD_SECONDS`，`callback_dispatch_lost` 看 `BKAPP_DIAGNOSTICS_CALLBACK_CONFIRM_SECONDS`。
3. 超管在控制台对个别案例先"预览重放"，核对推导出的消息与证据一致后再"重放"。复核后看记录状态：`applied` 表示已恢复推进；`ineffective` 表示重放后仍卡住，按证据人工处置。`BKAPP_DIAGNOSTICS_APPLY_ENABLED` 同时放开控制台其他写动作的 `apply` 模式，打开前确认操作人范围，或只在需要时临时打开。
4. 指标 `pipeline_diagnostics_recovery_total{stuck_type, trigger, result, hostname}`：`result` 为 `dispatched`、`blocked`（派发报错）、`applied`、`obsolete`、`ineffective`。

回滚：关掉 `BKAPP_DIAGNOSTICS_RECOVERY_ENABLED` 即停止复核和预演，之后人工重放的记录也不再复核、停在 `dispatched`；人工重放由 `BKAPP_DIAGNOSTICS_APPLY_ENABLED` 控制。台账记录无害，可以保留。

## 三期自动重放灰度（P3-4）

需要 `bamboo-pipeline>=3.24.21`（依赖 `bamboo-engine==2.6.9`），P3-4 本身没有新迁移。

恢复任务在 P3-3 的基础上按开关自动重放，所以恢复任务本身要先打开（`BKAPP_DIAGNOSTICS_RECOVERY_ENABLED=1`）。在此基础上，以下三个条件同时满足才自动重放，否则仍然只预演：

1. `BKAPP_DIAGNOSTICS_RECOVERY_MODE=apply`；
2. 案例类型在 `BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES` 里；
3. 根流程所属项目在 `BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS` 里（逗号分隔的项目 ID，空表示不放开，`*` 表示全部；查不到对应任务、任务已删除或任务没有所属项目的根流程不放开）。

自动重放推导消息、其余阻断条件都与人工重放相同，只有两处不同：一是人工重放可以确认风险后继续的情况，自动重放一律阻断，在台账记一行 `blocked`：执行类、轮询类要求 `BKAPP_PIPELINE_FENCE_EMIT_ENABLED=1` 与 `BKAPP_PIPELINE_FENCE_ENFORCE=1` 都已打开，否则原因为 `fence emit is off` 或 `fence enforce is off`（`ENFORCE` 未开时人工重放同样不能继续）；节点或条件并行网关是被跳过的，原因为 `message came from a skip and carries no fence token`。二是不受 `BKAPP_DIAGNOSTICS_APPLY_ENABLED` 约束，也不写操作审计，台账记录的 `trigger` 为 `auto`。回调类不依赖门禁。

分两级放开：

| 级别 | `BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES` |
| --- | --- |
| 确定性形态 | `execute_dispatch_lost,parent_wakeup_lost,child_start_lost,callback_dispatch_lost` |
| 追加轮询 | 上面四个加 `poll_dispatch_lost` |

### 限次、每轮上限与熔断

- **限次**：同一案例同一消息（同一指纹）最多自动重放 3 次，派发报错的那次也算一次；两次之间至少隔一个收敛窗口（`BKAPP_DIAGNOSTICS_RECOVERY_SETTLE_SECONDS`）。第 3 次派发满一个收敛窗口后（第 3 次派发报错时是紧接着的下一轮），恢复任务如果仍推导出同一条消息、案例仍在自动重放范围内（模式为 `apply`、类型已放开、项目在白名单内，本轮也没有熔断或因 `auto replay skipped` 只预演），且没有其他阻断，就记一行 `manual_required`，打告警日志 `[pipeline_diagnostics_alert] type=recovery_manual_required`，之后不再自动重放这条消息，转人工处置；控制台人工重放不受次数限制，也不计入次数。轮询每推进一次就是新的指纹，次数重新计算。
- **每轮上限**：每轮最多自动重放 20 个，其余留到下一轮。
- **熔断**：最近 5 分钟新立案的可重放案例超过 50 个时，本轮只预演，打告警日志 `[pipeline_diagnostics_alert] type=recovery_breaker_open`，指标 `pipeline_diagnostics_recovery_breaker_open_total{hostname}` 加一。这种突增通常说明 MQ 大面积丢消息，先排查 MQ，再在控制台人工重放；熔断不影响人工重放。

两种告警日志都受 `BKAPP_DIAGNOSTICS_ALERT_ENABLED` 控制（默认关闭，要在 `pipeline` 模块打开）；关闭时，转人工和熔断仍会体现在指标 `pipeline_diagnostics_recovery_total{result="manual_required"}`、`pipeline_diagnostics_recovery_breaker_open_total` 和下面恢复任务日志里的计数上，转人工还会出现在预演报告 `auto_apply` 的 `manual_required` 里。

这几个上限使用引擎默认值（Django 配置 `PIPELINE_DIAGNOSTICS_RECOVERY_MAX_ATTEMPTS`、`PIPELINE_DIAGNOSTICS_RECOVERY_MAX_PER_ROUND`、`PIPELINE_DIAGNOSTICS_RECOVERY_BREAKER_WINDOW_SECONDS`、`PIPELINE_DIAGNOSTICS_RECOVERY_BREAKER_THRESHOLD`），bk-sops 不单独提供 env。

恢复任务日志 `[pipeline_diagnostics_recovery] cases=... outcomes=...` 中与自动重放有关的计数：

| 计数 | 含义 |
| --- | --- |
| `auto_dispatched` | 已派发 |
| `auto_failed` | 派发报错（台账记一行 `blocked`，也算一次重放） |
| `auto_waiting` | 上一次重放还在等复核，或距上一次不到一个收敛窗口 |
| `auto_deferred` | 超出每轮上限，留到下一轮 |
| `manual_required` | 本轮用尽次数、转人工 |
| `auto_exhausted` | 之前已转人工，跳过 |
| `breaker_open` | 本轮熔断，只预演 |

开关都配了却没有案例被自动重放时，先看恢复任务日志的计数里有没有 `breaker_open`（本轮熔断，只预演），再查日志 `[pipeline_diagnostics_recovery] auto replay skipped`：后面跟 `scope resolver is not configured`（没有配置范围判定函数）、`cannot import <路径>`（范围判定函数导入失败）或 `scope setup failed`（准备本轮范围时出错，例如熔断计数查询失败），出现这些日志的轮次只预演。某个根流程的范围判定报错时日志为 `[pipeline_diagnostics_recovery] scope resolver failed: <root_pipeline_id>`，这个根流程本轮按范围外处理。案例在范围内但被阻断时，台账记一行 `blocked`，原因在台账记录的 `detail.blockers` 和预演报告的 `blockers` 里；放开初期常见的是 `fence emit is off`、`fence enforce is off`（`pipeline` 模块的门禁开关没打开）和 `message came from a skip and carries no fence token`（节点或条件并行网关是被跳过的）。都没有时，核对三个开关是否在 `pipeline` 模块生效、类型名是否拼对（写错的类型名被忽略，不报错）。

预演报告 `diagnostics_recovery_report` 的 `apply` 是人工和自动重放的结果合计，`auto_apply` 是其中自动重放的部分。

### env 开关速查（P3-4）

| 环境变量 | 默认 | 作用 |
| --- | --- | --- |
| `BKAPP_DIAGNOSTICS_RECOVERY_MODE` | `preview` | `apply` 时按下面两个开关自动重放 |
| `BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES` | 空 | 允许自动重放的类型，逗号分隔 |
| `BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS` | 空 | 允许自动重放的项目 ID，逗号分隔；`*` 表示全部 |

这三个变量只由 `pipeline` 模块消费 `task_data_clean` 队列的 worker 在恢复任务运行时读取，项目白名单也由这个 worker 里运行的范围判定函数读取，`default` 模块不读取；只设在 `default` 模块上不会报错，但也不会生效，所以直接设成应用级环境变量。

### 上线步骤（P3-4）

1. 前提：P3-3 已只预演观察过，各类型的阻断原因都能解释；门禁 `EMIT`、`ENFORCE` 都已打开；转人工和熔断的告警已接好：在 `pipeline` 模块打开 `BKAPP_DIAGNOSTICS_ALERT_ENABLED`（同时会打开引擎调度锁冲突的告警日志 `type=schedule_lock_conflict`），或者对指标 `pipeline_diagnostics_recovery_total{result="manual_required"}`、`pipeline_diagnostics_recovery_breaker_open_total` 配监控告警。新立案数一直超过熔断阈值时，每轮都会再打一次熔断告警日志、指标也每轮加一，告警规则要去重。
2. 选一两个项目：`BKAPP_DIAGNOSTICS_RECOVERY_MODE=apply`，`BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES` 配确定性形态的四个类型，`BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS` 配这些项目的 ID。
3. 每天看 `python manage.py diagnostics_recovery_report --hours 24` 的 `auto_apply`：绝大多数应为 `applied`；出现 `ineffective`、`manual_required` 时按证据查原因。同时关注转人工与熔断：告警日志 `type=recovery_manual_required`、`type=recovery_breaker_open`（打开告警时），或上面的指标。
4. 稳定后逐步扩大项目范围，最后配 `*`。
5. 轮询阈值和排除列表确认后，在 `BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES` 追加 `poll_dispatch_lost`。

指标 `pipeline_diagnostics_recovery_total{stuck_type, trigger, result, hostname}` 的 `result` 新增 `manual_required`。

回滚：设 `BKAPP_DIAGNOSTICS_RECOVERY_MODE=preview`（清空 `BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES` 效果相同），恢复任务回到只预演；只要恢复任务保持打开（`BKAPP_DIAGNOSTICS_RECOVERY_ENABLED=1`），已派发的重放照常复核。只清空 `BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS` 也会停止自动重放，但熔断仍每轮计算：新立案数超过阈值时仍累加熔断指标，打开告警时还会打 `recovery_breaker_open` 告警日志，所以不建议用它回滚。直接关掉 `BKAPP_DIAGNOSTICS_RECOVERY_ENABLED` 也会停止自动重放，但同时停止复核，已派发的记录停在 `dispatched`。

### 已知限制（P3-4）

- 范围内的案例派发时不写预演记录，但以下情况仍会在同一案例同一消息第一次看到时记一行预演：熔断或出现 `auto replay skipped` 日志的轮次、范围判定对该根流程报错时、有其他阻断时，以及放开之前。这些预演记录复核前如果已被自动重放修好，也算自愈。所以放开后预演报告的 `self_heal_ratio` 主要反映范围外的案例，而且偏高，只作参考。
- 熔断按所有项目、所有可重放类型的新立案数计算，不区分是否在白名单内。
- 范围内但有阻断原因（如后继不唯一、同一节点丢失多条回调）的案例只在台账记一行 `blocked`，不单独告警，需要在控制台或报告的 `blockers` 里查看。
- 每轮先处理最新发现的案例；可派发的超过 20 个时，较早的案例顺延到下一轮。
- `execute_dispatch_lost` 的节点、或 `child_start_lost` 父进程所在的条件并行网关是被跳过的（人工跳过，或节点超时策略"强制失败并跳过"），这类案例不自动重放：跳过接口派发的消息不带令牌，原消息晚到时会绕过门禁再执行一次。它们在台账记一行 `blocked`，原因 `message came from a skip and carries no fence token`；确认已排除队列积压后，在控制台人工重放（需要确认风险）。
- 并行分支结束时如果生成唤醒父进程的令牌失败（引擎日志 `[fence] build fence for process(...) failed, dispatch without fence`），这条唤醒消息不带令牌；原消息如果只是延迟，之后对这个 `parent_wakeup_lost` 案例的自动重放会和它各执行一次。这种情况很少见，出现时按这个日志关键字排查。
