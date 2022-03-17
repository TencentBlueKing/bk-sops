### Functional description

Query periodic task for business

### Request Parameters

#### Interface Parameters

| Field          |  Type       | Required   |  Description             |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   YES   |  business ID |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project'|

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx"
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "data": [
        {
            "cron": "*/1 15 * * * (m/h/d/dM/MY)",
            "total_run_count": 1,
            "name": "from api 3",
            "creator": "admin",
            "last_run_at": "2018-11-28 15:57:01 +0900",
            "enabled": false,
            "id": 11,
            "template_id": "2",
            "auth_actions": [
                "periodic_task_view",
                "periodic_task_delete",
                "periodic_task_edit"
            ]
        },
        {
            "cron": "1,2,3-19/2 2 3 4 5 (m/h/d/dM/MY)",
            "total_run_count": 0,
            "name": "from api 1",
            "creator": "admin",
            "last_run_at": "",
            "enabled": false,
            "id": 6,
            "template_id": "2",
            "auth_actions": [
                "periodic_task_view",
                "periodic_task_delete",
                "periodic_task_edit"
            ]
        },
        {
            "cron": "*/5 * * * * (m/h/d/dM/MY)",
            "total_run_count": 0,
            "name": "task",
            "creator": "admin",
            "last_run_at": "",
            "enabled": false,
            "id": 4,
            "template_id": "2",
            "auth_actions": [
                "periodic_task_view",
                "periodic_task_delete",
                "periodic_task_edit"
            ]
        }
    ],
    "result": true,
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
|  request_id     |    string  | esb request id             |
|  trace_id     |    string  | open telemetry trace_id        |

#### data

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  cron      |    string    |      crontab expression    |
|  total_run_count      |    int    |    how much times the task run   |
|  name      |    string    |    task name   |
|  creator      |    string    |    creator   |
|  last_run_at      |    string    |    date of last run   |
|  enabled      |    bool    |   is the task enabled   |
|  id      |    int    |    task id   |
|  template_id      |    string    |    template id for the task   |
|  auth_actions      |    array   |      actions with permissions for the current user   |
