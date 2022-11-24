### 功能描述

导入项目流程

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   template_data    |   string     |   是   |  项目流程数据，即从标准运维 - 项目流程 - 导出功能下载的文件的内容 |
|   project_id    |   string     |   是   |  项目 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "template_data": "xxx",
    "project_id": "3",
    "bk_username": "cmdb_biz",
    "scope":"cmdb_biz"
}
```

### 返回结果示例

```
{
    "message": "Successfully imported 2 flows",
    "data": {
        "flows": {
              11: "flowA",
              12: "flowB",
              ...
        },
        "count": 2
    },
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  message      | string     | result=false 时错误信息        |
|  data         | dict        | 返回数据                    |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  count      |    int    |      导入的流程数    |
|  flows      |    dict |      导入的流程ID与名字的映射 |