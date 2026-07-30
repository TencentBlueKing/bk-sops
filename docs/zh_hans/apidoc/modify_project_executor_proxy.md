### 功能描述

修改项目执行代理人配置

### 请求参数

#### 接口参数

| 字段                       |  类型       | 必选   |  描述             |
|----------------------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   executor_proxy           |   string   |   是   |  执行代理人；仅允许设置为调用方本人用户名，允许传空串表示清空该配置 |
|   executor_proxy_exempts   |   string   |   是   |  执行代理人豁免列表，多个用英文逗号分隔；允许传空串表示清空豁免列表 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "admin",
    "executor_proxy": "admin",
    "executor_proxy_exempts": "user1,user2"
}
```

### 返回结果示例

```
{
    "code": 0,
    "data": {
        "executor_proxy": "admin",
        "executor_proxy_exempts": "user1,user2",
        "project_id": 123
    },
    "result": true,
    "message": "",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称       |  类型     |           说明                    |
| ------------ | --------- | --------------------------------- |
|  code        |  integer  |  错误码                           |
|  result      |  bool     |  true/false 操作是否成功          |
|  data        |  object   |  result=true 时成功数据           |
|  message     |  string   |  result=false 时错误信息          |
|  trace_id    |  string   |  open telemetry trace_id          |

#### data 字段说明

|   名称                    |  类型     |           说明                             |
| ------------------------- | --------- | ------------------------------------------ |
|  executor_proxy           |  string   |  执行代理人（仅允许为调用方本人用户名）    |
|  executor_proxy_exempts   |  string   |  执行代理人豁免列表，多个用英文逗号分隔    |
|  project_id               |  integer  |  项目ID                                    |
