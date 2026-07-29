### 功能描述

获取某个业务下的任务列表，支持任务名关键词搜索

#### 接口参数

| 字段          | 类型 | 必选   |  描述             |
|-------------|--|---------|------------------|
| bk_biz_id   | string |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
| scope       | string |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
| keyword     | string |   否   |  根据任务名关键词过滤任务列表，默认不过滤 |
| is_started  | bool |   否   |  根据任务是否已开始过滤任务列表，默认不过滤 |
| is_finished | bool |   否   |  根据任务是否已结束过滤任务列表，默认不过滤 |
| executor    | string |   否   |  根据任务执行人过滤任务列表，默认不过滤 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "keyword": "定时",
    "is_started": true,
    "is_finished": "false",
    "scope":"cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": 5
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict    |      result=true 时成功数据，详细信息请见下面说明     |
|  message     |    string  |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

