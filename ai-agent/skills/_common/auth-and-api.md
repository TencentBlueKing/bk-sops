# 认证与 API 调用约定

> 本模块为 SOPS Skill 公共依赖，在打包时内联到各 Skill 的 SKILL.md 中。

---

## 0. 环境就绪检查

**每次 Skill 启动时，在执行任何工作流程之前，必须先完成以下就绪检查。**

### 检查流程

1. **检查 MCP 服务可用性**：根据 §3.3 接入关系表，确认本 Skill 所需的 MCP Server 均已配置
   - 尝试列出可用的 MCP Server 列表，或对所需 Server 发起一次轻量调用
   - [就绪] 全部就绪 → 继续
   - [缺失] 存在缺失 → **阻塞后续流程**，按 §3.5 引导用户配置
2. **检查认证信息**：按 §2 检查环境变量
   - [就绪] 就绪 → 进入 Skill 工作流程
   - [缺失] 缺失 → 按 §2 引导用户配置

### 缺失 MCP 服务时的标准话术

```
[风险提示] 当前缺少以下标准运维 MCP 服务，无法执行本 Skill 的核心功能：

  {缺失的 MCP Server 列表，含名称和用途}

请在 Cursor Settings → MCP 中添加对应的 MCP 服务配置。
配置方法和参数请参考下方说明。
```

随后输出 §3.5 中对应 MCP Server 的配置 JSON 片段，供用户直接复制使用。

### 扩展就绪检查（按需执行）

以下三个维度不在 Skill 启动时阻塞检查，而是在工作流程的相应步骤中按需评估：

| 维度 | 检查内容 | 检查时机 | 缺失时处理 |
|------|---------|---------|-----------|
| **知识覆盖** | 当前场景是否有对应的知识库类目 | flow-review / flow-builder 识别类目后 | 标记为"知识盲区"，降低建议置信度，回退到通用最佳实践 |
| **记忆完整度** | 当前操作所需的记忆章节是否存在 | 按各 Skill 上下文需求清单检查 | 标记缺失章节，提示对当前操作的影响（如"无参数偏好，需全部手动填写"），用降级策略兜底 |
| **模板丰富度** | 当前业务是否有可用的流程模板 | task-runner 定位流程时 / flow-builder 查重时 | 引导新建流程 |

**与启动阻塞检查的区别**：基础设施和认证是硬性前提（缺失则阻塞），扩展维度是软性评估（缺失则降级但不阻塞）。

### 失败归因：错误 vs 环境缺口

当操作执行失败或结果不理想时，在分析具体错误原因之前，优先做一轮环境缺口检查：

| 失败现象 | 可能的环境缺口 | 检查方法 | 补救措施 |
|---------|--------------|---------|---------|
| flow-review 给出的建议明显不相关 | 知识覆盖缺失——场景未被任何类目覆盖 | 检查 `_references/INDEX.md` 匹配结果 | 标记为知识盲区，回退到通用最佳实践 |
| task-runner 参数全部要求手动填写 | 记忆缺失——该业务无参数偏好 | 检查记忆中 `## 参数偏好` 章节 | 执行完成后引导建立参数记忆 |
| change-validator 使用默认阈值但用户觉得不合理 | 约束缺失——业务未自定义风控规则 | 检查记忆中 `## 约束规则` 章节 | 引导用户配置业务专属规则 |
| flow-builder 查重未发现相似模板 | 模板缺失——业务模板库空或太少 | 检查 `get_template_list` 结果数 | 直接基于知识库构建新流程 |
| troubleshooter 无法匹配已知问题 | 问题库缺失——该业务无历史问题记录 | 检查记忆中 `## 已知问题` 章节 | 本次排查后引导沉淀为首条已知问题 |

**处理原则**：环境缺口不是错误，是改进信号。检测到缺口时：
1. **透明**：告知用户当前能力受限的原因
2. **兜底**：用降级策略完成当前操作（如用默认值、通用建议）
3. **引导**：操作完成后引导用户填补缺口（如建立记忆、配置规则）

---

## 1. 认证方式

所有标准运维 API 请求必须携带以下 HTTP 请求头：

| Header | 说明 |
|--------|------|
| `X-Bkapi-Authorization` | JSON 对象，包含 `bk_app_code`、`bk_app_secret`、`access_token` |
| `X-Bkapi-Ai-Platform` | 固定值 `openclaw`，标识请求来自 OpenClaw 平台 |
| `X-Bkapi-Ai-Skill` | 当前 Skill 名称，如 `bk-sops-task-runner` |

**示例**：
```
X-Bkapi-Authorization: {"bk_app_code":"xxx","bk_app_secret":"xxx","access_token":"xxx"}
X-Bkapi-Ai-Platform: openclaw
X-Bkapi-Ai-Skill: bk-sops-task-runner
```

---

## 2. 认证信息获取

1. **检查环境变量**：依次读取 `BK_APP_ID`、`BK_APP_SECRET`、`ACCESS_TOKEN`
2. **缺失时**：引导用户完成配置，并说明如何获取：
   - `bk_app_code` / `bk_app_secret`：在蓝鲸开发者中心创建应用后获取
   - `access_token`：通过蓝鲸 API 网关或用户登录态获取
3. **认证失败时**：给出明确错误说明和排查路径，例如：
   - Token 过期 → 提示重新获取 access_token
   - 应用未授权 → 提示检查应用是否已接入目标环境

---

## 3. 标准运维 MCP 服务

标准运维按业务领域提供 **4 个 MCP Server**，各 Skill 按需接入对应域的 Server。

### 3.1 MCP 服务概览

| MCP Server | 名称 | 工具数 | 定位 |
|---|---|---|---|
| `bk-sops-prod-task` | 【标准运维】任务管理MCP | 15 | 任务全生命周期：创建/启动/操作/状态/日志/参数修改 |
| `bk-sops-prod-template` | 【标准运维】流程模板MCP | 9 | 模板/公共流程/执行方案/插件查询 |
| `bk-sops-prod-periodic` | 【标准运维】周期任务MCP | 6 | 周期任务 CRUD + cron/参数修改 |
| `bk-sops-prod-analytics` | 【标准运维】数据分析MCP | 4 | 任务列表/统计/轻应用/职能化 |

### 3.2 各域工具清单

**任务域 `bk-sops-prod-task`**（15 个）：
`create_task` / `start_task` / `operate_task` / `operate_node` / `get_task_status` / `get_task_detail` / `get_task_node_detail` / `get_task_node_log` / `get_task_plugin_log` / `get_node_job_executed_log` / `modify_constants_for_task` / `get_tasks_status` / `get_task_node_data` / `get_task_operate_record` / `node_callback`

**模板域 `bk-sops-prod-template`**（9 个）：
`get_template_list` / `get_template_info` / `get_common_template_list` / `get_common_template_info` / `get_template_schemes` / `preview_task_tree` / `get_plugin_list` / `get_plugin_detail` / `get_plugin_base_info`

**周期任务域 `bk-sops-prod-periodic`**（6 个）：
`get_periodic_task_list` / `get_periodic_task_info` / `set_periodic_task_enabled` / `modify_cron_for_periodic_task` / `modify_constants_for_periodic_task` / `create_periodic_task`

**数据分析域 `bk-sops-prod-analytics`**（4 个）：
`get_task_list` / `get_task_effective_time` / `get_mini_app_list` / `get_functionalization_task_list`

### 3.3 Skill → MCP Server 接入关系

| Skill | tasks | templates | periodic | analytics |
|-------|:-----:|:---------:|:--------:|:---------:|
| task-runner | ● | ● | | |
| task-monitor | ● | | | ● |
| troubleshooter | ● | ● | | |
| permission-manager | ● | ● | | |
| flow-review | | ● | | |
| change-validator | | ● | | |
| audit-reporter | ● | | | ● |
| health-checker | | ● | ● | ● |
| flow-builder | | ● | | |
| ops-insight | | ● | ● | ● |

### 3.4 调用规则

1. **使用 MCP 工具**：根据接口所属域调用对应 MCP Server
2. **API Base URL**（极少数 MCP 未覆盖的场景兜底）：
   - 生产环境（默认）：`https://bk-sops.apigw.o.woa.com/prod`
   - 预发环境：`https://bk-sops.apigw.o.woa.com/stage`

### 3.5 MCP 服务配置引导

当用户缺少所需的 MCP 服务时，引导用户在 **Cursor Settings → MCP** 中添加以下配置。

**配置位置**：Cursor Settings → Features → MCP Servers → Add new MCP server

每个 MCP Server 的配置如下（用户需将 `bk_app_secret` 和 `access_token` 替换为自己的实际值）：

#### bk-sops-prod-task（任务管理）

```json
{
  "bk-sops-prod-task": {
    "type": "streamableHttp",
    "url": "https://bk-apigateway.apigw.o.woa.com/prod/api/v2/mcp-servers/bk-sops-prod-task/mcp/",
    "description": "【标准运维】任务管理MCP",
    "headers": {
      "X-Bkapi-Authorization": "{\"bk_app_code\": \"bksops\", \"bk_app_secret\": \"<替换为实际值>\", \"access_token\": \"<替换为实际值>\"}",
      "X-Bkapi-Timeout": "300",
      "Content-Type": "application/json"
    }
  }
}
```

#### bk-sops-prod-template（流程模板）

```json
{
  "bk-sops-prod-template": {
    "type": "streamableHttp",
    "url": "https://bk-apigateway.apigw.o.woa.com/prod/api/v2/mcp-servers/bk-sops-prod-template/mcp/",
    "description": "【标准运维】流程模板MCP",
    "headers": {
      "X-Bkapi-Authorization": "{\"bk_app_code\": \"bksops\", \"bk_app_secret\": \"<替换为实际值>\", \"access_token\": \"<替换为实际值>\"}",
      "X-Bkapi-Timeout": "300",
      "Content-Type": "application/json"
    }
  }
}
```

#### bk-sops-prod-periodic（周期任务）

```json
{
  "bk-sops-prod-periodic": {
    "type": "streamableHttp",
    "url": "https://bk-apigateway.apigw.o.woa.com/prod/api/v2/mcp-servers/bk-sops-prod-periodic/mcp/",
    "description": "【标准运维】周期任务MCP",
    "headers": {
      "X-Bkapi-Authorization": "{\"bk_app_code\": \"bksops\", \"bk_app_secret\": \"<替换为实际值>\", \"access_token\": \"<替换为实际值>\"}",
      "X-Bkapi-Timeout": "300",
      "Content-Type": "application/json"
    }
  }
}
```

#### bk-sops-prod-analytics（数据分析）

```json
{
  "bk-sops-prod-analytics": {
    "type": "streamableHttp",
    "url": "https://bk-apigateway.apigw.o.woa.com/prod/api/v2/mcp-servers/bk-sops-prod-analytics/mcp/",
    "description": "【标准运维】数据分析MCP",
    "headers": {
      "X-Bkapi-Authorization": "{\"bk_app_code\": \"bksops\", \"bk_app_secret\": \"<替换为实际值>\", \"access_token\": \"<替换为实际值>\"}",
      "X-Bkapi-Timeout": "300",
      "Content-Type": "application/json"
    }
  }
}
```

**认证参数获取方式**：
- `bk_app_secret`：在蓝鲸开发者中心 → 应用管理 → 应用详情中获取
- `access_token`：通过蓝鲸 API 网关获取（有效期通常 30 天，过期需重新获取）

**提示**：只需配置本 Skill 实际使用的 MCP Server（参见 §3.3 接入关系表），无需全部添加。

---

## 4. 错误处理

| 情况 | 处理方式 |
|------|----------|
| `result: false` | 提取响应体中的 `message` 字段，展示给用户 |
| 401 / 403 | 引导用户检查 access_token 有效性和权限配置 |
| 网络错误 | 建议检查网络连通性及 VPN 状态 |
