### Functional description

Get plugin categories exposed by the plugin gateway.

#### Interface Parameters

None

### Request Example

```text
GET /apigw/plugin-gateway/categories/
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
