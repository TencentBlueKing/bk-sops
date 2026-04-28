### Functional description

Get the detail of a single plugin gateway run.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `run_id` | `string` | YES | run identifier |

### Request Example

```text
GET /apigw/plugin-gateway/runs/4f3c2b1a0d9e8f7766554433221100aa/
```

### Return Result Example

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

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `data.open_plugin_run_id` | `string` | run identifier |
| `data.status` | `string` | run status |
| `data.plugin_id` | `string` | plugin id |
| `data.plugin_version` | `string` | plugin version |
| `data.outputs` | `object` | output payload |
| `data.error_message` | `string` | error message |
