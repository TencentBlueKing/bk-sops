### Functional description

Get the list of plugins exposed by the open plugin gateway.

#### Interface Parameters

None

### Request Example

```text
GET /apigw/plugin-gateway/plugins/
```

### Return Result Example

```json
{
  "result": true,
  "data": {
    "total": 2,
    "apis": [
      {
        "id": "plugin_job_execute",
        "name": "JOB Execute",
        "default_version": "1.2.0",
        "versions": ["1.2.0", "1.3.0"],
        "meta_url_template": "https://bk-sops.example/apigw/plugin-gateway/plugins/plugin_job_execute/?version={version}"
      }
    ]
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `data.total` | `int` | total number of plugins |
| `data.apis` | `list` | plugin list |
| `data.apis[].id` | `string` | plugin id |
| `data.apis[].versions` | `list` | available versions |
| `data.apis[].meta_url_template` | `string` | URL template for detail query |
