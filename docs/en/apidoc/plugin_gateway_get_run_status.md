### Functional description

Poll the run status of an open plugin execution.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `task_tag` | `string` | YES | run identifier, equal to `open_plugin_run_id` |

### Request Example

```text
GET /apigw/plugin-gateway/runs/status/?task_tag=run-001
```

### Return Result Example

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

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `data.status` | `string` | run status |
| `data.outputs` | `object` | output payload |
| `data.error_message` | `string` | error message when failed |
