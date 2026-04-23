### 功能描述

查询单条插件执行记录详情。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `run_id` | `string` | 是 | 运行 ID |

### 请求参数示例

```text
GET /apigw/plugin-gateway/runs/4f3c2b1a0d9e8f7766554433221100aa/
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
    "status": "SUCCEEDED",
    "plugin_id": "plugin_job_execute",
    "plugin_version": "1.2.0",
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
| `data.open_plugin_run_id` | `string` | 运行 ID |
| `data.status` | `string` | 运行状态 |
| `data.plugin_id` | `string` | 插件 ID |
| `data.plugin_version` | `string` | 插件版本 |
| `data.outputs` | `object` | 输出数据 |
| `data.error_message` | `string` | 错误信息 |
