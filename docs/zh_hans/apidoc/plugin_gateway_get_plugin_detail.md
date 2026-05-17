### 功能描述

按插件 ID 和版本查询插件详情。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `plugin_id` | `string` | 是 | 插件 ID |
| `version` | `string` | 否 | 插件版本；不传时使用默认版本 |

### 请求参数示例

```text
GET /apigw/plugin-gateway/plugins/bk_plugin_demo/?version=1.1.0
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "id": "bk_plugin_demo",
    "name": "Demo Plugin",
    "plugin_source": "third_party",
    "plugin_code": "bk_plugin_demo",
    "plugin_version": "1.1.0",
    "wrapper_version": "2.0.0",
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
| `data.inputs` | `list` | 插件输入 schema 列表 |
| `data.outputs` | `list` | 插件输出 schema 列表 |
| `data.polling.url` | `string` | 轮询状态地址 |
| `data.polling.task_tag_key` | `string` | 轮询时使用的任务标识字段 |
