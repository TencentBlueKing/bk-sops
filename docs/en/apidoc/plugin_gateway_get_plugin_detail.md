### Functional description

Get the detail of an exposed plugin by plugin id and version.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `plugin_id` | `string` | YES | plugin id |
| `version` | `string` | NO | plugin version; default version is used when omitted |

### Request Example

```text
GET /apigw/plugin-gateway/plugins/plugin_job_execute/?version=1.2.0
```

### Return Result Example

```json
{
  "result": true,
  "data": {
    "id": "plugin_job_execute",
    "plugin_version": "1.2.0",
    "url": "https://bk-sops.example/apigw/plugin-gateway/runs/",
    "methods": ["POST"],
    "polling": {
      "url": "https://bk-sops.example/apigw/plugin-gateway/runs/status/",
      "task_tag_key": "open_plugin_run_id"
    }
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `data.plugin_version` | `string` | resolved plugin version |
| `data.url` | `string` | execution registration URL |
| `data.methods` | `list` | allowed methods |
| `data.polling.url` | `string` | polling URL |
| `data.polling.task_tag_key` | `string` | polling task identifier field |
