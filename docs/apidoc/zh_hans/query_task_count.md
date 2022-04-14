### 功能描述

查询任务实例分类统计总数

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   group_by     |   string     |   是   |  分类统计维度，status：按任务状态（未执行、执行中、已完成）统计，category：按照任务类型统计，flow_type：按照流程类型统计，create_method：按照创建方式 |
|   conditions     |   dict     |   否   |  任务过滤条件 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

#### conditions

| 字段      | 类型      | 必选 | 描述      |
| ------------ | ---------- |--------| ------------------------------ |
|  template_id      |    string    |   否   |      创建任务的模板ID    |
|  name      |    string    |   否   |      任务名称   |
|  creator      |    string    |   否   |      创建人    |
|  create_time__gte      |    string    |   否   |      任务创建时间起始时间   |
|  create_time__lte      |    string    |   否   |      任务创建时间截止时间   |
|  executor      |    string    |   否   |      执行人    |
|  start_time__gte      |    string   |   否   |      任务执行时间起始时间  |
|  start_time__lte      |    string   |   否   |      任务执行时间截止时间  |
|  is_started      |    bool   |   否   |      任务是否启动  |
|  is_finished      |    bool   |   否   |      任务是否完成  |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "conditions": {
        "template_id": "1",
        "name": "template"
        "create_time__gte": "2018-07-12 10:00:00",
        "create_time__lte": "2018-07-13 15:00:00",
        "start_time__gte": "2018-07-13 11:00:00",
        "start_time__lte": "2018-07-13 12:00:00",
        "is_started": true,
        "creator": admin,
        "executor": admin,
        "is_started": true,
        "is_finished": true,
    },
    "group_by": "flow_type",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "data": {
        "total": 180,
        "groups": [
            {
                "code": "common",
                "name": "默认任务流程",
                "value": 166
            },
            {
                "code": "common_func",
                "name": "职能化任务流程",
                "value": 14
            }
        ]
    },
    "result": true,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      | bool    |      true/false 操作是否成功     |
|  data        | dict  |      result=true 时返回分类统计信息，详细信息见下面说明    |
|  message     | string  |      result=false 时错误信息     |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  total      |    int    |      按照过滤条件获取的任务总数    |
|  groups     |    list   |      按照过滤条件分类分类统计详情   |

#### data.groups[]
| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  code      |    string    |      分类统计类型编码    |
|  name      |    string    |      分类统计类型名称    |
|  value     |    string    |      当前分类任务数量    |
