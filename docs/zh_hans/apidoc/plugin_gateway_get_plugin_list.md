### 功能描述

查询开放插件网关可消费的插件列表。

#### 接口参数

无

### 请求参数示例

```text
GET /apigw/plugin-gateway/plugins/
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "total": 2,
    "apis": [
      {
        "id": "plugin_job_execute",
        "name": "JOB 执行作业",
        "plugin_source": "builtin",
        "plugin_code": "job_execute_task",
        "wrapper_version": "v4.0.0",
        "default_version": "1.2.0",
        "latest_version": "1.3.0",
        "versions": ["1.2.0", "1.3.0"],
        "meta_url_template": "https://bk-sops.example/apigw/plugin-gateway/plugins/plugin_job_execute/?version={version}"
      }
    ]
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.total` | `int` | 插件总数 |
| `data.apis` | `list` | 插件列表 |
| `data.apis[].id` | `string` | 插件 ID |
| `data.apis[].versions` | `list` | 可选版本列表 |
| `data.apis[].meta_url_template` | `string` | 查询详情的 URL 模板 |
