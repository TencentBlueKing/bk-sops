### Request Address

/v2/sops/create_and_start_task/

### Request Method

POST

### Functional description

Create a task with a flow template

### Request Parameters

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

| Field         |  Type      | Required   |  Description |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   YES   |  the business ID |
|   template_id  |   string     |   YES   |  the flow template ID |
|   template_source | string   | NO    | source of flow，default value is business. business: from business, common: from common flow |
|   name         |   string     |   YES   |  task name |
|   flow_type    |   string     |   NO    |  flow type，common: common flow，common_func：functional flow. Default is common |
|   constants    |   dict       |   NO    |  global variables，details are described below |
|   exclude_task_nodes_id | list |   NO   |  nodes id not be executed, which are set ignore in flow |
| description           | string | NO       | pipeline_instance's description                              |

#### constants KEY

constant KEY, the format is like ${key}

#### constants.VALUE

constant value, the type of value should be same with data from API[get_template_info]

### Request Parameters Example

```
{
    "app_code":"bk_sops",
    "bk_app_secret":"xxx",
    "bk_token":"xxx",
    "bk_username":"xxx",
    "template_id":"xxx",
    "template_source": "business",
    "bk_biz_id":"xxx",
    "name": "tasktest",
    "flow_type": "common"
    "constants": {
        "${content}": "echo 1",
        "${params}": "",
        "${script_timeout}": 20
    },
    "exclude_task_nodes_id":[1, 2, 3],
    "description":"description"
}
```

### Return Result Example

```
{
    "result": true,
    "code": 0,
    "data": {
        "pipeline_tree": {
            "activities": {
                "nfccedff6c7637a3a2a6093fd8b48818": {
                    "component": {
                        "code": "wechat_work_send_message",
                        "data": {
                            "wechat_work_chat_id": {
                                "hook": false,
                                "value": "test_chat_id"
                            },
                            "msgtype": {
                                "hook": false,
                                "value": "text"
                            },
                            "message_content": {
                                "hook": false,
                                "value": "test"
                            },
                            "wechat_work_mentioned_members": {
                                "hook": false,
                                "value": "testuser"
                            }
                        },
                        "version": "1.0"
                    },
                    "error_ignorable": false,
                    "id": "nfccedff6c7637a3a2a6093fd8b48818",
                    "incoming": [
                        "l7005877547e3769890512baba0d01b9"
                    ],
                    "loop": null,
                    "name": "发送消息",
                    "optional": true,
                    "outgoing": "l1e2cb3a00383c6ea0d3686c729492fd",
                    "stage_name": "",
                    "type": "ServiceActivity",
                    "retryable": true,
                    "skippable": true,
                    "labels": []
                }
            },
            "constants": {
                "${bk_timing}": {
                    "source_tag": "sleep_timer.bk_timing",
                    "source_info": {
                        "node76393dcfedcf73dbc726f1c4786d": [
                            "bk_timing"
                        ]
                    },
                    "name": "定时时间",
                    "index": 0,
                    "custom_type": "",
                    "value": "100",
                    "show_type": "show",
                    "source_type": "component_inputs",
                    "key": "${bk_timing}",
                    "validation": "",
                    "desc": ""
                }
            },
            "end_event": {
                "id": "ncc1ac32fd1d338980c7831fd20bf908",
                "incoming": [
                    "l1e2cb3a00383c6ea0d3686c729492fd"
                ],
                "name": "",
                "outgoing": "",
                "type": "EmptyEndEvent",
                "labels": []
            },
            "flows": {
                "l7005877547e3769890512baba0d01b9": {
                    "id": "l7005877547e3769890512baba0d01b9",
                    "is_default": false,
                    "source": "na24da677f3a3b22a8a7daf8e5f7ac6f",
                    "target": "nfccedff6c7637a3a2a6093fd8b48818"
                },
                "l1e2cb3a00383c6ea0d3686c729492fd": {
                    "id": "l1e2cb3a00383c6ea0d3686c729492fd",
                    "is_default": false,
                    "source": "nfccedff6c7637a3a2a6093fd8b48818",
                    "target": "ncc1ac32fd1d338980c7831fd20bf908"
                }
            },
            "gateways": {},
            "line": [
                {
                    "id": "l7005877547e3769890512baba0d01b9",
                    "source": {
                        "arrow": "Right",
                        "id": "na24da677f3a3b22a8a7daf8e5f7ac6f"
                    },
                    "target": {
                        "arrow": "Left",
                        "id": "nfccedff6c7637a3a2a6093fd8b48818"
                    }
                },
                {
                    "id": "l1e2cb3a00383c6ea0d3686c729492fd",
                    "source": {
                        "arrow": "Right",
                        "id": "nfccedff6c7637a3a2a6093fd8b48818"
                    },
                    "target": {
                        "arrow": "Left",
                        "id": "ncc1ac32fd1d338980c7831fd20bf908"
                    }
                }
            ],
            "location": [
                {
                    "id": "na24da677f3a3b22a8a7daf8e5f7ac6f",
                    "type": "startpoint",
                    "x": 40,
                    "y": 150
                },
                {
                    "id": "nfccedff6c7637a3a2a6093fd8b48818",
                    "type": "tasknode",
                    "name": "发送消息",
                    "stage_name": "",
                    "x": 240,
                    "y": 145,
                    "group": "企业微信(WechatWork)",
                    "icon": ""
                },
                {
                    "id": "ncc1ac32fd1d338980c7831fd20bf908",
                    "type": "endpoint",
                    "x": 540,
                    "y": 150
                }
            ],
            "outputs": [],
            "start_event": {
                "id": "na24da677f3a3b22a8a7daf8e5f7ac6f",
                "incoming": "",
                "name": "",
                "outgoing": "l7005877547e3769890512baba0d01b9",
                "type": "EmptyStartEvent",
                "labels": []
            },
            "id": "n7d2258a508c373a8a047f4cb0c3528a"
        },
        "task_id": 5,
        "task_url": "http://{PAAS_HOST}/taskflow/execute/3/?instance_id=5"
    },
    "request_id": "xxx"
    "trace_id": "ebc2a953abbc4955a993f88242c7f808"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result      |    bool    |   true/false, indicate success or failure    |
|  data        |    dict  |   data returned when result is true, details are described below       |
|  message     |    string  |   error message returned when result is false |
|  request_id     |    string  | esb request id |
|  trace_id     |    string  | open telemetry trace_id|

#### data

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  task_id      |    int    |   the task instance ID    |
|  task_url     |    string |    task instance url     |
|  pipeline_tree     |    dict     |    task pipeline tree     |

#### data.pipeline_tree

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  start_event      |    dict    |      start node     |
|  end_event      |    dict    |      end node    |
|  activities      |    dict    |      task node（plugins or subprocess）info    |
|  gateways      |    dict    |      gateways（parallel gateway、exclusive gateway、exclusive gateway）info    |
|  flows      |    dict    |      sequenceFlow（the line between nodes）info    |
|  constants      |    dict    |  global variables, details are described below    |
|  outputs      |    list    |    outputs info, indicate outputs field of global  |

#### data.pipeline_tree.constants KEY

KEY, the format is like ${key}

#### data.pipeline_tree.constants VALUE

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  key      |    string    |      same with KEY     |
|  name      |    string    |     name    |
|  index      |    int    |       display order at the front end   |
|  desc      |    string    |     description   |
|  source_type  | string   |      source of variable, custom mean manual variable, component_inputs means variables comes from task node inputs parameters, component_outputs means variables comes from task node outputs parameters   |
|  custom_type  | string   |      custom type, which is not empty when source_type is custom, the value is input ,or textarea, or datetime, or int |
|  source_tag   | string   |      source tag and plugin info, which is not empty when source_type is  component_inputs or component_outputs  |
|  source_info | dict    |        source info about task node ID  |
