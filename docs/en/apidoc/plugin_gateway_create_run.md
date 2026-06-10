### Functional description

Create an execution record in the plugin gateway.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `source_key` | `string` | YES | source key |
| `plugin_id` | `string` | YES | plugin id |
| `plugin_version` | `string` | YES | plugin version |
| `client_request_id` | `string` | YES | idempotency key inside the caller app |
| `callback_url` | `string` | YES | callback URL |
| `callback_token` | `string` | YES | token written to `X-Callback-Token` |
| `inputs` | `object` | NO | plugin inputs |
| `operator` | `string` | NO | optional operator passed to downstream plugin context; when omitted, the gateway reuses the APIGW username if present |
| `project_id` | `int` | NO | project id |

### Request Example

```json
{
  "source_key": "bkflow",
  "plugin_id": "bk_plugin_demo",
  "plugin_version": "1.1.0",
  "client_request_id": "task_1_node_1_attempt_1",
  "callback_url": "https://bkflow.example.com/api/plugin-gateway/callback",
  "callback_token": "token-001",
  "inputs": {
    "target_ip": "127.0.0.1"
  },
  "operator": "bkflow-user"
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

### Error Field Description

Failure payloads may include `error_type` for common integration errors:

- `plugin_not_enabled`
- `plugin_version_unavailable`
- `plugin_removed`
- `source_unreachable`
