### 功能描述

获取某个业务下可用插件的基础信息列表（仅返回插件编码和名称），免用户认证

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   scope        |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "code": "sleep_timer",
            "name": "定时"
        },
        {
            "code": "job_fast_execute_script",
            "name": "快速执行脚本"
        },
        {
            "code": "pause_node",
            "name": "暂停"
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    array   |      result=true 时插件基础信息列表，详细信息请见下面说明     |
|  message     |    string  |      result=false 时错误信息     |
|  trace_id    |    string  |      open telemetry trace_id     |

#### data[]

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  code        |    string  |      插件编码     |
|  name        |    string  |      插件名称     |
