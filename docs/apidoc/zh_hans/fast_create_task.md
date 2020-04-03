### 功能描述

创建一次性任务

### 请求参数

{{ common_args_desc }}

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   project_id  |   int      |   是   |  项目ID           |
|   name        |   string   |   是   |  任务名称         |
|   pipeline_tree | dict     |   是   |  任务实例树，详细信息请见下面说明 |
|   flow_type   |   string   |   否   |  任务流程类型，common: 常规流程，common_func：职能化流程，默认值为common |
|   description |   string   |   否   |  任务描述         |
|   category    |   string   |   否   |  任务分类，详细信息请见下面说明 |

#### category

| 值           | 描述     |
|--------------|----------|
| OpsTools     | 运维工具  |
| MonitorAlarm | 监控告警  |
| ConfManage   | 配置管理  |
| DevTools     | 开发工具  |
| EnterpriseIT | 企业IT   |
| OfficeApp    | 办公应用  |
| Other        | 其它     |

#### pipeline_tree

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|--------|-----------|
|  start_event | dict  | 是     |  开始节点，详细信息请见下面说明 |
|  end_event   | dict  | 是     |  结束节点，详细信息请见下面说明 |
|  activities  | dict  | 是     |  任务节点（标准插件和子流程），详细信息请见下面说明 |
|  flows       | dict  | 是     |  顺序流（节点连线），详细信息请见下面说明 |
|  gateways    | dict  | 否     |  网关节点（并行网关、分支网关和汇聚网关），详细信息请见下面说明 |
|  constants   | dict  | 否     |  全局变量，详细信息请见下面说明    |
|  outputs     | list  | 否     |  输出参数，标记 constants 中的输出字段    |

#### pipeline_tree.start_event

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  id       |  string  | 是    | 开始节点 ID，在 pipeline_tree 所有ID中全局唯一 |
|  type     |  string  | 是    | 开始节点类型，当前只支持 EmptyStartEvent: 空开始类 |
|  name     |  string  | 是    | 开始节点名称，可为空 |
|  incoming |  string  | 是    | 入度顺序流 ID，必须为空字符串    |
|  outgoing |  string  | 是    | 出度顺序流 ID    |

#### pipeline_tree.end_event

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  id       |  string  | 是    | 结束节点 ID，在 pipeline_tree 所有ID中全局唯一 |
|  type     |  string  | 是    | 结束节点类型，当前只支持 EmptyEndEvent：空结束类 |
|  name     |  string  | 是    | 结束节点名称，可为空 |
|  incoming |  string  | 是    | 入度顺序流 ID    |
|  outgoing |  string  | 是    | 出度顺序流 ID，必须为空字符串    |

#### pipeline_tree.activities KEY、pipeline_tree.flows KEY、pipeline_tree.gateways KEY

流程元素 ID，string 类型，在 pipeline_tree 所有 ID 中全局唯一，用来标识拓扑关系

#### pipeline_tree.activities VALUE

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  id       |  string  | 是    | 任务节点 ID，同 KEY 一致 |
|  type     |  string  | 是    | 任务节点类型，当前只支持 ServiceActivity：标准插件节点 |
|  name     |  string  | 是    | 任务节点名称 |
|  component |  dict   | 是    | 插件配置，详细信息请见下面说明 |
|  error_ignorable | bool | 是 | 节点失败是否自动忽略 |
|  retryable |  bool   | 是    | 节点失败后是否可以重试，error_ignorable 为 true 时该参数无效 |
|  skippable |  bool   | 是    | 节点失败后是否可以跳过，error_ignorable 为 true 时该参数无效 |
|  incoming |  string  | 是    | 入度顺序流 ID |
|  outgoing |  string  | 是    | 出度顺序流 ID |
|  stage_name | string | 否    | 步骤分组名称 |

#### pipeline_tree.activities VALUE.component

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  code     |  string  | 是    | 标准插件编码 |
|  data     |  dict    | 是    | 标准插件输入参数 |

#### pipeline_tree.flows VALUE

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
| id        |  string  | 是    | 顺序流 ID，同 KEY 一致 |
| is_default|  bool    | 是    | 是否默认分支 |
| source    |  string  | 是    | 来源节点 ID |
| target    |  string  | 是    | 目的节点 ID |

#### pipeline_tree.gateways VALUE

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  id       |  string  | 是    | 网关节点 ID，同 KEY 一致 |
|  type     |  string  | 是    | 网关类型，ParallelGateway：并行网关，ExclusiveGateway：分支网关，ConvergeGateway：汇聚网关|
|  name     |  string  | 是    | 网关节点名称，可为空 |
|  incoming |  string/list| 是 | 入度顺序流 ID，type 为 ConvergeGateway 时是 list，否则是 string|
|  outgoing |  string/list| 是 | 出度顺序流 ID，type 为 ConvergeGateway 时是 string，否则是 list |
|  conditions | dict   | 否    | 分支条件，type 为 ExclusiveGateway 必填， 详细信息请见下面说明 |

#### pipeline_tree.gateways VALUE.conditions KEY

网关出度顺序流 ID，和 outgoing 列表中一一对应

#### pipeline_tree.gateways VALUE.conditions VALUE

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
| evaluate  |  string  | 是    | 分支表达式，支持的语法请参考产品白皮书等文档 |

#### pipeline_tree.constants KEY

全局变量 KEY，"${key}" 格式

#### pipeline_tree.constants VALUE

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  key      |    string | 是    | 同 KEY 一致 |
|  name     |    string | 是    | 变量名字    |
|  index    |    int    | 是    | 变量在任务中的显示顺序    |
|  desc     |    string | 是    | 变量说明   |
|  source_type | string | 是    | 变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选 |
|  custom_type | string | 是    | source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数 |
|  source_tag  | string | 是    | source_type=component_inputs 或 component_outputs 时有效，变量的来源插件和 Tag   |
|  source_info | dict   | 是    | source_type=component_inputs 或 component_outputs 时有效，变量的来源节点信息   |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "name": "tasktest",
    "flow_type": "common",
    "pipeline_tree"：{
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

### 返回结果示例

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
    }
}
```

### 返回结果参数说明

| 字段      | 类型      | 说明      |
|-----------|----------|-----------|
|  result   |  bool    | true/false 操作是否成功     |
|  data     |  dict    | result=true 时成功数据，详细信息请见下面说明      |
|  message  |  string  | result=false 时错误信息     |

####  data

| 字段      | 类型      | 说明      |
|-----------|----------|-----------|
|  task_id  | int      | 任务实例ID |
|  task_url | string   | 任务实例链接 |
|  pipeline_tree | dict | 任务实例树  |

#### data.pipeline_tree

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  start_event      |    dict    |      开始节点信息     |
|  end_event      |    dict    |      结束节点信息    |
|  activities      |    dict    |      任务节点（原子和子流程）信息    |
|  gateways      |    dict    |      网关节点（并行网关、分支网关和汇聚网关）信息    |
|  flows      |    dict    |     顺序流（节点连线）信息    |
|  constants      |    dict    |  全局变量信息，详情见下面    |
|  outputs      |    list    |  模板输出信息，标记 constants 中的输出字段    |

#### data.form.KEY, data.pipeline_tree.constants.KEY

全局变量 KEY，${key} 格式

#### data.form.VALUE, data.pipeline_tree.constants.VALUE

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从原子输入参数勾选，component_outputs：从原子输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs/component_outputs 时有效，变量的来源原子   |
|  source_info   |   dict  |  source_type=component_inputs/component_outputs 时有效，变量的来源节点信息 |
