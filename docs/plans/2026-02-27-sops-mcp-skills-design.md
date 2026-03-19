# 标准运维 MCP Skills 设计文档

## 背景

标准运维 (SOPS) 已提供 MCP 服务，运维用户可通过 AI 编码助手（Cursor、CodeBuddy、Claude Code）直接对话完成任务创建、状态查询等操作。当前缺少 Skill 来引导 AI 正确使用这些 MCP 工具，导致 AI 对 SOPS 领域知识不足，无法高效辅助用户。

## 目标

构建一套面向运维用户的 AI Skill，主要聚焦 MCP 调用场景，让 AI 能够：

1. 正确选择和调用 SOPS MCP 工具
2. 按照合理的工作流编排多步操作
3. 将 API 响应转化为用户可理解的信息
4. 处理常见错误并给出建议

## 目标用户

标准运维平台的运维使用者，通过 AI 编码助手与 SOPS 交互。

## 设计约束

- Skill 格式：SKILL.md，兼容 Cursor、CodeBuddy、Claude Code
- 文档策略：Skill 引导 AI 查阅项目中已有的 API 文档（`docs/apidoc/zh_hans/`），不内嵌完整参数说明
- 跨平台：使用 YAML Front Matter + 纯 Markdown，不依赖平台特有语法

## 架构

### 文件结构

```
.cursor/skills/
├── sops-mcp-basics/
│   └── SKILL.md
├── sops-task-execution/
│   └── SKILL.md
├── sops-task-monitoring/
│   └── SKILL.md
└── sops-template-query/
    └── SKILL.md
```

### 依赖关系

```
sops-mcp-basics (基础层)
    ↑ 被引用
    ├── sops-task-execution
    ├── sops-task-monitoring
    └── sops-template-query
```

### MCP Server 对照

| MCP Server | 工具列表 | 定位 |
|------------|---------|------|
| 任务执行 MCP | create_task, get_task_detail, get_task_node_detail, get_task_status, start_task | 任务创建与执行 |
| 通用查询 MCP | get_task_detail, get_task_node_detail, get_task_status, get_template_info, get_template_list, get_task_list | 信息查询 |

## Skill 详细设计

### 1. sops-mcp-basics

**定位**：基础层，被其他 Skill 引用。

**触发条件**：用户提到标准运维、SOPS、任务、模板等关键词。

**内容**：

- **MCP Server 说明**：两个 MCP Server 的工具清单、适用场景、选择策略
- **通用参数**：
  - `bk_biz_id`：业务 ID 或项目 ID（必填）
  - `scope`：bk_biz_id 的作用域，`cmdb_biz`（默认）或 `project`
- **统一响应格式**：`result`(bool) / `data` / `message`(string) / `trace_id`(string)
- **MCP 响应过滤**：MCP 调用与 API 网关的响应差异，哪些字段在 MCP 下不返回
- **错误处理**：检查 result 字段、读取 message、使用 trace_id 排查
- **文档查阅指引**：`docs/apidoc/zh_hans/{api_name}.md` 包含每个 API 的完整参数说明

### 2. sops-task-execution

**定位**：场景 Skill，引导 AI 完成"从模板创建并执行任务"的完整流程。

**触发条件**：用户要创建任务、执行任务、启动流程、跑一个模板。

**工作流**：

```
Step 1: get_template_list
  └─ 用 name_keyword 搜索或列出模板，帮用户找到目标模板
Step 2: get_template_info (include_constants=true)
  └─ 获取模板的全局变量（constants），注意 MCP 下不返回 pipeline_tree
Step 3: 向用户确认参数值
  └─ 提取 show_type="show" 的变量，展示 name/desc/custom_type，让用户填值
Step 4: create_task
  └─ 传入 template_id、name、constants
Step 5: start_task
  └─ 传入 task_id 启动执行
Step 6: get_task_status
  └─ 确认任务已启动（state=RUNNING）
```

**关键指引**：

- constants 的 KEY 格式为 `${key}`，VALUE 类型需与模板中定义保持一致
- `simplify_vars` 可将复杂类型变量简化为文本输入
- MCP 下 create_task 响应不含 `pipeline_tree`
- 创建后需要单独调用 start_task 启动，create_task 只是创建不执行

### 3. sops-task-monitoring

**定位**：场景 Skill，引导 AI 帮用户查看任务状态、定位失败原因。

**触发条件**：用户要查看任务状态、查看执行结果、排查失败、看节点详情。

**工作流**：

```
Step 1: get_task_status (with_ex_data=true)
  └─ 获取任务整体状态和所有节点 children
Step 2: 解读状态
  ├─ FINISHED → 任务成功完成，展示完成时间和耗时
  ├─ RUNNING → 任务执行中，展示当前正在执行的节点
  ├─ FAILED → 进入 Step 3
  ├─ SUSPENDED → 任务已暂停
  └─ REVOKED → 任务已终止
Step 3: 定位失败节点
  └─ 从 children 中递归查找 state="FAILED" 的节点，获取 node_id
Step 4: get_task_node_detail
  └─ 传入 task_id + node_id，获取 inputs/outputs/ex_data
Step 5: 分析并展示
  └─ 解读 ex_data 错误信息，向用户说明失败原因和建议操作
```

**关键指引**：

- 任务状态枚举：CREATED / RUNNING / FAILED / SUSPENDED / REVOKED / FINISHED
- children 是嵌套结构（dict of dict），需要递归遍历找到失败节点
- ex_data 可能是 JSON 字符串、HTML 字符串或普通字符串，需要适当解析
- MCP 下 get_task_node_detail 不返回 `histories`（重试记录）
- 向用户展示时应包含：节点名称、失败原因、输入参数、建议操作

### 4. sops-template-query

**定位**：场景 Skill，引导 AI 帮用户查找和理解流程模板。

**触发条件**：用户要查找模板、了解模板参数、看有哪些模板。

**工作流**：

```
Step 1: get_template_list
  └─ 支持 name_keyword 搜索、template_source 过滤（business/project/common）
Step 2: 展示模板列表
  └─ 以表格形式展示：ID、名称、分类、创建人、最后编辑时间
Step 3: get_template_info (按需)
  └─ 用户指定模板后，获取详情
Step 4: 解读并展示
  └─ 展示模板的全局变量、分类、创建信息
```

**关键指引**：

- MCP 下 get_template_list 不返回 `auth_actions`
- MCP 下 get_template_info 不返回 `pipeline_tree`
- category 枚举值对照：OpsTools=运维工具、MonitorAlarm=监控告警、ConfManage=配置管理、DevTools=开发工具、EnterpriseIT=企业IT、OfficeApp=办公应用、Other=其它
- template_source 对照：business=业务流程、project=项目流程、common=公共流程
- constants 中 show_type="show" 的变量是用户可见的输入参数

## Skill 通用结构

每个 SKILL.md 遵循以下结构：

```markdown
---
name: skill-name
description: "触发条件描述"
---

# Skill 标题

## 适用场景
何时触发此 Skill

## 前置条件
需要用户提供的信息（如 bk_biz_id）

## 工作流程
分步骤的 MCP 工具调用编排

## 结果展示规范
如何将 API 响应转化为用户可读信息

## API 文档查阅指引
需要详细参数时去哪里读文档

## 常见问题
典型错误和解决方法
```

## API 文档索引

Skill 引导 AI 查阅的文档路径：

| API 名称 | 文档路径 |
|----------|---------|
| create_task | docs/apidoc/zh_hans/create_task.md |
| start_task | docs/apidoc/zh_hans/start_task.md |
| get_task_status | docs/apidoc/zh_hans/get_task_status.md |
| get_task_detail | docs/apidoc/zh_hans/get_task_detail.md |
| get_task_list | docs/apidoc/zh_hans/get_task_list.md |
| get_task_node_detail | docs/apidoc/zh_hans/get_task_node_detail.md |
| get_task_node_data | docs/apidoc/zh_hans/get_task_node_data.md |
| operate_task | docs/apidoc/zh_hans/operate_task.md |
| operate_node | docs/apidoc/zh_hans/operate_node.md |
| get_template_list | docs/apidoc/zh_hans/get_template_list.md |
| get_template_info | docs/apidoc/zh_hans/get_template_info.md |
| get_template_schemes | docs/apidoc/zh_hans/get_template_schemes.md |
| preview_task_tree | docs/apidoc/zh_hans/preview_task_tree.md |

## 后续扩展

当前 4 个 Skill 覆盖核心场景，未来可扩展：

- `sops-periodic-task`：周期任务管理（创建/修改/启停周期任务）
- `sops-api-scripting`：帮用户编写 API 网关调用脚本（非 MCP 场景）
- `sops-batch-operations`：批量任务操作的最佳实践
