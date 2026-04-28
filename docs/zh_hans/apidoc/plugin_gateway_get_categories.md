### 功能描述

查询插件网关的插件分类。

#### 接口参数

无

### 请求参数示例

```text
GET /apigw/plugin-gateway/categories/
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "categories": [
      {"id": "builtin", "name": "标准运维内置插件"},
      {"id": "third_party", "name": "标准运维第三方插件"}
    ]
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `result` | `bool` | 是否成功 |
| `data` | `dict` | 成功时返回的数据 |
| `data.categories` | `list` | 插件分类列表 |
| `message` | `string` | 失败时错误信息 |
| `trace_id` | `string` | open telemetry trace_id |
