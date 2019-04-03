# API DOC

请通过 APIGW 或者 ESB 访问

## get_template_list

### 功能描述
查询业务下的模板列表

### 请求方法
GET

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  业务ID |
|   template_source | string   | 否         | 流程模板来源，business:默认值，业务流程，common：公共流程 |

### 返回结果说明
|      名称     |     类型   |               说明              |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 查询成功与否     |
|  data        |    list      |      result=true时模板列表，详细信息见下面说明     |
|  message      |    string    |    result=false时错误信息     |

#### data[] 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  bk_biz_id      |    string    |      业务ID     |
|  bk_biz_name      |    string    |      业务名称    |
|  id      |    int    |      模板ID    |
|  name      |    string    |      模板名称    |
|  category      |    string    |      模板分类，分类信息见下面说明    |
|  creator      |    string    |      模板创建人   |
|  create_time      |    string    |      模板创建时间   |
|  editor      |    string 或者 null    |      模板编辑人   |
|  edit_time      |    string   |      模板最新编辑时间   |

#### data[][category] 说明
```
CATEGORY = {
	"OpsTools": u"运维工具",
	"MonitorAlarm": u"监控告警",
	"ConfManage": u"配置管理",
	"DevTools": u"开发工具",
	"EnterpriseIT": u"企业IT",
	"OfficeApp": u"办公应用",
	"Other": u"其它",
}
```

### HTTP 请求调用示例
```python
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
}
response = requests.get("http://{stageVariables.domain}/apigw/get_template_list/2/", kwargs)
result = response.json()
```

### ESB SDK 调用示例
```python
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
}
# 路径参数
path_kwargs = {
	"bk_biz_id": "2"
}
result = client.api.api_test(kwargs, path_kwargs)
```

### 返回结果示例
```
{
	"result": true,
    "data": [
        {
            "category": "Other",
            "edit_time": "2018-04-23 17:30:48 +0800",
            "create_time": "2018-04-23 17:26:40 +0800",
            "name": "testname",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "blueking",
            "id": 32,
            "editor": "admin"
        },
        {
            "category": "Other",
            "edit_time": "2018-04-19 12:04:42 +0800",
            "create_time": "2018-04-19 12:04:42 +0800",
            "name": "new201804191218",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "blueking",
            "id": 31,
            "editor": null
        },
        {
            "category": "Other",
            "edit_time": "2018-04-18 17:09:39 +0800",
            "create_time": "2018-04-16 21:43:15 +0800",
            "name": "new20180416213944",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "blueking",
            "id": 30,
            "editor": "admin"
        },
	]
}
```

## get_template_info

### 功能描述
查询业务下的单个模板详情

### 请求方法
GET

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  业务ID |
|   template_id     |   string     |   是   |  模板ID |
|   template_source | string   | 否         | 流程模板来源，business:默认值，业务流程，common：公共流程 |

### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 查询成功与否     |
|  data        |    dict      |      result=true 时模板详情，详细信息见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

#### data 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  bk_biz_id      |    string    |      业务ID     |
|  bk_biz_name      |    string    |      业务名称    |
|  id      |    int    |      模板ID    |
|  name      |    string    |      模板名称    |
|  category      |    string    |      模板分类，分类信息见下面说明    |
|  creator      |    string    |      模板创建人   |
|  create_time      |    string    |      模板创建时间   |
|  editor      |    string 或者 null    |      模板编辑人   |
|  edit_time      |    string   |      模板最新编辑时间   |
|  pipeline_tree      |    dict   |      模板任务树信息，详细信息见下面说明   |

##### data[category] 说明
```
CATEGORY = {
	"OpsTools": u"运维工具",
	"MonitorAlarm": u"监控告警",
	"ConfManage": u"配置管理",
	"DevTools": u"开发工具",
	"EnterpriseIT": u"企业IT",
	"OfficeApp": u"办公应用",
	"Other": u"其它",
}
```

##### data[pipeline_tree] 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  start_event      |    dict    |      开始节点信息     |
|  end_event      |    dict    |      结束节点信息    |
|  activities      |    dict    |      任务节点（标准插件和子流程）信息    |
|  gateways      |    dict    |      网关节点（并行网关、分支网关和汇聚网关）信息    |
|  flows      |    dict    |     顺序流（节点连线）信息    |
|  constants      |    dict    |  全局变量信息，详情见下面    |
|  outputs      |    list    |  模板输出信息，标记 constants 中的输出字段    |

###### data[pipeline_tree][constants] 说明

KEY：
全局变量 KEY，${key} 格式

VALUE：

|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs|component_outputs 时有效，变量的来源标准插件   |
|  source_info   |   dict  |  source_type=component_inputs|component_outputs 时有效，变量的来源节点信息 |


### HTTP 请求调用示例
```python
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
}
response = requests.get("http://{stageVariables.domain}/apigw/get_template_list/30/1/", kwargs)
result = response.json()
```

### ESB SDK 调用示例
```python
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
}
# 路径参数
path_kwargs = {
	"bk_biz_id": "1",
	"template_id": "30",
}
result = client.api.api_test(kwargs, path_kwargs)
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
                    "name": "script type",
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
                    "name": "timeout",
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

## create_task

### 功能描述
通过流程模板创建任务

### 请求方法
POST

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  业务ID |
|   template_id     |   string     |   是   |  模板ID |
|   template_source | string   | 否         | 流程模板来源，business:默认值，业务流程，common：公共流程 |
|   name     |   string     |   是   |  任务名称 |
|   flow_type     |   string     |   否   |  任务流程类型，common: 常规流程，common_func：职能化流程 |
|   constants     |   dict     |   否   |  任务全局参数，详细信息见下面说明 |
|   exclude_task_nodes_id | list |   否   |  跳过执行的节点ID列表 |

##### constants 说明
KEY：变量 KEY，${key} 格式

VALUE：变量值，value 的类型和从模板获取的全局变量中 value 类型保持一致 


### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功返回数据，详细信息见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

#### data 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  task_id     |    int     |    任务实例 ID     |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
	"name": "tasktest",
	"flow_type": "common",
	"constants": {
		"${content}": "echo 1",
		"${params}": "",
		"${script_timeout}": 20
	}
}
response = requests.post("http://{stageVariables.domain}/apigw/create_task/10/2/", json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```python
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
	"name": "tasktest",
	"flow_type": "common",
	"constants": {
		"${content}": "echo 1",
		"${params}": "",
		"${script_timeout}": 20
	}
}
# 路径参数
path_kwargs = {
	"bk_biz_id": "1",
	"template_id": "30",
}
result = client.api.api_test(kwargs, path_kwargs)
```

### 返回结果示例
```
{
	"result": true,
    "data": {
        "task_id": 10
    }
}
```

## start_task

### 功能描述
开始执行任务

### 请求方法
POST

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   task_id      |   string     |   是   |  任务ID |


### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 任务是否执行     |
|  data        |    dict      |      result=true 时成功返回数据    |
|  message        |    string      |      result=false 时错误信息     |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
}
response = requests.post("http://{stageVariables.domain}/apigw/start_task/10/2/", json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```python
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
}
# 路径参数
path_kwargs = {
	"bk_biz_id": "2",
	"task_id": "10",
}
result = client.api.api_test(kwargs, path_kwargs)
```

### 返回结果示例
```
{
	"result": true,
    "data": "Success"
}
```

## operate_task

### 功能描述
操作任务，如开始、暂停、继续、终止等

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   task_id      |   string     |   是   |  任务ID |
|   action      |   string     |   是   |  操作类型 |

##### action 说明
```
CATEGORY = {
	"start": u"开始任务" # 等效于调用 start_task 接口
	"pause": u"暂停任务，任务处于执行状态时调用"
	"resume": u"继续任务，任务处于暂停状态时调用"
	"revoke": u"终止任务"
}
```

### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时返回数据     |
|  message        |    string      |      result=false 时错误信息     |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
	"action": "start"
}
response = requests.post("http://{stageVariables.domain}/apigw/operate_task/10/2/", json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```python
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
	"action": "start"
}
# 路径参数
path_kwargs = {
	"bk_biz_id": "2",
	"task_id": "10",
}
result = client.api.api_test(kwargs, path_kwargs)
```

### 返回结果示例
```
{
	"result": true,
    "data": "Success"
}
```

## get_task_status

### 功能描述
查询任务或任务节点执行状态

### 请求方法
GET

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   task_id     |   string     |   是   |  任务或节点ID  |

### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 查询成功与否     |
|  data        |    dict      |      result=true 时返回数据，详细信息见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

#### data 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  state      |    string    |      任务或节点状态，详细信息见下面说明    |
|  id      |    string    |      任务或节点执行态ID，不等于 task_id    |
|  skip      |    bool    |      是否跳过执行    |
|  retry      |    int    |      重试和跳过总次数   |
|  start_time      |    string    |      任务或节点执行开始时间   |
|  finish_time      |    string    |      任务或节点执行结束时间    |
|  children      |    dict   |      任务节点执行详情，详细信息见下面说明   |


##### data[state] 说明
```python
STATE = {
	"CREATED": u"未执行"
	"RUNNING": u"执行中"
	"FAILED": u"失败"
	"SUSPENDED": u"暂停"
	"REVOKED": u"已撤销"
	"FINISHED": u"已完成"
}
```

##### data[children] 说明

KEY：
任务节点 执行态ID

VALUE：
同 data 格式


### HTTP 请求调用示例
```python
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
}
response = requests.get("http://{stageVariables.domain}/apigw/get_task_status/10/2/", kwargs)
result = response.json()
```

### ESB SDK 调用示例
```python
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
}
# 路径参数
path_kwargs = {
	"bk_biz_id": "2",
	"task_id": "10",
}
result = client.api.get_task_status(kwargs, path_kwargs)
```

### 返回结果示例
```
{
	"result": true,
    "data": {
		"retry": 0,
		"name": "<class "pipeline.core.pipeline.Pipeline">",
		"finish_time": "",
		"skip": false,
		"start_time": "2018-04-26 16:08:34 +0800",
		"children": {
			"62d4784e20483f1585149ce90ed954c9": {
				"retry": 0,
				"name": "<class "pipeline.core.flow.event.EmptyStartEvent">",
				"finish_time": "2018-04-26 16:08:34 +0800",
				"skip": false,
				"start_time": "2018-04-26 16:08:34 +0800",
				"children": {},
				"state": "FINISHED",
				"version": "7447cc2801b630f497768493c02fb488",
				"id": "62d4784e20483f1585149ce90ed954c9",
				"loop": 1
			},
			"e8b128dff46637368b9b1bd921abc14e": {
				"retry": 0,
				"name": "<class "pipeline.core.flow.activity.ServiceActivity">",
				"finish_time": "2018-04-26 16:08:46 +0800",
				"skip": false,
				"start_time": "2018-04-26 16:08:34 +0800",
				"children": {},
				"state": "FAILED",
				"version": "914d35fe7d143c2186e6d3532870b37d",
				"id": "e8b128dff46637368b9b1bd921abc14e",
				"loop": 1
			}
		},
		"state": "FAILED",
		"version": "",
		"id": "5a1622f9f43e3429acb604e18dbd100a",
		"loop": 1
	}
}
```


## get_task_detail

### 资源描述
查询任务执行详情

### 输入参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务 ID |
|   task_id     |   string     |   是   |  任务 ID  |

### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 查询成功与否   |
|  data        |    dict    |      result=true 时返回数据，详细信息见下面说明 |
|  message     |    string  |      result=false 时错误信息   |

#### data 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
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

###### data[constants] 说明
KEY：  
全局变量 KEY，${key} 格式

VALUE：  
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs/component_outputs 时有效，变量的来源标准插件   |
|  source_info   |   dict  |  source_type=component_inputs/component_outputs 时有效，变量的来源节点信息 |

###### data[outputs][] 说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  name         | string     | 输出字段                   |
|  value        | string、int、bool、dict、list | 输出参数值  |
|  key          | string     | 输出参数 KEY                   |
|  preset       | bool       | 是否是标准插件定义中预设输出变量   |


### HTTP 请求调用示例
```python
import requests
kwargs = {
  "app_code": "app_code",
  "app_secret": "app_secret",
  "access_token": "access_token",
}
response = requests.get("http://{stageVariables.domain}/apigw/get_task_detail/10/2/", kwargs)
result = response.json()
```

### ESB SDK 调用示例
```python
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
}
# 路径参数
path_kwargs = {
  "bk_biz_id": "2",
  "task_id": "10",
}
result = client.api.get_task_detail(kwargs, path_kwargs)
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
        "template_id": "266"
    },
    "result": true
}
```


## get_task_node_detail

### 资源描述
查询任务节点执行详情

### 输入参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id     |   string   |   是   |  任务ID     |
|   act_id        | string     | 是         | 节点 ID                        |
|   component_code| string     | 否         | 标准插件编码，请求标准插件执行详情必填 |
|   subprocess_stack| string   | 否         | 子流程堆栈，json 格式的列表    |

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | dict       | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |

#### data说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  id           | string     | 节点 ID                        |
|  start_time   | string     | 最后一次执行开始时间           |
|  finish_time  | string     | 最后一次执行结束时间           |
|  elapsed_time | int        | 最后一次执行耗时，单位秒       |
|  state        | string     | 最后一次执行状态，CREATED：未执行，RUNNING：执行中，FAILED：失败，NODE_SUSPENDED：暂停，SUSPENDED：成功 |
|  skip         | bool       | 是否手动跳过                   |
|  retry        | int        | 重试次数                       |
|  inputs       | dict       | 输入参数，key：value格式       |
|  outputs      | list       | 输出参数，详情见下面说明       |
|  ex_data      | string     | 节点执行失败详情，json字符串或者HTML字符串、普通字符串 |
|  histories    | list       | 重试记录详情，详情见下面说明   |

##### outputs[]说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  name         | string     | 输出字段                   |
|  value        | string、int、bool、dict、list | 输出参数值  |
|  key          | string     | 输出参数 KEY                   |
|  preset       | bool       | 是否是标准插件定义中预设输出变量   |


##### histories[]说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  start_time   | string     | 执行开始时间                   |
|  finish_time  | string     | 执行结束时间                   |
|  elapsed_time | int        | 执行耗时                       |
|  state        | string     | 执行状态，CREATED：未执行，RUNNING：执行中，FAILED：失败，NODE_SUSPENDED：暂停，SUSPENDED：成功 |
|  skip         | bool       | 是否手动跳过                   |
|  retry        | int        | 重试次数                       |
|  histories    | list       | 重试记录详情，详情见下面说明   |
|  inputs       | dict       | 输入参数，key：value格式       |
|  outputs      | dict       | 输出参数，key：value格式       |
|  ex_data      | string     | 节点执行失败详情，json字符串或者HTML字符串、普通字符串 |


### HTTP 请求调用示例
```python
import requests
kwargs = {
    "app_code": "app_code",
    "app_secret": "app_secret",
    "access_token": "access_token",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd"
    "subprocess_stack": "[\"nodeaaa0ce51d2143aa9b0dbc27cb7df\"]",
    "component_code": "job_fast_execute_script",
}
response = requests.get("http://{stageVariables.domain}/apigw/get_task_node_detail/10/2/", kwargs)
result = response.json()
```

### ESB SDK 调用示例
```python
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
    "node_id": "node0df0431f8f553925af01a94854bd"
    "subprocess_stack": "[\"nodeaaa0ce51d2143aa9b0dbc27cb7df\"]",
    "component_code": "job_fast_execute_script",
}
# 路径参数
path_kwargs = {
    "bk_biz_id": "2",
    "task_id": "10",
}
result = client.api.get_task_node_detail(kwargs, path_kwargs)
```

### 返回结果示例
```
{
    "message": "",
    "data": {
        "inputs": {
            "job_account": "root",
            "job_script_timeout": "",
            "job_script_source": "manual",
            "job_script_list_public": "",
            "job_content": "echo 0\nexit 0",
            "job_script_type": "1",
            "job_script_param": "",
            "job_script_list_general": "",
            "job_ip_list": "127.0.0.1"
        },
        "retry": 0,
        "name": "<class "pipeline.core.flow.activity.ServiceActivity">",
        "finish_time": "2019-01-17 22:02:46 +0800",
        "skip": false,
        "start_time": "2019-01-17 22:02:37 +0800",
        "children": {},
        "histories": [],
        "ex_data": null,
        "elapsed_time": 9,
        "outputs": [
            {
                "value": 407584,
                "name": "JOB任务ID",
                "key": "job_inst_id"
            },
            {
                "value": "",
                "name": "JOB任务链接",
                "key": "job_inst_url"
            },
            {
                "value": true,
                "name": "执行结果",
                "key": "_result"
            }
        ],
        "state": "FINISHED",
        "version": "23ac8c29f62b3337aafcf1f538d277f8",
        "error_ignorable": false,
        "id": "node0df0431f8f553925af01a94854bd",
        "loop": 1
    },
    "result": true
}
```


## query_task_count

### 功能描述
查询任务实例分类统计总数

### 请求方法
POST

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   group_by     |   string     |   是   |  分类统计维度，status：按任务状态（未执行、执行中、已完成）统计，category：按照任务类型统计，flow_type：按照流程类型统计，create_method：按照创建方式 |
|   conditions     |   dict     |   否   |  任务过滤条件 |


##### conditions 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  template_id      |    string    |      创建任务的模板ID    |
|  name      |    string    |      任务名称   |
|  creator      |    string    |      创建人    |
|  create_time__gte      |    string    |      任务创建时间起始时间   |
|  create_time__lte      |    string    |      任务创建时间截止时间   |
|  executor      |    string    |      执行人    |
|  start_time__gte      |    string   |      任务执行时间起始时间  |
|  start_time__lte      |    string   |      任务执行时间截止时间  |
|  is_started      |    bool   |      任务是否启动  |
|  is_finished      |    bool   |      任务是否完成  |


### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

##### data 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  total      |    int    |      按照过滤条件获取的任务总数    |
|  groups     |    list    |      按照过滤条件分类分类统计详情   |

##### groups[] 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  code      |    string    |      分类统计类型编码    |
|  name      |    string    |      分类统计类型名称    |
|  value     |    string    |      当前分类任务数量    |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
	"conditions": {"create_time__lte": "2018-07-12 10:00:00", "is_started": True},
	"group_by": "flow_type"
}
response = requests.post("http://{stageVariables.domain}/apigw/query_task_count/2/", json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
	"conditions": {"create_time__lte": "2018-07-12 10:00:00", "is_started": True},
	"group_by": "flow_type"
}
# 路径参数
path_kwargs = {
	"bk_biz_id": "2",
}
result = client.api.query_task_count(kwargs, path_kwargs)
```

### 返回结果示例
```
{
    "data": {
        "total": 180,
        "groups": [
            {
                "code": "common",
                "name": "默认任务流程",
                "value": 166
            },
            {
                "code": "common_func",
                "name": "职能化任务流程",
                "value": 14
            }
        ]
    },
    "result": true
}
```


## get_periodic_task_list

### 功能描述
获取某个业务下所有的周期任务

### 请求方法
GET

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |

### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

##### data 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  cron      |    string    |      周期调度表达式    |
|  total_run_count      |    int    |    周期任务运行次数   |
|  name      |    string    |    周期任务名   |
|  creator      |    string    |    创建者   |
|  last_run_at      |    string    |    上次运行时间   |
|  enabled      |    bool    |    是否激活   |
|  id      |    int    |    周期任务ID   |
|  template_id      |    string    |    用于创建该任务的模板ID   |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
}
response = requests.get("http://{stageVariables.domain}/apigw/get_periodic_task_list/2/", json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
}
# 路径参数
path_kwargs = {
	"bk_biz_id": "2",
}
result = client.api.get_periodic_task_list(kwargs, path_kwargs)
```

### 返回结果示例
```
{
    "data": [
        {
            "cron": "*/1 15 * * * (m/h/d/dM/MY)",
            "total_run_count": 1,
            "name": "from api 3",
            "creator": "admin",
            "last_run_at": "2018-11-28 15:57:01 +0900",
            "enabled": false,
            "id": 11,
            "template_id": "2"
        },
        {
            "cron": "1,2,3-19/2 2 3 4 5 (m/h/d/dM/MY)",
            "total_run_count": 0,
            "name": "from api 1",
            "creator": "admin",
            "last_run_at": "",
            "enabled": false,
            "id": 6,
            "template_id": "2"
        },
        {
            "cron": "*/5 * * * * (m/h/d/dM/MY)",
            "total_run_count": 0,
            "name": "定时",
            "creator": "admin",
            "last_run_at": "",
            "enabled": false,
            "id": 4,
            "template_id": "2"
        }
    ],
    "result": true
}
```


## get_periodic_task_info

### 功能描述
获取某个周期任务的详情

### 请求方法
GET

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   task_id    |   string     |   是   |  周期任务ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |

### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

##### data 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  cron      |    string    |      周期调度表达式    |
|  total_run_count      |    int    |    周期任务运行次数   |
|  name      |    string    |    周期任务名   |
|  creator      |    string    |    创建者   |
|  last_run_at      |    string    |    上次运行时间   |
|  enabled      |    bool    |    是否激活   |
|  id      |    int    |    周期任务 ID   |
|  template_id      |    string    |    用于创建该任务的模板 ID   |
|  form      |    dict    |    该周期任务的参数表达对象   |
|  pipeline_tree      |    dict    |    该周期任务的实例树   |

##### data[pipeline_tree] 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  start_event      |    dict    |      开始节点信息     |
|  end_event      |    dict    |      结束节点信息    |
|  activities      |    dict    |      任务节点（标准插件和子流程）信息    |
|  gateways      |    dict    |      网关节点（并行网关、分支网关和汇聚网关）信息    |
|  flows      |    dict    |     顺序流（节点连线）信息    |
|  constants      |    dict    |  全局变量信息，详情见下面    |
|  outputs      |    list    |  模板输出信息，标记 constants 中的输出字段    |

###### data[form], data[pipeline_tree][constants] 说明

KEY：
全局变量 KEY，${key} 格式

VALUE：

|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs/component_outputs 时有效，变量的来源标准插件   |
|  source_info   |   dict  |  source_type=component_inputs/component_outputs 时有效，变量的来源节点信息 |

### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
}
response = requests.get("http://{stageVariables.domain}/apigw/get_periodic_task_info/8/2/", json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
}
# 路径参数
path_kwargs = {
    "task_id": "8",
	"bk_biz_id": "2",
}
result = client.api.get_periodic_task_info(kwargs, path_kwargs)
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

## create_periodic_task

### 功能描述
创建一个周期任务

### 请求方法
POST

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   template_id    |   string     |   是   |  用于创建周期任务的模板ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   name    |   string     |   是   |  要创建的周期任务名称 |
|   cron    |   dict     |   是   |  要创建的周期任务调度策略 |
|   constants    |   dict     |   否   | 任务全局参数，详细信息见下面说明 |
|   exclude_task_nodes_id    |   list     |   否   |  跳过执行的节点ID列表 |

##### constants 说明
KEY：变量 KEY，${key} 格式

VALUE：变量值

#### cron 说明
 
 |   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   minute    |   string     |   否   |  分，默认为 * |
|   hour    |   string     |   否   |  时，默认为 * |
|   day_of_week    |   string     |   否   |  一周内的某些天，默认为 * |
|   day_of_month    |   string     |   否   |  一个月中的某些天，默认为 * |
|   month_of_year    |   string     |   否   |  一年中的某些月份，默认为 * |

### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

##### data 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  cron      |    string    |      周期调度表达式    |
|  total_run_count      |    int    |    周期任务运行次数   |
|  name      |    string    |    周期任务名   |
|  creator      |    string    |    创建者   |
|  last_run_at      |    string    |    上次运行时间   |
|  enabled      |    bool    |    是否激活   |
|  id      |    int    |    周期任务 ID   |
|  template_id      |    string    |    用于创建该任务的模板 ID   |
|  form      |    dict    |    该周期任务的参数表达对象   |
|  pipeline_tree      |    dict    |    该周期任务的实例树   |

##### data[pipeline_tree] 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  start_event      |    dict    |      开始节点信息     |
|  end_event      |    dict    |      结束节点信息    |
|  activities      |    dict    |      任务节点（标准插件和子流程）信息    |
|  gateways      |    dict    |      网关节点（并行网关、分支网关和汇聚网关）信息    |
|  flows      |    dict    |     顺序流（节点连线）信息    |
|  constants      |    dict    |  全局变量信息，详情见下面    |
|  outputs      |    list    |  模板输出信息，标记 constants 中的输出字段    |

###### data[form], data[pipeline_tree][constants] 说明

KEY：
全局变量 KEY，${key} 格式

VALUE：

|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs|component_outputs 时有效，变量的来源标准插件   |
|  source_info   |   dict  |  source_type=component_inputs|component_outputs 时有效，变量的来源节点信息 |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
	"name": "from api 3",
	"cron" : {"minute": "*/1", "hour": "15", "day_of_week":"*", "day_of_month":"*", "month_of_year":"*"},
	"constants": {"${bk_timing}": "100"},
	"exclude_task_nodes_id": ["nodea5c396a3ef0f9f3cd7d4d7695f78"]
}
response = requests.get("http://{stageVariables.domain}/apigw/create_periodic_task/1/2/", json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
	"name": "from api 3",
	"cron" : {"minute": "*/1", "hour": "15", "day_of_week":"*", "day_of_month":"*", "month_of_year":"*"},
	"constants": {"${bk_timing}": "100"},
	"exclude_task_nodes_id": ["nodea5c396a3ef0f9f3cd7d4d7695f78"]
}
# 路径参数
path_kwargs = {
    "template_id": "1",
	"bk_biz_id": "2",
}
result = client.api.create_periodic_task(kwargs, path_kwargs)
```

### 返回结果示例
```
{
    "message": "",
    "data": {
        "cron": "*/1 15 * * * (m/h/d/dM/MY)",
        "total_run_count": 0,
        "name": "from api 3",
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
                "value": "100",
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
                "incoming": "linecf7b7f10c87187a88b72c5f91177",
                "outgoing": "",
                "type": "EmptyEndEvent",
                "id": "node375320830be9c46cd89f4069857d",
                "name": ""
            },
            "outputs": [],
            "flows": {
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
                    "target": "node375320830be9c46cd89f4069857d"
                }
            },
            "gateways": {},
            "line": [
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
                        "id": "node375320830be9c46cd89f4069857d",
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
        "enabled": false,
        "id": 11,
        "template_id": 2
    },
    "result": true
}
```

## set_periodic_task_enabled

### 功能描述
设置一个周期任务是否激活

### 请求方法
POST

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   task_id    |   string     |   是   |  周期任务ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   enabled    |   bool     |   否   | 该周期任务是否激活，不传则为 false |

### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

##### data 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  enabled      |    bool    |      当前周期任务是否已经激活    |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
	"enabled": False
}
response = requests.get("http://{stageVariables.domain}/apigw/set_periodic_task_enabled/1/2/", json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
    "enabled": False
}
# 路径参数
path_kwargs = {
    "task_id": "1",
	"bk_biz_id": "2",
}
result = client.api.set_periodic_task_enabled(kwargs, path_kwargs)
```

### 返回结果示例
```
{
    "data": {
        "enabled": false
    },
    "result": true
}
```

## modify_cron_for_periodic_task

### 功能描述
修改一个周期任务的调度策略

### 请求方法
POST

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   task_id    |   string     |   是   |  周期任务ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   cron    |   dict     |   否   | 调度策略对象 |

#### cron 说明
 
 |   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   minute    |   string     |   否   |  分，默认为 * |
|   hour    |   string     |   否   |  时，默认为 * |
|   day_of_week    |   string     |   否   |  一周内的某些天，默认为 * |
|   day_of_month    |   string     |   否   |  一个月中的某些天，默认为 * |
|   month_of_year    |   string     |   否   |  一年中的某些月份，默认为 * |


### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

##### data 说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  cron      |    string    |      调度策略表达式    |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
	"cron" : {"minute": "*/1", "hour": "15", "day_of_week":"*", "day_of_month":"*", "month_of_year":"*"},
}
response = requests.get("http://{stageVariables.domain}/apigw/modify_cron_for_periodic_task/1/2/", json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
    "cron" : {"minute": "*/1", "hour": "15", "day_of_week":"*", "day_of_month":"*", "month_of_year":"*"},
}
# 路径参数
path_kwargs = {
    "task_id": "1",
	"bk_biz_id": "2",
}
result = client.api.modify_cron_for_periodic_task(kwargs, path_kwargs)
```

### 返回结果示例
```
{
    "data": {
        "cron": "*/1 15 * * * (m/h/d/dM/MY)"
    },
    "result": true
}
```

## modify_constants_for_periodic_task

### 功能描述
修改一个周期任务的全局变量

### 请求方法
POST

### 请求参数说明
|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   task_id    |   string     |   是   |  周期任务ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   constants    |   dict     |   否   | 全局参数设置 |

#### constants 说明
 
KEY：变量 KEY，${key} 格式

VALUE：变量值

### 返回结果说明
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

##### data 说明
KEY：  
全局变量 KEY，${key} 格式

VALUE：   
|   字段   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs/component_outputs 时有效，变量的来源标准插件   |
|  source_info   |   dict  |  source_type=component_inputs/component_outputs 时有效，变量的来源节点信息 |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	"app_code": "app_code",
	"app_secret": "app_secret",
	"access_token": "access_token",
	"constants": {"${bk_timing}": "15"}
}
response = requests.get("http://{stageVariables.domain}/apigw/modify_constants_for_periodic_task/1/2/", json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
    "constants": {"${bk_timing}": "15"}
}
# 路径参数
path_kwargs = {
    "task_id": "1",
	"bk_biz_id": "2",
}
result = client.api.modify_constants_for_periodic_task(kwargs, path_kwargs)
```

### 返回结果示例
```
{
    "data": {
        "${bk_timing}": {
            "source_tag": "sleep_timer.bk_timing",
            "source_info": {
                "node76393dcfedcf73dbc726f1c4786d": [
                    "bk_timing"
                ]
            },
            "name": "定时时间",
            "custom_type": "",
            "index": 0,
            "value": "15",
            "show_type": "show",
            "source_type": "component_inputs",
            "key": "${bk_timing}",
            "validation": "",
            "desc": ""
        }
    },
    "result": true
}
```
