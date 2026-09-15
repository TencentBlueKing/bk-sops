### Functional description

Query task operation records

#### Interface Parameters

| Field          |  Type       | Required   |  Description            |
|---------------|------------|--------|------------------|
|   task_id     |   string   |   YES  |  the task ID |
|   bk_biz_id   |   string   |   YES  |  the unique ID of project, project ID or CMDB business ID |
|   node_id     |   string   |   NO   |  the task node ID. If not provided, return all operation records under the task |
|   scope       |   string   |   NO   |  bk_biz_id scope. default is cmdb_biz, and bk_biz_id means bindded CMDB business ID of a project; when set to project, bk_biz_id means the project ID |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node_id",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": [
        {
            "project_id": 2,
            "instance_id": 10,
            "operator": "admin",
            "operate_type": "retry",
            "operate_type_name": "重试",
            "operate_source": "app",
            "operate_source_name": "app 页面",
            "node_id": "n03f24c7017b3b6f95fbd3aa9ef6bf18",
            "operate_date": "2026-07-31T10:50:00+08:00",
            "extra_info": {}
        },
        {
            "project_id": 2,
            "instance_id": 10,
            "operator": "admin",
            "operate_type": "nodes_action",
            "operate_type_name": "节点操作",
            "operate_source": "api",
            "operate_source_name": "api 接口",
            "node_id": "na4e7a1439ba3037af5bcf8c22a5967f",
            "operate_date": "2026-07-31T10:55:00+08:00",
            "extra_info": {}
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### Return Result Description

| Name         | Type      | Description                   |
| ------------ | ---------- | ----------------------------- |
|  result      | bool       | true or false, indicate success or failure |
|  data        | array      | list of operation records returned when result is true |
|  message     | string     | error message returned when result is false |
|  trace_id    | string     | open telemetry trace_id       |

#### data

| Name                 | Type      | Description                       |
| -------------------- | ---------- | --------------------------------- |
|  project_id         | int        | Project ID                       |
|  instance_id        | int        | Task instance ID                  |
|  operator           | string     | Operator                          |
|  operate_type       | string     | Operation type                    |
|  operate_type_name  | string     | Operation type name in Chinese    |
|  operate_source     | string     | Operation source                  |
|  operate_source_name| string     | Operation source name in Chinese  |
|  node_id            | string     | Task node ID. Empty string means task-level operation |
|  operate_date       | string     | Operation time                    |
|  extra_info         | object     | Task node extended information     |

#### data.operate_type

| Value          | Description           |
|----------------|-----------------------|
| none           | none                  |
| create         | create                |
| task_clone     | clone(create)         |
| start          | start                 |
| pause          | pause                 |
| resume         | resume                |
| revoke         | revoke                |
| delete         | delete                |
| update         | update                |
| callback       | callback              |
| retry          | retry                 |
| skip           | skip                  |
| skip_exg       | skip failed gateway   |
| pause_subproc  | pause subprocess      |
| resume_subproc | resume subprocess     |
| nodes_action   | task node action      |
| forced_fail    | force fail            |

#### data.operate_source

| Value  | Description           |
|--------|-----------------------|
| app    | app page              |
| api    | api interface         |
| parent | parent task           |
