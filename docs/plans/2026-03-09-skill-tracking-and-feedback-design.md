# Skill 埋点与反馈机制设计

## 背景

标准运维后续会在 OpenClaw 构建 Skill 集，用于操作标准运维（构建流程、执行任务、查询状态等）。当前缺乏以下能力：

1. **全链路 API 追踪**：只有任务创建被标记为 MCP 来源（`create_method="mcp"`），模板查询、任务状态查询等读操作没有被追踪
2. **AI 提效度量**：无法统计用户通过 AI 完成一次完整操作的端到端耗时
3. **用户反馈收集**：没有机制让用户对 AI 操作结果给出满意度评价

## 设计目标

- 以 Skill 为追踪主体，在工作流关键节点主动上报事件
- 后端提供轻量追踪 API，Skill 通过 MCP Tool 直接调用
- 关键事件存 DB，全量明细写 OT span
- 支持用户反馈收集

## 整体架构

```
用户 ←→ OpenClaw AI Agent
              │
              │ 读取 Skill 指令
              ▼
        ┌──────────────┐
        │  SOPS Skill   │  ← 工作流编排（Markdown 指令）
        │  (e.g. task-  │
        │   execution)  │
        └──────┬───────┘
               │
     ┌─────────┼──────────┐
     │         │          │
     ▼         ▼          ▼
┌────────┐ ┌────────┐ ┌──────────────┐
│MCP Tool│ │MCP Tool│ │ Tracking API │  ← SOPS 后端新增
│(业务)  │ │(业务)  │ │ (apigw)      │
└────────┘ └────────┘ └──────────────┘
     │         │          │
     ▼         ▼          ▼
┌─────────────────────────────────────┐
│        SOPS Backend                  │
│  ┌─────────┐  ┌───────────────────┐ │
│  │现有业务  │  │ SkillTrackingEvent│ │
│  │逻辑     │  │ SkillFeedback     │ │
│  └─────────┘  └───────────────────┘ │
│                     │               │
│              ┌──────┴──────┐        │
│              │   OT Span   │        │
│              └─────────────┘        │
└─────────────────────────────────────┘
```

关键决策：

1. Skill 是追踪发起方，在工作流开始/关键步骤/结束时主动调用 Tracking API
2. Tracking API 是标准 apigw 接口，Skill 通过 MCP Tool 直接调用
3. 每次 Skill 执行生成一个 `session_id`（UUID），贯穿所有追踪事件
4. 关键事件（session_start / session_end）存 DB，全量事件同时写 OT span

## 后端 Tracking API

### report_skill_event — 上报 Skill 事件

```
POST /apigw/report_skill_event/
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | Skill 执行的唯一会话 ID（UUID，由 Skill 生成） |
| skill_name | string | 是 | Skill 名称（如 `sops-task-execution`） |
| action | string | 是 | 事件类型：`session_start` / `step_complete` / `session_end` / `session_error` |
| step_name | string | 否 | 当前步骤名（如 `find_template`、`create_task`） |
| bk_biz_id | int | 否 | 业务 ID |
| context | object | 否 | 上下文信息，如 `{"template_id": 123, "task_id": 456}` |
| elapsed_ms | int | 否 | 距 session 开始的累计耗时（毫秒） |
| error_message | string | 否 | 失败时的错误信息 |

### submit_skill_feedback — 提交用户反馈

```
POST /apigw/submit_skill_feedback/
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 关联的 Skill 会话 ID |
| skill_name | string | 是 | Skill 名称 |
| rating | int | 是 | 满意度评分（1-5） |
| comment | string | 否 | 文字反馈 |
| bk_biz_id | int | 否 | 业务 ID |

## 数据模型

放在 `gcloud/analysis_statistics` 模块下，复用现有统计体系。

### SkillTrackingEvent

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| session_id | CharField(64) | 会话 ID，索引 |
| skill_name | CharField(128) | Skill 名称 |
| action | CharField(32) | 事件类型 |
| step_name | CharField(128) | 步骤名称 |
| bk_biz_id | IntegerField | 业务 ID |
| operator | CharField(128) | 操作人 |
| app_code | CharField(128) | 调用方 app_code |
| context | JSONField | 上下文数据 |
| elapsed_ms | IntegerField | 累计耗时 |
| error_message | TextField | 错误信息 |
| created_at | DateTimeField | 创建时间 |

### SkillFeedback

| 字段 | 类型 | 说明 |
|------|------|------|
| id | AutoField | 主键 |
| session_id | CharField(64) | 会话 ID，索引 |
| skill_name | CharField(128) | Skill 名称 |
| rating | IntegerField | 满意度 1-5 |
| comment | TextField | 文字反馈 |
| operator | CharField(128) | 反馈人 |
| bk_biz_id | IntegerField | 业务 ID |
| created_at | DateTimeField | 创建时间 |

### 存储策略

- **DB**：`session_start`、`session_end`、`session_error` 事件 + 全部反馈记录
- **OT Span**：所有事件（含 `step_complete`）写 span attribute
- **过期清理**：复用 `STATISTICS_VALIDITY_DAY` 配置

## Skill 层追踪集成

### 新增基础 Skill：sops-tracking

新建 `sops-tracking` Skill，定义追踪规范。不直接面向用户，作为其他 Skill 的内部依赖。

核心内容：
- session_id 生成规则（UUID）
- 各事件的调用时机和参数组装
- 反馈收集的引导话术

### 追踪注入点

以 `sops-task-execution` 为例：

```
Step 0 (新增): 生成 session_id
    → report_skill_event(action=session_start, skill_name=sops-task-execution)

Step 1: 查找目标模板 → get_template_list
    → report_skill_event(action=step_complete, step_name=find_template, context={template_id})

Step 2: 获取模板参数 → get_template_info

Step 3: 向用户确认参数值

Step 4: 创建任务 → create_task
    → report_skill_event(action=step_complete, step_name=create_task, context={task_id})

Step 5: 启动任务 → start_task

Step 6: 确认任务启动 → get_task_status
    → report_skill_event(action=session_end, elapsed_ms=..., context={task_id, state})

Step 7 (新增): 引导用户反馈
    → 用户评分后调用 submit_skill_feedback(session_id, rating, comment)
```

失败场景：任何步骤失败时调用 `report_skill_event(action=session_error, error_message=...)`。

### 各 Skill 追踪注入点

| Skill | 注入点 |
|-------|--------|
| sops-template-query | session_start → 搜索模板(step) → 获取详情(step) → session_end → 反馈 |
| sops-task-monitoring | session_start → 获取状态(step) → 定位失败(step) → session_end → 反馈 |
| sops-task-execution | 如上文完整链路 |

### MCP Tool 注册

Tracking API 注册为 MCP Tool，Skill 通过 MCP 调用：

| MCP Tool | 对应 API | 注册位置 |
|----------|---------|---------|
| report_skill_event | POST /apigw/report_skill_event/ | 通用查询 MCP Server |
| submit_skill_feedback | POST /apigw/submit_skill_feedback/ | 通用查询 MCP Server |

### Skill 追踪规范（写入每个业务 Skill）

```markdown
## 追踪规范

本 Skill 执行全程遵循追踪规范：
1. 开始前：生成 UUID 作为 session_id，调用 report_skill_event 上报 session_start
2. 关键步骤完成后：调用 report_skill_event 上报 step_complete
3. 结束时：调用 report_skill_event 上报 session_end，包含总耗时
4. 失败时：调用 report_skill_event 上报 session_error
5. 最后一步：引导用户评分并调用 submit_skill_feedback
```

## AI 提效度量

### 度量指标

| 指标 | 计算方式 |
|------|---------|
| AI 操作耗时 | `session_end.elapsed_ms` |
| Skill 使用次数 | 按 skill_name 分组 count session_start |
| Skill 成功率 | session_end 数量 / session_start 数量 |
| 按业务维度统计 | 按 bk_biz_id 分组 |
| 按用户维度统计 | 按 operator 分组 |
| 步骤级耗时分布 | 同一 session 中相邻 step_complete 事件的时间差 |

### 反馈分析

| 指标 | 计算方式 |
|------|---------|
| 平均满意度 | 按 skill_name 分组 avg rating |
| 满意度趋势 | 按时间窗口聚合 |
| 低分反馈 | rating <= 2 的记录 + comment |

### 后续扩展（本期不做）

- 引入人工操作基线后，计算 "AI 提效比 = 人工平均耗时 / AI 平均耗时"
- 与 `TaskflowStatistics.create_method` 交叉分析 MCP vs 手工创建的任务特征

## 实现范围

### 后端

1. 新增 `SkillTrackingEvent` 和 `SkillFeedback` Model
2. 新增 `report_skill_event` 和 `submit_skill_feedback` apigw view
3. 注册 API 到 apigw 资源配置
4. 注册为 MCP Tool

### Skill

1. 新建 `sops-tracking` 基础 Skill
2. 改造 `sops-task-execution`、`sops-template-query`、`sops-task-monitoring` 三个 Skill，注入追踪和反馈步骤
