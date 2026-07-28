### 功能描述

修改流程模板的执行代理人（executor_proxy）

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   template_id    |   string     |   是   |  模板ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   executor_proxy    |   string     |   是   | 执行代理人用户名。仅可设置为当前登录用户本人；传空字符串代表清空执行代理人 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "template_id": "1",
    "executor_proxy": "11111",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "template_id": 1,
        "executor_proxy": "11111"
    },
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict    |      result=true 时成功数据，详细信息请见下面说明     |
|  code        |    int     |      错误码     |
|  message     |    string  |      result=false 时错误信息     |
|  trace_id    |    string  |      open telemetry trace_id     |

#### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  template_id      |    int    |      模板ID    |
|  executor_proxy   |    string |      更新后的执行代理人用户名    |
