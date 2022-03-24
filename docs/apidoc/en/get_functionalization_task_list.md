### Functional description

Get functionalization task list, support filtering with functionalization task status, ID and original task ID.

#### Request Parameters

| Field         | Type   | Required | Description                                                  |
| ------------- | ------ | -------- | ------------------------------------------------------------ |
| bk_app_code   | string | YES      | APP ID                                                       |
| bk_app_secret | string | YES      | APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
| bk_token      | string | NO       | Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie |
| bk_username   | string | NO       | Current user username, APP in the white list, can use this field to specify the current user |

#### Interface Parameters

| Field      | Type   | Required | Description                                                  |
| ---------- | ------ | -------- | ------------------------------------------------------------ |
| status     | string | NO       | functionalization task status. (submitted, claimed, rejected, executed, finished) |
| id_in      | string | NO       | functionalization task id list for filtering, separated by `,` |
| task_id_in | string | NO       | original task id list for filtering, separated by `,`（corresponding to "Task ID" in the web page） |
| limit      | int    | NO       | pagination, the number of tasks in the task list in each result. default is 100 |
| offset     | int    | NO       | pagination, the start index of task in the task list in each result. default is 0 |

### Request Parameters Example

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

### Return Result Example

```
{
    "result": true,
    "data": [
        {
            "id": 6,
            "name": "timer_20201110041712",
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
                "name": "timer_20201110041712",
                "category": "alert",
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
            "name": "timer_20201110034326",
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
                "name": "timer_20201110034326",
                "category": "alert",
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

### Return Result Description

| Field   | Type   | Description                                                  |
| ------- | ------ | ------------------------------------------------------------ |
| result  | bool   | true or false, indicate success or failure                   |
| data    | list   | data returned when result is true, details are described below |
| message | string | error message returned when result is false                  |
| count   | int    | amount of data list                                          |
|  request_id     |    string  | esb request id             |
|  trace_id     |    string  | open telemetry trace_id        |

##### data[item]

| Field          | Type   | Description                                                         |
| ------------- | ------ | ------------------------------------------------------------ |
| id            | int    | functionalization task ID                                    |
| name          | string | functionalization task name                                  |
| creator       | string | functionalization task creator                               |
| create_time   | string | functionalization task created time                          |
| claimant      | string | functionalization task claimant                              |
| claim_time    | string | functionalization task claimed time                          |
| rejecter      | string | functionalization task rejecter                              |
| reject_time   | string | functionalization task rejected time                         |
| predecessor   | string | functionalization task  predecessor                          |
| transfer_time | string | functionalization task transfered time                       |
| status        | string | functionalization task status. (submitted, claimed, rejected, executed, finished) |
| task          | dict   | original task corresponding to functionalization task        |

##### data.task

| Field           | Type   | Description                                  |
| --------------- | ------ | -------------------------------------------- |
| id              | int    | task ID                                      |
| name            | string | task name                                    |
| category        | string | task category                                |
| create_method   | string | task create method                           |
| creator         | string | task creator                                 |
| executor        | string | task executor                                |
| start_time      | string | task start time                              |
| finish_time     | string | task finish time                             |
| is_started      | bool   | task is already started                      |
| is_finished     | bool   | task is already finished                     |
| template_source | string | task template source, e.g. project or common |
| template_id     | string | task template ID                             |

