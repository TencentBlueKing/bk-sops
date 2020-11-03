### Functional description

Get tasks list for a business, support task name keyword searching

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|----------|------------------|
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   scope       |   string     |   NO   | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |
|   keyword     |   string     |   NO   |  keyword to filter the task list based on the task name. default is no filter |
|   is_started  |   bool       |   NO   |  task status to filter the task list based on the start status. default is no filter |
|   is_finished |   bool       |   NO   |  task status to filter the task list based on the finish status. default is no filter |
|   limit       |   int        |   NO   |  pagination, the number of tasks in the task list in each result. default is 15 |
|   offset      |   int        |   NO   |  pagination, the start index of task in the task list in each result. default is 0 |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "keyword": "定时",
    "is_started": true,
    "limit": 5,
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": 1595,
            "name": "定时任务1_clone_20200907043931",
            "category": "其它",
            "create_method": "app",
            "creator": "admin",
            "executor": "admin",
            "start_time": "2020-09-15T06:24:00.840Z",
            "finish_time": "2020-09-15T07:12:51.128Z",
            "is_started": true,
            "is_finished": true,
            "template_source": "project",
            "template_id": "2",
            "project_id": 1,
            "project_name": "蓝鲸",
            "bk_biz_id": 2,
            "bk_biz_name": "蓝鲸"
        },
        {
            "id": 166,
            "name": "定时测试1_20200623072621",
            "category": "运维工具",
            "create_method": "app",
            "creator": "admin",
            "executor": "admin",
            "start_time": "2020-06-23T07:26:29.522Z",
            "finish_time": null,
            "is_started": true,
            "is_finished": false,
            "template_source": "project",
            "template_id": "243",
            "project_id": 1,
            "project_name": "蓝鲸",
            "bk_biz_id": 2,
            "bk_biz_name": "蓝鲸"
        },
        {
            "id": 159,
            "name": "新定时_20200610033932_20200610200000",
            "category": "其它",
            "create_method": "periodic",
            "creator": "sops",
            "executor": "sops",
            "start_time": "2020-06-10T12:00:00.474Z",
            "finish_time": null,
            "is_started": true,
            "is_finished": false,
            "template_source": "project",
            "template_id": "246",
            "project_id": 1,
            "project_name": "蓝鲸",
            "bk_biz_id": 2,
            "bk_biz_name": "蓝鲸"
        },
        {
            "id": 158,
            "name": "新定时_20200610033932_20200610195200",
            "category": "其它",
            "create_method": "periodic",
            "creator": "sops",
            "executor": "sops",
            "start_time": "2020-06-10T11:52:01.245Z",
            "finish_time": null,
            "is_started": true,
            "is_finished": false,
            "template_source": "project",
            "template_id": "246",
            "project_id": 1,
            "project_name": "蓝鲸",
            "bk_biz_id": 2,
            "bk_biz_name": "蓝鲸"
        },
        {
            "id": 157,
            "name": "新定时_20200610033932_20200610193900",
            "category": "其它",
            "create_method": "periodic",
            "creator": "sops",
            "executor": "sops",
            "start_time": "2020-06-10T11:39:00.194Z",
            "finish_time": null,
            "is_started": true,
            "is_finished": false,
            "template_source": "project",
            "template_id": "246",
            "project_id": 1,
            "project_name": "蓝鲸",
            "bk_biz_id": 2,
            "bk_biz_name": "蓝鲸"
        }
    ]
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    list    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |

##### data[item]

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  id          |    int     | task ID |
|  name        |    string  | task name |
|  category    |    string  | task category |
|  create_method |  string  | task create method |
|  creator     |  string    | task creator |
|  executor    |  string    | task executor |
|  start_time  |  string    | task start time |
|  finish_time |  string    | task finish time |
|  is_started  |  bool      | task is already started |
|  is_finished |  bool      | task is already finished |
|  template_source |  string      | task template source, e.g. project or common |
|  template_id     |  string      | task template ID |
|  project_id      |  int         | project ID |
|  project_name    |  string      | project name |
|  bk_biz_id       |  int         | business ID  |
|  bk_biz_name     |  string      | business name |






