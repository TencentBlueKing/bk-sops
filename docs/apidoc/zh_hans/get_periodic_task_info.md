### 功能描述

查询某个周期任务的详情

### 请求参数

#### 通用参数

|   字段           |  类型       | 必选     |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   是    |  应用ID |
|   bk_app_secret |   string    |   是    |  安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
|   bk_token      |   string    |   否    |  当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取  |
|   bk_username   |   string    |   否    |  当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户              |

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   task_id    |   string     |   是   |  周期任务ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "task_id": "8"
}
```

### 返回结果示例

```
{
    "message": "",
    "data": {
        "cron": "1,2,3-19/2 2 3 4 5 (m/h/d/dM/MY)",
        "total_run_count": 0,
        "name": "定时2",
        "form": {
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
                    "name": "暂停",
                    "error_ignorable": false,
                    "component": {
                        "code": "pause_node",
                        "data": {}
                    },
                    "stage_name": "步骤1",
                    "optional": false,
                    "type": "ServiceActivity",
                    "id": "nodea5c396a3ef0f9f3cd7d4d7695f78",
                    "loop": {}
                },
                "node76393dcfedcf73dbc726f1c4786d": {
                    "outgoing": "linecf7b7f10c87187a88b72c5f91177",
                    "incoming": "linecd597f19606c1455d661f71a582d",
                    "name": "定时",
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
                    "stage_name": "步骤1",
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
                    "name": "定时时间",
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
                    "stage_name": "步骤1",
                    "name": "暂停",
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
                    "stage_name": "步骤1",
                    "name": "定时",
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

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

#### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  cron      |    string    |      周期调度表达式    |
|  total_run_count      |    int    |    周期任务运行次数   |
|  name      |    string    |    周期任务名   |
|  creator      |    string    |    创建者   |
|  last_run_at      |    string    |    上次运行时间   |
|  enabled      |    bool    |    是否激活   |
|  id      |    int    |    周期任务 ID   |
|  template_id      |    string    |    用于创建该任务的模板 ID   |
|  form      |    dict    |    该周期任务的参数表单对象   |
|  pipeline_tree      |    dict    |    该周期任务的实例树   |

#### data.pipeline_tree
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  start_event      |    dict    |      开始节点信息     |
|  end_event      |    dict    |      结束节点信息    |
|  activities      |    dict    |      任务节点（标准插件和子流程）信息    |
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
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs/component_outputs 时有效，变量的来源标准插件   |
|  source_info   |   dict  |  source_type=component_inputs/component_outputs 时有效，变量的来源节点信息 |
