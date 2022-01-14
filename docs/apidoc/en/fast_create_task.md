### Request Address

/v2/sops/fast_create_task/

### Request Method

POST

### Functional description

Create onetime task quickly

### Request Parameters

#### General Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|----------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

| Field         |  Type      | Required |  Description     |
|---------------|------------|----------|------------------|
|   bk_biz_id  |   int      |  YES     |  the project ID  |
|   name        |   string   |  YES     |  task name       |
|   pipeline_tree | dict     |  NO      |  task pipeline tree, details are described below |
|   has_common_subprocess | bool | NO |  the template type of the subprocess in the task，true：common template，false：project based task template. Default is false. |
|   flow_type   |   string   |  NO      |  flow task type，common: common flow，common_func：functional flow. Default is common |
|   description |   string   |  NO      |  task description|
|   category    |   string   |  NO      |  flow type, the value is described below |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to project_id. otherwise, bk_sops will find a project which id equal to project_id when scope value is 'project'|

#### category

| Value        | Description     |
|--------------|-----------------|
| OpsTools     | operation tools |
| MonitorAlarm | monitor alarm   |
| ConfManage   | configuration management |
| DevTools     | development tools |
| EnterpriseIT | enterprise IT   |
| OfficeApp    | official APPs   |
| Other        | other           |

#### pipeline_tree

| Field         |  Type      | Required   |  Description     |
|---------------|------------|------------|------------------|
|  start_event  | dict       | YES        |  start node, details are described below |
|  end_event    | dict       | YES        |  end node, details are described below |
|  activities   | dict       | YES        |  task node（standard plugins or subprocess）info, details are described below |
|  flows        | dict       | YES        |  sequenceFlow（the line between nodes）info, details are described below |
|  gateways     | dict       | NO         |  gateways（parallel gateway、exclusive gateway、exclusive gateway）info, details are described below |
|  constants    | dict       | NO         |  global variables, details are described below |
|  outputs      | list       | NO         |  outputs info, indicate outputs field of global variables |

#### pipeline_tree.start_event

| Field         |  Type      | Required   |  Description     |
|---------------|------------|------------|------------------|
|  id           |  string    | YES        | start node ID, globally unique across all IDs of pipeline_tree |
|  type         |  string    | YES        | start node type, must be "EmptyStartEvent" now |
|  name         |  string    | YES        | start node name, could be empty string |
|  incoming     |  string    | YES        | incoming sequence flow ID, must be empty string |
|  outgoing     |  string    | YES        | outgoing sequence flow ID    |

#### pipeline_tree.end_event

| Field         |  Type      | Required   |  Description     |
|---------------|------------|------------|------------------|
|  id           |  string    | YES        | end node ID, globally unique across all IDs of pipeline_tree |
|  type         |  string    | YES        | end node type, must by "EmptyEndEvent" now |
|  name         |  string    | YES        | end node name, could be empty string |
|  incoming     |  string    | YES        | incoming sequence flow ID    |
|  outgoing     |  string    | YES        | outgoing sequence flow ID, must be empty string |

#### pipeline_tree.activities KEY、pipeline_tree.flows KEY、pipeline_tree.gateways KEY

flow element ID, string type, which is globally unique across all IDs of pipeline_tree, used to identify topological relationships

#### pipeline_tree.activities VALUE

| Field         |  Type      | Required   |  Description     |
|---------------|------------|------------|------------------|
|  id           |  string    | YES        | task node ID, same with KEY |
|  type         |  string    | YES        | task node type, must be "ServiceActivity" now, which means standard plugin node |
|  name         |  string    | YES        | task node name   |
|  component    |  dict      | YES        | standard plugin configuration, details are described below |
|  error_ignorable | bool    | YES        | whether to automatically ignore after the node fails |
|  retryable    |  bool      | YES        | can I retry after the node fails, invalid when error_ignorable is true |
|  skippable    |  bool      | YES        | can I skip after  the node fails, invalid when error_ignorable is true |
|  incoming     |  string    | YES        | incoming sequence flow ID |
|  outgoing     |  string    | YES        | outgoing sequence flow ID |
|  stage_name   |  string    | NO         | stage name       |

#### pipeline_tree.activities VALUE.component

| Field         |  Type      | Required   |  Description     |
|---------------|------------|------------|------------------|
|  code         |  string    | YES        | unique code of a plugin |
|  data         |  dict      | YES        | input params of a plugin |

#### pipeline_tree.flows VALUE

| Field         |  Type      | Required   |  Description     |
|---------------|------------|------------|------------------|
| id            |  string    | YES        | sequence flow ID, same with KEY |
| is_default    |  bool      | YES        | whether is default branch |
| source        |  string    | YES        | source node ID   |
| target        |  string    | YES        | target node ID   |

#### pipeline_tree.gateways VALUE

| Field         |  Type      | Required   |  Description     |
|---------------|------------|------------|------------------|
|  id           | string     | YES        | gateway node ID, same with KEY  |
|  type         | string     | YES        | gateway type, ParallelGateway or ExclusiveGateway or ConvergeGateway |
|  name         | string     | YES        | gateway node name, could be empty string |
|  incoming     | string/list| YES        | incoming sequence flow ID , the format should be list when gateway type is "ConvergeGateway", otherwise string |
|  outgoing     | string/list| YES        | outgoing sequence flow ID, the format should be string when gateway type is "ConvergeGateway", otherwise list |
|  conditions   | dict       | NO         | exclusive, required when gateway type is "ExclusiveGateway", details are described below |

#### pipeline_tree.gateways VALUE.conditions KEY

gateway outgoing sequence flow ID, one-to-one correspondence with the outgoing list

#### pipeline_tree.gateways VALUE.conditions VALUE

| Field         |  Type      | Required   |  Description     |
|---------------|------------|------------|------------------|
| evaluate      |  string    | YES        | branch expression, for the supported syntax, please refer to the product white paper and other documents. |

#### pipeline_tree.constants KEY

KEY of global variables, the format is "${key}"

#### pipeline_tree.constants VALUE

| Field         |  Type      | Required   |  Description     |
|---------------|------------|------------|------------------|
|  key          | string     | YES        | same with KEY    |
|  name         | string     | YES        | name             |
|  index        | int        | YES        | display order at the front end |
|  desc         | string     | YES        | description      |
|  source_type  | string     | YES        | source of variable, custom mean manual variable, component_inputs means variables comes from task node inputs parameters, component_outputs means variables comes from task node outputs parameters |
|  custom_type  | string     | YES        | custom type, which is not empty when source_type is custom,  the value is input ,or textarea, or datetime, or int |
|  source_tag   | string     | YES        | source tag and standard plugin info, which is not empty when source_type is  component_inputs or component_outputs |
|  source_info  | dict       | YES        |  source info about task node ID |


### Request Parameters Example

```
{
    "project_id": "1",
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "name": "tasktest",
    "flow_type": "common",
    "description":"...",
    "has_common_subprocess":false
    "category":"OpsTools"
    "pipeline_tree": {
        "start_event": {
            "incoming": "",
            "outgoing": "line7ed74aa679d19063b6d7037ce6db",
            "type": "EmptyStartEvent",
            "id": "node20cbeaa5379d08e8d8ed7bb44fdc",
            "name": ""
        },
        "activities": {
            "node5310ec36c0364d3094d515f8f5ef": {
                "outgoing": "linec02d1e77e1076aa9c7c2c57238e4",
                "incoming": "line7ed74aa679d19063b6d7037ce6db",
                "name": "node1",
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
                "stage_name": "stage1",
                "retryable": true,
                "skippable": true,
                "type": "ServiceActivity",
                "id": "node5310ec36c0364d3094d515f8f5ef"
            },
            "node2bf42efcebe266706c3e21326dc4": {
                "outgoing": "linef0deadac69f769440a1b0e32587e",
                "incoming": "line7587c8804d34a091dae3d321f081",
                "name": "node2",
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
                "stage_name": "stage2",
                "retryable": true,
                "skippable": true,
                "type": "ServiceActivity",
                "id": "node2bf42efcebe266706c3e21326dc4"
            },
            "node3c7dcf31454c1e9bdc9cf1cdeacc": {
                "outgoing": "linebf8f91c96a8f4eb3794ca5eb9881",
                "incoming": "line429f64cdec5d20f368611e621ef5",
                "name": "node3",
                "error_ignorable": false,
                "component": {
                    "code": "sleep_timer",
                    "data": {
                        "bk_timing": {
                            "hook": false,
                            "value": "3"
                        }
                    }
                },
                "stage_name": "stage3",
                "retryable": true,
                "skippable": true,
                "type": "ServiceActivity",
                "id": "node3c7dcf31454c1e9bdc9cf1cdeacc"
            },
            "nodedb1478a75c13f90cc400f5379949": {
                "outgoing": "line24d28a3f9f80e23e4a4fab7c4ffd",
                "incoming": "linec43c77f26af408748a9c194dbcfe",
                "name": "node4",
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
                "stage_name": "stage3",
                "retryable": true,
                "skippable": true,
                "type": "ServiceActivity",
                "id": "nodedb1478a75c13f90cc400f5379949"
            }
        },
        "end_event": {
            "incoming": "line6ea858554964a04d868cead4435a",
            "outgoing": "",
            "type": "EmptyEndEvent",
            "id": "nodebe0db4ad30cc1723c7ede37b4b5f",
            "name": ""
        },
        "flows": {
            "line24d28a3f9f80e23e4a4fab7c4ffd": {
                "is_default": false,
                "source": "nodedb1478a75c13f90cc400f5379949",
                "id": "line24d28a3f9f80e23e4a4fab7c4ffd",
                "target": "node947e423b22e49aeb77bc77528bc0"
            },
            "linebf8f91c96a8f4eb3794ca5eb9881": {
                "is_default": false,
                "source": "node3c7dcf31454c1e9bdc9cf1cdeacc",
                "id": "linebf8f91c96a8f4eb3794ca5eb9881",
                "target": "node947e423b22e49aeb77bc77528bc0"
            },
            "line7587c8804d34a091dae3d321f081": {
                "is_default": false,
                "source": "node0863aab8325b84cfa3e5db52dc61",
                "id": "line7587c8804d34a091dae3d321f081",
                "target": "node2bf42efcebe266706c3e21326dc4"
            },
            "line429f64cdec5d20f368611e621ef5": {
                "is_default": false,
                "source": "node7e97af0f55fb64276e067951dd9d",
                "id": "line429f64cdec5d20f368611e621ef5",
                "target": "node3c7dcf31454c1e9bdc9cf1cdeacc"
            },
            "line6ea858554964a04d868cead4435a": {
                "is_default": false,
                "source": "node2b6f3285cfb3961c72834bafbe1b",
                "id": "line6ea858554964a04d868cead4435a",
                "target": "nodebe0db4ad30cc1723c7ede37b4b5f"
            },
            "line9dd9c8dbbad90943f268442ab7e0": {
                "is_default": false,
                "source": "node0863aab8325b84cfa3e5db52dc61",
                "id": "line9dd9c8dbbad90943f268442ab7e0",
                "target": "node7e97af0f55fb64276e067951dd9d"
            },
            "lineabc279d9be88eb98285132ba5b75": {
                "is_default": false,
                "source": "node947e423b22e49aeb77bc77528bc0",
                "id": "lineabc279d9be88eb98285132ba5b75",
                "target": "node2b6f3285cfb3961c72834bafbe1b"
            },
            "linef0deadac69f769440a1b0e32587e": {
                "is_default": false,
                "source": "node2bf42efcebe266706c3e21326dc4",
                "id": "linef0deadac69f769440a1b0e32587e",
                "target": "node2b6f3285cfb3961c72834bafbe1b"
            },
            "linec02d1e77e1076aa9c7c2c57238e4": {
                "is_default": false,
                "source": "node5310ec36c0364d3094d515f8f5ef",
                "id": "linec02d1e77e1076aa9c7c2c57238e4",
                "target": "node0863aab8325b84cfa3e5db52dc61"
            },
            "line7ed74aa679d19063b6d7037ce6db": {
                "is_default": false,
                "source": "node20cbeaa5379d08e8d8ed7bb44fdc",
                "id": "line7ed74aa679d19063b6d7037ce6db",
                "target": "node5310ec36c0364d3094d515f8f5ef"
            },
            "linec43c77f26af408748a9c194dbcfe": {
                "is_default": false,
                "source": "node7e97af0f55fb64276e067951dd9d",
                "id": "linec43c77f26af408748a9c194dbcfe",
                "target": "nodedb1478a75c13f90cc400f5379949"
            }
        },
        "gateways": {
            "node2b6f3285cfb3961c72834bafbe1b": {
                "incoming": ["linef0deadac69f769440a1b0e32587e", "lineabc279d9be88eb98285132ba5b75"],
                "outgoing": "line6ea858554964a04d868cead4435a",
                "type": "ConvergeGateway",
                "id": "node2b6f3285cfb3961c72834bafbe1b",
                "name": ""
            },
            "node0863aab8325b84cfa3e5db52dc61": {
                "outgoing": ["line7587c8804d34a091dae3d321f081", "line9dd9c8dbbad90943f268442ab7e0"],
                "incoming": "linec02d1e77e1076aa9c7c2c57238e4",
                "name": "",
                "type": "ExclusiveGateway",
                "conditions": {
                    "line9dd9c8dbbad90943f268442ab7e0": {
                        "evaluate": "${bk_timing} <= 10"
                    },
                    "line7587c8804d34a091dae3d321f081": {
                        "evaluate": "${bk_timing} > 10"
                    }
                },
                "id": "node0863aab8325b84cfa3e5db52dc61"
            },
            "node947e423b22e49aeb77bc77528bc0": {
                "incoming": ["linebf8f91c96a8f4eb3794ca5eb9881", "line24d28a3f9f80e23e4a4fab7c4ffd"],
                "outgoing": "lineabc279d9be88eb98285132ba5b75",
                "type": "ConvergeGateway",
                "id": "node947e423b22e49aeb77bc77528bc0",
                "name": ""
            },
            "node7e97af0f55fb64276e067951dd9d": {
                "incoming": "line9dd9c8dbbad90943f268442ab7e0",
                "outgoing": ["line429f64cdec5d20f368611e621ef5", "linec43c77f26af408748a9c194dbcfe"],
                "type": "ParallelGateway",
                "id": "node7e97af0f55fb64276e067951dd9d",
                "name": ""
            }
        },
        "constants": {
            "${bk_timing}": {
                "source_tag": "sleep_timer.bk_timing",
                "source_info": {
                    "node5310ec36c0364d3094d515f8f5ef": ["bk_timing"],
                    "node2bf42efcebe266706c3e21326dc4": ["bk_timing"],
                    "nodedb1478a75c13f90cc400f5379949": ["bk_timing"]
                },
                "name": "timing",
                "index": 0,
                "custom_type": "",
                "value": "1",
                "show_type": "show",
                "source_type": "component_inputs",
                "key": "${bk_timing}",
                "desc": ""
            }
        },
        "outputs": ["${bk_timing}"]
	}
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
            "start_event": {
                "incoming": "",
                "outgoing": "line7ed74aa679d19063b6d7037ce6db",
                "type": "EmptyStartEvent",
                "id": "node20cbeaa5379d08e8d8ed7bb44fdc",
                "name": ""
            },
            "activities": {
                "node5310ec36c0364d3094d515f8f5ef": {
                    "outgoing": "linec02d1e77e1076aa9c7c2c57238e4",
                    "incoming": "line7ed74aa679d19063b6d7037ce6db",
                    "name": "node1",
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
                    "stage_name": "stage1",
                    "retryable": true,
                    "skippable": true,
                    "type": "ServiceActivity",
                    "id": "node5310ec36c0364d3094d515f8f5ef"
                },
                "node2bf42efcebe266706c3e21326dc4": {
                    "outgoing": "linef0deadac69f769440a1b0e32587e",
                    "incoming": "line7587c8804d34a091dae3d321f081",
                    "name": "node2",
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
                    "stage_name": "stage2",
                    "retryable": true,
                    "skippable": true,
                    "type": "ServiceActivity",
                    "id": "node2bf42efcebe266706c3e21326dc4"
                },
                "node3c7dcf31454c1e9bdc9cf1cdeacc": {
                    "outgoing": "linebf8f91c96a8f4eb3794ca5eb9881",
                    "incoming": "line429f64cdec5d20f368611e621ef5",
                    "name": "node3",
                    "error_ignorable": false,
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {
                                "hook": false,
                                "value": "3"
                            }
                        }
                    },
                    "stage_name": "stage3",
                    "retryable": true,
                    "skippable": true,
                    "type": "ServiceActivity",
                    "id": "node3c7dcf31454c1e9bdc9cf1cdeacc"
                },
                "nodedb1478a75c13f90cc400f5379949": {
                    "outgoing": "line24d28a3f9f80e23e4a4fab7c4ffd",
                    "incoming": "linec43c77f26af408748a9c194dbcfe",
                    "name": "node4",
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
                    "stage_name": "stage3",
                    "retryable": true,
                    "skippable": true,
                    "type": "ServiceActivity",
                    "id": "nodedb1478a75c13f90cc400f5379949"
                }
            },
            "end_event": {
                "incoming": "line6ea858554964a04d868cead4435a",
                "outgoing": "",
                "type": "EmptyEndEvent",
                "id": "nodebe0db4ad30cc1723c7ede37b4b5f",
                "name": ""
            },
            "flows": {
                "line24d28a3f9f80e23e4a4fab7c4ffd": {
                    "is_default": false,
                    "source": "nodedb1478a75c13f90cc400f5379949",
                    "id": "line24d28a3f9f80e23e4a4fab7c4ffd",
                    "target": "node947e423b22e49aeb77bc77528bc0"
                },
                "linebf8f91c96a8f4eb3794ca5eb9881": {
                    "is_default": false,
                    "source": "node3c7dcf31454c1e9bdc9cf1cdeacc",
                    "id": "linebf8f91c96a8f4eb3794ca5eb9881",
                    "target": "node947e423b22e49aeb77bc77528bc0"
                },
                "line7587c8804d34a091dae3d321f081": {
                    "is_default": false,
                    "source": "node0863aab8325b84cfa3e5db52dc61",
                    "id": "line7587c8804d34a091dae3d321f081",
                    "target": "node2bf42efcebe266706c3e21326dc4"
                },
                "line429f64cdec5d20f368611e621ef5": {
                    "is_default": false,
                    "source": "node7e97af0f55fb64276e067951dd9d",
                    "id": "line429f64cdec5d20f368611e621ef5",
                    "target": "node3c7dcf31454c1e9bdc9cf1cdeacc"
                },
                "line6ea858554964a04d868cead4435a": {
                    "is_default": false,
                    "source": "node2b6f3285cfb3961c72834bafbe1b",
                    "id": "line6ea858554964a04d868cead4435a",
                    "target": "nodebe0db4ad30cc1723c7ede37b4b5f"
                },
                "line9dd9c8dbbad90943f268442ab7e0": {
                    "is_default": false,
                    "source": "node0863aab8325b84cfa3e5db52dc61",
                    "id": "line9dd9c8dbbad90943f268442ab7e0",
                    "target": "node7e97af0f55fb64276e067951dd9d"
                },
                "lineabc279d9be88eb98285132ba5b75": {
                    "is_default": false,
                    "source": "node947e423b22e49aeb77bc77528bc0",
                    "id": "lineabc279d9be88eb98285132ba5b75",
                    "target": "node2b6f3285cfb3961c72834bafbe1b"
                },
                "linef0deadac69f769440a1b0e32587e": {
                    "is_default": false,
                    "source": "node2bf42efcebe266706c3e21326dc4",
                    "id": "linef0deadac69f769440a1b0e32587e",
                    "target": "node2b6f3285cfb3961c72834bafbe1b"
                },
                "linec02d1e77e1076aa9c7c2c57238e4": {
                    "is_default": false,
                    "source": "node5310ec36c0364d3094d515f8f5ef",
                    "id": "linec02d1e77e1076aa9c7c2c57238e4",
                    "target": "node0863aab8325b84cfa3e5db52dc61"
                },
                "line7ed74aa679d19063b6d7037ce6db": {
                    "is_default": false,
                    "source": "node20cbeaa5379d08e8d8ed7bb44fdc",
                    "id": "line7ed74aa679d19063b6d7037ce6db",
                    "target": "node5310ec36c0364d3094d515f8f5ef"
                },
                "linec43c77f26af408748a9c194dbcfe": {
                    "is_default": false,
                    "source": "node7e97af0f55fb64276e067951dd9d",
                    "id": "linec43c77f26af408748a9c194dbcfe",
                    "target": "nodedb1478a75c13f90cc400f5379949"
                }
            },
            "gateways": {
                "node2b6f3285cfb3961c72834bafbe1b": {
                    "incoming": ["linef0deadac69f769440a1b0e32587e", "lineabc279d9be88eb98285132ba5b75"],
                    "outgoing": "line6ea858554964a04d868cead4435a",
                    "type": "ConvergeGateway",
                    "id": "node2b6f3285cfb3961c72834bafbe1b",
                    "name": ""
                },
                "node0863aab8325b84cfa3e5db52dc61": {
                    "outgoing": ["line7587c8804d34a091dae3d321f081", "line9dd9c8dbbad90943f268442ab7e0"],
                    "incoming": "linec02d1e77e1076aa9c7c2c57238e4",
                    "name": "",
                    "type": "ExclusiveGateway",
                    "conditions": {
                        "line9dd9c8dbbad90943f268442ab7e0": {
                            "evaluate": "${bk_timing} <= 10"
                        },
                        "line7587c8804d34a091dae3d321f081": {
                            "evaluate": "${bk_timing} > 10"
                        }
                    },
                    "id": "node0863aab8325b84cfa3e5db52dc61"
                },
                "node947e423b22e49aeb77bc77528bc0": {
                    "incoming": ["linebf8f91c96a8f4eb3794ca5eb9881", "line24d28a3f9f80e23e4a4fab7c4ffd"],
                    "outgoing": "lineabc279d9be88eb98285132ba5b75",
                    "type": "ConvergeGateway",
                    "id": "node947e423b22e49aeb77bc77528bc0",
                    "name": ""
                },
                "node7e97af0f55fb64276e067951dd9d": {
                    "incoming": "line9dd9c8dbbad90943f268442ab7e0",
                    "outgoing": ["line429f64cdec5d20f368611e621ef5", "linec43c77f26af408748a9c194dbcfe"],
                    "type": "ParallelGateway",
                    "id": "node7e97af0f55fb64276e067951dd9d",
                    "name": ""
                }
            },
            "constants": {
                "${bk_timing}": {
                    "source_tag": "sleep_timer.bk_timing",
                    "source_info": {
                        "node5310ec36c0364d3094d515f8f5ef": ["bk_timing"],
                        "node2bf42efcebe266706c3e21326dc4": ["bk_timing"],
                        "nodedb1478a75c13f90cc400f5379949": ["bk_timing"]
                    },
                    "name": "timing",
                    "index": 0,
                    "custom_type": "",
                    "value": "1",
                    "show_type": "show",
                    "source_type": "component_inputs",
                    "key": "${bk_timing}",
                    "desc": ""
                }
            },
            "outputs": ["${bk_timing}"]
        }
    },
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|------------|-----------|------------------|
|  result    | bool      | true or false, indicate success or failure |
|  data      | dict      | data returned when result is true, details are described below |
|  message   | string    | error message returned when result is false |
|  request_id     |    string  | esb request id             |
|  trace_id     |    string  | open telemetry trace_id        |

####  data

| Field      | Type      | Description      |
|------------|-----------|------------------|
| task_id    |    int    | the task instance ID |
| task_url   |    string | task instance url |
| pipeline_tree | dict   | task pipeline tree |

#### data.pipeline_tree

A task instance tree with all node IDs replaced with unique IDs, format is same with input param pipeline_tree
