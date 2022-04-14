### 功能描述

通过流程模板创建并开始执行任务

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
|   exclude_task_nodes_id | list |   否   |  跳过执行的节点ID列表 |
| description           | string | 否   | pipeline_instance的描述信息                               |

#### constants KEY

变量 KEY，${key} 格式

#### constants VALUE

变量值，value 的类型和从模板获取的全局变量中 value 类型保持一致

### 请求参数示例

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

### 返回结果示例

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

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时成功数据，详细信息请见下面说明      |
|  message     |    string  |      result=false 时错误信息     |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

####  data

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
