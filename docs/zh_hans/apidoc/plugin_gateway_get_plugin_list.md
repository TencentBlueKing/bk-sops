### 功能描述

查询插件网关可消费的插件列表。

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
    "total": 1,
    "apis": [
      {
        "id": "bk_plugin_demo",
        "name": "Demo Plugin",
        "plugin_source": "third_party",
        "plugin_code": "bk_plugin_demo",
        "wrapper_version": "2.0.0",
        "default_version": "1.1.0",
        "latest_version": "1.1.0",
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

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.total` | `int` | 插件总数 |
| `data.apis` | `list` | 插件列表 |
| `data.apis[].id` | `string` | 插件 ID |
| `data.apis[].category` | `string` | 插件分类，当前与 `plugin_source` 保持一致 |
| `data.apis[].versions` | `list` | 可选版本列表 |
| `data.apis[].meta_url_template` | `string` | 查询详情的 URL 模板 |
