### 请求地址

/v2/sops/get_functionalization_task_list/

### 请求方法

GET

### 功能描述

获取职能化任务列表，支持根据任务状态、原任务id和职能化任务id进行筛选。

#### 通用参数

|   字段           |  类型       | 必选     |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   是    |  应用ID |
|   bk_app_secret |   string    |   是    |  安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
|   bk_token      |   string    |   否    |  当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取  |
|   bk_username   |   string    |   否    |  当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户              |

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
| status |   string     |   否   | 职能化任务状态，对应关系：submitted:未认领, claimed:已认领, rejected:已驳回, executed:已执行, finished:已完成。 |
| id_in  |   string   |   否   | 职能化任务筛选id来源列表，以逗号`,`分隔 |
| task_id_in |   string   |   否   | 职能化任务筛选原任务id来源列表，以逗号`,`分隔（对应页面”任务ID“） |
|   limit       |   int        |   否   | 分页，返回任务列表任务数，默认为100 |
|   offset      |   int        |   否   |  分页，返回任务列表起始任务下标，默认为0 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "id_in": "412,411"
    "task_id_in": "414,413",
    "status": "submitted",
    "limit": 50,
    "offset": 0
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": 6,
            "name": "定时测试_20201110041712",
            "creator": "admin",
            "create_time": "2020-11-10T04:17:15.586Z",
            "claimant": "",
            "claim_time": null,
            "rejecter": "",
            "reject_time": null,
            "predecessor": "",
            "transfer_time": null,
            "status": "submitted",
            "task": {
                "id": 414,
                "name": "定时测试_20201110041712",
                "category": "监控告警",
                "create_method": "app",
                "creator": "admin",
                "executor": "",
                "start_time": null,
                "finish_time": null,
                "is_started": false,
                "is_finished": false,
                "template_source": "project",
                "template_id": "306"
            }
        },
        {
            "id": 5,
            "name": "定时测试_20201110034326",
            "creator": "admin",
            "create_time": "2020-11-10T03:43:29.104Z",
            "claimant": "",
            "claim_time": null,
            "rejecter": "",
            "reject_time": null,
            "predecessor": "",
            "transfer_time": null,
            "status": "submitted",
            "task": {
                "id": 413,
                "name": "定时测试_20201110034326",
                "category": "监控告警",
                "create_method": "app",
                "creator": "admin",
                "executor": "",
                "start_time": null,
                "finish_time": null,
                "is_started": false,
                "is_finished": false,
                "template_source": "project",
                "template_id": "306"
            }
        }
    ],
    "code": 0,
    "count": 2,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    list    |      result=true 时成功数据，详细信息请见下面说明     |
|  message     |    string  |      result=false 时错误信息     |
| count | int | data列表数量 |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

##### data[item]

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  id          |    int     | 职能化任务ID |
|  name        |    string  | 任务名称 |
| creator |    string  | 创建人 |
| create_time |  string  | 创建时间 |
| claimant |  string    | 认领人 |
| claim_time |  string    | 认领时间 |
|  rejecter  |  string    | 驳回人 |
| reject_time |  string    | 驳回时间 |
|  predecessor  |  string    | 转单人 |
| transfer_time |  string    | 转单时间 |
| status |  string      | 职能化任务状态，对应关系：submitted:未认领, claimed:已认领, rejected:已驳回, executed:已执行, finished:已完成。 |
|  task |  dict  | 职能化任务对应流程任务对象，详细信息见下面说明 |

##### data.task

| 名称            | 类型   | 说明           |
| --------------- | ------ | -------------- |
| id              | int    | 任务ID         |
| name            | string | 任务名称       |
| category        | string | 任务类型       |
| create_method   | string | 创建方式       |
| creator         | string | 创建人         |
| executor        | string | 执行人         |
| start_time      | string | 开始时间       |
| is_started      | bool   | 任务是否已开始 |
| finish_time     | string | 任务完成时间   |
| is_finished     | bool   | 任务是否已完成 |
| template_id     | string | 模版id         |
| template_source | string | 模版来源       |




