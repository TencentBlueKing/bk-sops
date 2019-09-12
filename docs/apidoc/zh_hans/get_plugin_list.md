### 功能描述

查询某个项目下的插件列表

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
|   project_id    |   string     |   是   |  项目ID |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 project_id 的项目；当值为 project 时则检索项目 ID 为 project_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "project_id": "2"
}
```

### 返回结果示例

```
{
    "data": [
        {
            "inputs": [
                {
                    "required": true,
                    "type": "string",
                    "name": "业务 ID",
                    "key": "biz_cc_id",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "当前操作所属的 CMDB 业务 ID"
                    }
                },
                {
                    "required": true,
                    "type": "string",
                    "name": "定时作业名称",
                    "key": "job_cron_name",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "待创建的定时作业名称"
                    }
                },
                {
                    "required": true,
                    "type": "string",
                    "name": "定时规则",
                    "key": "job_cron_expression",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "待创建的定时作业定时规则"
                    }
                },
                {
                    "required": true,
                    "type": "string",
                    "name": "定时作业状态",
                    "key": "job_cron_status",
                    "schema": {
                        "enum": [
                            1,
                            2
                        ],
                        "type": "int",
                        "description": "待创建的定时作业状态，暂停(1) 启动(2)"
                    }
                }
            ],
            "code": "job_cron_task",
            "name": "新建定时作业",
            "group_name": "作业平台(JOB)",
            "output": [
                {
                    "type": "int",
                    "name": "定时作业ID",
                    "key": "cron_id",
                    "schema": {
                        "enum": [],
                        "type": "int",
                        "description": "成功创建的定时作业 Id"
                    }
                },
                {
                    "type": "string",
                    "name": "定时作业状态",
                    "key": "status",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "成功创建的定时作业状态"
                    }
                },
                {
                    "type": "bool",
                    "name": "执行结果",
                    "key": "_result",
                    "schema": {
                        "enum": [],
                        "type": "boolean",
                        "description": "是否执行成功"
                    }
                }
            ],
            "desc": ""
        },
        {
            "inputs": [
                {
                    "required": true,
                    "type": "string",
                    "name": "业务 ID",
                    "key": "biz_cc_id",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "当前操作所属的 CMDB 业务 ID"
                    }
                },
                {
                    "required": true,
                    "type": "string",
                    "name": "主机 IP",
                    "key": "cc_host_ip",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "转移到资源池的主机内网 IP，多个以 \",\" 分隔"
                    }
                }
            ],
            "code": "cmdb_transfer_host_resource",
            "name": "转移主机至资源池",
            "group_name": "配置平台(CMDB)",
            "output": [
                {
                    "type": "bool",
                    "name": "执行结果",
                    "key": "_result",
                    "schema": {
                        "enum": [],
                        "type": "boolean",
                        "description": "是否执行成功"
                    }
                }
            ],
            "desc": ""
        },
        {
            "inputs": [
                {
                    "required": true,
                    "type": "string",
                    "name": "业务 ID",
                    "key": "biz_cc_id",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "当前操作所属的 CMDB 业务 ID"
                    }
                },
                {
                    "required": true,
                    "type": "string",
                    "name": "主机 IP",
                    "key": "cc_host_ip",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "转移到故障机的主机内网 IP，多个以 \",\" 分隔"
                    }
                }
            ],
            "code": "cmdb_transfer_fault_host",
            "name": "转移主机到业务的故障机模块",
            "group_name": "配置平台(CMDB)",
            "output": [
                {
                    "type": "bool",
                    "name": "执行结果",
                    "key": "_result",
                    "schema": {
                        "enum": [],
                        "type": "boolean",
                        "description": "是否执行成功"
                    }
                }
            ],
            "desc": ""
        }
    ],
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
|  inputs      |    list    |      插件的输入参数    |
|  code      |    string    |    插件的编码   |
|  name      |    string    |    插件名   |
|  group_name      |    string    |   插件所属的组名   |
|  outputs      |    list    |   插件的输出参数   |
|  desc      |    string    |   插件描述   |

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