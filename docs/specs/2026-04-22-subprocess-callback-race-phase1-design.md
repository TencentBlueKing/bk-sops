# 独立子流程 Callback 竞态一期修复设计

## 概述

本设计聚焦修复独立子流程节点在 `task_success=False` 与 `task_success=True` callback 近时间触发时，成功 callback 可能因为 `schedule lock` 冲突被静默丢弃的问题。

一期目标是尽快止血，并为后续更通用的卡住诊断与恢复能力建设留出扩展点；不在本期重构 callback 事件模型，不引入全局事件排序语义。

## 问题背景

本次线上 case 体现出的核心问题链路如下：

1. 独立子流程节点会收到多次 callback，至少包含失败态通知和最终完成通知
2. `bamboo-engine` 对普通 `CALLBACK` 类型节点在 `schedule lock` 获取失败时直接返回，不会重试
3. 当失败 callback 持锁较久、成功 callback 随后到达时，成功 callback 可能已经写入 `CallbackData`，但对应的 `schedule` 未被真正消费
4. 父流程节点状态未能正确推进，后续容易衍生 `Process / State / Schedule / CallbackData` 漂移，人工误用 `runtime.execute()` 还会进一步放大问题

## 一期目标

- 修复独立子流程节点“最终成功 callback 因锁竞争静默丢失”的问题
- 不扩大 `bamboo-engine` 对所有 `CALLBACK` 节点的既有行为面
- 提供专用的竞态识别工具和安全重放工具，替代裸 `runtime.execute()` 人工恢复
- 保持现网数据模型兼容，不引入必须的数据迁移

## 非目标

- 不做全局“最新 callback 胜出”的事件排序机制
- 不把所有 `CALLBACK` 节点改造成可重试语义
- 不在本期建设通用卡住分型平台和工作台
- 不修改 `bk-sops` 的独立子流程业务语义和已有状态流转定义

## 设计原则

### 1. 优先修复 `bamboo-engine` 侧核心竞态

真正导致成功 callback 丢失的根因在 `bamboo-engine` 的 `schedule lock` 冲突处理逻辑里，因此一期修复必须落在引擎侧。

### 2. 默认关闭，按节点能力精确开启

新增能力必须是 `bamboo-engine` 的通用扩展点，但默认关闭。一期仅允许独立子流程节点开启，且仅对 `task_success=True` 的 callback 生效。

### 3. 不改主状态模型

一期不增加 `Process / State / Schedule / CallbackData` 的状态字段和迁移，只通过调度行为补丁、日志与工具实现止血。

### 4. 人工恢复必须走正式 callback 链路

恢复工具只能走已有的 callback / schedule / state 逻辑，不允许用 `runtime.execute()` 直接推动汇聚或后继节点。

## 方案设计

## 一、`bamboo-engine` 运行时补丁

### 1. 新增 Service 级扩展点

在 `Service` 基类新增一个默认返回 `False` 的能力钩子：

- 文件：`../bamboo-engine/runtime/bamboo-pipeline/pipeline/core/flow/activity/service_activity.py`
- 方法：`callback_lock_retryable(callback_data=None)`

用途：声明“当前 callback 在 `schedule lock` 冲突时是否允许有界重试”。

### 2. 独立子流程节点开启该能力

在 `SubprocessPluginService` 中重写该方法，仅当 callback payload 中 `task_success is True` 时返回 `True`。

- 文件：`pipeline_plugins/components/collections/subprocess_plugin/v1_0_0.py`

这样可以保证：

- `task_success=False` 仍保持现有行为，不会因为一期补丁被重复放大
- 只有“最终成功 callback”在锁竞争时得到一次补偿机会

### 3. 调整 `Engine.schedule` 的锁冲突分支

在 `../bamboo-engine/bamboo_engine/engine.py` 中：

- 保留 `MULTIPLE_CALLBACK` 既有重试行为
- 对普通 `CALLBACK` 节点，增加一段精确判定：
  - 若存在 `callback_data_id`
  - 且对应 service 声明 `callback_lock_retryable == True`
  - 则允许对当前 callback 做有界重试
- 重试次数放在 `headers` 中，不改数据库字段
- 达到上限后记录错误日志并返回

### 4. 一期不引入全局乱序仲裁

本期不做 callback 序号、最新事件水位等机制，依赖现有门禁兜底：

- `schedule.finished`
- `state.version != schedule.version`
- `state.name != RUNNING`

这保证了旧 callback 就算重放，也不会越过已有状态门禁错误覆盖终态。

## 二、`bk-sops` 工具补充

### 1. 离线识别竞态候选

新增管理命令，针对导出的任务关联记录识别“独立子流程 false/true callback 竞态”：

- 文件：`gcloud/taskflow3/management/commands/analyze_subprocess_callback_race.py`

识别特征包括：

- 同一 `node_id + version` 下同时存在 `task_success=False/True`
- `callback_data_count > schedule_times`
- 节点仍有未结束 schedule
- 节点状态仍为 `RUNNING / FAILED`

### 2. 安全重放最新成功 callback

新增管理命令，专用于独立子流程节点安全重放最新成功 callback：

- 文件：`gcloud/taskflow3/management/commands/replay_subprocess_success_callback.py`

校验条件包括：

- 当前任务为 engine v2
- 当前节点是 `subprocess_plugin`
- `state` 为 `RUNNING / FAILED`
- `schedule` 未 finished
- 当前节点能定位到唯一 sleep process
- 存在最新成功 callback data

如果节点当前为 `FAILED`，先按既有恢复语义把节点从 `FAILED -> READY -> RUNNING`，再通过 `NodeCommandDispatcher(...).dispatch(command="callback")` 进入正式 callback 链路。

## 三、日志与观测

一期不做完整埋点体系，但在引擎锁冲突分支补充足够的排障信息：

- `callback_data_id`
- `retry_count`
- callback payload
- retry exhausted 错误日志

这样后续再遇到类似问题时，至少能明确回答：

- 哪条 callback 因锁冲突进入重试
- 是否达到重试上限
- 当时的 callback payload 是失败还是成功

## 影响范围评估

### `bamboo-engine`

- 改动仅落在 `schedule lock` 冲突分支
- 默认行为不变
- 仅当 service 显式声明可重试时，普通 `CALLBACK` 节点才会重试
- 一期只有 `subprocess_plugin` 命中该逻辑

### `bk-sops`

- 独立子流程节点仅新增一个“成功 callback 可重试”的 service 级声明
- 新增两个应急命令，不影响线上主流程执行
- 未修改既有业务 API、前端、数据库模型

## 风险与控制

### 风险 1：旧 callback 乱序到达

控制方式：

- 仅对 `task_success=True` 开启重试
- 保留现有 `schedule.finished / version mismatch / state not running` 门禁

### 风险 2：把单次 callback 节点语义改宽

控制方式：

- 一期不修改全局 `CALLBACK` 语义
- 仅通过 service 钩子对白名单节点生效

### 风险 3：人工恢复误操作

控制方式：

- 官方恢复工具只支持独立子流程节点
- 默认 `dry-run`
- 必须通过安全校验才允许 `--apply`

## 测试策略

### `bamboo-engine`

- `subprocess_plugin` 的 `false -> true` 锁冲突补偿路径
- 重试达到上限后的退出路径
- 普通 `CALLBACK` 节点在锁冲突时仍保持原行为

### `bk-sops`

- `SubprocessPluginService.callback_lock_retryable`
- `analyze_subprocess_callback_race` 对竞态样本的识别
- `replay_subprocess_success_callback` 的安全检查与恢复路径

## 发布建议

1. 先回修 `bamboo-engine` 对应线上 tag
2. 同步落 `bk-sops` 的 service 适配和命令工具
3. 灰度观察引擎日志中的 callback 重试信息
4. 稳定后再评估同步到主干和其他维护分支
