### Functional description

Batch query task status

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|---------|------------------|
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   scope       |   string     |   NO   | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |
|   include_children_status     |   bool     |   NO   |  whether include children status in response  |

### Request Parameters Example

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
            "create_time": "2020-03-18 15:44:31 +0800",
            "start_time": "2020-03-18 15:44:35 +0800",
            "finish_time": "",
            "url": "url"
        }
    ],
    "code": 0
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    list    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |


#### data
| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  id      |    string    |      task ID    |
|  name      |    string    |    task name    |
|  status      |    dict    |      status detail    |
|  create_time      |    string    |     task create time   |
|  start_time      |    string    |     task start time   |
|  finish_time      |    string    |      task finish time    |
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

##### data[children]

KEY：
node id

VALUE：
same as data.status