### Admin read request headers and behavior

Admin read calls are available only to a configured PO backend. The caller must send both `X-BkSops-Admin-Read: true` and `X-BkSops-Audit-Operator: <authenticated username>`.

This mode bypasses only view permission checks. It does not change `auth_actions` and grants no edit, create, operation, or download permissions. An invalid declaration returns `REQUEST_FORBIDDEN_INVALID`; requests without this declaration continue to use normal IAM authorization.

### Functional description

Get user project list

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx"
}
```

### Return Result Example

```
{
    "result": true,
    "data": [
        {
            "project_id": 13,
            "bk_biz_id": 2,
            "name": "蓝鲸"
        },
        {
            "project_id": 14,
            "bk_biz_id": 3,
            "name": "la"
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    list    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |
|  trace_id     |    string  | open telemetry trace_id       |


#### data
| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  project_id | int        | proejct ID       |
|  bk_biz_id | int        | bound cmdb business id       |
|  name  | string     | project name           |

### MCP Request Notice

When the request comes from gateway MCP, no fields will be filtered from the response.
