### Functional description

Receive internal callback data from callback-mode plugins and asynchronously advance a plugin gateway run.

This endpoint is intended for the bk-sops plugin runtime shell. Normal consumers should not call it directly. Repeated callbacks for terminal runs return the current status idempotently.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `run_id` | `string` | YES | run identifier |
| `callback_data` | `object` | NO | plugin callback data |

### Request Example

```text
POST /apigw/plugin-gateway/runs/4f3c2b1a0d9e8f7766554433221100aa/internal-callback/
```

```json
{
  "callback_data": {
    "status": "success",
    "job_instance_id": 1001
  }
}
```

### Return Result Example

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
    "status": "WAITING_CALLBACK"
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `data.open_plugin_run_id` | `string` | run identifier |
| `data.status` | `string` | current run status |
