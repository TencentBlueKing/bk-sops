### Functional description

Get plugin categories exposed by the open plugin gateway.

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
  "data": {
    "categories": [
      {"id": "builtin", "name": "Built-in Plugins"},
      {"id": "third_party", "name": "Third-Party Plugins"}
    ]
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `result` | `bool` | whether the request succeeds |
| `data.categories` | `list` | plugin category list |
| `message` | `string` | error message when failed |
| `trace_id` | `string` | open telemetry trace_id |
