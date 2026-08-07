### Functional description

Get the recent execution records of a node

#### Interface Parameters

| Field            | Type   | Required | Description                                                                                                           |
|------------------|--------|----------|-----------------------------------------------------------------------------------------------------------------------|
| bk_biz_id        | string | YES      | the unique ID of project, project ID or CMDB business ID                                                              |
| template_id      | string | YES      | the template ID                                                                                                           |
| template_node_id | string | YES      | the template node ID of the node to query                                                                             |
| scope            | string | NO       | bk_biz_id scope. default is cmdb_biz, and bk_biz_id means bindded CMDB business ID of a project; when set to project, bk_biz_id means the project ID |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "template_id": "10",
    "template_node_id": "node0df0431f8f553925af01a94854bd",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": {
        "execution_time": [
            {
                "archived_time": "2019-01-17 22:02:46 +0800",
                "elapsed_time": 9
            },
            {
                "archived_time": "2019-01-16 15:30:12 +0800",
                "elapsed_time": 12
            }
        ],
        "total": 2
    },
    "message": "",
    "code": 0
}
```

### Return Result Description

| Field    | Type   | Description                                      |
|----------|--------|--------------------------------------------------|
| result   | bool   | true or false, indicate success or failure       |
| data     | dict   | data returned when result is true, details are described below |
| message  | string | error message returned when result is false      |
| code     | int    | error code, 0 indicates success                  |

#### data

| Field          | Type | Description                               |
|----------------|------|-------------------------------------------|
| execution_time | list | list of recent execution records, details are described below |
| total          | int  | total number of node executions           |

#### data.execution_time[]

| Field         | Type   | Description                |
|---------------|--------|----------------------------|
| archived_time | string | archived time              |
| elapsed_time  | int    | elapsed time in seconds    |
