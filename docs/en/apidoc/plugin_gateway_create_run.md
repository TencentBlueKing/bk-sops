### Functional description

Create an execution record in the plugin gateway. A new run starts as `CREATED` and is dispatched by the `open_plugin_dispatch` queue.

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
| `context` | `object` | NO | business context. Recommended keys: `scope_type`, `scope_value`, `operator`; optional pass-through keys: `space_id`, `task_id`, `node_id`, `task_name` |
| `operator` | `string` | NO | compatibility field; used when `context.operator` is absent, and falls back to APIGW username when omitted |
| `project_id` | `int` | NO | compatibility field; new integrations should pass `context` and let bk-sops resolve the project |

### Request Example

```json
{
  "source_key": "bkflow",
  "plugin_id": "builtin__job_execute_task",
  "plugin_version": "legacy",
  "client_request_id": "task_1_node_1_attempt_1",
  "callback_url": "https://bkflow.example.com/api/plugin-gateway/callback",
  "callback_token": "token-001",
  "inputs": {
    "target_ip": "127.0.0.1"
  },
  "context": {
    "scope_type": "biz",
    "scope_value": "2",
    "operator": "bkflow-user",
    "space_id": "bkflow-space-1",
    "task_id": "task_1",
    "node_id": "node_1",
    "task_name": "demo task"
  }
}
```

### Return Result Example

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
    "status": "CREATED"
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

### Context And Project Resolution

- When `context.scope_type` is `biz` or `cmdb_biz` and `context.scope_value` is a business id, bk-sops first resolves the project by `Project.bk_biz_id`.
- If no business project is found, bk-sops checks source config `scope_project_map["<scope_type>:<scope_value>"]`.
- If no mapping is found, bk-sops falls back to source config `default_project_id`.
- If no project can be resolved, the run fails with an explicit error.
- `context.operator` is written into the plugin runtime context for downstream systems such as JOB or CC to perform real-user permission checks and audit.

### Error Field Description

Failure payloads may include `error_type` for common integration errors:

- `plugin_not_enabled`
- `plugin_version_unavailable`
- `plugin_removed`
- `source_unreachable`
