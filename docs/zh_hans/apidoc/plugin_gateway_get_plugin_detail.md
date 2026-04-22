### 功能描述

按插件 ID 和版本查询开放插件详情。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `plugin_id` | `string` | 是 | 插件 ID |
| `version` | `string` | 否 | 插件版本；不传时使用默认版本 |

### 请求参数示例

```text
GET /apigw/plugin-gateway/plugins/plugin_job_execute/?version=1.2.0
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "id": "plugin_job_execute",
    "name": "JOB 执行作业",
    "plugin_source": "builtin",
    "plugin_code": "job_execute_task",
    "plugin_version": "1.2.0",
    "wrapper_version": "v4.0.0",
    "url": "https://bk-sops.example/apigw/plugin-gateway/runs/",
    "methods": ["POST"],
    "inputs": [],
    "polling": {
      "url": "https://bk-sops.example/apigw/plugin-gateway/runs/status/",
      "task_tag_key": "open_plugin_run_id"
    }
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.plugin_version` | `string` | 当前返回的插件版本 |
| `data.url` | `string` | 创建执行记录的地址 |
| `data.methods` | `list` | 允许的调用方法 |
| `data.polling.url` | `string` | 轮询状态地址 |
| `data.polling.task_tag_key` | `string` | 轮询时使用的任务标识字段 |
