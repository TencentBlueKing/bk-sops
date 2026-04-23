### Functional description

Cancel a single plugin gateway run record.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `run_id` | `string` | YES | run identifier |

### Request Example

```text
POST /apigw/plugin-gateway/runs/4f3c2b1a0d9e8f7766554433221100aa/cancel/
```

The slashless compatibility path is also accepted:

```text
POST /apigw/plugin-gateway/runs/4f3c2b1a0d9e8f7766554433221100aa/cancel
```

### Return Result Example

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
    "status": "CANCELLED"
  },
  "code": 0,
  "trace_id": "xxx"
}
```

The gateway also performs a best-effort terminal callback after the run is marked as `CANCELLED`.

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `data.open_plugin_run_id` | `string` | run identifier |
| `data.status` | `string` | updated status |
