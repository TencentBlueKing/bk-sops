### Functional description

Get the detail of an exposed plugin by plugin id and version. Built-in plugin ids use `builtin__<component_code>`, while third-party plugins keep the bare code.

#### Interface Parameters

| Field | Type | Required | Description |
|------|------|------|------|
| `plugin_id` | `string` | YES | plugin id |
| `version` | `string` | NO | plugin version; default version is used when omitted |
| `source_key` | `string` | NO | source identifier; when omitted, detail keeps the legacy behavior and does not resolve `form_context` |
| `scope_type` | `string` | NO | scope type used for project resolution; used only when `source_key` is provided |
| `scope_value` | `string` | NO | scope value used for project resolution; used only when `source_key` is provided |

`operator` is not an API parameter. Without `source_key`, detail keeps the legacy behavior. With `source_key`, bk-sops uses only the non-empty username carried by the signed JWT and delegated by an APIGW-authenticated caller app that has permission for this resource. This path does not read `operator` from the query/body and does not require `user.verified=true` or a browser user token. APIGW resource permission should be granted only to trusted caller apps.

### Request Example

```text
GET /apigw/plugin-gateway/plugins/builtin__job_execute_task/?version=legacy&source_key=bkflow&scope_type=biz&scope_value=2
```

### Return Result Example

```json
{
  "result": true,
  "data": {
    "id": "builtin__job_execute_task",
    "name": "JOB Execute",
    "plugin_source": "builtin",
    "plugin_code": "job_execute_task",
    "plugin_version": "legacy",
    "version": "v4.0.0",
    "wrapper_version": "v4.0.0",
    "description": "",
    "desc": "",
    "url": "https://bk-sops.example/apigw/plugin-gateway/runs/",
    "methods": ["POST"],
    "inputs": [
      {
        "key": "biz_id",
        "name": "Business ID",
        "type": "int",
        "desc": "Business ID",
        "description": "Business ID",
        "required": true
      }
    ],
    "forms": {
      "input": {
        "type": "component_js",
        "key": "job_execute_task",
        "data": "https://bk-sops.example/static/components/job_execute_task.js",
        "is_embedded": false,
        "base": null
      },
      "output": null
    },
    "form_context": {
      "project": {
        "id": 2001,
        "bk_biz_id": 2,
        "from_cmdb": true
      },
      "biz_cc_id": 2,
      "site_url": "https://bk-sops.example/",
      "component": "https://bk-sops.example/api/v3/component/",
      "variable": "https://bk-sops.example/api/v3/variable/",
      "template": "https://bk-sops.example/api/v3/template/",
      "instance": "https://bk-sops.example/api/v3/taskflow/",
      "bk_plugin_api_host": {}
    },
    "outputs": [
      {
        "key": "job_instance_id",
        "name": "JOB instance ID",
        "type": "int",
        "desc": "JOB instance id",
        "description": "JOB instance id"
      }
    ],
    "polling": {
      "url": "https://bk-sops.example/apigw/plugin-gateway/runs/status/",
      "task_tag_key": "open_plugin_run_id",
      "success_tag": {
        "key": "data.status",
        "value": "SUCCEEDED",
        "data_key": "data.outputs"
      },
      "fail_tag": {
        "key": "data.status",
        "value": "FAILED",
        "msg_key": "data.error_message"
      },
      "running_tag": {
        "key": "data.status",
        "value": "RUNNING"
      }
    }
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### Return Result Description

| Field | Type | Description |
|------|------|------|
| `data.id` | `string` | plugin id |
| `data.plugin_source` | `string` | plugin source, `builtin` or `third_party` |
| `data.plugin_code` | `string` | original plugin code |
| `data.plugin_version` | `string` | resolved plugin version |
| `data.version` | `string` | uniform_api wrapper version, currently `v4.0.0` |
| `data.wrapper_version` | `string` | uniform_api wrapper version, currently `v4.0.0` |
| `data.url` | `string` | execution registration URL |
| `data.methods` | `list` | allowed methods |
| `data.inputs` | `list` | input schema list using `string`, `int`, `bool`, `list`, or `json`; retained as the compatibility rendering path |
| `data.forms` | `object` | native form protocol; always contains `input` and `output`, each a form descriptor or `null` |
| `data.forms.input` | `object` / `null` | input form descriptor; `null` when no native input form exists |
| `data.forms.output` | `object` / `null` | output form descriptor; `null` when no native output form exists |
| `data.forms.*.type` | `string` | form type: `component_js`, `renderform`, or the optional provider extension `jsonschema` supported by the consumer |
| `data.forms.*.key` | `string` | form registration key; built-in input and output forms both use the component code (`<component_code>`) |
| `data.forms.*.data` | `string` / `object` | raw form data or an absolute URL for a non-embedded form; raw JSON Schema for `jsonschema` |
| `data.forms.*.is_embedded` | `boolean` | whether `data` is embedded in the response |
| `data.forms.*.base` | `string` / `null` | form dependency base URL; `null` when absent |
| `data.form_schema` | `object` | transition compatibility field that may still be present; new integrations should read `forms` |
| `data.form_context` | `object` | optional JSON-only form context, returned only when the request supplies `source_key` |
| `data.form_context.project` | `object` | resolved bk-sops Project with fixed `id`, `bk_biz_id`, and `from_cmdb` members |
| `data.form_context.project.id` | `integer` | non-null Project primary key |
| `data.form_context.project.bk_biz_id` | `integer` | non-null CMDB business ID held by the Project |
| `data.form_context.project.from_cmdb` | `boolean` | non-null flag indicating whether the Project comes from CMDB |
| `data.form_context.biz_cc_id` | `integer` | business ID equal to `project.bk_biz_id` |
| `data.form_context.site_url` | `string` | bk-sops site root URL |
| `data.form_context.component` | `string` | component API root URL |
| `data.form_context.variable` | `string` | variable API root URL |
| `data.form_context.template` | `string` | template API root URL |
| `data.form_context.instance` | `string` | task instance API root URL |
| `data.form_context.bk_plugin_api_host` | `object` | map from plugin code to data API root URL; contains the current third-party plugin and is empty for built-ins |
| `data.outputs` | `list` | output schema list |
| `data.polling.url` | `string` | polling URL |
| `data.polling.task_tag_key` | `string` | polling task identifier field |
| `data.polling.running_tag` | `object` | running-state matching rule; current value is `RUNNING` |

Consume `forms` with these four semantics:

1. `component_js`: a native built-in input or output form. When `is_embedded=true`, `data` is inline form JavaScript; otherwise it is an accessible absolute static URL.
2. `renderform`: the third-party plugin's raw `renderform`, without conversion to a bk-sops declarative schema.
3. `jsonschema`: an optional provider extension supported by the consumer. Raw JSON Schema is preserved when supplied, but not every current standard-plugin provider is expected to emit it.
4. `null`: no native form for that direction; use the compatible `inputs`/`outputs` rendering path.

Standard control names in `form_schema` include `input`, `textarea`, `password`, `codeEditor`, `select`, `radio`, `checkbox`, `switcher`, and `table`. `codeEditor` may specify `language`, `height`, and `showMiniMap`. This field is retained only during the transition; new integrations must not depend on it.
