### Functional description

Get the list of plugins exposed by the plugin gateway, including built-in and third-party plugins. Plugins in source-level `do_not_open_list` are filtered from this list.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `plugin_source` | `string` | NO | source filter, `builtin` or `third_party`; omit to merge both sources |
| `category` | `string` | NO | plugin category; `all` or omitted disables filtering |
| `key` | `string` | NO | fuzzy search by plugin id, name, or original code |

### Request Example

```text
GET /apigw/plugin-gateway/plugins/?plugin_source=builtin
```

### Return Result Example

```json
{
  "result": true,
  "data": {
    "total": 2,
    "apis": [
      {
        "id": "builtin__job_execute_task",
        "name": "JOB Execute",
        "plugin_source": "builtin",
        "plugin_code": "job_execute_task",
        "group": "JOB",
        "wrapper_version": "v4.0.0",
        "default_version": "legacy",
        "latest_version": "legacy",
        "versions": ["legacy"],
        "category": "JOB",
        "description": "",
        "meta_url_template": "https://bk-sops.example/apigw/plugin-gateway/plugins/builtin__job_execute_task/?version={version}"
      },
      {
        "id": "bk_plugin_demo",
        "name": "Demo Plugin",
        "plugin_source": "third_party",
        "plugin_code": "bk_plugin_demo",
        "group": "DEVOPS",
        "wrapper_version": "v4.0.0",
        "default_version": "1.1.0",
        "latest_version": "1.1.0",
        "versions": ["1.0.0", "1.1.0"],
        "category": "DEVOPS",
        "description": "Demo plugin",
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
| `data.apis[].id` | `string` | plugin id; built-in plugins use `builtin__<component_code>`, third-party plugins keep the bare code |
| `data.apis[].plugin_source` | `string` | plugin source, `builtin` or `third_party` |
| `data.apis[].plugin_code` | `string` | original plugin code |
| `data.apis[].group` | `string` | plugin group |
| `data.apis[].category` | `string` | plugin category |
| `data.apis[].wrapper_version` | `string` | uniform_api wrapper version, currently fixed at `v4.0.0` |
| `data.apis[].default_version` | `string` | default version |
| `data.apis[].latest_version` | `string` | latest version |
| `data.apis[].versions` | `list` | available business versions, preserved exactly as returned by the provider |
| `data.apis[].meta_url_template` | `string` | URL template for detail query |
