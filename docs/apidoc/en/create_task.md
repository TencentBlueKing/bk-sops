### Request Address

/v2/sops/create_task/

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
|   exclude_task_nodes_id | list |   NO   | nodes id not be executed, which are set ignore in flow(if you have execute_task_nodes_id and exclude_task_nodes_id, then execute_task_nodes_id will be using.) |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project'|
|   simplify_vars    |   list       |   NO    |  list of constants key for type simplify.(after the task is created, the simplified constants will lose the type originally configured in the template, and they will all become variables of this textarea. By using this option, the difference in value format of different types of constants can be shielded when API calls are made, and they are uniformly passed through the text type. value) |
| execute_task_nodes_id | list | NO | nodes id only be executed.(if you have execute_task_nodes_id and exclude_task_nodes_id, then execute_task_nodes_id will be using.) |

#### constants KEY

constant KEY, the format is like ${key}

#### constants.VALUE

constant value, the type of value should be same with data from API[get_template_info]

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "name": "tasktest",
    "bk_biz_id":"1",
    "template_id":"1",
    "template_source":"business",
    "flow_type": "common",
    "constants": {
        "${content}": "echo 1",
        "${params}": "",
        "${script_timeout}": 20
    },
    "simplify_vars": ["${k1}", "${k2}", "${ip}", "${force_check}"],
    "execute_task_nodes_id": [1, 2, 3],
    "exclude_task_nodes_id": [4, 5, 6],
    "scope": "cmdb_biz",
}
```

### Return Result Example

```
{
    "result": true,
    "data": {
        "task_id": 10,
        "task_url": "http://bk_sops_host/taskflow/execute/3/?instance_id=10",
        "pipeline_tree": {
            "activities": {
                "node9b5ae13799d63e179f0ce3088b62": {
                    "outgoing": "line27bc7b4ccbcf37ddb9d1f6572a04",
                    "incoming": "line490caa49d2a03e64829693281032",
                    "name": "timing",
                    "error_ignorable": false,
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {
                                "hook": false,
                                "value": "2"
                            }
                        }
                    },
                    "stage_name": "stage1",
                    "retryable": true,
                    "skippable": true,
                    "type": "ServiceActivity",
                    "optional": false,
                    "id": "node9b5ae13799d63e179f0ce3088b62",
                    "loop": null
                },
                "node880ded556c6c3c269be3cedc64b6": {
                    "outgoing": "line490caa49d2a03e64829693281032",
                    "incoming": "lineb83161d6e0593ad68d9ec73a961b",
                    "name": "pause",
                    "error_ignorable": false,
                    "component": {
                        "code": "pause_node",
                        "data": {}
                    },
                    "stage_name": "stage1",
                    "retryable": true,
                    "skippable": true,
                    "type": "ServiceActivity",
                    "optional": true,
                    "id": "node880ded556c6c3c269be3cedc64b6",
                    "loop": null
                }
            },
            "end_event": {
                "type": "EmptyEndEvent",
                "outgoing": "",
                "incoming": "line27bc7b4ccbcf37ddb9d1f6572a04",
                "id": "node5c48f37aa9f0351e8b43ab6a2295",
                "name": ""
            },
            "outputs": [],
            "flows": {
                "line490caa49d2a03e64829693281032": {
                    "is_default": false,
                    "source": "node880ded556c6c3c269be3cedc64b6",
                    "id": "line490caa49d2a03e64829693281032",
                    "target": "node9b5ae13799d63e179f0ce3088b62"
                },
                "lineb83161d6e0593ad68d9ec73a961b": {
                    "is_default": false,
                    "source": "noded383bc1d7387391f889c6bab18b8",
                    "id": "lineb83161d6e0593ad68d9ec73a961b",
                    "target": "node880ded556c6c3c269be3cedc64b6"
                },
                "line27bc7b4ccbcf37ddb9d1f6572a04": {
                    "is_default": false,
                    "source": "node9b5ae13799d63e179f0ce3088b62",
                    "id": "line27bc7b4ccbcf37ddb9d1f6572a04",
                    "target": "node5c48f37aa9f0351e8b43ab6a2295"
                }
            },
            "gateways": {},
            "line": [
                {
                    "source": {
                        "id": "node9b5ae13799d63e179f0ce3088b62",
                        "arrow": "Right"
                    },
                    "target": {
                        "id": "node5c48f37aa9f0351e8b43ab6a2295",
                        "arrow": "Left"
                    },
                    "id": "line27bc7b4ccbcf37ddb9d1f6572a04"
                },
                {
                    "source": {
                        "id": "node880ded556c6c3c269be3cedc64b6",
                        "arrow": "Right"
                    },
                    "target": {
                        "id": "node9b5ae13799d63e179f0ce3088b62",
                        "arrow": "Left"
                    },
                    "id": "line490caa49d2a03e64829693281032"
                },
                {
                    "source": {
                        "id": "noded383bc1d7387391f889c6bab18b8",
                        "arrow": "Right"
                    },
                    "id": "lineb83161d6e0593ad68d9ec73a961b",
                    "target": {
                        "id": "node880ded556c6c3c269be3cedc64b6",
                        "arrow": "Left"
                    }
                }
            ],
            "start_event": {
                "type": "EmptyStartEvent",
                "outgoing": "lineb83161d6e0593ad68d9ec73a961b",
                "incoming": "",
                "id": "noded383bc1d7387391f889c6bab18b8",
                "name": ""
            },
            "id": "node7ef6970d06ad3bc092594cb5ec5f",
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
            "location": [
                {
                    "stage_name": "stage1",
                    "name": "pause",
                    "y": 135,
                    "x": 300,
                    "type": "tasknode",
                    "id": "node880ded556c6c3c269be3cedc64b6"
                },
                {
                    "y": 150,
                    "x": 1000,
                    "type": "endpoint",
                    "id": "node5c48f37aa9f0351e8b43ab6a2295"
                },
                {
                    "stage_name": "stage",
                    "name": "timing",
                    "y": 135,
                    "x": 595,
                    "type": "tasknode",
                    "id": "node9b5ae13799d63e179f0ce3088b62"
                },
                {
                    "y": 150,
                    "x": 80,
                    "type": "startpoint",
                    "id": "noded383bc1d7387391f889c6bab18b8"
                }
            ]
        }
    },
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result      |    bool    |   true/false, indicate success or failure     |
|  data        |    dict  |   data returned when result is true, details are described below        |
|  message     |    string  |   error message returned when result is false |
|  request_id     |    string  | esb request id             |
|  trace_id     |    string  | open telemetry trace_id        |

####  data

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
|  custom_type  | string   |      custom type, which is not empty when source_type is custom,  the value is input ,or textarea, or datetime, or int |
|  source_tag   | string   |      source tag and plugin info, which is not empty when source_type is  component_inputs or component_outputs  |
|  source_info | dict    |        source info about task node ID  |
