### Functional description

Query a task execution details

### Request Parameters

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

| Field          |  Type       | Required   |  Description          |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   task_id     |   string   |   YES   |  the task ID   |

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
    "data": {
        "creator": "admin",
        "outputs": [
            {
                "value": "1",
                "key": "${job_script_type}",
                "name": "type"
            },
            {
                "value": "127.0.0.1",
                "key": "${IP}",
                "name": "IP"
            },
            {
                "value": "0",
                "key": "${EXIT}",
                "name": "EXIT"
            }
        ],
        "start_time": "2019-01-17 04:13:08",
        "business_id": 2,
        "create_time": "2019-01-17 04:13:03",
        "business_name": "blueking",
        "id": 10,
        "constants": {
            "${IP}": {
                "source_tag": "var_ip_picker.ip_picker",
                "source_info": {},
                "name": "IP",
                "index": 2,
                "custom_type": "ip",
                "value": {
                    "var_ip_custom_value": "127.0.0.1",
                    "var_ip_method": "custom",
                    "var_ip_tree": []
                },
                "show_type": "show",
                "source_type": "custom",
                "validator": [],
                "key": "${IP}",
                "desc": "",
                "validation": "",
                "is_meta": false
            },
            "${job_script_type}": {
                "source_tag": "job_fast_execute_script.job_script_type",
                "source_info": {
                    "node554316ea019a341f8c28cc6a7da9": [
                        "job_script_type"
                    ]
                },
                "name": "type",
                "index": 0,
                "custom_type": "",
                "value": "1",
                "show_type": "show",
                "source_type": "component_inputs",
                "key": "${job_script_type}",
                "validation": "",
                "desc": ""
            },
            "${EXIT}": {
                "source_tag": "",
                "source_info": {},
                "name": "EXIT",
                "index": 1,
                "custom_type": "input",
                "value": "0",
                "show_type": "show",
                "source_type": "custom",
                "validator": [],
                "key": "${EXIT}",
                "validation": "^.+$",
                "desc": ""
            }
        },
        "create_method": "app",
        "elapsed_time": 7,
        "ex_data": "",
        "instance_name": "job_20190117121300",
        "end_time": "2019-01-17 04:13:15",
        "executor": "admin",
        "template_id": "266",
        "task_url": "http://bk_sops_host/taskflow/execute/3/?instance_id=15364",
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
                    "can_retry": true,
                    "isSkipped": true,
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
                    "can_retry": true,
                    "isSkipped": true,
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
            "constants": {},
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
                    "stage_name": "stage1",
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
    "result": true
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
|  id      |    int    |      the unique ID of task    |
|  name    |    string    |      the name of task               |
|  business_id      |  int       |  the business ID    |
|  business_name    |  string    |  the business name   |
|  template_id      |  int       |  the ID of flow used to create task  |
|  create_time      |  string    |  datetime when this task created   |
|  create_method    |  string    |  method how  this task created  |
|  start_time       |  string    |  start time   |
|  finish_time      |  string    |  finish time   |
|  elapsed_time     |  int       |  elapsed time(seconds) |
|  creator          |  string    |  person who created this task     |
|  executor         |  string    |  person who executed this task     |
|  constants        |  dict      |  global variables, details are described below |
|  outputs          |  list      |  outputs info of this task，details are described below |
|  task_url     |    str     |    task instance url     |
|  pipeline_tree     |    dict     |    task pipeline tree     |

#### data.constants.KEY

KEY, the format is like ${key}


#### data.constants.VALUE
| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      same with KEY     |
|  name      |    string    |     name    |
|  index      |    int    |       display order at the front end   |
|  desc      |    string    |     description   |
|  source_type  | string   |      source of variable, custom mean manual variable, component_inputs means variables comes from task node inputs parameters, component_outputs means variables comes from task node outputs parameters   |
|  custom_type  | string   |      custom type, which is not empty when source_type is custom,  the value is input ,or textarea, or datetime, or int |
|  source_tag   | string   |      source tag and plugin info, which is not empty when source_type is  component_inputs or component_outputs  |
|  source_info | dict    |        source info about task node ID  |


#### data.outputs[] 
| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  name         | string     | name of output variable                   |
|  value        | string、int、bool、dict、list | value  |
|  key          | string     | KEY                   |
|  preset       | bool       | where to display in Standard Plugins   |

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
