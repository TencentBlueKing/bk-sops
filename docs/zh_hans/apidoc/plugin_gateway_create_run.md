### 功能描述

创建一条插件执行记录。记录创建后会进入 `CREATED`，再由 `open_plugin_dispatch` 队列调度组件运行壳执行。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `source_key` | `string` | 是 | 来源标识 |
| `plugin_id` | `string` | 是 | 插件 ID |
| `plugin_version` | `string` | 是 | 插件版本 |
| `client_request_id` | `string` | 是 | 调用方内的幂等键 |
| `callback_url` | `string` | 是 | 回调地址 |
| `callback_token` | `string` | 是 | 回调时写入 `X-Callback-Token` 的 token |
| `inputs` | `object` | 否 | 插件输入 |
| `context` | `object` | 否 | 业务上下文。推荐传 `scope_type`、`scope_value`、`operator`，可选透传 `space_id`、`task_id`、`node_id`、`task_name` |
| `operator` | `string` | 否 | 兼容字段；未传 `context.operator` 时会写入运行上下文，未传时若网关请求带用户名则自动复用 |
| `project_id` | `int` | 否 | 兼容字段；新接入方推荐使用 `context` 由标准运维侧解析项目 |

### 请求参数示例

```json
{
  "source_key": "bkflow",
  "plugin_id": "builtin__job_execute_task",
  "plugin_version": "legacy",
  "client_request_id": "task_1_node_1_attempt_1",
  "callback_url": "https://bkflow.example.com/api/plugin-gateway/callback",
  "callback_token": "token-001",
  "inputs": {
    "target_ip": "127.0.0.1"
  },
  "context": {
    "scope_type": "biz",
    "scope_value": "2",
    "operator": "bkflow-user",
    "space_id": "bkflow-space-1",
    "task_id": "task_1",
    "node_id": "node_1",
    "task_name": "demo task"
  }
}
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
    "status": "CREATED"
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.open_plugin_run_id` | `string` | 运行 ID |
| `data.status` | `string` | 当前运行状态 |

### 上下文与项目解析

- `context.scope_type=biz` 或 `cmdb_biz` 且 `scope_value` 为业务 ID 时，优先按 `Project.bk_biz_id` 自动解析标准运维项目。
- 未解析到业务项目时，按来源配置 `scope_project_map["<scope_type>:<scope_value>"]` 映射项目。
- 仍未解析到项目时，回退来源配置 `default_project_id`。
- 都拿不到项目时，本次 run 会失败并返回明确错误。
- `context.operator` 会写入插件运行上下文，供 JOB/CC 等底层系统做真实操作人与权限校验。

### 错误字段说明

失败响应会额外返回 `error_type`，用于区分常见联调错误：

- `plugin_not_enabled`
- `plugin_version_unavailable`
- `plugin_removed`
- `source_unreachable`
