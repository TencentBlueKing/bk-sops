### 功能描述

取消一条插件执行记录。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `run_id` | `string` | 是 | 运行 ID |

### 请求参数示例

```text
POST /apigw/plugin-gateway/runs/run-001/cancel/
```

兼容无尾斜杠路径：

```text
POST /apigw/plugin-gateway/runs/run-001/cancel
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "run-001",
    "status": "CANCELLED"
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.open_plugin_run_id` | `string` | 运行 ID |
| `data.status` | `string` | 更新后的状态 |
