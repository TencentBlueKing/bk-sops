### Request Address

/v2/sops/query_task_count/

### Request Method

POST

### Functional description

Query task instance classification statistics

### Request Parameters

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

| Field         |  Type      | Required   |  Description             |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   YES   |  the business ID |
|   group_by     |   string     |   YES   |  classified statistical dimension, status：Statistics by task status(Created、Executing、Finished), category：Statistics by task type, flow_type：Statistics by flow type, create_method：Statistics by creation method |
|   conditions     |   dict     |   NO   |  task filter |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project'|

#### conditions

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  template_id      |    string    |      the template id    |
|  name      |    string    |      the task name   |
|  creator      |    string    |      creator    |
|  create_time__gte      |    string    |      task creation time start time   |
|  create_time__lte      |    string    |      task creation time end time   |
|  executor      |    string    |      executor    |
|  start_time__gte      |    string   |      task execution time start time  |
|  start_time__lte      |    string   |      task execution time end time  |
|  is_started      |    bool   |      whether the task started  |
|  is_finished      |    bool   |      whether the task finished  |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "conditions": {
        "template_id": "1",
        "name": "template"
        "create_time__gte": "2018-07-12 10:00:00",
        "create_time__lte": "2018-07-13 15:00:00",
        "start_time__gte": "2018-07-13 11:00:00",
        "start_time__lte": "2018-07-13 12:00:00",
        "is_started": true,
        "creator": admin,
        "executor": admin,
        "is_started": true,
        "is_finished": true,
    },
    "group_by": "flow_type",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "data": {
        "total": 180,
        "groups": [
            {
                "code": "common",
                "name": "",
                "value": 166
            },
            {
                "code": "common_func",
                "name": "",
                "value": 14
            }
        ]
    },
    "result": true,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result      | bool    |      true/false indicate success or failure     |
|  data     |    dict    |      data returned when result is true, details are described below |
|  message  |    string  |      error message returned when result is false|
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |

#### data

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  total      |    int    |      total number of tasks obtained by filter criteria    |
|  groups     |    list   |      sort statistic details by filter criteria   |

#### data.groups[]
| Field      | Type      | Description      |
|-----------|----------|-----------|
|  code      |    string    |      classification statistic type coding    |
|  name      |    string    |      classification statistic type name    |
|  value     |    string    |      current number of classified tasks    |
