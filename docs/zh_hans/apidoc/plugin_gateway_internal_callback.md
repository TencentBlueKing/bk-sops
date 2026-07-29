### 功能描述

接收回调型插件写回的内部回调数据，并异步推进插件网关运行记录。

该接口由标准运维插件运行壳使用，不建议普通接入方直接调用。终态 run 重复回调会幂等返回当前状态。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `run_id` | `string` | 是 | 运行 ID |
| `callback_data` | `object` | 否 | 插件回调数据 |

### 请求参数示例

```text
POST /apigw/plugin-gateway/runs/4f3c2b1a0d9e8f7766554433221100aa/internal-callback/
```

```json
{
  "callback_data": {
    "status": "success",
    "job_instance_id": 1001
  }
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
