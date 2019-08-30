### Functional description

Query periodic task detail

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
|---------------|------------|--------|------------------|
|   task_id    |   string     |   YES   |  task ID |
|   bk_biz_id    |   string     |   YES   |  business ID |


### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "task": "8"
}
```

### Return Result Example

```
{
    "message": "",
    "data": {
        "cron": "1,2,3-19/2 2 3 4 5 (m/h/d/dM/MY)",
        "total_run_count": 0,
        "name": "task2",
        "form": {
            "${bk_timing}": {
                "source_tag": "sleep_timer.bk_timing",
                "source_info": {
                    "node76393dcfedcf73dbc726f1c4786d": [
                        "bk_timing"
                    ]
                },
                "name": "time",
                "index": 0,
                "custom_type": "",
                "value": "2",
                "show_type": "show",
                "source_type": "component_inputs",
                "key": "${bk_timing}",
                "validation": "",
                "desc": ""
            }
        },
        "creator": "admin",
        "pipeline_tree": {
            "activities": {
                "nodea5c396a3ef0f9f3cd7d4d7695f78": {
                    "outgoing": "linef69b59d165fb8c0061b46588c515",
                    "incoming": "linecf7b7f10c87187a88b72c5f91177",
                    "name": "pause",
                    "error_ignorable": false,
                    "component": {
                        "code": "pause_node",
                        "data": {}
                    },
                    "stage_name": "step1",
                    "optional": false,
                    "type": "ServiceActivity",
                    "id": "nodea5c396a3ef0f9f3cd7d4d7695f78",
                    "loop": {}
                },
                "node76393dcfedcf73dbc726f1c4786d": {
                    "outgoing": "linecf7b7f10c87187a88b72c5f91177",
                    "incoming": "linecd597f19606c1455d661f71a582d",
                    "name": "time",
                    "error_ignorable": false,
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {
                                "hook": true,
                                "value": "${bk_timing}"
                            }
                        }
                    },
                    "stage_name": "step1",
                    "optional": false,
                    "type": "ServiceActivity",
                    "id": "node76393dcfedcf73dbc726f1c4786d",
                    "loop": {}
                }
            },
            "end_event": {
                "incoming": "linef69b59d165fb8c0061b46588c515",
                "outgoing": "",
                "type": "EmptyEndEvent",
                "id": "node375320830be9c46cd89f4069857d",
                "name": ""
            },
            "outputs": [],
            "flows": {
                "linef69b59d165fb8c0061b46588c515": {
                    "is_default": false,
                    "source": "nodea5c396a3ef0f9f3cd7d4d7695f78",
                    "id": "linef69b59d165fb8c0061b46588c515",
                    "target": "node375320830be9c46cd89f4069857d"
                },
                "linecd597f19606c1455d661f71a582d": {
                    "is_default": false,
                    "source": "node4e87796ddd76b0d59337b08f385d",
                    "id": "linecd597f19606c1455d661f71a582d",
                    "target": "node76393dcfedcf73dbc726f1c4786d"
                },
                "linecf7b7f10c87187a88b72c5f91177": {
                    "is_default": false,
                    "source": "node76393dcfedcf73dbc726f1c4786d",
                    "id": "linecf7b7f10c87187a88b72c5f91177",
                    "target": "nodea5c396a3ef0f9f3cd7d4d7695f78"
                }
            },
            "gateways": {},
            "line": [
                {
                    "source": {
                        "id": "nodea5c396a3ef0f9f3cd7d4d7695f78",
                        "arrow": "Right"
                    },
                    "target": {
                        "id": "node375320830be9c46cd89f4069857d",
                        "arrow": "Left"
                    },
                    "id": "linef69b59d165fb8c0061b46588c515"
                },
                {
                    "source": {
                        "id": "node4e87796ddd76b0d59337b08f385d",
                        "arrow": "Right"
                    },
                    "id": "linecd597f19606c1455d661f71a582d",
                    "target": {
                        "id": "node76393dcfedcf73dbc726f1c4786d",
                        "arrow": "Left"
                    }
                },
                {
                    "source": {
                        "id": "node76393dcfedcf73dbc726f1c4786d",
                        "arrow": "Right"
                    },
                    "target": {
                        "id": "nodea5c396a3ef0f9f3cd7d4d7695f78",
                        "arrow": "Left"
                    },
                    "id": "linecf7b7f10c87187a88b72c5f91177"
                }
            ],
            "start_event": {
                "incoming": "",
                "outgoing": "linecd597f19606c1455d661f71a582d",
                "type": "EmptyStartEvent",
                "id": "node4e87796ddd76b0d59337b08f385d",
                "name": ""
            },
            "constants": {
                "${bk_timing}": {
                    "source_tag": "sleep_timer.bk_timing",
                    "source_info": {
                        "node76393dcfedcf73dbc726f1c4786d": [
                            "bk_timing"
                        ]
                    },
                    "name": "time",
                    "index": 0,
                    "custom_type": "",
                    "value": "2",
                    "show_type": "show",
                    "source_type": "component_inputs",
                    "key": "${bk_timing}",
                    "validation": "",
                    "desc": ""
                }
            },
            "location": [
                {
                    "stage_name": "step1",
                    "name": "pause",
                    "y": 133,
                    "x": 631,
                    "type": "tasknode",
                    "id": "nodea5c396a3ef0f9f3cd7d4d7695f78"
                },
                {
                    "y": 150,
                    "x": 80,
                    "type": "startpoint",
                    "id": "node4e87796ddd76b0d59337b08f385d"
                },
                {
                    "y": 149,
                    "x": 1092,
                    "type": "endpoint",
                    "id": "node375320830be9c46cd89f4069857d"
                },
                {
                    "stage_name": "step1",
                    "name": "time",
                    "y": 133,
                    "x": 300,
                    "type": "tasknode",
                    "id": "node76393dcfedcf73dbc726f1c4786d"
                }
            ]
        },
        "last_run_at": "",
        "enabled": true,
        "id": 5,
        "template_id": "2"
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
| ------------ | ---------- | ------------------------------ |
|  cron      |    string    |      crontab expression    |
|  total_run_count      |    int    |    how much times the task run   |
|  name      |    string    |    task name   |
|  creator      |    string    |    creator   |
|  last_run_at      |    string    |    date of last run   |
|  enabled      |    bool    |   is the task enabled   |
|  id      |    int    |    task id   |
|  template_id      |    string    |    template id for the task   |
|  form      |    dict    |    form dict for the task   |
|  pipeline_tree      |    dict    |    flow tree for the task   |


#### data.pipeline_tree

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  start_event      |    dict    |      start node     |
|  end_event      |    dict    |      end node    |
|  activities      |    dict    |      task node（standard plugins or subprocess）info    |
|  gateways      |    dict    |      gateways（parallel gateway、exclusive gateway、exclusive gateway）info    |
|  flows      |    dict    |      sequenceFlow（the line between nodes）info    |
|  constants      |    dict    |  global variables, details are described below    |
|  outputs      |    list    |    outputs info, indicate outputs field of global variables|

#### data.form.KEY, data.pipeline_tree.constants.KEY

KEY, the format is like ${key}

#### data.form.VALUE, data.pipeline_tree.constants.VALUE

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  key      |    string    |      same with KEY     |
|  name      |    string    |     name    |
|  index      |    int    |       display order at the front end   |
|  desc      |    string    |     description   |
|  source_type  | string   |      source of variable, custom mean manual variable, component_inputs means variables comes from task node inputs parameters, component_outputs means variables comes from task node outputs parameters   |
|  custom_type  | string   |      custom type, which is not empty when source_type is custom,  the value is input ,or textarea, or datetime, or int |
|  source_tag   | string   |      source tag and standard plugin info, which is not empty when source_type is  component_inputs or component_outputs  |
|  source_info | dict    |        source info about task node ID  |
