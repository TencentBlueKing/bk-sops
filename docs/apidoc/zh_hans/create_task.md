### 功能描述

通过流程模板创建任务

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   template_id     |   string     |   是   |  模板ID |
|   template_source | string   | 否         | 流程模板来源，business:默认值，业务流程，common：公共流程 |
|   name     |   string     |   是   |  任务名称 |
|   flow_type     |   string     |   否   |  任务流程类型，common: 常规流程，common_func：职能化流程 |
|   constants     |   dict     |   否   |  任务全局参数，详细信息见下面说明 |
|   exclude_task_nodes_id | list |   否   | 跳过执行的节点ID列表（与execute_task_nodes_id同时存在时execute_task_nodes_id优先） |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|
|   simplify_vars     |   list     |   否   |  需要进行类型简化的参数 key 列表。（类型简化后的参数在创建任务后会丢失模板中原本配置的类型，全部变成本文框类型的变量，通过使用这个选项能够在 API 调用时屏蔽不同类型变量 value 格式的差异，统一通过文本类型传递 value） |
| execute_task_nodes_id | list | 否 | 仅执行的节点ID列表（与exclude_task_nodes_id同时存在时execute_task_nodes_id优先） |

#### constants KEY

变量 KEY，${key} 格式

#### constants VALUE

变量值，value 的类型和从模板获取的全局变量中 value 类型保持一致

### 请求参数示例

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

### 返回结果示例

```
{
    "result": true,
    "data": {
        "task_id": 10,
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
                    "stage_name": "步骤1",
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
                    "name": "暂停",
                    "error_ignorable": false,
                    "component": {
                        "code": "pause_node",
                        "data": {}
                    },
                    "stage_name": "步骤1",
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
                    "stage_name": "步骤1",
                    "name": "暂停",
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
                    "stage_name": "步骤1",
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

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时成功数据，详细信息请见下面说明      |
|  message     |    string  |      result=false 时错误信息     |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  task_id      |    int    |      任务实例ID     |
|  task_url     |    str     |    任务实例链接     |
|  pipeline_tree     |    dict     |    任务实例树     |

#### data.pipeline_tree

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  start_event      |    dict    |      开始节点信息     |
|  end_event      |    dict    |      结束节点信息    |
|  activities      |    dict    |      任务节点（标准插件和子流程）信息    |
|  gateways      |    dict    |      网关节点（并行网关、分支网关和汇聚网关）信息    |
|  flows      |    dict    |     顺序流（节点连线）信息    |
|  constants      |    dict    |  全局变量信息，详情见下面    |
|  outputs      |    list    |  模板输出信息，标记 constants 中的输出字段    |

#### data.pipeline_tree.constants KEY

全局变量 KEY，${key} 格式

#### data.pipeline_tree.constants VALUE

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs/component_outputs 时有效，变量的来源标准插件   |
|  source_info   |   dict  |  source_type=component_inputs/component_outputs 时有效，变量的来源节点信息 |
