### 功能描述

查询公共流程模板详情

### 请求参数

#### 通用参数

|   字段           |  类型       | 必选     |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   是    |  应用ID |
|   bk_app_secret |   string    |   是    |  安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
|   bk_token      |   string    |   否    |  当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取  |
|   bk_username   |   string    |   否    |  当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户              |

#### 接口参数

| 字段          |  类型       | 必选   |  描述          |
|---------------|------------|--------|---------------|
| template_id   | string     |   是   |  模板ID        |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "template_id": "30",
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "category": "Other",
        "edit_time": "2018-04-27 16:24:24 +0800",
        "create_time": "2018-04-16 21:43:15 +0800",
        "name": "new20180416213944",
        "creator": "admin",
        "pipeline_tree": {
            "activities": {
                "631b6576cc5dfbdcaa4f510ce88a7e67": {
                    "outgoing": "44ab36ebf4cf119edaf2d20401da87e4",
                    "incoming": "fb2f3a8b533ca5c67e2440b4164f7632",
                    "name": "节点_1",
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
                    "name": "脚本类型",
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
                    "name": "内容",
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
                    "name": "超时时间",
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
                    "name": "参数",
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
        "id": 30,
        "editor": "admin"
    },
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
| result    | bool     | true/false 查询成功与否 |
| data      | dict     | result=true 时模板详情，详细信息见下面说明 |
| message   | string   | result=false 时错误信息 |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  id            |    int       |      模板ID             |
|  name          |    string    |      模板名称            |
|  category      |    string    |      模板分类，分类信息见下面说明    |
|  creator       |    string    |      模板创建人             |
|  create_time   |    string    |      模板创建时间           |
|  editor        |    string 或者 null    |      模板编辑人   |
|  edit_time     |    string    |      模板最新编辑时间        |
|  pipeline_tree |    dict      |      模板任务树信息，详细信息见下面说明   |

#### data.category

| 返回值        | 描述     |
|--------------|----------|
| OpsTools     | 运维工具  |
| MonitorAlarm | 监控告警  |
| ConfManage   | 配置管理  |
| DevTools     | 开发工具  |
| EnterpriseIT | 企业IT   |
| OfficeApp    | 办公应用  |
| Other        | 其它     |

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

#### data.pipeline_tree.constants.KEY

全局变量 KEY，${key} 格式

#### data.pipeline_tree.constants.VALUE

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type  | string   |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选   |
|  custom_type  | string   |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag   | string   |      source_type=component_inputs或component_outputs 时有效，变量的来源标准插件   |
|   source_info | dict    |  source_type=component_inputs或component_outputs 时有效，变量的来源节点信息  |
