### 功能描述

查询插件网关可消费的插件列表，返回内置插件和第三方插件。来源配置中的 `do_not_open_list` 会在列表阶段统一过滤。

#### 接口参数

无

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
        "group": "作业平台(JOB)",
        "wrapper_version": "",
        "default_version": "legacy",
        "latest_version": "legacy",
        "versions": ["legacy"],
        "category": "作业平台(JOB)",
        "description": "",
        "meta_url_template": "https://bk-sops.example/apigw/plugin-gateway/plugins/builtin__job_execute_task/?version={version}"
      },
      {
        "id": "bk_plugin_demo",
        "name": "Demo Plugin",
        "plugin_source": "third_party",
        "plugin_code": "bk_plugin_demo",
        "group": "third_party",
        "wrapper_version": "2.0.0",
        "default_version": "1.1.0",
        "latest_version": "1.1.0",
        "versions": ["1.0.0", "1.1.0"],
        "category": "third_party",
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
| `data.apis[].default_version` | `string` | 默认版本 |
| `data.apis[].latest_version` | `string` | 最新版本 |
| `data.apis[].versions` | `list` | 可选版本列表 |
| `data.apis[].meta_url_template` | `string` | 查询详情的 URL 模板 |
