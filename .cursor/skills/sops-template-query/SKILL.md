---
name: sops-template-query
description: "当用户需要查找模板、了解模板参数、查看有哪些流程模板时触发。引导通过 MCP 工具完成模板搜索和详情查询。"
---

# SOPS 模板查询技能

## 适用场景

用户意图包括：查找模板、模板列表、模板参数、有哪些模板、搜索流程、查看模板详情。

## 前置条件

用户必须提供：

- **bk_biz_id**：业务 ID

若用户未提供，主动询问。

## 工作流程

### Step 1：搜索模板列表

使用 MCP 工具 `get_template_list`，参数说明：

| 参数 | 必填 | 说明 |
|------|------|------|
| bk_biz_id | 是 | 业务 ID |
| name_keyword | 否 | 模板名称关键词搜索（英文不区分大小写） |
| template_source | 否 | 模板来源：`business`（业务流程，默认）/ `project`（项目流程）/ `common`（公共流程） |
| id_in | 否 | 逗号分隔的模板 ID 列表，用于过滤 |

> 注意：MCP 下 `get_template_list` 响应**不包含** `auth_actions`。

### Step 2：展示模板列表

将结果以 Markdown 表格呈现：

| ID | 名称 | 分类 | 创建人 | 最后编辑时间 |
|----|------|------|--------|------------|

分类字段中文映射：

| 原始值 | 中文 |
|--------|------|
| OpsTools | 运维工具 |
| MonitorAlarm | 监控告警 |
| ConfManage | 配置管理 |
| DevTools | 开发工具 |
| EnterpriseIT | 企业IT |
| OfficeApp | 办公应用 |
| Other | 其它 |

### Step 3：获取模板详情（用户请求时）

使用 MCP 工具 `get_template_info`，参数说明：

| 参数 | 必填 | 说明 |
|------|------|------|
| bk_biz_id | 是 | 业务 ID |
| template_id | 是 | 模板 ID |
| template_source | 否 | 模板来源：`business` / `project` / `common` |
| include_constants | 是 | 设为 `true`，获取变量信息 |
| include_executor_proxy | 否 | 设为 `true`，获取执行代理信息 |
| include_subprocess | 否 | 设为 `true`，获取子流程信息 |
| include_notify | 否 | 设为 `true`，获取通知信息 |
| unfold_subprocess | 否 | 展开子流程完整配置。设为 `true` 时，`pipeline_tree` 中每个 SubProcess 节点将包含 `pipeline` 字段，其中包含该子流程的完整 `pipeline_tree`（递归展开所有层级）。适用于 AI Agent 分析、流程可视化等需要获取完整流程结构的场景。默认 `false`。 |

> 注意：MCP 下 `get_template_info` 响应**不包含** `pipeline_tree`，但可通过设置 `unfold_subprocess=true` 在各 SubProcess 节点的 `pipeline` 字段中获取子流程的完整结构。
>
> `unfold_subprocess` 注意事项：只对有子流程的模板有效；递归深度受 `TEMPLATE_MAX_RECURSIVE_NUMBER` 限制；展开失败时返回 `result=False`。

### Step 4：展示模板详情

**基本信息**：名称、分类（中文）、创建人、创建时间、最后编辑人、最后编辑时间。

**变量参数表**（仅展示 `show_type="show"` 的变量）：

| 变量KEY | 变量名称 | 类型 | 来源 | 默认值 | 说明 |

来源（`source_type`）映射：

| source_type | 中文 |
|-------------|------|
| custom | 自定义变量 |
| component_inputs | 插件输入参数 |
| component_outputs | 插件输出结果 |

类型（`custom_type`，当 `source_type=custom` 时）映射：

| custom_type | 中文 |
|-------------|------|
| input | 输入框 |
| textarea | 文本框 |
| datetime | 日期时间 |
| int | 整数 |

## 关键规则

- `get_template_list` 不返回 `auth_actions`
- `get_template_info` 不返回顶层 `pipeline_tree`
- `unfold_subprocess=true` 时，各 SubProcess 节点将通过 `pipeline` 字段携带其完整子流程结构（递归展开）
- `show_type="show"` 的变量是创建任务时用户需要填写的参数
- `show_type="hide"` 的变量是隐藏变量，通常不展示给用户
- `template_source` 决定模板来源：`business`=业务流程，`project`=项目流程，`common`=公共流程
- `name_keyword` 搜索英文不区分大小写

## 常见问题

- **查不到模板**：确认 `bk_biz_id` 是否正确，确认 `template_source` 是否匹配
- **模板没有参数**：该模板不需要用户输入参数，可直接创建任务
- **想了解模板的流程结构**：使用 `unfold_subprocess=true` 调用 `get_template_info`，可在各 SubProcess 节点的 `pipeline` 字段中获取子流程完整结构；如需查看顶层 `pipeline_tree`，建议用户在标准运维 Web 界面查看

## API 文档查阅

需要详细参数信息时，参阅以下文档：

- `.cursor/skills/references/get_template_list.md`
- `.cursor/skills/references/get_template_info.md`
