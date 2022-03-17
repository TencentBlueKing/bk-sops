### 功能描述

批量查询任务执行状态

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   task_id_list     |   array     |   是   |  任务 ID 列表，限制最多查询50个任务  |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
|   include_children_status     |   bool     |   否   |  返回的结果中是否需要包含任务中节点的状态  |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id_list": [30000105, 30000101, 30000100],
    "scope": "cmdb_biz",
    "include_children_status": false
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": 30000105,
            "name": "task test tree",
            "status": {
                "id": "n580c9bf42a93bfc9a6cfe309bb3b418",
                "state": "FINISHED",
                "name": "<class 'pipeline.core.pipeline.Pipeline'>",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "",
                "elapsed_time": 41,
                "start_time": "2020-03-18 17:22:05 +0800",
                "finish_time": "2020-03-18 17:22:46 +0800"
            },
            "flow_type": "common",
            "current_flow": "finished",
            "is_deleted": false,
            "create_time": "2020-03-18 17:21:24 +0800",
            "start_time": "2020-03-18 17:22:04 +0800",
            "finish_time": "2020-03-18 17:22:46 +0800",
            "url": "url"
        },
        {
            "id": 30000101,
            "name": "task test1111",
            "status": {
                "id": "nd68a418afd23d64a6f0e69338130787",
                "state": "FAILED",
                "name": "<class 'pipeline.core.pipeline.Pipeline'>",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "",
                "elapsed_time": 1375959,
                "start_time": "2020-03-18 17:15:34 +0800",
                "finish_time": ""
            },
            "flow_type": "common",
            "current_flow": "finished",
            "is_deleted": false,
            "create_time": "2020-03-18 17:14:44 +0800",
            "start_time": "2020-03-18 17:15:33 +0800",
            "finish_time": "",
            "url": "url"
        },
        {
            "id": 30000100,
            "name": "task_name",
            "status": {
                "id": "nd14eca299643b958761e7a3e5e4b7de",
                "state": "RUNNING",
                "name": "<class 'pipeline.core.pipeline.Pipeline'>",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "",
                "elapsed_time": 1381417,
                "start_time": "2020-03-18 15:44:36 +0800",
                "finish_time": ""
            },
            "flow_type": "common",
            "current_flow": "finished",
            "is_deleted": false,
            "create_time": "2020-03-18 15:44:31 +0800",
            "start_time": "2020-03-18 15:44:35 +0800",
            "finish_time": "",
            "url": "url"
        }
    ],
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 查询成功与否     |
|  data        |    dict      |      result=true 时返回数据，详细信息见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data 说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  id      |    string    |      任务 ID    |
|  name      |    string    |    任务名    |
|  status      |    dict    |    状态详情，详细信息见下面说明    |
|  create_time      |    string    |     任务创建时间   |
|  start_time      |    string    |     任务开始时间   |
|  finish_time      |    string    |      任务完成时间    |
| flow_type | stirng | 任务流程类型（common:普通流程任务, common_func: 职能化任务） |
| current_flow | string | 任务当前流程，详细信息见下面说明 |
| is_deleted | bool | 任务当前是否删除 |
|  children      |    dict   |      任务节点执行详情，详细信息见下面说明   |

#### data.status 说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  id      |    string    |      节点 ID    |
|  state        | string     | 执行状态，CREATED：未执行，RUNNING：执行中，FAILED：失败，NODE_SUSPENDED：暂停，FINISHED：成功 |
|  name      |    string    |     节点名   |
|  retry      |    int    |     重试次数   |
|  loop      |    int    |     循环次数   |
|  skip      |    bool    |     是否跳过   |
|  error_ignorable      |    bool    |     是否忽略错误   |
|  version      |    string    |     节点版本   |
|  elapsed_time      |    int    |     节点耗时(秒)   |
|  start_time      |    string    |     节点开始时间   |
|  finish_time      |    string    |      节点完成时间    |

#### data.children KEY

任务节点 执行态ID

#### data.children VALUE

同 status 格式

#### data.current_flow（flow_type为common）

| 名称         | 含义     |
| ------------ | -------- |
| select_steps | 步骤选择 |
| fill_params  | 参数填写 |
| execute_task | 任务执行 |
| finished     | 完成     |

#### data.current_flow（flow_type为common_func）

| 名称         | 含义       |
| ------------ | ---------- |
| select_steps | 步骤选择   |
| func_submit  | 提交需求   |
| func_claim   | 职能化认领 |
| execute_task | 任务执行   |
| finished     | 完成       |

