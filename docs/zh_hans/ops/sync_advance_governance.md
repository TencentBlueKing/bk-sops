# S7 同步节点推进中断：检测与安全恢复

同步节点成功后通常由同一个 worker 继续下一节点，正常推进不经过回调、轮询或后继消息队列。节点 FINISHED 写入早于输出保存，所以仅看到成功和长时间无动静，不能直接补发后继。

本次功能默认关闭，首次随 `bamboo-pipeline==3.24.21` 和配套的 `bamboo-engine==2.6.9` 正式发布；`bamboo-pipeline==3.24.22` 修复了检查点开关打开后的两处问题，仍依赖 `bamboo-engine==2.6.9`。应用当前固定 3.24.22，引擎由运行时精确依赖安装。发包完成不代表已部署生产或开启功能。原有 S1 专指异步调度完成后的后继消息未推进，S7 类型为 `sync_advance_stalled`。

## 检测与恢复条件

启用后，signature 快档也检查清醒的同步进程。对运行中的流程，核对成功源节点、版本、静默时间、没有当前版本 Schedule，以及暂停/冻结等条件。无匹配检查点时仅登记疑似中断；历史任务越过扫描位置后需要显式回扫，不能承诺自动补扫全部历史。

输出全部保存后，引擎才创建输出检查点。每个 Process 最多一条，正常 worker 与恢复方在事务中竞争推进权：

| 状态 | 含义 | 允许的处理 |
| --- | --- | --- |
| READY | 输出完整、推进权未被领取 | 正常 worker 或恢复方竞争，只有一方成功 |
| RELEASED | 恢复方已接管，原 worker 不得继续 | 通过正式入口补发带预期状态的唯一后继；消息再次丢失且仍在源节点时可重试 |
| CLAIMED | 原 worker 已取得推进权 | 不允许超时抢占；原 worker 崩溃也转人工 |
| 无匹配记录 | 输出完整性与推进权没有足够证据 | 只诊断，人工核查；不能伪造 READY |

接管会原子更新检查点和 Process 休眠标志，再发送后继 execute；不重跑成功插件、不强改业务节点成功状态。过期版本、跳过、忽略错误、后继不唯一、暂停/冻结/结束均禁止恢复。S7 不能用 confirm_risk 绕过安全条件。重复后继消息复用已有预期状态检查；迟到的旧 worker 和数据库中断重试也核对推进权。

## 配置与发布顺序

应用侧统一入口（运行时仍使用原有两个配置）：

| bk-sops 环境变量 | 默认 | 作用 |
| --- | --- | --- |
| BKAPP_DIAGNOSTICS_S7_ENABLED | 0 | 同时启用输出检查点与 S7 检测能力，恢复仍受防重复检查和恢复模式限制 |

旧 `BKAPP_PIPELINE_SYNC_ADVANCE_CHECKPOINT_ENABLED` 和 `BKAPP_DIAGNOSTICS_SYNC_ADVANCE_ENABLED` 保留兼容；未配置新入口时原有组合不变，新旧同时配置时须一致。不配置新旧变量时两项均关闭。旧应用版本不认识新入口，回退前需按对应值恢复旧变量。

仍需启用 signature 扫描、发送与执行预期状态检查（FENCE_EMIT_ENABLED / FENCE_ENFORCE）。人工恢复由 apply 开关控制；自动恢复由恢复模式、类型与项目白名单、限次、自动暂停等原有约束控制，不依赖人工 apply 开关。自动类型名称是 `sync_advance_stalled`。

包含统一开关改动的应用版本，配置 `BKAPP_DIAGNOSTICS_S7_ENABLED=1` 后，还需使用检测总开关（扫描范围包含 `signature`）、`BKAPP_PIPELINE_FENCE_MODE=enforce` 和 `BKAPP_DIAGNOSTICS_RECOVERY_POLICY=preview/auto` 配置上述能力，见 [统一开关与旧配置迁移](stuck_governance_switches.md)。S7 入口不会自动放开检测、人工或自动恢复。

1. 使用 `bamboo-pipeline==3.24.22`（精确依赖 `bamboo-engine==2.6.9`）构建应用，保持 `BKAPP_DIAGNOSTICS_S7_ENABLED=0`（旧变量已移除或同为 `0`）。打开检查点开关前，所有 worker 至少为 3.24.22；3.24.21 在开关打开时存在下文所述的暂停/撤销与 READY 重试问题。使用该版本执行 `python manage.py migrate --noinput`，确认命令退出码为 `0`，并通过 `python manage.py showmigrations eri` 确认 `0006_syncadvancecheckpoint` 标记为 `[X]`。迁移失败时停止发布；即使不开 S7，也必须完成此迁移，不能仅以 `bin/pre_release` 最终返回成功作为依据。
2. 迁移成功后，再启动新版 worker/cleaner，并升级所有可能处理这些流程的 worker。混合旧 worker 期间禁止 S7 接管；旧 worker 不认识推进权协议。保持开关关闭，验证代表性的历史任务清理成功、耗时与资源开销可接受，再考虑启用 S7。
3. 评估额外数据库查询、锁、写入吞吐后，开启检查点和诊断，先仅预览；确认样本后再按项目开启 apply。
4. 回退时先关闭所有恢复 apply，保留新 worker 与执行预期状态检查，处理完在途任务和检查点后，再关闭检查点或退回旧 worker。不要直接删除检查点表。

新模型使用 ORM 级关联删除，不建数据库外键。新版 cleaner 删除 Process 时，即使 S7 开关关闭且检查点表为空，也会访问该表并增加关联清理操作，所以关闭开关不能代替迁移与清理验证。旧运行时删除 Process 不会被新表阻止，但可能留下孤立检查点；后续清理须核实 Process 已不存在，不得按时间删除仍有效记录。

## 已验证与未验证

2026-10-28 配套正式包已发布到 PyPI：[bamboo-pipeline 3.24.21](https://pypi.org/project/bamboo-pipeline/3.24.21/)、[bamboo-engine 2.6.9](https://pypi.org/project/bamboo-engine/2.6.9/)。发布包的文件哈希、配套依赖、S7 代码及迁移文件已核验；Python 3.6 独立环境安装、`pip check`、两个 S7 开关默认关闭和内存 SQLite 迁移验证通过。这些检查不代替应用部署与生产数据库验证。

2026-11-02 发布 [bamboo-pipeline 3.24.22](https://pypi.org/project/bamboo-pipeline/3.24.22/)，仍依赖 `bamboo-engine==2.6.9`，没有新增迁移。修正两处检查点开关打开后的问题：同步节点运行中暂停或撤销整个任务时，worker 仍写入并竞争推进权，再按原有逻辑把进程标记为暂停或结束，继续后任务可以跑完，不再被判为疑似中断；输出检查点为 READY 时遇到数据库中断，重试只在 RELEASED/CLAIMED 时放弃，READY 时继续竞争，不丢消息、不重跑插件。本机 MySQL 8.0 复现与 bamboo-engine 完整 CI 通过；发布包的文件哈希、依赖和修复代码已核验。尚未在 stag 打开开关验证，也没有容量数据。

2026-10-27 独立 DevCloud：211 项引擎相关测试、277 项默认配置 diagnostics 回归通过；最新16项 S7 契约测试通过（与前述测试部分重叠），模型与迁移检查一致。真实 worker 终止/暂停复现后，通过正式恢复入口验证人工、自动、再次补发、迟到原 worker、重复消息与拒绝恢复边界。所有源同步节点无 Schedule，输出传递与源/后继执行次数分别验证。

原 E2E 47 个任务保留。本次新增任务与截图见 [S7 端到端验证](https://doc.weixin.qq.com/smartpage/a1_AIoAtXhKAM4CNoWUrHdy0T3OW9AVW_a?p=gSFXsn)。原始任务通过 DevCloud IP 端口 18081 访问，需要内网连接。新增恢复完成后已关闭 apply，保留卡住样本。

未进行生产部署、生产容量验证或所有业务插件副作用的恰好一次证明。原有不带预期状态的人工直接操作不在本次安全保证内。
