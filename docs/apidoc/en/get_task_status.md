### Functional description

Query a task or task node execution status

### Request Parameters

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

| Field          |  Type       | Required   |  Description            |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   task_id     |   string   |   YES   |  the task ID a task node ID  |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "task_id": "10"
}
```

### Return Result Example

```
{
	"result": true,
    "data": {
		"retry": 0,
		"name": "<class 'pipeline.core.pipeline.Pipeline'>",
		"finish_time": "",
		"skip": false,
		"start_time": "2018-04-26 16:08:34 +0800",
		"children": {
			"62d4784e20483f1585149ce90ed954c9": {
				"retry": 0,
				"name": "<class 'pipeline.core.flow.event.EmptyStartEvent'>",
				"finish_time": "2018-04-26 16:08:34 +0800",
				"skip": false,
				"start_time": "2018-04-26 16:08:34 +0800",
				"children": {},
				"state": "FINISHED",
				"version": "7447cc2801b630f497768493c02fb488",
				"id": "62d4784e20483f1585149ce90ed954c9",
				"loop": 1
			},
			"e8b128dff46637368b9b1bd921abc14e": {
				"retry": 0,
				"name": "<class 'pipeline.core.flow.activity.ServiceActivity'>",
				"finish_time": "2018-04-26 16:08:46 +0800",
				"skip": false,
				"start_time": "2018-04-26 16:08:34 +0800",
				"children": {},
				"state": "FAILED",
				"version": "914d35fe7d143c2186e6d3532870b37d",
				"id": "e8b128dff46637368b9b1bd921abc14e",
				"loop": 1
			}
		},
		"state": "FAILED",
		"version": "",
		"id": "5a1622f9f43e3429acb604e18dbd100a",
		"loop": 1
	}
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    dict    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |

#### data

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  state      |    string    |      status of the task or a task node, details are described below    |
|  id         |    string    |      the unique ID of task or a task node       |
|  skip       |    bool      |      skipped or not when the task node is failed    |
|  retry      |    int       |      retry or skip times of a task node   |
|  start_time |    string    |      start time   |
|  finish_time|    string    |      finish time    |
|  children   |    dict      |      task detail of children nodes, details are described below   |
|  name   |    string      |      node name   |

#### data.state

| value    | Description      |
|----------|-----------|
| CREATED   | cerated but not executed   |  
| RUNNING   | running   |
| FAILED    | failed    |
| SUSPENDED | suspended |
| REVOKED   | revoked   |
| FINISHED  | finished  |  

#### data.children.KEY
the unique ID of a task node

#### data.children.VALUE
the detail of a task node, the format is same with data
