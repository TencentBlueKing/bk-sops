### Request Address

/v2/sops/get_task_status/

### Request Method

GET

### Functional description

Query a task or task node execution status

### Request Parameters

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

| Field          |  Type       | Required   |  Description            |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   task_id     |   string   |   YES   |  the task ID or a task node ID  |
|   subprocess_id |   string   |   NO   |  the subprocess ID   |
|   with_ex_data     |   bool   |   NO   |  with exception data of failed nodes or not|
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project'|

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "subprocess_id": "xxx",
    "with_ex_data": true,
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": {
        "id": "ndf194ddb9e6365da1902dbd51610e9a",
        "state": "FAILED",
        "name": "<class 'pipeline.core.pipeline.Pipeline'>",
        "retry": 0,
        "loop": 1,
        "skip": false,
        "error_ignorable": false,
        "version": "",
        "state_refresh_at": "2020-08-17T12:13:53.320Z",
        "elapsed_time": 55035,
        "children": {
            "n00e3a0396403a19a4517d8e2eb0b015": {
                "id": "n00e3a0396403a19a4517d8e2eb0b015",
                "state": "FINISHED",
                "name": "<class 'pipeline.core.flow.event.EmptyStartEvent'>",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "22daf98a558737e39a5ae8d3876fac7d",
                "state_refresh_at": "2020-08-17T12:13:53.254Z",
                "elapsed_time": 0,
                "children": {},
                "start_time": "2020-08-17 20:13:53 +0800",
                "finish_time": "2020-08-17 20:13:53 +0800"
            },
            "nb346e202d17387082189f95dd3f80ca": {
                "id": "nb346e202d17387082189f95dd3f80ca",
                "state": "FAILED",
                "name": "Timing",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "e74df19258f535509cb104ad1ca94f00",
                "state_refresh_at": "2020-08-17T12:13:53.279Z",
                "elapsed_time": 0,
                "children": {},
                "start_time": "2020-08-17 20:13:53 +0800",
                "finish_time": "2020-08-17 20:13:53 +0800"
            }
        },
        "start_time": "2020-08-17 20:13:53 +0800",
        "finish_time": "",
        "ex_data": {
            "nb346e202d17387082189f95dd3f80ca": "Timing time needs to be later than current time"
        }
    },
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    dict    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |

#### data

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  state      |    string    |      status of the task or a task node, details are described below    |
|  id         |    string    |      the unique ID of task or a task node       |
|  skip       |    bool      |      skipped or not when the task node is failed    |
|  retry      |    int       |      retry or skip times of a task node   |
|  start_time |    string    |      start time   |
|  finish_time|    string    |      finish time    |
|  children   |    dict      |      task detail of children nodes, details are described below   |
|  name   |    string      |      node name   |
|  ex_data  |  dict  | key is the failed node ID，value is the corresponding exception data |

#### data.state

| value    | Description      |
|----------|-----------|
| CREATED   | cerated but not executed   |  
| RUNNING   | running   |
| FAILED    | failed    |
| SUSPENDED | suspended |
| REVOKED   | revoked   |
| FINISHED  | finished  |  

#### data.children KEY
the unique ID of a task node

#### data.children VALUE
the detail of a task node, the format is same with data
