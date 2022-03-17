### 功能描述

根据插件code获取某个业务下对应插件信息

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id       |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   scope           |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
|   code            |   string     |   是   |  插件编码code |
|   version         |   string     |   否   |  插件版本，默认为 legacy | 

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_username": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "code": "sleep_timer",
    "version": "legacy",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "inputs": [
            {
                "name": "定时时间",
                "key": "bk_timing",
                "type": "string",
                "schema": {
                    "type": "string",
                    "description": "定时时间，格式为秒(s) 或 (%%Y-%%m-%%d %%H:%%M:%%S)",
                    "enum": []
                },
                "required": true
            },
            {
                "name": "是否强制晚于当前时间",
                "key": "force_check",
                "type": "bool",
                "schema": {
                    "type": "string",
                    "description": "用户输入日期格式时是否强制要求时间晚于当前时间，只对日期格式定时输入有效",
                    "enum": []
                },
                "required": true
            }
        ],
        "outputs": [
            {
                "name": "执行结果",
                "key": "_result",
                "type": "bool",
                "schema": {
                    "type": "boolean",
                    "description": "执行结果的布尔值，True or False",
                    "enum": []
                }
            },
            {
                "name": "循环次数",
                "key": "_loop",
                "type": "int",
                "schema": {
                    "type": "int",
                    "description": "循环执行次数",
                    "enum": []
                }
            }
        ],
        "desc": "",
        "code": "sleep_timer",
        "name": "定时",
        "group_name": "蓝鲸服务(BK)",
        "version": "legacy",
        "form": "/static/components/atoms/bk/timer.js"
    },
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

##### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  inputs      |    array    |      插件输入参数列表    |
|  outputs      |    array    |      插件输出参数列表    |
|  desc      |    string    |      插件描述    |
|  code      |    string    |      插件代码    |
|  name      |    string    |      插件名    |
|  group_name      |    string    |      插件组名    |
|  version      |    string    |      插件版本    |
|  form         |    string    |      插件表单静态资源链接    |

##### inputs

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
| required | bool | 是否是必填参数 |
| type | string | 参数类型 |
| name | string | 参数名 |
| key | string | 参数唯一键 |
| schema | dict | 参数 schema |

###### inputs.schema

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
| type | string | 参数类型 |
| enum | list | 参数可选范围 |
|  description      |    string    |   参数描述   |
| properties | dict | 对象属性 schema，当 type 为 object 时，会存在该字段，该对象的属性的值为另一个 schema 对象  |
| items | dict | 列表元素 schema，当 type 为 array 时，会存在该字段 |

##### outputs

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
| type | string | 参数类型 |
| name | string | 参数名 |
| key | string | 参数唯一键 |
| schema | dict | 参数 schema |

###### outputs.schema

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
| type | string | 参数类型 |
| enum | list | 参数可选范围 |
|  description      |    string    |   参数描述   |
| properties | dict | 对象属性 schema，当 type 为 object 时，会存在该字段，该对象的属性的值为另一个 schema 对象  |
| items | dict | 列表元素 schema，当 type 为 array 时，会存在该字段 |