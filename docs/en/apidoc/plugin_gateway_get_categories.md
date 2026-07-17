### Functional description

Get plugin categories exposed by the plugin gateway.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `plugin_source` | `string` | NO | source filter, `builtin` or `third_party`; omit to merge both sources |

### Request Example

```text
GET /apigw/plugin-gateway/categories/?plugin_source=builtin
```

### Return Result Example

```json
{
  "result": true,
  "data": [
    {"id": "all", "name": "全部"},
    {"id": "DEVOPS", "name": "Development Tools"},
    {"id": "JOB", "name": "JOB"}
  ],
  "code": 0,
  "trace_id": "xxx"
}
```

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `result` | `bool` | whether the request succeeds |
| `data` | `list` | plugin categories; `all` disables filtering and other IDs match `apis[].category` |
| `message` | `string` | error message when failed |
| `trace_id` | `string` | open telemetry trace_id |
