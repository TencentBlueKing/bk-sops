### Functional description

Query individual flow template details of the business

### Request Parameters

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

| Field         |   Type     | Required   |  Description    |
|---------------|------------|---------|--------------------|
| bk_biz_id     | string     |   YES   |  the business ID   |
| template_id   | string     |   YES   |  the task ID       |
| template_source | string   |   NO    | source of flow，default value is business. business: from business, common: from common flow |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "1",
    "template_id": "30",
    "template_source": "business"
}
```

### Return Result Example

```
{
    "result": true,
    "data": {
        "category": "Other",
        "edit_time": "2018-04-27 16:24:24 +0800",
        "create_time": "2018-04-16 21:43:15 +0800",
        "name": "new20180416213944",
        "bk_biz_id": "2",
        "creator": "admin",
        "pipeline_tree": {
            "activities": {
                "631b6576cc5dfbdcaa4f510ce88a7e67": {
                    "outgoing": "44ab36ebf4cf119edaf2d20401da87e4",
                    "incoming": "fb2f3a8b533ca5c67e2440b4164f7632",
                    "name": "node_1",
                    "error_ignorable": false,
                    "component": {
                        "code": "job_fast_execute_script",
                        "data": {
                            "account": {
                                "hook": false,
                                "value": "root"
                            },
                            "ip_list": {
                                "hook": false,
                                "value": "127.0.0.1"
                            },
                            "script_timeout": {
                                "hook": true,
                                "value": "${script_timeout}"
                            },
                            "content": {
                                "hook": false,
                                "value": "${content}"
                            },
                            "script_param": {
                                "hook": false,
                                "value": "${params}"
                            },
                            "script_type": {
                                "hook": true,
                                "value": "${script_type}"
                            }
                        }
                    },
                    "optional": false,
                    "type": "ServiceActivity",
                    "id": "631b6576cc5dfbdcaa4f510ce88a7e67",
                    "loop": null
                }
            },
            "end_event": {
                "type": "EmptyEndEvent",
                "outgoing": "",
                "incoming": "44ab36ebf4cf119edaf2d20401da87e4",
                "id": "60c81e383d048d8a3c574d3436e1b82c",
                "name": ""
            },
            "outputs": [],
            "flows": {
                "fb2f3a8b533ca5c67e2440b4164f7632": {
                    "is_default": false,
                    "source": "48afea1016ab70ee37179fa0eb1e1a14",
                    "id": "fb2f3a8b533ca5c67e2440b4164f7632",
                    "target": "631b6576cc5dfbdcaa4f510ce88a7e67"
                },
                "44ab36ebf4cf119edaf2d20401da87e4": {
                    "is_default": false,
                    "source": "631b6576cc5dfbdcaa4f510ce88a7e67",
                    "id": "44ab36ebf4cf119edaf2d20401da87e4",
                    "target": "60c81e383d048d8a3c574d3436e1b82c"
                }
            },
            "start_event": {
                "type": "EmptyStartEvent",
                "outgoing": "fb2f3a8b533ca5c67e2440b4164f7632",
                "incoming": "",
                "id": "48afea1016ab70ee37179fa0eb1e1a14",
                "name": ""
            },
            "constants": {
                "${script_type}": {
                    "source_tag": "job_fast_execute_script.script_type",
                    "source_info": {
                        "631b6576cc5dfbdcaa4f510ce88a7e67": [
                            "script_type"
                        ]
                    },
                    "name": "script_type",
                    "index": 0,
                    "custom_type": "radio",
                    "value": "4",
                    "show_type": "show",
                    "source_type": "component_inputs",
                    "key": "${script_type}",
                    "validation": "^.*$",
                    "desc": ""
                },
                "${content}": {
                    "source_tag": "",
                    "source_info": {},
                    "name": "content",
                    "index": 2,
                    "custom_type": "textarea",
                    "value": "",
                    "show_type": "show",
                    "source_type": "custom",
                    "key": "${content}",
                    "desc": ""
                },
                "${script_timeout}": {
                    "source_tag": "job_fast_execute_script.script_timeout",
                    "source_info": {
                        "631b6576cc5dfbdcaa4f510ce88a7e67": [
                            "script_timeout"
                        ]
                    },
                    "name": "script_timeout",
                    "index": 1,
                    "custom_type": "input",
                    "value": "",
                    "show_type": "show",
                    "source_type": "component_inputs",
                    "key": "${script_timeout}",
                    "validation": "^.*$",
                    "desc": ""
                },
                "${params}": {
                    "source_tag": "",
                    "source_info": {},
                    "name": "params",
                    "index": 3,
                    "custom_type": "input",
                    "value": "",
                    "show_type": "show",
                    "source_type": "custom",
                    "key": "${params}",
                    "desc": ""
                }
            },
            "gateways": {}
        },
        "bk_biz_name": "blueking",
        "id": 30,
        "editor": "admin"
    },
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
|  bk_biz_id     |    string    |      the business ID      |
|  bk_biz_name   |    string    |      the business name    |
|  id            |    int       |      flow template ID             |
|  name          |    string    |      flow template name            |
|  category      |    string    |      flow type，the value is described below    |
|  creator       |    string    |      person who created this flow template      |
|  create_time   |    string    |      datetime when this flow template created   |
|  editor        |    string or null | person who edited this flow template last |
|  edit_time     |    string    |      datetime when this flow template edited          |
|  pipeline_tree |    dict      |      template tree info, details are described below    |

#### data.category

| Value        | Description     |
|--------------|----------|
| OpsTools     | operation tools  |
| MonitorAlarm | monitor alarm  |
| ConfManage   | configuration management  |
| DevTools     | development tools  |
| EnterpriseIT | enterprise IT   |
| OfficeApp    | official APPs  |
| Other        | other     |

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

#### data.pipeline_tree.constants.KEY

KEY, the format is like ${key}

#### data.pipeline_tree.constants.VALUE

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
