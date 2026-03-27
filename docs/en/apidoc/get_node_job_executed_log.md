### Functional description

Get the JOB platform execution log of a task node

#### Interface Parameters

| Field          | Type       | Required | Description             |
|----------------|------------|----------|-------------------------|
| bk_biz_id      | string     | YES      | the business ID |
| task_id        | string     | YES      | the task ID |
| node_id        | string     | YES      | the node ID |
| target_ip      | string     | NO       | target IP, used to filter logs of a specific host |
| scope          | string     | NO       | bk_biz_id scope. default is cmdb_biz, and bk_biz_id means bindded CMDB business ID of a project; when set to project, bk_biz_id means the project ID |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd",
    "target_ip": "127.0.0.1",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "message": "success",
    "logs": "[127.0.0.1] GSE AGENT is normal\n[127.0.0.1] Start executing script...\n[127.0.0.1] Script execution completed, return code: 0"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure     |
|  logs     |    string  |      JOB platform execution log content     |
|  message  |    string  |      error message returned when result is false     |
