### Functional description

Batch query task status

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|---------|------------------|
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   task_id_list     |   array     |   YES   |  task id list, task number must smaller than 50  |
|   scope       |   string     |   NO   | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |
|   include_children_status     |   bool     |   NO   |  whether include children status in response  |

### Request Parameters Example

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

### Return Result Example

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

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    list    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |


#### data
| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  id      |    string    |      task ID    |
|  name      |    string    |    task name    |
|  status      |    dict    |      status detail    |
|  create_time      |    string    |     task create time   |
|  start_time      |    string    |     task start time   |
|  finish_time      |    string    |      task finish time    |
| flow_type | string | task type (common: normal template task, common_func: functionalization task) |
| current_flow | string | task current status |
| is_deleted | bool | task existence |
|  children      |    dict   |      children status   |


#### data.status 

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  id      |    string    |      node id    |
|  state      |    string    |     node status, CREATED,RUNNING,FAILED,NODE_SUSPENDED,FINISHED   |
|  name      |    string    |     node name   |
|  retry      |    int    |     retry times   |
|  loop      |    int    |     loop times   |
|  skip      |    bool    |     is skip   |
|  error_ignorable      |    bool    |     whether error ignorable   |
|  version      |    string    |     node version   |
|  elapsed_time      |    int    |     node elapse time   |
|  start_time      |    string    |     start time   |
|  finish_time      |    string    |      finish time    |

#### data.children KEY
the unique ID of a task node

#### data.children VALUE
same as data.status

#### data.current_flow（flow_type is common）

| Field         | Description                                           |
| ------------ | ---------------------------------------------- |
| select_steps | the task is in the stage of selecting steps    |
| fill_params  | the task is in the stage of filling parameters |
| execute_task | the task is in the stage of executing          |
| finished     | the task is finished                           |

#### data.current_flow（flow_type is common_func）

| Field         | Description                                                         |
| ------------ | ------------------------------------------------------------ |
| select_steps | the functionalization task is in the stage of selecting steps |
| func_submit  | the functionalization task is in the stage of submitting     |
| func_claim   | the functionalization task is in the stage of claiming       |
| execute_task | the functionalization task is in the stage of executing      |
| finished     | the functionalization task is finished                       |

