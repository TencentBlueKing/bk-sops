### 功能描述

按运行 ID 轮询插件执行状态。该接口用于 `uniform_api v4.0.0` 的 polling 协议。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `task_tag` | `string` | 是 | 运行 ID，对应 `open_plugin_run_id` |

### 请求参数示例

```text
GET /apigw/plugin-gateway/runs/status/?task_tag=4f3c2b1a0d9e8f7766554433221100aa
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "status": "SUCCEEDED",
    "outputs": {
      "job_instance_id": 1001
    },
    "error_message": ""
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.status` | `string` | 运行状态 |
| `data.outputs` | `object` | 输出数据 |
| `data.error_message` | `string` | 失败时的错误信息 |

### 状态说明

`status` 可能为 `CREATED`、`RUNNING`、`WAITING_CALLBACK`、`SUCCEEDED`、`FAILED`、`CANCELLED`。其中 `RUNNING` 对应插件详情中的 `polling.running_tag`。
