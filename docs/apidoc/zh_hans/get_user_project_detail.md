### 功能描述

获取项目的详情

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id       |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |

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
    "data": {
        "project_id": 13,
        "project_name": "蓝鲸",
        "bk_biz_id": 2,
        "from_cmdb": true,
        "bk_biz_name": "蓝鲸",
        "bk_biz_developer": "",
        "bk_biz_maintainer": "admin,gcloudadmin",
        "bk_biz_tester": "",
        "bk_biz_productor": ""
    },
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | dict       | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  project_id | int        | 项目 ID       |
|  project_name  | string     | 项目名           |
|  bk_biz_id | int        | 绑定的 CMDB 业务 ID       |
|  from_cmdb | bool        | 该项目是否是从 CMDB 业务同步的       |
|  bk_biz_name  | string     | 项目名           |
|  bk_biz_developer  | string     | 业务开发人员列表           |
|  bk_biz_maintainer  | string     | 业务运维人员列表           |
|  bk_biz_tester  | string     | 业务测试人员列表           |
|  bk_biz_productor  | string     | 业务产品人员列表           |
