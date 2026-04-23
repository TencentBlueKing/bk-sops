### Functional description

Get the list of plugins exposed by the plugin gateway.

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
    "total": 1,
    "apis": [
      {
        "id": "bk_plugin_demo",
        "name": "Demo Plugin",
        "plugin_source": "third_party",
        "plugin_code": "bk_plugin_demo",
        "wrapper_version": "2.0.0",
        "default_version": "1.1.0",
        "versions": ["1.0.0", "1.1.0"],
        "category": "third_party",
        "meta_url_template": "https://bk-sops.example/apigw/plugin-gateway/plugins/bk_plugin_demo/?version={version}"
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
| `data.apis[].category` | `string` | plugin category, currently aligned with `plugin_source` |
| `data.apis[].versions` | `list` | available versions |
| `data.apis[].meta_url_template` | `string` | URL template for detail query |
