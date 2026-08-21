### 功能描述

按插件 ID 和版本查询插件详情。内置插件 ID 使用 `builtin__<component_code>`，第三方插件 ID 兼容裸 `code`。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `plugin_id` | `string` | 是 | 插件 ID |
| `version` | `string` | 否 | 插件版本；不传时使用默认版本 |
| `source_key` | `string` | 否 | 来源标识；不传时保持旧 detail 行为，不解析 `form_context` |
| `scope_type` | `string` | 否 | 项目解析使用的范围类型；仅在提供 `source_key` 时参与解析 |
| `scope_value` | `string` | 否 | 项目解析使用的范围值；仅在提供 `source_key` 时参与解析 |

操作人不作为接口参数传入。不传 `source_key` 时沿用旧 detail 行为；提供 `source_key` 时，标准运维只使用 APIGW 已认证且获该资源权限的调用应用代传、由 signed JWT 携带的非空 username。该路径不读取 query/body 中的 `operator`，不要求 `user.verified=true` 或浏览器 user token；APIGW 资源权限只应授予受信任调用应用。

### 请求参数示例

```text
GET /apigw/plugin-gateway/plugins/builtin__job_execute_task/?version=legacy&source_key=bkflow&scope_type=biz&scope_value=2
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "id": "builtin__job_execute_task",
    "name": "作业执行",
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
        "name": "业务 ID",
        "type": "int",
        "desc": "业务 ID",
        "description": "业务 ID",
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
        "name": "作业实例 ID",
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

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.id` | `string` | 插件 ID |
| `data.plugin_source` | `string` | 插件来源，取值为 `builtin` 或 `third_party` |
| `data.plugin_code` | `string` | 插件原始 code |
| `data.plugin_version` | `string` | 当前返回的插件版本 |
| `data.version` | `string` | uniform_api 运行壳版本，当前为 `v4.0.0` |
| `data.wrapper_version` | `string` | uniform_api 运行壳版本，当前为 `v4.0.0` |
| `data.url` | `string` | 创建执行记录的地址 |
| `data.methods` | `list` | 允许的调用方法 |
| `data.inputs` | `list` | 插件输入 schema 列表；类型使用 `string`、`int`、`bool`、`list`、`json`，作为兼容渲染路径 |
| `data.forms` | `object` | 原生表单协议；固定包含 `input` 和 `output`，每项为表单描述符或 `null` |
| `data.forms.input` | `object` / `null` | 输入表单描述符；没有原生输入表单时为 `null` |
| `data.forms.output` | `object` / `null` | 输出表单描述符；没有原生输出表单时为 `null` |
| `data.forms.*.type` | `string` | 表单类型：`component_js`、`renderform`，或消费端支持的可选 provider 扩展 `jsonschema` |
| `data.forms.*.key` | `string` | 表单注册 key；内置 input/output 表单均使用组件 code（`<component_code>`） |
| `data.forms.*.data` | `string` / `object` | 原始表单数据或非内嵌表单的绝对 URL；`jsonschema` 时为原始 JSON Schema |
| `data.forms.*.is_embedded` | `boolean` | `data` 是否内嵌在响应中 |
| `data.forms.*.base` | `string` / `null` | 表单依赖基地址；不存在时为 `null` |
| `data.form_schema` | `object` | 过渡期兼容字段，仍可能存在；新接入应读取 `forms` |
| `data.form_context` | `object` | 可选的 JSON 表单上下文；仅在请求提供 `source_key` 时返回 |
| `data.form_context.project` | `object` | 已解析的标准运维项目，固定包含 `id`、`bk_biz_id` 和 `from_cmdb` |
| `data.form_context.project.id` | `integer` | Project 主键，非空 |
| `data.form_context.project.bk_biz_id` | `integer` | Project 对应的 CMDB 业务 ID，非空 |
| `data.form_context.project.from_cmdb` | `boolean` | Project 是否来自 CMDB，非空 |
| `data.form_context.biz_cc_id` | `integer` | 与 `project.bk_biz_id` 一致的业务 ID |
| `data.form_context.site_url` | `string` | 标准运维站点根地址 |
| `data.form_context.component` | `string` | 组件 API 根地址 |
| `data.form_context.variable` | `string` | 变量 API 根地址 |
| `data.form_context.template` | `string` | 模板 API 根地址 |
| `data.form_context.instance` | `string` | 任务实例 API 根地址 |
| `data.form_context.bk_plugin_api_host` | `object` | 插件 code 到 data API 根地址的映射；第三方插件包含当前插件，内置插件为空对象 |
| `data.outputs` | `list` | 插件输出 schema 列表 |
| `data.polling.url` | `string` | 轮询状态地址 |
| `data.polling.task_tag_key` | `string` | 轮询时使用的任务标识字段 |
| `data.polling.running_tag` | `object` | 运行中状态匹配规则，当前值为 `RUNNING` |

`forms` 按以下四种语义消费：

1. `component_js`：内置插件的原生输入或输出表单；`is_embedded=true` 时 `data` 是内嵌表单 JavaScript，否则是可访问的绝对静态 URL。
2. `renderform`：第三方插件原始 `renderform`；不转换为标准运维声明式 schema。
3. `jsonschema`：消费端支持的可选 provider 扩展；provider 提供时保留原始 JSON Schema 对象，但不保证所有当前标准插件 provider 都会返回。
4. `null`：该方向没有原生表单，接入方使用兼容的 `inputs`/`outputs` 渲染路径。

`form_schema` 中的标准控件名包括 `input`、`textarea`、`password`、`codeEditor`、`select`、`radio`、`checkbox`、`switcher` 和 `table`。其中 `codeEditor` 的配置可包含 `language`、`height` 和 `showMiniMap`。该字段只用于过渡期兼容；新接入不应依赖它。
