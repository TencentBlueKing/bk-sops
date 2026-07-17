### 功能描述

查询插件网关可消费的插件列表，返回内置插件和第三方插件。来源配置中的 `do_not_open_list` 会在列表阶段统一过滤。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `category` | `string` | 否 | 插件分类；`all` 或不传表示不过滤 |
| `key` | `string` | 否 | 按插件 ID、名称或原始 code 模糊搜索 |

### 请求参数示例

```text
GET /apigw/plugin-gateway/plugins/
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "total": 2,
    "apis": [
      {
        "id": "builtin__job_execute_task",
        "name": "作业执行",
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

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.total` | `int` | 插件总数 |
| `data.apis` | `list` | 插件列表 |
| `data.apis[].id` | `string` | 插件 ID；内置插件格式为 `builtin__<component_code>`，第三方插件兼容裸 `code` |
| `data.apis[].plugin_source` | `string` | 插件来源，取值为 `builtin` 或 `third_party` |
| `data.apis[].plugin_code` | `string` | 插件原始 code |
| `data.apis[].group` | `string` | 插件分组 |
| `data.apis[].category` | `string` | 插件分类 |
| `data.apis[].wrapper_version` | `string` | uniform_api 运行壳版本，当前固定为 `v4.0.0` |
| `data.apis[].default_version` | `string` | 默认版本 |
| `data.apis[].latest_version` | `string` | 最新版本 |
| `data.apis[].versions` | `list` | 可选业务版本列表，版本字符串按提供方原样返回 |
| `data.apis[].meta_url_template` | `string` | 查询详情的 URL 模板 |
