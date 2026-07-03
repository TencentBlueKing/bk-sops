### 功能描述

按插件 ID 和版本查询插件详情。内置插件 ID 使用 `builtin__<component_code>`，第三方插件 ID 兼容裸 `code`。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `plugin_id` | `string` | 是 | 插件 ID |
| `version` | `string` | 否 | 插件版本；不传时使用默认版本 |

### 请求参数示例

```text
GET /apigw/plugin-gateway/plugins/builtin__job_execute_task/?version=legacy
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "id": "builtin__job_execute_task",
    "name": "作业执行",
    "plugin_source": "builtin",
    "plugin_code": "job_execute_task",
    "plugin_version": "legacy",
    "wrapper_version": "",
    "description": "",
    "url": "https://bk-sops.example/apigw/plugin-gateway/runs/",
    "methods": ["POST"],
    "inputs": [
      {
        "key": "biz_id",
        "name": "业务 ID",
        "type": "integer",
        "description": "业务 ID",
        "required": true
      }
    ],
    "outputs": [
      {
        "key": "job_instance_id",
        "name": "作业实例 ID",
        "type": "integer",
        "description": "JOB instance id"
      }
    ],
    "polling": {
      "url": "https://bk-sops.example/apigw/plugin-gateway/runs/status/",
      "task_tag_key": "open_plugin_run_id",
      "success_tag": {
        "key": "data.status",
        "value": "SUCCEEDED",
        "data_key": "data.outputs"
      },
      "fail_tag": {
        "key": "data.status",
        "value": "FAILED",
        "msg_key": "data.error_message"
      },
      "running_tag": {
        "key": "data.status",
        "value": "RUNNING"
      }
    }
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.id` | `string` | 插件 ID |
| `data.plugin_source` | `string` | 插件来源，取值为 `builtin` 或 `third_party` |
| `data.plugin_code` | `string` | 插件原始 code |
| `data.plugin_version` | `string` | 当前返回的插件版本 |
| `data.url` | `string` | 创建执行记录的地址 |
| `data.methods` | `list` | 允许的调用方法 |
| `data.inputs` | `list` | 插件输入 schema 列表 |
| `data.outputs` | `list` | 插件输出 schema 列表 |
| `data.polling.url` | `string` | 轮询状态地址 |
| `data.polling.task_tag_key` | `string` | 轮询时使用的任务标识字段 |
| `data.polling.running_tag` | `object` | 运行中状态匹配规则，当前值为 `RUNNING` |
