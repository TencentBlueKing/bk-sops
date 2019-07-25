### Functional description

callback specific node

### Request Parameters

#### General Parameters
|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

| Field          |  Type       | Required   |  Description             |
| ------------ | ------------ | ------ | ---------------- |
|   bk_biz_id    |   string     |   YES   |  the business ID |
|   task_id     |   string   |   YES   |  the task ID     |
|   node_id        | string     | YES         | node id                        |
|   callback_data        | dict     | NO         | callback data          |           |

### Request Parameters Example

```
{
    "bk_app_code": "app_code",
    "bk_app_secret": "app_secret",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd",
    "callback_data": {
        "data": {}
    }
}
```

### Return Result Example

```
{
    "result": true,
    "message": "success"
}
```

### Return Result Description

| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  result   |    bool    |      true or false, indicate success or failure   |
|  message  |    string  |      error message returned when result is false  |
