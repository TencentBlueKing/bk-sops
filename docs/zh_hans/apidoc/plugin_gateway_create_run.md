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
| `project_id` | `int` | 否 | 项目 ID |

### 请求参数示例

```json
{
  "source_key": "bkflow",
  "plugin_id": "plugin_job_execute",
  "plugin_version": "1.2.0",
  "client_request_id": "task_1_node_1_attempt_1",
  "callback_url": "https://bkflow.example.com/api/open-plugin/callback",
  "callback_token": "token-001",
  "inputs": {
    "target_ip": "127.0.0.1"
  }
}
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "run-001",
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
