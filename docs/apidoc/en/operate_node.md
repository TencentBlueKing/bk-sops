### Functional description

Operate node

### Request Parameters

{{ common_args_desc }}

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
| ------------ | ------------ | ------ | ---------------- |
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   scope       |   string     |   NO   | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |
|   task_id       |   int     |   YES   |  task ID |
| node_id        | string     | YES         | node ID                        |
| action        | string     | YES         | operate type，can be: callback(node callback), skip_exg(skip fail exclusive gateway), retry(retry fail node), skip(skip fail node), pause_subproc(pause running subprocess), resume_subproc(resume paused subprocess) |
| data | object   | NO         | callback data when action is callback    |
| inputs | object   | NO         | inputs data when action is retry     |
| flow_id | string   | NO         | execution flow id when action is skip_exg     |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "task_id": "12",
    "node_id": "node_id",
    "action": "skip"
}
```

### Return Result Example

```
{
    "result": true,
    "data": "success",
    "code": 0
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    string    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |