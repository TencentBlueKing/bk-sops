### 请求地址

/v2/sops/preview_common_task_tree/

### 请求方法

POST

### 功能描述

获取节点选择后新的任务树（针对公共流程）

#### 通用参数

|   字段           |  类型       | 必选     |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   是    |  应用ID |
|   bk_app_secret |   string    |   是    |  安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
|   bk_token      |   string    |   否    |  当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取  |
|   bk_username   |   string    |   否    |  当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户              |

#### 接口参数

| 字段          | 类型     | 必选   |  描述             |
|-----------------|--------|---------|------------------|
|   bk_biz_id       | string |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   template_id       | int    |   是   |  模板 ID |
|   scope       | string |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
|   version | string |   否   |  模板的版本，不填时默认为最新版本 |
|   exclude_task_nodes_id   | list   |   否   |  需要移除的可选节点 ID 列表，不填时默认为 [] |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_token": "bk_username",
    "bk_biz_id": "2",
    "template_id": "10001",
    "scope": "cmdb_biz",
    "version": "xxx",
    "exclude_task_nodes_id": [1, 2, 3]
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "pipeline_tree": {
            "activities": {
                "node7082deed0725aed8c72ecff079ba": {
                    "component": {
                        "code": "pause_node",
                        "data": {},
                        "version": "legacy"
                    },
                    "error_ignorable": false,
                    "id": "node7082deed0725aed8c72ecff079ba",
                    "incoming": [
                        "lineda60368b01cd8828a72585115f88"
                    ],
                    "loop": null,
                    "name": "暂停",
                    "optional": true,
                    "outgoing": "line4598d41ef39573f7d7493f934bd8",
                    "stage_name": "步骤1",
                    "type": "ServiceActivity",
                    "retryable": true,
                    "skippable": true
                },
                "node88d9050f288765b94a15cbe023ab": {
                    "component": {
                        "code": "pause_node",
                        "data": {},
                        "version": "legacy"
                    },
                    "error_ignorable": false,
                    "id": "node88d9050f288765b94a15cbe023ab",
                    "incoming": [
                        "line4598d41ef39573f7d7493f934bd8"
                    ],
                    "loop": null,
                    "name": "暂停",
                    "optional": true,
                    "outgoing": "line9c757e214b4f2ff64437653b8408",
                    "stage_name": "步骤1",
                    "type": "ServiceActivity",
                    "retryable": true,
                    "skippable": true
                }
            },
            "constants": {},
            "end_event": {
                "id": "node253645bb6f162119e55b7352d8b2",
                "incoming": [
                    "line9c757e214b4f2ff64437653b8408"
                ],
                "name": "",
                "outgoing": "",
                "type": "EmptyEndEvent"
            },
            "flows": {
                "lineda60368b01cd8828a72585115f88": {
                    "id": "lineda60368b01cd8828a72585115f88",
                    "is_default": false,
                    "source": "nodeb9a3a2a32bb4cfe8761377b2270f",
                    "target": "node7082deed0725aed8c72ecff079ba"
                },
                "line4598d41ef39573f7d7493f934bd8": {
                    "id": "line4598d41ef39573f7d7493f934bd8",
                    "is_default": false,
                    "source": "node7082deed0725aed8c72ecff079ba",
                    "target": "node88d9050f288765b94a15cbe023ab"
                },
                "line9c757e214b4f2ff64437653b8408": {
                    "id": "line9c757e214b4f2ff64437653b8408",
                    "is_default": false,
                    "source": "node88d9050f288765b94a15cbe023ab",
                    "target": "node253645bb6f162119e55b7352d8b2"
                }
            },
            "gateways": {},
            "line": [
                {
                    "id": "lineda60368b01cd8828a72585115f88",
                    "source": {
                        "arrow": "Right",
                        "id": "nodeb9a3a2a32bb4cfe8761377b2270f"
                    },
                    "target": {
                        "arrow": "Left",
                        "id": "node7082deed0725aed8c72ecff079ba"
                    }
                },
                {
                    "source": {
                        "arrow": "Right",
                        "id": "node7082deed0725aed8c72ecff079ba"
                    },
                    "target": {
                        "id": "node88d9050f288765b94a15cbe023ab",
                        "arrow": "Left"
                    },
                    "id": "line4598d41ef39573f7d7493f934bd8"
                },
                {
                    "source": {
                        "arrow": "Right",
                        "id": "node88d9050f288765b94a15cbe023ab"
                    },
                    "target": {
                        "id": "node253645bb6f162119e55b7352d8b2",
                        "arrow": "Left"
                    },
                    "id": "line9c757e214b4f2ff64437653b8408"
                }
            ],
            "location": [
                {
                    "id": "nodeb9a3a2a32bb4cfe8761377b2270f",
                    "type": "startpoint",
                    "x": 80,
                    "y": 150
                },
                {
                    "id": "node7082deed0725aed8c72ecff079ba",
                    "type": "tasknode",
                    "name": "暂停",
                    "stage_name": "步骤1",
                    "x": 300,
                    "y": 150,
                    "group": "蓝鲸服务(BK)",
                    "icon": ""
                },
                {
                    "id": "node253645bb6f162119e55b7352d8b2",
                    "type": "endpoint",
                    "x": 820,
                    "y": 150
                },
                {
                    "id": "node88d9050f288765b94a15cbe023ab",
                    "type": "tasknode",
                    "name": "暂停",
                    "stage_name": "步骤1",
                    "x": 500,
                    "y": 150,
                    "group": "蓝鲸服务(BK)",
                    "icon": ""
                }
            ],
            "outputs": [],
            "start_event": {
                "id": "nodeb9a3a2a32bb4cfe8761377b2270f",
                "incoming": "",
                "name": "",
                "outgoing": "lineda60368b01cd8828a72585115f88",
                "type": "EmptyStartEvent"
            }
        },
        "constants_not_referred": {}
    },
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | dict       | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  pipeline_tree      |    dict   |      模板任务树信息，详细信息见下面说明   |
|  constants_not_referred | dict | 流程模板中未引用的全局变量，数据结构同pepeline[constants] |

##### data.pipeline_tree
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  start_event      |    dict    |      开始节点信息     |
|  end_event      |    dict    |      结束节点信息    |
|  activities      |    dict    |      任务节点（原子和子流程）信息    |
|  gateways      |    dict    |      网关节点（并行网关、分支网关和汇聚网关）信息    |
|  flows      |    dict    |     顺序流（节点连线）信息    |
|  constants      |    dict    |  全局变量信息，详情见下面    |
|  outputs      |    list    |  模板输出信息，标记 constants 中的输出字段    |

###### data.pipeline_tree.constants.KEY

全局变量 KEY，${key} 格式

###### data.pipeline_tree.constants.VALUE

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从原子输入参数勾选，component_outputs：从原子输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs|component_outputs 时有效，变量的来源原子   |
|  source_info   |   dict  |  source_type=component_inputs|component_outputs 时有效，变量的来源节点信息
