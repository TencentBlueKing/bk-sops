### 功能描述

查询任务执行详情

### 请求参数

#### 通用参数

|   字段           |  类型       | 必选     |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   是    |  应用ID |
|   bk_app_secret |   string    |   是    |  安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
|   bk_token      |   string    |   否    |  当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取  |
|   bk_username   |   string    |   否    |  当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户              |

#### 接口参数

| 字段          |  类型       | 必选   |  描述            |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string   |   是   |  所属业务ID   |
|   task_id     |   string   |   是   |  任务ID     |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "task_id": "10"
}
```

### 返回结果示例

```
{
    "data": {
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
        "business_id": 2,
        "create_time": "2019-01-17 04:13:03",
        "business_name": "蓝鲸",
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
                    "name": "暂停",
                    "error_ignorable": false,
                    "component": {
                        "code": "pause_node",
                        "data": {}
                    },
                    "stage_name": "步骤1",
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
    "result": true
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    dict    |      result=true 时返回数据，详细信息见下面说明     |
|  message  |    string  |      result=false 时错误信息     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  id      |    int    |      任务 ID，即 task_id    |
|  name    |    string    |      任务名称               |
|  business_id      |  int       |  所属业务 ID    |
|  business_name    |  string    |  所属业务名称   |
|  template_id      |  int       |  创建任务所用的流程模板 ID    |
|  create_time      |  string    |  任务创建时间   |
|  create_method    |  string    |  任务创建方式   |
|  start_time       |  string    |  任务执行时间   |
|  finish_time      |  string    |  任务完成时间   |
|  elapsed_time     |  int       |  任务执行耗时(秒） |
|  creator          |  string    |  任务创建人     |
|  executor         |  string    |  任务执行人     |
|  constants        |  dict      |  输入的全局变量，详情见下面说明 |
|  outputs          |  list      |  任务输出参数，详情见下面说明 |
|  task_url     |    str     |    任务实例链接     |
|  pipeline_tree     |    dict     |    任务实例树     |

#### data.constants.KEY

全局变量 KEY，${key} 格式


#### data.constants.VALUE
|   字段   |  类型  |           描述             |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs/component_outputs 时有效，变量的来源标准插件   |
|  source_info   |   dict  |  source_type=component_inputs/component_outputs 时有效，变量的来源节点信息 |


#### data.outputs[] 
|      字段     |     类型   |               描述             |
| ------------  | ---------- | ------------------------------ |
|  name         | string     | 输出参数名称                   |
|  value        | string、int、bool、dict、list | 输出参数值  |
|  key          | string     | 输出参数 KEY                   |
|  preset       | bool       | 是否是标准插件定义中预设输出变量   |

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
