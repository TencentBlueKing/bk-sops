# 流程卡住治理二期设计

## 概述

二期目标不是继续围绕本次独立子流程 callback 竞态做定点修补，而是把“流程为什么卡住、如何快速识别、如何安全介入、何时触发告警”沉淀成一套可复用的治理能力。

设计上采用两层结构：

- `bamboo-engine`：沉淀通用运行时诊断、分型、安全操作和告警底座
- `bk-sops`：补业务语义映射、任务级展示入口、业务增强规则和运维操作包装

这样其他使用 `bamboo-engine` 的平台也能复用大部分能力，只有少量和 `TaskFlowInstance / TaskCallBackRecord / 独立子流程业务语义` 强耦合的内容留在 `bk-sops`。

## 背景与问题抽象

一期暴露的是一个典型症状：运行时对象已经出现 `Process / State / Schedule / CallbackData` 漂移，但现有系统很难快速回答以下问题：

1. 当前任务到底卡在哪一种类型的问题上
2. 是运行时本身异常，还是业务层关系断裂
3. 现在是否还能安全恢复，应该恢复哪一步
4. 哪类问题在一段时间内正在变多，是否是某次发布引入的回归

因此二期不应继续按“发现一个 case 修一个 case”的方式推进，而应建设一套：

- 能采集关键运行时事件
- 能对历史 case 做统计和分型
- 能在实时场景下给出明确诊断结论
- 能对人工操作施加边界和审计
- 能按类型触发更有意义告警

## 二期目标

- 建立 `bamboo-engine` 通用的流程卡住事件埋点与诊断底座
- 建立历史卡住 case 样本库和可扩展的分型体系
- 建立可复用的“实时诊断 + 安全操作”框架
- 在 `bk-sops` 提供任务级诊断视角和业务增强能力
- 建立从基础症状到趋势异常的分层告警体系

## 非目标

- 不在二期直接重构整个 callback / schedule / process 状态模型
- 不尝试一次性覆盖所有历史异常场景，先从高价值类型开始
- 不把所有平台逻辑都塞进 `bamboo-engine`
- 不在本期做大规模前端重构，优先保证底座和诊断能力可用

## 设计原则

### 1. 先通用，后平台适配

只要问题判断依赖的对象是 `Process / State / Schedule / CallbackData / Node / ack` 这些引擎运行时对象，就优先进入 `bamboo-engine`。只有依赖 `bk-sops` 自身业务概念的规则和展示才留在 `bk-sops`。

### 2. 先可观测，再自动化

在缺乏运行时事件和历史样本的情况下，过早做通用自动修复风险很高。二期先建立“看得见、分得清、可追溯”的底座，再逐步开放更多安全操作。

### 3. 诊断与操作分离

诊断引擎负责判断“是什么问题”；安全操作框架负责判断“能不能动、怎么动、动完如何审计”。避免把判断逻辑散落在人工脚本里。

### 4. 最小侵入现网模型

优先通过事件埋点、日志、指标和少量持久化诊断信息解决问题；只有在确实需要时才增加少量兼容字段，不进行重型迁移。

## 总体架构

二期采用如下分层：

### 一、`bamboo-engine` 通用治理底座

负责：

- 统一事件埋点
- 运行时快照与诊断输入
- 历史异常样本沉淀
- 通用卡住分型
- 通用安全操作
- 通用告警原语

### 二、`bk-sops` 业务适配层

负责：

- `task_id / project_id / template_id` 等业务对象与引擎对象的映射
- 独立子流程、任务回调记录、任务实例状态等业务增强规则
- 面向运维同学的任务级诊断入口
- 权限、审计、操作记录和提示文案

## `bamboo-engine` 通用建设项

## 一、统一事件埋点模型

二期在 `bamboo-engine` 内部沉淀统一事件模型，覆盖流程执行关键路径上的重要时刻。第一批建议覆盖：

- `callback_accepted`
- `callback_data_persisted`
- `schedule_sent`
- `schedule_received`
- `schedule_lock_conflict`
- `schedule_retried`
- `schedule_consumed`
- `process_child_finished`
- `parent_ack_updated`
- `parent_wakeup`
- `state_changed`
- `manual_action_triggered`

建议统一字段：

- `root_pipeline_id`
- `node_id`
- `version`
- `process_id`
- `schedule_id`
- `callback_data_id`
- `event_type`
- `result`
- `reason`
- `duration`
- `operator`
- `engine_version`

这些字段全部使用引擎概念，不强制依赖 `bk-sops` 的任务语义。

## 二、历史异常样本库

基于引擎事件和运行时快照，建立一套历史 case 统计任务。目标是把“过去出现过哪些卡住任务”沉淀成结构化样本，而不是散落在临时日志里。

建议每条样本包含：

- `case_id`
- `root_pipeline_id`
- `first_seen_at`
- `severity`
- `stuck_type`
- `key_evidence`
- `last_status`
- `manual_actions`
- `final_resolution`

`bk-sops` 可以在此基础上补充业务字段，例如 `task_id / project_id / template_source`，但底层样本结构应先保持 engine 通用。

## 三、通用卡住分型框架

分型框架是二期核心。第一版优先从纯引擎运行时特征出发，建立可扩展规则集。建议先支持以下类型：

- `callback_lock_conflict`
- `schedule_lock_stuck`
- `missing_state_for_live_process`
- `process_alive_but_terminal_state`
- `parallel_ack_not_converged`
- `multiple_sleep_process_for_node`
- `version_mismatch_dropped_schedule`
- `schedule_finished_but_process_not_exited`

每种类型都定义：

- 命中条件
- 关键证据字段
- 风险等级
- 推荐检查项
- 可用安全操作
- 禁止直接操作项

规则输出格式必须统一，便于被 CLI、工作台和告警系统复用。

## 四、通用安全操作框架

二期需要在 `bamboo-engine` 提供受控操作入口，而不是继续让平台侧或人工脚本直接调用底层 runtime。

第一批建议提供的通用操作：

- replay callback data
- resend schedule
- expire schedule
- inspect process ack / converge status
- inspect node runtime readiness

每个操作都必须支持：

- `dry-run`
- 前置校验
- 风险提示
- 执行结果结构化返回
- 操作审计钩子

具体哪些操作对外开放，由上层平台按权限和风险决定。

## 五、通用告警原语

二期在 `bamboo-engine` 先沉淀最基础的异常症状告警能力，建议包括：

- callback 锁冲突重试耗尽
- schedule 长时间 `scheduling=True`
- 同节点存在多个 sleep process
- live process 当前节点缺少 state
- 父进程 `need_ack > ack_num` 持续超阈值

这些原语不直接面向业务方展示“任务故障原因”，而是作为平台侧更高层任务告警的输入。

## `bk-sops` 适配层建设项

## 一、业务增强规则

在通用分型结果基础上，`bk-sops` 增加依赖自身业务语义的增强规则。首批建议包括：

- `subprocess_relation_broken`
- `task_callback_record_inconsistent`
- `manual_bypass_caused_state_drift`
- `taskflow_terminal_state_mismatch`

这些规则可以引用：

- `TaskFlowInstance`
- `TaskFlowRelation`
- `TaskCallBackRecord`
- `TaskCallBackRecord.extra_info`
- `PipelineInstance`

但要避免把底层引擎分型逻辑反向塞进 `bamboo-engine`。

## 二、任务级实时诊断入口

`bk-sops` 负责把引擎侧诊断结果翻译成运维可直接使用的任务级视图，至少提供：

- 当前卡住类型
- 关键证据
- 当前风险等级
- 推荐检查动作
- 可执行人工操作
- 禁止直接操作的原因

初期可以先用命令行或管理页形式提供，不要求一开始就建设完整前端工作台。

## 三、任务级人工操作包装

平台侧负责把 engine 的通用安全操作包装成更容易理解的任务级动作，例如：

- 重放某个独立子流程节点的最新成功 callback
- 重投某个任务节点当前 schedule
- 标记某个过期 schedule 为人工失效

所有操作都必须具备：

- 操作权限校验
- 任务上下文校验
- 审计记录
- 风险说明
- 执行后结果回显

## 四、任务级告警编排

`bk-sops` 在通用告警原语之上做任务视角的聚合，分三层输出：

### 1. 基础症状告警

直接来自 `bamboo-engine` 的异常原语。

### 2. 任务级卡住告警

以任务实例为单位，聚合症状和分型结果，输出“任务卡住类型 + 证据摘要 + 推荐动作”。

### 3. 趋势类告警

按版本、组件、节点类型或时间窗口观测某类异常是否显著上升，用于识别回归发布或系统性风险。

## 实施阶段建议

二期按以下顺序推进：

### 阶段一：通用事件与样本沉淀

先把关键事件打全，并建立历史 case 样本库，解决“没有足够数据支撑通用治理”的问题。

### 阶段二：通用分型与实时诊断

在有样本和事件后，建设分型框架和诊断结果输出，让系统能稳定回答“当前是什么问题”。

### 阶段三：安全操作与任务级包装

在规则和边界稳定后，再把受控操作逐步开放给平台侧，并提供任务级入口和审计。

### 阶段四：全面告警

最后把基础症状、任务级异常和趋势异常接入完整告警体系，形成值班闭环。

## 与一期的关系

一期是二期的前置止血和最小验证：

- 一期新增的 callback 重试日志和 `callback_data_id / retry_count` 信息，可以直接复用到二期事件模型
- 一期的专用竞态分析命令和重放命令，可以演进为二期任务级工具的早期原型
- 一期验证了“引擎通用扩展点 + 平台业务适配层”这一分层策略是成立的

## 风险与控制

### 风险 1：过早把业务逻辑塞进 `bamboo-engine`

控制方式：

- 运行时特征进 engine
- 业务关系和任务语义留在 `bk-sops`
- 任何规则设计先判断依赖的是 engine 对象还是业务对象

### 风险 2：规则泛化过快导致误判

控制方式：

- 先从高确定性的纯运行时特征规则开始
- 用历史样本回放评估命中准确率
- 允许规则版本演进和逐步扩充

### 风险 3：安全操作开放过早

控制方式：

- 所有操作必须先支持 `dry-run`
- 默认只开放读操作和低风险动作
- 高风险动作必须经过更严格校验与审计

## 成功标准

二期完成后，至少应能回答：

- 某个引擎实例当前属于哪一类卡住问题
- 这种问题在过去一段时间是否高发
- 哪些人工操作是安全的，哪些不应执行
- 哪类异常是否在某个版本发布后显著上升

对于 `bk-sops`，额外要求：

- 运维同学输入任务 ID 后，能实时看到任务级诊断结果
- 常见卡住场景不再依赖人工翻表和临时脚本

## 发布建议

二期虽然整体由 `bk-sops` 牵头推动，但底座应优先从 `bamboo-engine` 开始：

1. 先在 `bamboo-engine` 落事件埋点、样本库和分型基础框架
2. 再在 `bk-sops` 增加业务增强规则和任务级展示
3. 最后分批开放安全操作和告警编排

这样可以最大化复用价值，也能降低未来多平台重复建设成本。
