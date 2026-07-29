### Function Description

Query the list of scheduled tasks under a business

### Request Parameters

#### Interface Parameters

| Field              | Type    | Required | Description                                                                                                                                                                             |
|--------------------|---------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bk_biz_id          | string  | Yes      | Unique project ID, which can be the project ID or the CMDB business ID                                                                                                                  |
| scope              | string  | No       | Search scope for bk_biz_id. Default is cmdb_biz, which searches for projects bound to the CMDB business ID bk_biz_id; when set to project, it searches for projects with project ID bk_biz_id |
| id                 | integer | No       | Filter the list by scheduled task ID; no filter by default                                                                                                                              |
| task_name          | string  | No       | Filter the list by scheduled task name keyword, fuzzy search is supported; no filter by default                                                                                         |
| creator            | string  | No       | Filter the list by creator, fuzzy search is supported; no filter by default                                                                                                             |
| editor             | string  | No       | Filter the list by editor, fuzzy search is supported; no filter by default                                                                                                              |
| state              | string  | No       | Filter the list by scheduled task state; no filter by default                                                                                                                           |
| expected_timezone  | string  | No       | Expected timezone for time-related fields in the response, e.g. Asia/Shanghai                                                                                                           |
| limit              | integer | No       | Pagination, number of items returned in the list, default is 100                                                                                                                        |
| offset             | integer | No       | Pagination, starting index of the items returned in the list, default is 0                                                                                                              |

### Request Parameter Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "id": 1,
    "scope": "cmdb_biz"
}
```

### Response Result Example

```
{
    "result": true,
    "data": [
        {
            "id": 1,
            "task_parameters": {
                "constants": {},
                "template_schemes_id": []
            },
            "creator": "xxxx",
            "editor": "",
            "state": "not_started",
            "plan_start_time": "2026-04-11 00:00:00+0800",
            "create_time": "2026-04-10 17:01:20+0800",
            "edit_time": "2026-04-10 17:01:20+0800",
            "project_id": 1,
            "task_id": null,
            "task_name": "xxxx",
            "template_id": 1,
            "template_name": "xxxx",
            "template_source": "project",
            "clocked_task_id": 15,
            "auth_actions": [
                "clocked_task_view",
                "clocked_task_edit",
                "clocked_task_delete",
                "flow_view"
            ]
        }
    ],
    "count": 1,
    "code": 0,
    "trace_id": "xxxx"
}
```

### Response Result Parameter Description

| Field    | Type    | Description                                                        |
|----------|---------|--------------------------------------------------------------------|
| result   | bool    | true/false whether the query succeeded                             |
| data     | list    | Scheduled task list when result=true, item information see below   |
| count    | integer | Number of items in the data list                                   |
| code     | integer | Error code                                                         |
| message  | string  | Error message when result=false                                    |
| trace_id | string  | Open Telemetry trace_id                                            |

#### data

| Field           | Type    | Description                                  |
|-----------------|---------|----------------------------------------------|
| id              | integer | Task unique identifier                       |
| clocked_task_id | integer | Scheduled task Celery task ID                |
| auth_actions    | list    | Operation permissions the current user has for this task |
| creator         | string  | Creator                                      |
| create_time     | string  | Task creation time                           |
| editor          | string  | Editor                                       |
| edit_time       | string  | Task edit time                               |
| plan_start_time | string  | Planned start time                           |
| project_id      | integer | Project ID                                   |
| state           | string  | Scheduled task state                         |
| task_id         | integer | Taskflow task ID (may be null)               |
| task_name       | string  | Scheduled task name                          |
| task_parameters | object  | Task parameters, see details below           |
| template_id     | integer | Template ID                                  |
| template_name   | string  | Template name                                |
| template_source | string  | Template source                              |

#### data.task_parameters

| Field               | Type   | Description                                      |
|---------------------|--------|--------------------------------------------------|
| constants           | object | Scheduled task parameters                        |
| template_schemes_id | list   | List of execution schemes used by the scheduled task |

### MCP Request Description

When the request comes from the gateway MCP, the following fields will be filtered out in the response and not returned:

- `data.[].auth_actions` - Permission operation list for each clocked task item in the array