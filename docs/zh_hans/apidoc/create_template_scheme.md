### 功能描述

创建流程模板的执行方案

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   template_id  |   int        |   是   |  模板 ID |
|   scope        |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
|   name         |   string     |   是   |  执行方案名称，长度不超过 64 个字符 |
|   data         |   string/list |   是   |  执行方案包含的节点 ID 列表，支持传入 JSON 字符串或字符串列表，例如 `["node19fe67fe8e59c75a63b3a639a605d8"]`；<br/>节点必须为该流程 pipeline_tree 中**真实存在且为可选（optional=true）**的节点，且不能为空，否则返回参数错误 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "1",
    "template_id": "96",
    "scope": "cmdb_biz",
    "name": "方案一",
    "data": "[\"node19fe67fe8e59c75a63b3a639a605d8\"]"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "id": 1,
        "unique_id": "96-方案一",
        "name": "方案一",
        "data": "[\"node19fe67fe8e59c75a63b3a639a605d8\"]"
    },
    "code": 0,
    "message": "success",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时成功数据，详细信息请见下面说明      |
|  message     |    string  |      result=false 时错误信息     |
|  code        |    int     |      返回码，0 表示成功     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  id      |    int    |      执行方案 ID     |
|  unique_id     |    string     |    执行方案唯一 ID，格式为 `{模板ID}-{方案名}`     |
|  name     |    string     |    执行方案名称     |
|  data     |    string     |    执行方案中包含的节点 ID 列表（JSON 字符串）     |
