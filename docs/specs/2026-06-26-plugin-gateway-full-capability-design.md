# 插件网关全量插件能力设计（标准运维侧）

## 概述

本设计是 `docs/specs/2026-04-21-plugin-gateway-design.md`（插件网关 MVP）的演进版，目标是把标准运维**全部插件能力（内置 + 第三方）**通过插件网关暴露给 BKFlow，并让 BKFlow 选定的「有业务含义的空间」能够以**真实用户身份 + 业务上下文**真实执行这些插件。

原 MVP 的实现边界是「仅第三方 + 同步完成型、目录只返回第三方」。本设计在该基线之上给出标准运维侧的完整方案；MVP 设计文档已在本轮迭代后回写为已收敛状态。

> 配套文档：BKFlow 侧设计见 BKFlow 仓库 `docs/specs/2026-06-26-sops-open-plugin-full-capability-design.md`；需求与协议背景见 BKFlow 仓库 `docs/specs/2026-04-20-sops-open-plugin-integration-design.md`。本文为 brainstorming skill 输出。

## 范围

本设计聚焦**标准运维侧**职责：

- 开放插件目录：内置 + 第三方统一暴露
- 执行：基于组件运行壳（不建引擎实例）真实执行插件，支持同步 / 轮询 / 回调
- 业务上下文与身份解析：由 BKFlow 透传的 `context` 解析 `project` 与 operator
- 协议：`uniform_api v4.0.0` execute 体新增可选 `context` 的标准运维侧读取与兜底
- 状态机、回调桥接、异步、取消、超时、错误处理
- 来源治理：不开放黑名单、回调域白名单、跨应用隔离

BKFlow 侧的协议构造、空间准入与服务端校验在配套 BKFlow 设计中描述，不在本文展开。

## 目标与非目标

### 目标

1. 目录暴露内置组件与第三方插件，分类透传标准运维内部 `group/category`。
2. 以**方案 B（组件运行壳）**真实执行插件：直接调用组件 `Service.execute/schedule`，不创建引擎 `PipelineModel` 实例。
3. 支持同步、轮询、回调三种执行模式。
4. 由 `context` 解析 `project`（混合映射）并以**真实 operator** 执行，权限校验委托组件与底层系统。
5. 架构支持全部插件，提供来源级「不开放黑名单」排除少数高风险/强依赖用户级凭证的插件。
6. 开放插件执行进入独立 worker 域，不与存量任务 worker 混跑。

### 非目标

1. 不改造标准运维引擎本身，也不在网关内复刻完整引擎（仅实现薄运行壳）。
2. 不新增用户级凭证透传/代理身份的完整模型（operator 权限由底层系统校验，强依赖用户级凭证的插件进黑名单）。
3. 不在网关内为多版本插件做进程级隔离。
4. 不升 `uniform_api` wrapper 版本（向后兼容地补齐 v4.0.0 的 `context`）。

## 关键设计决策

1. **执行架构 = 方案 B**：在 `plugin_gateway` 内实现「组件运行壳」，复用 bamboo-pipeline 的 `Service / Data / parent_data` 原语，自行驱动 schedule / 回调 / 超时 / 重试，**不建引擎实例**（无任务列表污染）。
2. **统一执行路径**：内置组件与第三方组件（`RemotePluginComponent`）都走运行壳，逐步退役直连 `PluginServiceApiClient` 的执行路径。
3. **真实 operator**：`context.operator` 写入 `parent_data` 的 executor/operator，权限校验交由组件与底层系统（JOB/CC 等）执行；网关不自造权限。
4. **project 混合映射**：`scope_type==biz → bk_biz_id → sops Project` 自动解析；否则来源映射表；否则 `default_project_id` 兜底；都拿不到则 run 明确失败。
5. **协议向后兼容**：execute 体新增可选 `context`；不传则按 `default_project_id` 兜底，老第三方来源零改造。
6. **不开放黑名单**：来源级 `do_not_open_list`，在目录列表 / 详情 / 执行登记三处一致拦截。
7. **运行态恢复 `RUNNING`**：状态机恢复 `CREATED→RUNNING→(WAITING_CALLBACK)→SUCCEEDED/FAILED/CANCELLED`，`detail_meta.running_tag` 恢复为 `RUNNING` 以支持轮询模式。

## 整体数据流

```text
（BKFlow）平台授权空间可接入来源 → 空间内 per-plugin 开关
        ↓
（BKFlow）uniform_api v4.0.0 组件 execute，透传 inputs + context{scope_type,scope_value,operator,space_id,task_id,...}
        ↓
（标准运维）plugin_gateway 登记 run（幂等）
        · context 解析 sops Project / bk_biz_id / operator
        · open_plugin_dispatch 队列：实例化组件 Service，构造 data(inputs)+parent_data，调 service.execute()
        · need_schedule → 落 RUNNING/WAITING_CALLBACK，转 polling/callback
        ↓
（标准运维）组件直接执行（无引擎实例）
        · 轮询型：open_plugin_polling 队列按 service.interval 驱动 service.schedule()
        · 回调型：open_plugin_callback 入口收到下游回调 → service.schedule(callback_data=...)
        ↓
组件终态 → 读 data.outputs/ex_data → gateway run 落终态 → 回调 BKFlow（或 BKFlow 轮询 status）
```

## 1. 目录统一抽象

### 1.1 内置组件适配器

新增内置组件元数据适配器，遍历 `ComponentLibrary` / 组件注册表，输出 v4 字段：

- `plugin_source = "builtin"`
- `plugin_code = 组件 code`
- `plugin_id`：对外不透明、URL-safe、稳定标识（建议 `{source}__{code}` 形式的可逆编码）
- `name`、`group/category`（透传标准运维内部分类）
- `versions / default_version / latest_version`：取组件注册版本集（`ComponentModel.version`）

第三方插件沿用现有来源（`plugin_source = "third_party"`），`plugin_id` 规则与内置统一。列表 / 详情合并输出，对 BKFlow 表现为同一来源下的统一目录。

### 1.2 分类

透传标准运维内部 `group/category`，避免只粗分 builtin / third_party 两档（沿用 `2026-04-20` 集成设计 5.3）。分类与列表接口支持用 `plugin_source=builtin|third_party` 固定过滤来源，供 BKFlow 配置为两个独立的顶层 API 插件入口；过滤后左侧分类仍返回各来源内部真实的 `group/category`，不会把 `builtin / third_party` 当作业务分类。两个入口在治理和执行层仍属于同一个标准运维来源。

### 1.3 schema 转换

把组件 `inputs_format / outputs_format / form` 转成 v4 `inputs / outputs` schema。现有 `_convert_schema_fields` 是 JSON-Schema 形态雏形，需适配内置组件的 schema 形态。

### 1.4 黑名单一致性

来源级 `do_not_open_list(plugin_id)` 在 list / detail / execute 登记三处一致拦截：不暴露、不可取详情、不可执行。

## 2. 执行：组件运行壳（方案 B 核心）

在 `plugin_gateway` 内新增薄运行壳，复用 bamboo-pipeline 的 `Service / Data / parent_data` 原语，**不创建 `PipelineModel`**。

### 2.1 dispatch（`open_plugin_dispatch` 队列）

1. 取组件类：内置走 `ComponentLibrary.get_component_class(code)`，第三方走 `RemotePluginComponent`。
2. 构造 `data`(inputs) 与 `parent_data`(operator / executor / project_id / bk_biz_id 等)。
3. 调 `service.execute(data, parent_data)`：
   - 返回 False → `FAILED`（取 `data.outputs.ex_data`）。
   - `service.need_schedule()` 为真 → 落 `RUNNING` / `WAITING_CALLBACK`，进入下一阶段。
   - 否则同步完成 → 读 `data.get_outputs()` → `SUCCEEDED`。

### 2.2 polling（`open_plugin_polling` 队列）

按 `service.interval` 周期调 `service.schedule(data, parent_data, callback_data=None)`，`is_schedule_finished()` 为真则落终态；schedule 返回 False → `FAILED`。设**最大 schedule 次数 / 总时长**保护，防止无限循环。

### 2.3 callback（`open_plugin_callback` 队列）

回调型组件：网关暴露内部回调入口，收到下游回调后调 `service.schedule(data, parent_data, callback_data=...)`。

### 2.4 约束（必须正视）

不同组件依赖的 `parent_data` 键不同，运行壳无法对任意组件构造完备上下文。设计取向：**只暴露上下文可由 scope/operator/project 满足的组件**；构造不出必需上下文的组件进黑名单或标记不可用，而非硬塞。落地时以组件 `context_inputs` 声明为依据做可用性判定。

## 3. project / identity 解析（`services/context.py`）

输入：execute 体的 `context{scope_type, scope_value, operator, space_id, ...}`。

- **project 解析顺序**：
  1. `scope_type == "biz"` → `bk_biz_id = scope_value` → 复用标准运维「业务→Project」解析/同步获取 sops Project。
  2. 否则查来源映射表（来源级配置：BKFlow scope → sops project_id）。
  3. 否则 `default_project_id` 兜底。
  4. 都拿不到 → run 以明确错误失败。
- **identity**：`operator = context.operator`，写入 `parent_data` 的 executor/operator。底层系统调用沿用标准运维既有 ESB/APIGW client，以 operator 身份发起；**权限校验委托底层系统**。

## 4. 协议：`uniform_api v4.0.0` 的 `context`（标准运维侧）

execute 体新增可选 `context` 对象，标准运维侧读取字段：`scope_type / scope_value / operator / space_id / task_id / node_id / task_name`。

- 不传 `context`（老来源 / 老协议）→ 按 `default_project_id` 兜底，保持兼容。
- `detail_meta`、polling / callback 协议不变。
- 不升 wrapper 版本：这是补齐 `2026-04-20` 集成设计 6.5 中规划但 MVP 未实现的 `context`。

## 5. 状态机与回调桥接

- 运行态：`CREATED / RUNNING / WAITING_CALLBACK / SUCCEEDED / FAILED / CANCELLED`。
- 恢复 `RUNNING` 态与 `detail_meta.running_tag = "RUNNING"`（MVP 清理时改成了 `WAITING_CALLBACK`，本设计恢复以支持轮询模式）。
- 组件终态 → 落 gateway run 终态 + outputs / error → 回调 BKFlow，沿用现有 callback 能力（`raise_for_status`、`callback_delivered_at` 去重、有限重试、输出截断）。

## 6. worker 隔离

独立队列 `open_plugin_dispatch / open_plugin_polling / open_plugin_callback`，与存量任务队列物理隔离（沿用 `2026-04-20` 集成设计 5.8）。隔离原则按「调用来源」划分，内置与第三方都优先由开放插件 worker 承接。

## 7. 异步 / 取消 / 超时 / 错误 / 截断

- **异步**：轮询型组件维持 `RUNNING`，BKFlow 按 polling 查 gateway status；回调型组件落 `WAITING_CALLBACK`，BKFlow 停轮询等回调。
- **超时**：网关侧给 run 设执行超时窗口（来源/插件级可配），超时主动置 `FAILED` 并回调；`callback_token` TTL ≥ 节点超时窗口 + 容差；BKFlow 节点 timeout 作为最终兜底。
- **取消**：BKFlow cancel → `cancel_run` → 运行壳 best-effort 调底层取消，置 `CANCELLED` 并回调；取消失败不阻塞 BKFlow，记审计；已终态幂等返回。
- **错误映射**：登记期错误（project 解析失败 / operator 缺失 / 命中黑名单 / 版本失效）→ 同步 4xx；运行期失败（execute/schedule 抛异常或失败）→ 异步回调 `FAILED` + `ex_data`。
- **输出截断**：沿用现有 `MAX_OUTPUT_BYTES`，超限截断大字段并打 `truncated / truncated_fields` 标记。

## 8. 安全边界

- 来源级 `do_not_open_list` 与回调域白名单显式治理。
- run 查询按 `caller_app_code` 做跨应用隔离。
- operator 鉴权委托底层系统；强依赖用户级凭证的插件进黑名单。
- 回调 token 加密存储。

## 9. 测试与验收（标准运维侧）

- 目录返回内置 + 第三方，分类透传 `group/category`；黑名单三处一致拦截。
- 内置插件经运行壳真实执行：同步 / 异步轮询 / 回调三模式。
- project 混合映射（biz 自动 / 映射表 / default）；operator 透传且无权限被正确拒绝。
- 独立 worker 队列隔离，不影响存量任务执行链路。
- 遵循 TDD：先写失败测试再实现。

## 10. 迁移与兼容

- **协议向后兼容**：不传 `context` → `default_project_id` 兜底，老第三方来源零改造。
- **第三方执行切换**：从直连 `PluginServiceApiClient` 改走运行壳（`RemotePluginComponent`），需回归证明行为等价；建议先并存、再收敛。
- **`running_tag` 恢复 `RUNNING`**：影响轮询语义，需回归现有第三方链路。
- **配套产物**：同步 APIGW 资源定义、中英文 apidoc、`apigw-docs.tgz` 归档。

## 11. 风险与后续

1. 方案 B 的运行壳需复刻引擎的 schedule / 回调 / 超时 / 重试语义，回调型组件最难；引擎/组件框架升级可能导致行为漂移。缓解：运行壳尽量薄、尽量直接复用框架原语，把漂移面控制到最小。
2. `parent_data` 构造对任意组件不完备：以 `context_inputs` 声明做可用性判定，构造不出的进黑名单。
3. operator 权限依赖：BKFlow 用户需在对应业务下有权限，否则插件执行被底层系统拒绝；这是产品前提，需在联调与运营中明确。
4. 统计口径需扩展到 `(plugin_source, plugin_code, plugin_version)`，避免不同来源同 code / 跨版本统计混淆。
