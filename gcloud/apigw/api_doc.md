# API DOC

请通过 APIGW 或者 ESB 访问

## get_template_list

### 功能描述
查询业务下的模板列表

### 请求方法
GET

### 请求参数说明
|   参数名称   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |

### 返回结果说明
|      名称     |     类型   |               说明              |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 查询成功与否     |
|  data        |    list      |      result=true时模板列表，item 信息见下面说明     |
|  message      |    string    |    result=false时错误信息     |

#### data[item] 说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  bk_biz_id      |    string    |      模板所属业务ID     |
|  bk_biz_name      |    string    |      模板所属业务名称    |
|  id      |    int    |      模板ID    |
|  name      |    string    |      模板名称    |
|  category      |    string    |      模板分类，分类信息见下面说明    |
|  creator      |    string    |      模板创建人   |
|  create_time      |    string    |      模板创建时间   |
|  editor      |    string 或者 null    |      模板编辑人   |
|  edit_time      |    string   |      模板最新编辑时间   |

#### data[item][category] 说明
```
CATEGORY = {
	'OpsTools': u"运维工具",
	'MonitorAlarm': u"监控告警",
	'ConfManage': u"配置管理",
	'DevTools': u"开发工具",
	'EnterpriseIT': u"企业IT",
	'OfficeApp': u"办公应用",
	'Other': u"其它",
}
```

### HTTP 请求调用示例
```python
import requests
kwargs = {
	'app_code': 'app_code',
	'app_secret': 'app_secret',
	'access_token': 'access_token',
}
response = requests.get('http://{stageVariables.domain}/apigw/get_template_list/2/', kwargs)
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
	'bk_biz_id': '2'
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
|   参数名称   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   template_id     |   string     |   是   |  模板ID |

### 返回结果说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 查询成功与否     |
|  data        |    dict      |      result=true 时模板详情，详细信息见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

#### data 说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  bk_biz_id      |    string    |      模板所属业务ID     |
|  bk_biz_name      |    string    |      模板所属业务名称    |
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
	'OpsTools': u"运维工具",
	'MonitorAlarm': u"监控告警",
	'ConfManage': u"配置管理",
	'DevTools': u"开发工具",
	'EnterpriseIT': u"企业IT",
	'OfficeApp': u"办公应用",
	'Other': u"其它",
}
```

##### data[pipeline_tree] 说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  start_event      |    dict    |      开始节点信息     |
|  end_event      |    dict    |      结束节点信息    |
|  activities      |    dict    |      任务节点（原子和子流程）信息    |
|  gateways      |    dict    |      网关节点（并行网关、分支网关和汇聚网关）信息    |
|  flows      |    dict    |     顺序流（节点连线）信息    |
|  constants      |    dict    |  全局变量信息，详情见下面    |
|  outputs      |    list    |  模板输出信息，标记 constants 中的输出字段    |

###### data[pipeline_tree][constants] 说明

KEY：
全局变量 KEY，${key} 格式

VALUE：

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


### HTTP 请求调用示例
```python
import requests
kwargs = {
	'app_code': 'app_code',
	'app_secret': 'app_secret',
	'access_token': 'access_token',
}
response = requests.get('http://{stageVariables.domain}/apigw/get_template_list/30/1/', kwargs)
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
	'bk_biz_id': '1',
	'template_id': '30',
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
|   参数名称   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   template_id     |   string     |   是   |  模板ID |
|   name     |   string     |   是   |  任务名称 |
|   flow_type     |   string     |   否   |  任务流程类型，common: 常规流程，common_func：职能化流程 |
|   constants     |   dict     |   否   |  任务全局参数，详细信息见下面说明 |
|   exclude_task_nodes_id | list |   否   |  跳过执行的节点ID列表 |

##### constants 说明
KEY：变量 KEY，${key} 格式

VALUE：变量值，value 的类型和从模板获取的全局变量中 value 类型保持一致 


### 返回结果说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功返回数据，详细信息见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

#### data 说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  task_id     |    int     |    任务实例 ID     |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	'app_code': 'app_code',
	'app_secret': 'app_secret',
	'access_token': 'access_token',
	'name': 'tasktest',
	'flow_type': 'common',
	'constants': {
		'${content}': 'echo 1',
		'${params}': '',
		'${script_timeout}': 20
	}
}
response = requests.post('http://{stageVariables.domain}/apigw/create_task/10/2/', json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```python
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
	'name': 'tasktest',
	'flow_type': 'common',
	'constants': {
		'${content}': 'echo 1',
		'${params}': '',
		'${script_timeout}': 20
	}
}
# 路径参数
path_kwargs = {
	'bk_biz_id': '1',
	'template_id': '30',
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
|   参数名称   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   task_id      |   string     |   是   |  任务ID |


### 返回结果说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 任务是否执行     |
|  data        |    dict      |      result=true 时成功返回数据    |
|  message        |    string      |      result=false 时错误信息     |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	'app_code': 'app_code',
	'app_secret': 'app_secret',
	'access_token': 'access_token',
}
response = requests.post('http://{stageVariables.domain}/apigw/start_task/10/2/', json.dumps(kwargs))
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
	'bk_biz_id': '2',
	'task_id': '10',
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
|   参数名称   |    参数类型  |  必须  |     参数说明     |
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
	'start': u"开始任务" # 等效于调用 start_task 接口
	'pause': u"暂停任务，任务处于执行状态时调用"
	'resume': u"继续任务，任务处于暂停状态时调用"
	'revoke': u"终止任务"
}
```

### 返回结果说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时返回数据     |
|  message        |    string      |      result=false 时错误信息     |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	'app_code': 'app_code',
	'app_secret': 'app_secret',
	'access_token': 'access_token',
	'action': 'start'
}
response = requests.post('http://{stageVariables.domain}/apigw/operate_task/10/2/', json.dumps(kwargs))
result = response.json()
```

### ESB SDK 调用示例
```python
from bkapigw.app_code.shortcuts import get_client_by_request
client = get_client_by_request(request)
# 填充参数
kwargs = {
	'action': 'start'
}
# 路径参数
path_kwargs = {
	'bk_biz_id': '2',
	'task_id': '10',
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
|   参数名称   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   task_id     |   string     |   是   |  任务或节点ID  |

### 返回结果说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 查询成功与否     |
|  data        |    dict      |      result=true 时返回数据，详细信息见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

#### data 说明
|   名称   |  类型  |           说明             |
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
	'CREATED': u"未执行"
	'RUNNING': u"执行中"
	'FAILED': u"失败"
	'SUSPENDED': u"暂停"
	'REVOKED': u"已撤销"
	'FINISHED': u"已完成"
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
	'app_code': 'app_code',
	'app_secret': 'app_secret',
	'access_token': 'access_token',
}
response = requests.get('http://{stageVariables.domain}/apigw/get_template_list/10/2/', kwargs)
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
	'bk_biz_id': '2',
	'task_id': '10',
}
result = client.api.api_test(kwargs, path_kwargs)
```

### 返回结果示例
```
{
	"result": true,
    "data": {
		"retry": 0,
		"name": "<class 'pipeline.core.pipeline.Pipeline'>",
		"finish_time": "",
		"skip": false,
		"start_time": "2018-04-26 16:08:34 +0800",
		"children": {
			"62d4784e20483f1585149ce90ed954c9": {
				"retry": 0,
				"name": "<class 'pipeline.core.flow.event.EmptyStartEvent'>",
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
				"name": "<class 'pipeline.core.flow.activity.ServiceActivity'>",
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

## query_task_count

### 功能描述
查询任务实例分类统计总数

### 请求方法
POST

### 请求参数说明
|   参数名称   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   group_by     |   string     |   是   |  分类统计维度，status：按任务状态（未执行、执行中、已完成）统计，category：按照任务类型统计，flow_type：按照流程类型统计，create_method：按照创建方式 |
|   conditions     |   dict     |   否   |  任务过滤条件 |


##### conditions 说明
|   名称   |  类型  |           说明             |
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
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

##### data 说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  total      |    int    |      按照过滤条件获取的任务总数    |
|  groups      |    list    |      按照过滤条件分类分类统计详情   |

##### groups[item] 说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  code      |    string    |      分类统计类型编码    |
|  name      |    string    |      分类统计类型名称    |
|  value     |    string    |      当前分类任务数量    |


### HTTP 请求调用示例
```python
import json
import requests
kwargs = {
	'app_code': 'app_code',
	'app_secret': 'app_secret',
	'access_token': 'access_token',
	"conditions": {"create_time__lte": "2018-07-12 10:00:00", "is_started": True},
	"group_by": "flow_type"
}
response = requests.post('http://{stageVariables.domain}/apigw/query_task_count/2/', json.dumps(kwargs))
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
	'bk_biz_id': '2',
}
result = client.api.api_test(kwargs, path_kwargs)
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
