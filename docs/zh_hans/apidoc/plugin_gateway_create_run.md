### 功能描述

创建一条插件执行记录。

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
| `operator` | `string` | 否 | 可选操作人；传入后会透传给下游插件上下文 |
| `project_id` | `int` | 否 | 项目 ID |

### 请求参数示例

```json
{
  "source_key": "bkflow",
  "plugin_id": "bk_plugin_demo",
  "plugin_version": "1.1.0",
  "client_request_id": "task_1_node_1_attempt_1",
  "callback_url": "https://bkflow.example.com/api/plugin-gateway/callback",
  "callback_token": "token-001",
  "inputs": {
    "target_ip": "127.0.0.1"
  },
  "operator": "bkflow-user"
}
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
    "status": "WAITING_CALLBACK"
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

### 错误字段说明

失败响应会额外返回 `error_type`，用于区分常见联调错误：

- `plugin_not_enabled`
- `plugin_version_unavailable`
- `plugin_removed`
- `source_unreachable`
