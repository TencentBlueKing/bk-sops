### Functional description

Get the detail of an exposed plugin by plugin id and version. Built-in plugin ids use `builtin__<component_code>`, while third-party plugins keep the bare code.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `plugin_id` | `string` | YES | plugin id |
| `version` | `string` | NO | plugin version; default version is used when omitted |

### Request Example

```text
GET /apigw/plugin-gateway/plugins/builtin__job_execute_task/?version=legacy
```

### Return Result Example

```json
{
  "result": true,
  "data": {
    "id": "builtin__job_execute_task",
    "name": "JOB Execute",
    "plugin_source": "builtin",
    "plugin_code": "job_execute_task",
    "plugin_version": "legacy",
    "version": "v4.0.0",
    "wrapper_version": "v4.0.0",
    "description": "",
    "url": "https://bk-sops.example/apigw/plugin-gateway/runs/",
    "methods": ["POST"],
    "inputs": [
      {
        "key": "biz_id",
        "name": "Business ID",
        "type": "integer",
        "description": "Business ID",
        "required": true
      }
    ],
    "outputs": [
      {
        "key": "job_instance_id",
        "name": "JOB instance ID",
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

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `data.id` | `string` | plugin id |
| `data.plugin_source` | `string` | plugin source, `builtin` or `third_party` |
| `data.plugin_code` | `string` | original plugin code |
| `data.plugin_version` | `string` | resolved plugin version |
| `data.version` | `string` | uniform_api wrapper version, currently `v4.0.0` |
| `data.wrapper_version` | `string` | uniform_api wrapper version, currently `v4.0.0` |
| `data.url` | `string` | execution registration URL |
| `data.methods` | `list` | allowed methods |
| `data.inputs` | `list` | input schema list |
| `data.outputs` | `list` | output schema list |
| `data.polling.url` | `string` | polling URL |
| `data.polling.task_tag_key` | `string` | polling task identifier field |
| `data.polling.running_tag` | `object` | running-state matching rule; current value is `RUNNING` |
