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
  "data": [
    {"id": "all", "name": "全部"},
    {"id": "DEVOPS", "name": "研发工具"},
    {"id": "JOB", "name": "JOB"}
  ],
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `result` | `bool` | 是否成功 |
| `data` | `list` | 插件分类列表；`all` 表示不过滤，其他 ID 与插件列表中的 `category` 一致 |
| `message` | `string` | 失败时错误信息 |
| `trace_id` | `string` | open telemetry trace_id |
