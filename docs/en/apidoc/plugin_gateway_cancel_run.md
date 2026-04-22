### Functional description

Cancel a single open plugin run record.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `run_id` | `string` | YES | run identifier |

### Request Example

```text
POST /apigw/plugin-gateway/runs/run-001/cancel/
```

### Return Result Example

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

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `data.open_plugin_run_id` | `string` | run identifier |
| `data.status` | `string` | updated status |
