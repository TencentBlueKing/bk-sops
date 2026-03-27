### 功能描述

查询任务执行详情

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述            |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string   |   是   |  所属业务ID   |
|   task_id     |   string   |   是   |  任务ID     |
| include_edit_info | bool | 否 | 是否包含任务更新信息，默认 false |
| include_webhook_history | bool | 否 | 是否包含 webhook 回调信息，默认 false |
| include_children_status | bool | 否 | 是否包含任务节点状态，默认 false |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|
| include_pipeline_tree | bool | 否 | MCP 请求时是否返回精简后的 pipeline_tree，默认 false。非 MCP 请求忽略此参数 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "data": {
        "name": "xxx",
        "creator": "admin",
        "outputs": [
            {
                "value": "1",
                "key": "${job_script_type}",
                "name": "脚本类型"
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
        "project_id": 2,
        "create_time": "2019-01-17 04:13:03",
        "project_name": "蓝鲸",
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
                "name": "脚本类型",
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
        "finish_time":"",
        "instance_name": "job输出变量测试_20190117121300",
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
            "constants": {},
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
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    dict    |      result=true 时返回数据，详细信息见下面说明     |
|  message  |    string  |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

### MCP 请求说明

当请求来源于网关MCP时，部分字段会在响应中被过滤或精简：

- `data.pipeline_tree` - 默认不返回；传入 `include_pipeline_tree=true` 时返回精简版本（移除前端渲染、画布布局等冗余信息，仅保留语义信息）
- `data.task_webhook_history` - 不返回