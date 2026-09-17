> 本文档由脚本自动从 GitHub 同步，源仓库：
> https://github.com/TencentBlueKing/bk-sops/tree/master/docs/zh_hans/apidoc
>
> 如需修改请在 GitHub 提交 PR，下次同步时会自动更新。

---

## 目录

**项目管理**
- [get_user_project_list](#get_user_project_list)
- [get_user_project_detail](#get_user_project_detail)
- [register_project](#register_project)

**模板管理**
- [get_template_list](#get_template_list)
- [get_template_info](#get_template_info)
- [get_template_schemes](#get_template_schemes)
- [preview_task_tree](#preview_task_tree)
- [import_project_template](#import_project_template)
- [get_common_template_list](#get_common_template_list)
- [get_common_template_info](#get_common_template_info)
- [preview_common_task_tree](#preview_common_task_tree)
- [import_common_template](#import_common_template)

**任务管理**
- [create_task](#create_task)
- [create_and_start_task](#create_and_start_task)
- [fast_create_task](#fast_create_task)
- [start_task](#start_task)
- [operate_task](#operate_task)
- [get_task_list](#get_task_list)
- [get_task_count](#get_task_count)
- [query_task_count](#query_task_count)
- [get_task_detail](#get_task_detail)
- [get_task_status](#get_task_status)
- [get_tasks_status](#get_tasks_status)
- [get_task_effective_time](#get_task_effective_time)
- [modify_constants_for_task](#modify_constants_for_task)

**节点操作**
- [get_task_node_data](#get_task_node_data)
- [get_task_node_detail](#get_task_node_detail)
- [operate_node](#operate_node)
- [node_callback](#node_callback)
- [get_tasks_manual_intervention_state](#get_tasks_manual_intervention_state)

**周期任务**
- [create_periodic_task](#create_periodic_task)
- [get_periodic_task_list](#get_periodic_task_list)
- [get_periodic_task_info](#get_periodic_task_info)
- [modify_cron_for_periodic_task](#modify_cron_for_periodic_task)
- [modify_constants_for_periodic_task](#modify_constants_for_periodic_task)
- [set_periodic_task_enabled](#set_periodic_task_enabled)

**计划任务**
- [create_clocked_task](#create_clocked_task)

**职能化任务**
- [get_functionalization_task_list](#get_functionalization_task_list)
- [claim_functionalization_task](#claim_functionalization_task)

**轻应用**
- [get_mini_app_list](#get_mini_app_list)

**插件**
- [get_plugin_list](#get_plugin_list)
- [get_plugin_detail](#get_plugin_detail)

**其他**
- [apply_webhook_configs](#apply_webhook_configs)
- [create_template](#create_template)
- [get_clocked_task_list](#get_clocked_task_list)
- [get_node_job_executed_log](#get_node_job_executed_log)
- [get_plugin_base_info](#get_plugin_base_info)
- [get_task_node_log](#get_task_node_log)
- [get_task_plugin_log](#get_task_plugin_log)
- [modify_project_executor_proxy](#modify_project_executor_proxy)
- [modify_template_executor_proxy](#modify_template_executor_proxy)
- [modify_template_notify](#modify_template_notify)
- [plugin_gateway_cancel_run](#plugin_gateway_cancel_run)
- [plugin_gateway_create_run](#plugin_gateway_create_run)
- [plugin_gateway_get_categories](#plugin_gateway_get_categories)
- [plugin_gateway_get_plugin_detail](#plugin_gateway_get_plugin_detail)
- [plugin_gateway_get_plugin_list](#plugin_gateway_get_plugin_list)
- [plugin_gateway_get_run_detail](#plugin_gateway_get_run_detail)
- [plugin_gateway_get_run_status](#plugin_gateway_get_run_status)
- [plugin_gateway_internal_callback](#plugin_gateway_internal_callback)

---

# 项目管理

## get_user_project_list

### 功能描述

查询用户有权限的项目列表


### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "project_id": 13,
            "bk_biz_id": 2,
            "name": "蓝鲸"
        },
        {
            "project_id": 14,
            "bk_biz_id": 3,
            "name": "la"
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | dict       | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  project_id | int        | 项目 ID       |
|  bk_biz_id | int        | 绑定的 CMDB 业务 ID       |
|  name  | string     | 项目名           |

### MCP 请求说明

当请求来源于网关MCP时，响应中不会过滤任何字段。

---

## get_user_project_detail

### 功能描述

获取项目的详情

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id       |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "project_id": 13,
        "project_name": "蓝鲸",
        "bk_biz_id": 2,
        "from_cmdb": true,
        "bk_biz_name": "蓝鲸",
        "bk_biz_developer": "",
        "bk_biz_maintainer": "admin,gcloudadmin",
        "bk_biz_tester": "",
        "bk_biz_productor": "",
        "auth_actions": [
            "project_view",
            "project_edit",
            "project_fast_create_task"
        ]
    },
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | dict       | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  project_id | int        | 项目 ID       |
|  project_name  | string     | 项目名           |
|  bk_biz_id | int        | 绑定的 CMDB 业务 ID       |
|  from_cmdb | bool        | 该项目是否是从 CMDB 业务同步的       |
|  bk_biz_name  | string     | 项目名           |
|  bk_biz_developer  | string     | 业务开发人员列表           |
|  bk_biz_maintainer  | string     | 业务运维人员列表           |
|  bk_biz_tester  | string     | 业务测试人员列表           |
|  bk_biz_productor  | string     | 业务产品人员列表           |
|  auth_actions  | list     | 当前用户对该项目对象拥有的操作权限           |

---

## register_project

### 功能描述

第三方系统项目cmdb同步注册

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id     |   int |   是   |  CMDB 业务 ID |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": 6,
}
```

### 返回结果示例

```
{
    "data": {
        "project_id": 10,
        "project_name": "test"
    },
    "result": true,
    "code": 0
}
```

### 返回结果参数说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  message      | string     | result=false 时错误信息        |
|  data         | dict        | 返回数据                    |

#### data
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  project_id |    int    |  标准运维项目ID |
|  project_name |    string | 标准运维项目名称 |

---

# 模板管理

## get_template_list

### 功能描述

查询业务下的模板列表

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|-------------------|
| bk_biz_id     |  string    | 是     | 模板所属业务ID     |
| template_source | string   | 否     | 流程模板来源，可选值：business（业务流程，默认值）、project（项目流程）、common（公共流程） |
| id_in         |  string    | 否     | 流程模板id来源列表，以逗号`,`分隔 |
| name_keyword  |  string    | 否     | 流程模板名称关键词，英文不区分大小写 |
| include_executor_proxy | bool | 否 | 是否包含执行人代理信息，默认 false |
| include_subprocess | bool | 否 | 是否包含子流程信息，默认 false |
| include_constants | bool | 否 | 是否包含全局变量信息，默认 false |
| include_notify | bool | 否 | 是否包含通知信息，默认 false |
| include_labels | bool | 否 | 是否包含标签信息（仅对业务流程和项目流程有效），默认 false |
| expected_timezone | string |   否   |  任务时间相关字段期望返回的时区，形如Asia/Shanghai |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "id_in": "1, 2, 3"
    "template_source": "business",
    "scope": "cmdb_biz",
    "name_keyword": "xxx"
}
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
            "name": "快速执行脚本",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "蓝鲸",
            "project_id": 3,
            "project_name": "蓝鲸",
            "id": 32,
            "editor": "admin",
            "creator":"admin",
            "auth_actions": [
                "flow_create",
                "flow_view",
                "flow_edit",
                "flow_delete",
                "flow_create_task",
                "flow_create_mini_app",
                "flow_create_periodic_task",
                "flow_create_clocked_task"
            ]
        },
        {
            "category": "Other",
            "edit_time": "2018-04-19 12:04:42 +0800",
            "create_time": "2018-04-19 12:04:42 +0800",
            "name": "new201804191218",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "蓝鲸",
            "project_id": 3,
            "project_name": "蓝鲸",
            "id": 31,
            "editor": null,
            "creator": "admin",
            "auth_actions": [
                "flow_create",
                "flow_view",
                "flow_edit",
                "flow_delete",
                "flow_create_task",
                "flow_create_mini_app",
                "flow_create_periodic_task",
                "flow_create_clocked_task"
            ]
        },
        {
            "category": "Other",
            "edit_time": "2018-04-18 17:09:39 +0800",
            "create_time": "2018-04-16 21:43:15 +0800",
            "name": "new20180416213944",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "蓝鲸",
            "project_id": 3,
            "project_name": "蓝鲸",
            "id": 30,
            "editor": "admin",
            "creator": "admin",
            "auth_actions": [
                "flow_create",
                "flow_view",
                "flow_edit",
                "flow_delete",
                "flow_create_task",
                "flow_create_mini_app",
                "flow_create_periodic_task",
                "flow_create_clocked_task"
            ]
        },
    ],
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
| result    | bool     | true/false 查询成功与否 |
| data      | list     | result=true时模板列表，item 信息见下面说明 |
| message   | string   | result=false时错误信息 |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段           | 类型      | 描述             |
|--------------|----------|----------------|
| bk_biz_id    |    string    | 模板所属业务ID       |
| bk_biz_name  |    string    | 模板所属业务名称       |
| project_id   |    string    | 模板所属项目ID       |
| project_name |    string    | 模板所属项目名称       |
| id           |    int    | 模板ID           |
| name         |    string    | 模板名称           |
| category     |    string    | 模板分类，分类信息见下面说明 |
| creator      |    string    | 模板创建人          |
| create_time  |    string    | 模板创建时间         |
| editor       |    string 或者 null    | 模板编辑人          |
| edit_time    |    string   | 模板最新编辑时间       |
| auth_actions |    array   | 用户对该资源有权限的操作   |

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

### MCP 请求说明

当请求来源于网关MCP时，以下字段会在响应中被过滤，不会返回：

- `data.[].auth_actions` - 数组中每个模板项的权限操作列表

---

## get_template_info

### 功能描述

查询业务下的单个模板详情

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述          |
|---------------|------------|--------|---------------|
| bk_biz_id     | string     |   是   |  模板所属业务ID |
| template_id   | string     |   是   |  模板ID        |
| template_source | string   | 否     | 流程模板来源，可选值：business（业务流程，默认值）、project（项目流程）、common（公共流程） |
| include_executor_proxy | bool | 否 | 是否包含执行人代理信息，默认 false |
| include_subprocess | bool | 否 | 是否包含子流程信息，默认 false |
| include_constants | bool | 否 | 是否包含全局变量信息，默认 false |
| include_notify | bool | 否 | 是否包含通知信息，默认 false |
| unfold_subprocess | bool | 否 | 是否展开子流程完整配置，默认 false。设为 true 时，pipeline_tree 中每个 SubProcess 节点将包含 pipeline 字段，其中包含该子流程的完整 pipeline_tree（递归展开所有层级）。展开失败时返回 result=false。 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|
| format | string | 否 | pipeline_tree 的返回格式，可选值 json（默认）、yaml。设为 yaml 时，pipeline_tree 字段返回与页面导出一致的 YAML schema 字符串（含 schema_version/meta/spec 结构）。注意：format=yaml 时若同时传入 include_constants=true，template_constants 仍为 JSON 对象（从原始 pipeline_tree 提取），与 YAML 格式的 pipeline_tree 独立 |
| include_pipeline_tree | bool | 否 | MCP 请求时是否返回精简后的 pipeline_tree，默认 false。非 MCP 请求忽略此参数 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "1",
    "template_id": "30",
    "template_source": "business",
    "scope": "cmdb_biz"
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
        "bk_biz_id": "2",
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
        "bk_biz_name": "蓝鲸",
        "project_id": 3,
        "project_name": "blueking",
        "id": 30,
        "editor": "admin"
    },
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
| result    | bool     | true/false 查询成功与否 |
| data      | dict     | result=true 时模板详情，详细信息见下面说明 |
| message   | string   | result=false 时错误信息 |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |



#### data

| 字段            | 类型      | 描述                |
|---------------|----------|-------------------|
| bk_biz_id     |    string    | 模板所属业务ID          |
| bk_biz_name   |    string    | 模板所属业务名称          |
| project_id    |    string    | 模板所属项目ID          |
| project_name  |    string    | 模板所属项目名称          |
| id            |    int       | 模板ID              |
| name          |    string    | 模板名称              |
| category      |    string    | 模板分类，分类信息见下面说明    |
| creator       |    string    | 模板创建人             |
| create_time   |    string    | 模板创建时间            |
| editor        |    string 或者 null    | 模板编辑人             |
| edit_time     |    string    | 模板最新编辑时间          |
| pipeline_tree |    dict 或 string      | 模板任务树信息。format=json 时为 dict（详细信息见下面说明），format=yaml 时为 YAML schema 字符串 |

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

#### data.pipeline_tree.constants KEY

全局变量 KEY，${key} 格式

#### data.pipeline_tree.constants VALUE

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

### MCP 请求说明

当请求来源于网关MCP时，`pipeline_tree` 字段默认不返回（向后兼容）。如需获取精简后的流程树，请传入 `include_pipeline_tree=true`：

- `data.pipeline_tree` - 默认不返回；传入 `include_pipeline_tree=true` 时返回精简版本（移除前端渲染、画布布局等冗余信息，仅保留语义信息）

---

## get_template_schemes

### 功能描述

获取模板的执行方案列表

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id       |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   template_id       |   int     |   是   |  模板 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
|   with_constants       |   string     |   否   |  是否需要返回执行方案的变量详情，取值为 true 或 false，不传时默认为 false |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "template_id": "12",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": "47-1",
            "name": "1",
            "data": "[\"node7082deed0725aed8c72ecff079ba\",\"node88d9050f288765b94a15cbe023ab\"]",
            "detail": {
                "constants": {
                    "key1": {
                        "key": "key1",
                        "name": "参数1",
                        "value": "默认值"
                    }
                }
            }
        },
        {
            "id": "47-2",
            "name": "2",
            "data": "[\"node7082deed0725aed8c72ecff079ba\"]",
            "detail": {
                "constants": {
                    "key2": {
                        "key": "key2",
                        "name": "参数2",
                        "value": "默认值"
                    }
                }
            }
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | dict       | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  id  | string     | 执行方案 ID           |
|  name  | string     | 执行方案名           |
|  data  | string     | 执行方案中包含的节点 ID 列表（JSON 字符串）  |
|  detail  | object     | 执行方案详情，包含输入参数信息。当 with_constants 为 true 时返回  |

#### detail说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  constants  | object     | 执行方案对应的输入参数，结构同模板的 constants  |

---

## preview_task_tree

### 功能描述

获取节点选择后新的任务树

#### 接口参数

| 字段          | 类型     | 必选   |  描述             |
|-----------------|--------|---------|------------------|
|   bk_biz_id       | string |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   template_id       | int    |   是   |  模板 ID |
|   scope       | string |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
|   version | string |   否   |  模板的版本，不填时默认为最新版本 |
|    exclude_task_nodes_id  | list   |   否   |  需要移除的可选节点 ID 列表，不填时默认为 [] |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "template_id": "12",
    "version":"1.0.0",
    "scope":cmdb_biz, 
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
    "trace_id": "xxx"
}
```

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | dict       | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  pipeline_tree      |    dict   |      模板任务树信息，详细信息见下面说明   |
| constants_not_referred | dict | 流程模板中未引用的全局变量，数据结构同pepeline[constants] |

##### data.pipeline_tree
| 名称          | 类型   | 说明                         |
|-------------|------|----------------------------|
| start_event | dict | 开始节点信息                     |
| end_event   | dict | 结束节点信息                     |
| activities  | dict | 任务节点（原子和子流程）信息             |
| gateways    | dict | 网关节点（并行网关、分支网关和汇聚网关）信息     |
| flows       | dict | 顺序流（节点连线）信息                |
| constants   | dict | 全局变量信息，详情见下面               |
| line        | list | 连线信息                       |
| location    | list | 节点位置信息                     |
| outputs     | list | 模板输出信息，标记 constants 中的输出字段 |

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
|   source_info   |   dict  |  source_type=component_inputs|component_outputs 时有效，变量的来源节点信息

---

## import_project_template

### 功能描述

导入项目流程

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   template_data    |   string     |   是   |  项目流程数据，即从标准运维 - 项目流程 - 导出功能下载的文件的内容 |
|   project_id    |   string     |   是   |  项目 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "template_data": "xxx",
    "project_id": "3",
    "bk_username": "cmdb_biz",
    "scope":"cmdb_biz"
}
```

### 返回结果示例

```
{
    "message": "Successfully imported 2 flows",
    "data": {
        "flows": {
              11: "flowA",
              12: "flowB",
              ...
        },
        "count": 2
    },
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  message      | string     | result=false 时错误信息        |
|  data         | dict        | 返回数据                    |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  count      |    int    |      导入的流程数    |
|  flows      |    dict |      导入的流程ID与名字的映射 |

---

## get_common_template_list

### 功能描述

查询公共模板列表

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|-------------------|
| include_executor_proxy | bool | 否 | 是否包含执行人代理信息，默认 false |
| include_subprocess | bool | 否 | 是否包含子流程信息，默认 false |
| include_constants | bool | 否 | 是否包含全局变量信息，默认 false |
| include_notify | bool | 否 | 是否包含通知信息，默认 false |
| include_labels | bool | 否 | 是否包含标签信息，默认 false |
| expected_timezone | string |   否   |  任务时间相关字段期望返回的时区，形如Asia/Shanghai |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
}
```

### 返回结果示例

```
{
    "data": [
        {
            "category": "Other",
            "name": "父流程",
            "creator": "admin",
            "edit_time": "2019-07-15 15:13:22 +0800",
            "create_time": "2019-07-15 15:13:22 +0800",
            "editor": "admin",
            "id": 10014,
            "auth_actions": [
                "common_flow_create_task",
                "common_flow_edit",
                "common_flow_delete",
                "common_flow_view",
                "common_flow_create",
                "common_flow_create_periodic_task"
            ]
        },
        {
            "category": "Other",
            "name": "子流程",
            "creator": "admin",
            "edit_time": "2019-07-15 15:13:22 +0800",
            "create_time": "2019-07-15 15:13:22 +0800",
            "editor": "admin",
            "id": 10013,
            "auth_actions": [
                "common_flow_create_task",
                "common_flow_edit",
                "common_flow_delete",
                "common_flow_view",
                "common_flow_create",
                "common_flow_create_periodic_task"
            ]
        },
    ],
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
| result    | bool     | true/false 查询成功与否 |
| data      | list     | result=true时模板列表，item 信息见下面说明 |
| message   | string   | result=false时错误信息 |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  id      |    int    |      模板ID    |
|  name      |    string    |      模板名称    |
|  category      |    string    |      模板分类，分类信息见下面说明    |
|  creator      |    string    |      模板创建人   |
|  create_time      |    string    |      模板创建时间   |
|  editor      |    string 或者 null    |      模板编辑人   |
|  edit_time      |    string   |      模板最新编辑时间   |
|  auth_actions      |    array   |      用户对该资源有权限的操作   |

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

---

## get_common_template_info

### 功能描述

查询公共流程模板详情

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述          |
|---------------|------------|--------|---------------|
| template_id   | string     |   是   |  模板ID        |
| include_executor_proxy | bool | 否 | 是否包含执行人代理信息，默认 false |
| include_subprocess | bool | 否 | 是否包含子流程信息，默认 false |
| include_constants | bool | 否 | 是否包含全局变量信息，默认 false |
| include_notify | bool | 否 | 是否包含通知信息，默认 false |
| include_pipeline_tree | bool | 否 | MCP 请求时是否返回精简后的 pipeline_tree，默认 false。非 MCP 请求忽略此参数 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
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
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
| result    | bool     | true/false 查询成功与否 |
| data      | dict     | result=true 时模板详情，详细信息见下面说明 |
| message   | string   | result=false 时错误信息 |
|  trace_id     |    string  |      open telemetry trace_id     |

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

| 返回值          | 描述   |
|--------------|------|
| OpsTools     | 运维工具 |
| MonitorAlarm | 监控告警 |
| ConfManage   | 配置管理 |
| DevTools     | 开发工具 |
| EnterpriseIT | 企业IT |
| OfficeApp    | 办公应用 |
| Other        | 其它   |
| Default      | 默认   |

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

### MCP 请求说明

当请求来源于网关MCP时，部分字段会在响应中被过滤或精简：

- `data.pipeline_tree` - 默认不返回；传入 `include_pipeline_tree=true` 时返回精简版本（移除前端渲染、画布布局等冗余信息，仅保留语义信息）
- `data.template_constants` - 不返回

---

## preview_common_task_tree

### 功能描述

获取节点选择后新的任务树（针对公共流程）

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
    "trace_id": "xxx"
}
```

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | dict       | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |
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

---

## import_common_template

### 功能描述

导入公共流程

### 请求参数

#### 接口参数

|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   template_data    |   string     |   是   |  公共流程数据，即从标准运维 - 公共流程 - 导出功能下载的文件的内容 |
|   override        | bool     | 否         | 是否覆盖 ID 相同的流程           |           |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "template_data": "xxx",
    "override": true
}
```

### 返回结果示例

```
{
    "message": "Successfully imported 2 common flows",
    "data": {
        "count": 2,
        "flows": {
              11: "flowA",
              12: "flowB",
              ...
        },
    },
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  message      | string     | result=false 时错误信息        |
|  data         | dict        | 返回数据                    |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 名称    | 类型   | 说明         |
|-------|------|------------|
| count | int  | 导入的流程数     |
| flows  | dict | 导入的流程ID与名字的映射 |

---

# 任务管理

## create_task

### 功能描述

通过流程模板创建任务

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
|   exclude_task_nodes_id | list |   否   | 跳过执行的节点ID列表（与execute_task_nodes_id同时存在时execute_task_nodes_id优先） |
|   template_schemes_id | list/string/integer |   否   | 执行方案 ID 列表或单个执行方案 ID，支持 get_template_schemes 返回的字符串 ID 和执行方案整型 ID；不能与 pipeline_tree 同时使用；与 exclude_task_nodes_id、execute_task_nodes_id 同时存在非空值时会返回参数错误 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|
|   simplify_vars     |   list     |   否   |  需要进行类型简化的参数 key 列表。（类型简化后的参数在创建任务后会丢失模板中原本配置的类型，全部变成本文框类型的变量，通过使用这个选项能够在 API 调用时屏蔽不同类型变量 value 格式的差异，统一通过文本类型传递 value） |
| execute_task_nodes_id | list | 否 | 仅执行的节点ID列表（与exclude_task_nodes_id同时存在时execute_task_nodes_id优先） |
| callback_url | string | 否 | 任务执行完成后的回调地址 |

#### constants KEY

变量 KEY，${key} 格式

#### constants VALUE

变量值，value 的类型和从模板获取的全局变量中 value 类型保持一致

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "name": "tasktest",
    "bk_biz_id":"1",
    "template_id":"1",
    "template_source":"business",
    "flow_type": "common",
    "constants": {
        "${content}": "echo 1",
        "${params}": "",
        "${script_timeout}": 20
    },
    "simplify_vars": ["${k1}", "${k2}", "${ip}", "${force_check}"],
    "execute_task_nodes_id": [],
    "exclude_task_nodes_id": [],
    "template_schemes_id": ["1-方案A"],
    "scope": "cmdb_biz",
    "callback_url": "http://xxx.com"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "task_id": 10,
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
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时成功数据，详细信息请见下面说明      |
|  message     |    string  |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

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

### MCP 请求说明

当请求来源于网关MCP时，以下字段会在响应中被过滤，不会返回：

- `data.pipeline_tree` - 流程树信息

---

## create_and_start_task

### 功能描述

通过流程模板创建并开始执行任务

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   template_id     |   string     |   是   |  模板ID |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |
|   template_source | string   | 否         | 流程模板来源，business:默认值，业务流程，common：公共流程 |
|   name     |   string     |   是   |  任务名称 |
|   flow_type     |   string     |   否   |  任务流程类型，common: 常规流程，common_func：职能化流程 |
|   constants     |   dict     |   否   |  任务全局参数，详细信息见下面说明 |
|   exclude_task_nodes_id | list |   否   |  跳过执行的节点ID列表 |
|   template_schemes_id | list/string/integer | 否 | 执行方案 ID 列表或单个执行方案 ID，支持 get_template_schemes 返回的字符串 ID 和执行方案整型 ID；与 exclude_task_nodes_id 同时存在非空值时会返回参数错误 |
| description           | string | 否   | pipeline_instance的描述信息                               |
| callback_url | string | 否 | 任务执行完成后的回调地址 |

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
    "scope": "cmdb_biz",
    "name": "tasktest",
    "flow_type": "common",
    "constants": {
        "${content}": "echo 1",
        "${params}": "",
        "${script_timeout}": 20
    },
    "exclude_task_nodes_id": [],
    "template_schemes_id": ["1-方案A"],
    "callback_url": "http://xxx.com",
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
    "trace_id": "ebc2a953abbc4955a993f88242c7f808"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时成功数据，详细信息请见下面说明      |
|  message     |    string  |      result=false 时错误信息     |
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

---

## fast_create_task

### 功能描述

创建一次性任务

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id  |   int      |   是   |  项目ID           |
|   name        |   string   |   是   |  任务名称         |
|   pipeline_tree | dict     |   是   |  任务实例树，详细信息请见下面说明 |
|   has_common_subprocess | bool | 否 |  所包含的子流程来源，true：来自公共流程模版，false：来自项目流程模版，默认值为false |
|   flow_type   |   string   |   否   |  任务流程类型，common: 常规流程，common_func：职能化流程，默认值为common |
|   description |   string   |   否   |  任务描述         |
|   category    |   string   |   否   |  任务分类，详细信息请见下面说明 |

#### category

| 值           | 描述     |
|--------------|----------|
| OpsTools     | 运维工具  |
| MonitorAlarm | 监控告警  |
| ConfManage   | 配置管理  |
| DevTools     | 开发工具  |
| EnterpriseIT | 企业IT   |
| OfficeApp    | 办公应用  |
| Other        | 其它     |

#### pipeline_tree

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|--------|-----------|
|  start_event | dict  | 是     |  开始节点，详细信息请见下面说明 |
|  end_event   | dict  | 是     |  结束节点，详细信息请见下面说明 |
|  activities  | dict  | 是     |  任务节点（标准插件和子流程），详细信息请见下面说明 |
|  flows       | dict  | 是     |  顺序流（节点连线），详细信息请见下面说明 |
|  gateways    | dict  | 否     |  网关节点（并行网关、分支网关和汇聚网关），详细信息请见下面说明 |
|  constants   | dict  | 否     |  全局变量，详细信息请见下面说明    |
|  outputs     | list  | 否     |  输出参数，标记 constants 中的输出字段    |

#### pipeline_tree.start_event

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  id       |  string  | 是    | 开始节点 ID，在 pipeline_tree 所有ID中全局唯一 |
|  type     |  string  | 是    | 开始节点类型，当前只支持 EmptyStartEvent: 空开始类 |
|  name     |  string  | 是    | 开始节点名称，可为空 |
|  incoming |  string  | 是    | 入度顺序流 ID，必须为空字符串    |
|  outgoing |  string  | 是    | 出度顺序流 ID    |

#### pipeline_tree.end_event

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  id       |  string  | 是    | 结束节点 ID，在 pipeline_tree 所有ID中全局唯一 |
|  type     |  string  | 是    | 结束节点类型，当前只支持 EmptyEndEvent：空结束类 |
|  name     |  string  | 是    | 结束节点名称，可为空 |
|  incoming |  string  | 是    | 入度顺序流 ID    |
|  outgoing |  string  | 是    | 出度顺序流 ID，必须为空字符串    |

#### pipeline_tree.activities KEY、pipeline_tree.flows KEY、pipeline_tree.gateways KEY

流程元素 ID，string 类型，在 pipeline_tree 所有 ID 中全局唯一，用来标识拓扑关系

#### pipeline_tree.activities VALUE

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  id       |  string  | 是    | 任务节点 ID，同 KEY 一致 |
|  type     |  string  | 是    | 任务节点类型，当前只支持 ServiceActivity：标准插件节点 |
|  name     |  string  | 是    | 任务节点名称 |
|  component |  dict   | 是    | 插件配置，详细信息请见下面说明 |
|  error_ignorable | bool | 是 | 节点失败是否自动忽略 |
|  retryable |  bool   | 是    | 节点失败后是否可以重试，error_ignorable 为 true 时该参数无效 |
|  skippable |  bool   | 是    | 节点失败后是否可以跳过，error_ignorable 为 true 时该参数无效 |
|  incoming |  string  | 是    | 入度顺序流 ID |
|  outgoing |  string  | 是    | 出度顺序流 ID |
|  stage_name | string | 否    | 步骤分组名称 |

#### pipeline_tree.activities VALUE.component

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  code     |  string  | 是    | 标准插件编码 |
|  data     |  dict    | 是    | 标准插件输入参数 |

#### pipeline_tree.flows VALUE

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
| id        |  string  | 是    | 顺序流 ID，同 KEY 一致 |
| is_default|  bool    | 是    | 是否默认分支 |
| source    |  string  | 是    | 来源节点 ID |
| target    |  string  | 是    | 目的节点 ID |

#### pipeline_tree.gateways VALUE

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  id       |  string  | 是    | 网关节点 ID，同 KEY 一致 |
|  type     |  string  | 是    | 网关类型，ParallelGateway：并行网关，ExclusiveGateway：分支网关，ConvergeGateway：汇聚网关|
|  name     |  string  | 是    | 网关节点名称，可为空 |
|  incoming |  string/list| 是 | 入度顺序流 ID，type 为 ConvergeGateway 时是 list，否则是 string|
|  outgoing |  string/list| 是 | 出度顺序流 ID，type 为 ConvergeGateway 时是 string，否则是 list |
|  conditions | dict   | 否    | 分支条件，type 为 ExclusiveGateway 必填， 详细信息请见下面说明 |

#### pipeline_tree.gateways VALUE.conditions KEY

网关出度顺序流 ID，和 outgoing 列表中一一对应

#### pipeline_tree.gateways VALUE.conditions VALUE

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
| evaluate  |  string  | 是    | 分支表达式，支持的语法请参考产品白皮书等文档 |

#### pipeline_tree.constants KEY

全局变量 KEY，"${key}" 格式

#### pipeline_tree.constants VALUE

| 字段      | 类型      | 必选   | 描述      |
|-----------|----------|-------|-----------|
|  key      |    string | 是    | 同 KEY 一致 |
|  name     |    string | 是    | 变量名字    |
|  index    |    int    | 是    | 变量在任务中的显示顺序    |
|  desc     |    string | 是    | 变量说明   |
|  source_type | string | 是    | 变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选 |
|  custom_type | string | 是    | source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数 |
|  source_tag  | string | 是    | source_type=component_inputs 或 component_outputs 时有效，变量的来源插件和 Tag   |
|  source_info | dict   | 是    | source_type=component_inputs 或 component_outputs 时有效，变量的来源节点信息   |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "name": "tasktest",
    "flow_type": "common",
    "description":"...",
    "has_common_subprocess":false
    "category":"OpsTools"
    "pipeline_tree": {
        "start_event": {
            "incoming": "",
            "outgoing": "line7ed74aa679d19063b6d7037ce6db",
            "type": "EmptyStartEvent",
            "id": "node20cbeaa5379d08e8d8ed7bb44fdc",
            "name": ""
        },
        "activities": {
            "node5310ec36c0364d3094d515f8f5ef": {
                "outgoing": "linec02d1e77e1076aa9c7c2c57238e4",
                "incoming": "line7ed74aa679d19063b6d7037ce6db",
                "name": "node1",
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
                "stage_name": "stage1",
                "retryable": true,
                "skippable": true,
                "type": "ServiceActivity",
                "id": "node5310ec36c0364d3094d515f8f5ef"
            },
            "node2bf42efcebe266706c3e21326dc4": {
                "outgoing": "linef0deadac69f769440a1b0e32587e",
                "incoming": "line7587c8804d34a091dae3d321f081",
                "name": "node2",
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
                "stage_name": "stage2",
                "retryable": true,
                "skippable": true,
                "type": "ServiceActivity",
                "id": "node2bf42efcebe266706c3e21326dc4"
            },
            "node3c7dcf31454c1e9bdc9cf1cdeacc": {
                "outgoing": "linebf8f91c96a8f4eb3794ca5eb9881",
                "incoming": "line429f64cdec5d20f368611e621ef5",
                "name": "node3",
                "error_ignorable": false,
                "component": {
                    "code": "sleep_timer",
                    "data": {
                        "bk_timing": {
                            "hook": false,
                            "value": "3"
                        }
                    }
                },
                "stage_name": "stage3",
                "retryable": true,
                "skippable": true,
                "type": "ServiceActivity",
                "id": "node3c7dcf31454c1e9bdc9cf1cdeacc"
            },
            "nodedb1478a75c13f90cc400f5379949": {
                "outgoing": "line24d28a3f9f80e23e4a4fab7c4ffd",
                "incoming": "linec43c77f26af408748a9c194dbcfe",
                "name": "node4",
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
                "stage_name": "stage3",
                "retryable": true,
                "skippable": true,
                "type": "ServiceActivity",
                "id": "nodedb1478a75c13f90cc400f5379949"
            }
        },
        "end_event": {
            "incoming": "line6ea858554964a04d868cead4435a",
            "outgoing": "",
            "type": "EmptyEndEvent",
            "id": "nodebe0db4ad30cc1723c7ede37b4b5f",
            "name": ""
        },
        "flows": {
            "line24d28a3f9f80e23e4a4fab7c4ffd": {
                "is_default": false,
                "source": "nodedb1478a75c13f90cc400f5379949",
                "id": "line24d28a3f9f80e23e4a4fab7c4ffd",
                "target": "node947e423b22e49aeb77bc77528bc0"
            },
            "linebf8f91c96a8f4eb3794ca5eb9881": {
                "is_default": false,
                "source": "node3c7dcf31454c1e9bdc9cf1cdeacc",
                "id": "linebf8f91c96a8f4eb3794ca5eb9881",
                "target": "node947e423b22e49aeb77bc77528bc0"
            },
            "line7587c8804d34a091dae3d321f081": {
                "is_default": false,
                "source": "node0863aab8325b84cfa3e5db52dc61",
                "id": "line7587c8804d34a091dae3d321f081",
                "target": "node2bf42efcebe266706c3e21326dc4"
            },
            "line429f64cdec5d20f368611e621ef5": {
                "is_default": false,
                "source": "node7e97af0f55fb64276e067951dd9d",
                "id": "line429f64cdec5d20f368611e621ef5",
                "target": "node3c7dcf31454c1e9bdc9cf1cdeacc"
            },
            "line6ea858554964a04d868cead4435a": {
                "is_default": false,
                "source": "node2b6f3285cfb3961c72834bafbe1b",
                "id": "line6ea858554964a04d868cead4435a",
                "target": "nodebe0db4ad30cc1723c7ede37b4b5f"
            },
            "line9dd9c8dbbad90943f268442ab7e0": {
                "is_default": false,
                "source": "node0863aab8325b84cfa3e5db52dc61",
                "id": "line9dd9c8dbbad90943f268442ab7e0",
                "target": "node7e97af0f55fb64276e067951dd9d"
            },
            "lineabc279d9be88eb98285132ba5b75": {
                "is_default": false,
                "source": "node947e423b22e49aeb77bc77528bc0",
                "id": "lineabc279d9be88eb98285132ba5b75",
                "target": "node2b6f3285cfb3961c72834bafbe1b"
            },
            "linef0deadac69f769440a1b0e32587e": {
                "is_default": false,
                "source": "node2bf42efcebe266706c3e21326dc4",
                "id": "linef0deadac69f769440a1b0e32587e",
                "target": "node2b6f3285cfb3961c72834bafbe1b"
            },
            "linec02d1e77e1076aa9c7c2c57238e4": {
                "is_default": false,
                "source": "node5310ec36c0364d3094d515f8f5ef",
                "id": "linec02d1e77e1076aa9c7c2c57238e4",
                "target": "node0863aab8325b84cfa3e5db52dc61"
            },
            "line7ed74aa679d19063b6d7037ce6db": {
                "is_default": false,
                "source": "node20cbeaa5379d08e8d8ed7bb44fdc",
                "id": "line7ed74aa679d19063b6d7037ce6db",
                "target": "node5310ec36c0364d3094d515f8f5ef"
            },
            "linec43c77f26af408748a9c194dbcfe": {
                "is_default": false,
                "source": "node7e97af0f55fb64276e067951dd9d",
                "id": "linec43c77f26af408748a9c194dbcfe",
                "target": "nodedb1478a75c13f90cc400f5379949"
            }
        },
        "gateways": {
            "node2b6f3285cfb3961c72834bafbe1b": {
                "incoming": ["linef0deadac69f769440a1b0e32587e", "lineabc279d9be88eb98285132ba5b75"],
                "outgoing": "line6ea858554964a04d868cead4435a",
                "type": "ConvergeGateway",
                "id": "node2b6f3285cfb3961c72834bafbe1b",
                "name": ""
            },
            "node0863aab8325b84cfa3e5db52dc61": {
                "outgoing": ["line7587c8804d34a091dae3d321f081", "line9dd9c8dbbad90943f268442ab7e0"],
                "incoming": "linec02d1e77e1076aa9c7c2c57238e4",
                "name": "",
                "type": "ExclusiveGateway",
                "conditions": {
                    "line9dd9c8dbbad90943f268442ab7e0": {
                        "evaluate": "${bk_timing} <= 10"
                    },
                    "line7587c8804d34a091dae3d321f081": {
                        "evaluate": "${bk_timing} > 10"
                    }
                },
                "id": "node0863aab8325b84cfa3e5db52dc61"
            },
            "node947e423b22e49aeb77bc77528bc0": {
                "incoming": ["linebf8f91c96a8f4eb3794ca5eb9881", "line24d28a3f9f80e23e4a4fab7c4ffd"],
                "outgoing": "lineabc279d9be88eb98285132ba5b75",
                "type": "ConvergeGateway",
                "id": "node947e423b22e49aeb77bc77528bc0",
                "name": ""
            },
            "node7e97af0f55fb64276e067951dd9d": {
                "incoming": "line9dd9c8dbbad90943f268442ab7e0",
                "outgoing": ["line429f64cdec5d20f368611e621ef5", "linec43c77f26af408748a9c194dbcfe"],
                "type": "ParallelGateway",
                "id": "node7e97af0f55fb64276e067951dd9d",
                "name": ""
            }
        },
        "constants": {
            "${bk_timing}": {
                "source_tag": "sleep_timer.bk_timing",
                "source_info": {
                    "node5310ec36c0364d3094d515f8f5ef": ["bk_timing"],
                    "node2bf42efcebe266706c3e21326dc4": ["bk_timing"],
                    "nodedb1478a75c13f90cc400f5379949": ["bk_timing"]
                },
                "name": "timing",
                "index": 0,
                "custom_type": "",
                "value": "1",
                "show_type": "show",
                "source_type": "component_inputs",
                "key": "${bk_timing}",
                "desc": ""
            }
        },
        "outputs": ["${bk_timing}"]
	}
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "task_id": 10,
        "task_url": "http://bk_sops_host/taskflow/execute/3/?instance_id=10",
        "pipeline_tree": {
            "start_event": {
                "incoming": "",
                "outgoing": "line7ed74aa679d19063b6d7037ce6db",
                "type": "EmptyStartEvent",
                "id": "node20cbeaa5379d08e8d8ed7bb44fdc",
                "name": ""
            },
            "activities": {
                "node5310ec36c0364d3094d515f8f5ef": {
                    "outgoing": "linec02d1e77e1076aa9c7c2c57238e4",
                    "incoming": "line7ed74aa679d19063b6d7037ce6db",
                    "name": "node1",
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
                    "stage_name": "stage1",
                    "retryable": true,
                    "skippable": true,
                    "type": "ServiceActivity",
                    "id": "node5310ec36c0364d3094d515f8f5ef"
                },
                "node2bf42efcebe266706c3e21326dc4": {
                    "outgoing": "linef0deadac69f769440a1b0e32587e",
                    "incoming": "line7587c8804d34a091dae3d321f081",
                    "name": "node2",
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
                    "stage_name": "stage2",
                    "retryable": true,
                    "skippable": true,
                    "type": "ServiceActivity",
                    "id": "node2bf42efcebe266706c3e21326dc4"
                },
                "node3c7dcf31454c1e9bdc9cf1cdeacc": {
                    "outgoing": "linebf8f91c96a8f4eb3794ca5eb9881",
                    "incoming": "line429f64cdec5d20f368611e621ef5",
                    "name": "node3",
                    "error_ignorable": false,
                    "component": {
                        "code": "sleep_timer",
                        "data": {
                            "bk_timing": {
                                "hook": false,
                                "value": "3"
                            }
                        }
                    },
                    "stage_name": "stage3",
                    "retryable": true,
                    "skippable": true,
                    "type": "ServiceActivity",
                    "id": "node3c7dcf31454c1e9bdc9cf1cdeacc"
                },
                "nodedb1478a75c13f90cc400f5379949": {
                    "outgoing": "line24d28a3f9f80e23e4a4fab7c4ffd",
                    "incoming": "linec43c77f26af408748a9c194dbcfe",
                    "name": "node4",
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
                    "stage_name": "stage3",
                    "retryable": true,
                    "skippable": true,
                    "type": "ServiceActivity",
                    "id": "nodedb1478a75c13f90cc400f5379949"
                }
            },
            "end_event": {
                "incoming": "line6ea858554964a04d868cead4435a",
                "outgoing": "",
                "type": "EmptyEndEvent",
                "id": "nodebe0db4ad30cc1723c7ede37b4b5f",
                "name": ""
            },
            "flows": {
                "line24d28a3f9f80e23e4a4fab7c4ffd": {
                    "is_default": false,
                    "source": "nodedb1478a75c13f90cc400f5379949",
                    "id": "line24d28a3f9f80e23e4a4fab7c4ffd",
                    "target": "node947e423b22e49aeb77bc77528bc0"
                },
                "linebf8f91c96a8f4eb3794ca5eb9881": {
                    "is_default": false,
                    "source": "node3c7dcf31454c1e9bdc9cf1cdeacc",
                    "id": "linebf8f91c96a8f4eb3794ca5eb9881",
                    "target": "node947e423b22e49aeb77bc77528bc0"
                },
                "line7587c8804d34a091dae3d321f081": {
                    "is_default": false,
                    "source": "node0863aab8325b84cfa3e5db52dc61",
                    "id": "line7587c8804d34a091dae3d321f081",
                    "target": "node2bf42efcebe266706c3e21326dc4"
                },
                "line429f64cdec5d20f368611e621ef5": {
                    "is_default": false,
                    "source": "node7e97af0f55fb64276e067951dd9d",
                    "id": "line429f64cdec5d20f368611e621ef5",
                    "target": "node3c7dcf31454c1e9bdc9cf1cdeacc"
                },
                "line6ea858554964a04d868cead4435a": {
                    "is_default": false,
                    "source": "node2b6f3285cfb3961c72834bafbe1b",
                    "id": "line6ea858554964a04d868cead4435a",
                    "target": "nodebe0db4ad30cc1723c7ede37b4b5f"
                },
                "line9dd9c8dbbad90943f268442ab7e0": {
                    "is_default": false,
                    "source": "node0863aab8325b84cfa3e5db52dc61",
                    "id": "line9dd9c8dbbad90943f268442ab7e0",
                    "target": "node7e97af0f55fb64276e067951dd9d"
                },
                "lineabc279d9be88eb98285132ba5b75": {
                    "is_default": false,
                    "source": "node947e423b22e49aeb77bc77528bc0",
                    "id": "lineabc279d9be88eb98285132ba5b75",
                    "target": "node2b6f3285cfb3961c72834bafbe1b"
                },
                "linef0deadac69f769440a1b0e32587e": {
                    "is_default": false,
                    "source": "node2bf42efcebe266706c3e21326dc4",
                    "id": "linef0deadac69f769440a1b0e32587e",
                    "target": "node2b6f3285cfb3961c72834bafbe1b"
                },
                "linec02d1e77e1076aa9c7c2c57238e4": {
                    "is_default": false,
                    "source": "node5310ec36c0364d3094d515f8f5ef",
                    "id": "linec02d1e77e1076aa9c7c2c57238e4",
                    "target": "node0863aab8325b84cfa3e5db52dc61"
                },
                "line7ed74aa679d19063b6d7037ce6db": {
                    "is_default": false,
                    "source": "node20cbeaa5379d08e8d8ed7bb44fdc",
                    "id": "line7ed74aa679d19063b6d7037ce6db",
                    "target": "node5310ec36c0364d3094d515f8f5ef"
                },
                "linec43c77f26af408748a9c194dbcfe": {
                    "is_default": false,
                    "source": "node7e97af0f55fb64276e067951dd9d",
                    "id": "linec43c77f26af408748a9c194dbcfe",
                    "target": "nodedb1478a75c13f90cc400f5379949"
                }
            },
            "gateways": {
                "node2b6f3285cfb3961c72834bafbe1b": {
                    "incoming": ["linef0deadac69f769440a1b0e32587e", "lineabc279d9be88eb98285132ba5b75"],
                    "outgoing": "line6ea858554964a04d868cead4435a",
                    "type": "ConvergeGateway",
                    "id": "node2b6f3285cfb3961c72834bafbe1b",
                    "name": ""
                },
                "node0863aab8325b84cfa3e5db52dc61": {
                    "outgoing": ["line7587c8804d34a091dae3d321f081", "line9dd9c8dbbad90943f268442ab7e0"],
                    "incoming": "linec02d1e77e1076aa9c7c2c57238e4",
                    "name": "",
                    "type": "ExclusiveGateway",
                    "conditions": {
                        "line9dd9c8dbbad90943f268442ab7e0": {
                            "evaluate": "${bk_timing} <= 10"
                        },
                        "line7587c8804d34a091dae3d321f081": {
                            "evaluate": "${bk_timing} > 10"
                        }
                    },
                    "id": "node0863aab8325b84cfa3e5db52dc61"
                },
                "node947e423b22e49aeb77bc77528bc0": {
                    "incoming": ["linebf8f91c96a8f4eb3794ca5eb9881", "line24d28a3f9f80e23e4a4fab7c4ffd"],
                    "outgoing": "lineabc279d9be88eb98285132ba5b75",
                    "type": "ConvergeGateway",
                    "id": "node947e423b22e49aeb77bc77528bc0",
                    "name": ""
                },
                "node7e97af0f55fb64276e067951dd9d": {
                    "incoming": "line9dd9c8dbbad90943f268442ab7e0",
                    "outgoing": ["line429f64cdec5d20f368611e621ef5", "linec43c77f26af408748a9c194dbcfe"],
                    "type": "ParallelGateway",
                    "id": "node7e97af0f55fb64276e067951dd9d",
                    "name": ""
                }
            },
            "constants": {
                "${bk_timing}": {
                    "source_tag": "sleep_timer.bk_timing",
                    "source_info": {
                        "node5310ec36c0364d3094d515f8f5ef": ["bk_timing"],
                        "node2bf42efcebe266706c3e21326dc4": ["bk_timing"],
                        "nodedb1478a75c13f90cc400f5379949": ["bk_timing"]
                    },
                    "name": "timing",
                    "index": 0,
                    "custom_type": "",
                    "value": "1",
                    "show_type": "show",
                    "source_type": "component_inputs",
                    "key": "${bk_timing}",
                    "desc": ""
                }
            },
            "outputs": ["${bk_timing}"]
        }
    },
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 说明      |
|-----------|----------|-----------|
|  result   |  bool    | true/false 操作是否成功     |
|  data     |  dict    | result=true 时成功数据，详细信息请见下面说明      |
|  message  |  string  | result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 说明      |
|-----------|----------|-----------|
|  task_id  | int      | 任务实例ID |
|  task_url | string   | 任务实例链接 |
|  pipeline_tree | dict | 任务实例树  |

#### data.pipeline_tree

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  start_event      |    dict    |      开始节点信息     |
|  end_event      |    dict    |      结束节点信息    |
|  activities      |    dict    |      任务节点（原子和子流程）信息    |
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
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从原子输入参数勾选，component_outputs：从原子输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs/component_outputs 时有效，变量的来源原子   |
|  source_info   |   dict  |  source_type=component_inputs/component_outputs 时有效，变量的来源节点信息 |

---

## start_task

### 功能描述

开始执行任务

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string     |   是   |  模板所属业务ID |
|   task_id     |   string     |   是   |  任务ID         |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

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
    "result": true,
    "task_url": "http://paas_url/taskflow/execute/xxx/?instance_id=xxx",
    "data": {
            "task_url": task_url
    },
    "code": 3545100,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时返回数据      |
|  message     |    string  |      result=false 时错误信息     |
|  task_url    |    string  |      任务对应的url  |
|  trace_id     |    string  |      open telemetry trace_id     |

---

## operate_task

### 功能描述

操作任务，如开始、暂停、继续、终止等

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string     |   是   |  模板所属业务ID |
|   task_id     |   string     |   是   |  任务ID         |
|   action      |   string     |   是   |  操作类型       |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

#### action

| 值        | 描述     |
|-----------|----------|
| start     | 开始任务，等效于调用 start_task 接口 |
| pause     | 暂停任务，任务处于执行状态时调用  |
| resume    | 继续任务，任务处于暂停状态时调用  |
| revoke    | 终止任务  |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "action": "start",
    "bk_biz_id": "2",
    "task_id": "10",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {},
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时返回数据      |
|  message     |    string  |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

---

## get_task_list

### 功能描述

获取某个业务下的任务列表，支持任务名关键词搜索

#### 接口参数

| 字段          | 类型 | 必选   |  描述             |
|-------------|--|---------|------------------|
| bk_biz_id   | string |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
| scope       | string |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
| keyword     | string |   否   |  根据任务名关键词过滤任务列表，默认不过滤 |
| is_started  | bool |   否   |  根据任务是否已开始过滤任务列表，默认不过滤 |
| is_finished | bool |   否   |  根据任务是否已结束过滤任务列表，默认不过滤 |
| executor    | string |   否   |  根据任务执行人过滤任务列表，默认不过滤 |
| create_method | string |   否   |  根据任务创建方式过滤任务列表，可选值：app（手动）、api（API网关）、app_maker（轻应用）、periodic（周期任务）、clocked（计划任务）、mobile（移动端），默认不过滤 |
| template_id | string |   否   |  根据模板ID过滤任务列表（单个模板），默认不过滤 |
| template_ids | string |   否   |  根据模板ID列表过滤任务列表（多个模板，逗号分隔，如：1,2,3），默认不过滤 |
| is_child_taskflow | bool |   否   |  根据是否为子任务过滤任务列表，默认不过滤 |
| expected_timezone | string |   否   |  任务时间相关字段期望返回的时区，形如Asia/Shanghai |
| create_time_start | string |   否   |  根据任务创建时间起始过滤任务列表，支持格式：YYYY-MM-DD HH:MM:SS、YYYY-MM-DD HH:MM:SS +HHMM、YYYY-MM-DD HH:MM:SS+HHMM、YYYY-MM-DDTHH:MM:SSZ 或 YYYY-MM-DD，默认不过滤 |
| create_time_end | string |   否   |  根据任务创建时间结束过滤任务列表，支持格式：YYYY-MM-DD HH:MM:SS、YYYY-MM-DD HH:MM:SS +HHMM、YYYY-MM-DD HH:MM:SS+HHMM、YYYY-MM-DDTHH:MM:SSZ 或 YYYY-MM-DD，默认不过滤 |
| limit       | int |   否   |  分页，返回任务列表任务数，默认为100 |
| offset      | int |   否   |  分页，返回任务列表起始任务下标，默认为0 |
| without_count  | bool |   否   |  有无count，默认返回count |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "keyword": "定时",
    "is_started": true,
    "limit": 5,
    "offset":0,
    "is_finished": "false",
    "scope":"cmdb_biz"
}
```

#### 时间范围过滤示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "create_time_start": "2024-01-01 00:00:00",
    "create_time_end": "2024-01-31 23:59:59",
    "limit": 10,
    "offset": 0
}
```

支持的时间格式示例：
- `2024-01-01 12:00:00` - 标准格式（使用系统默认时区）
- `2024-01-01 12:00:00 +0800` - 带时区偏移（带空格）
- `2024-01-01 12:00:00+0800` - 带时区偏移（不带空格）
- `2024-01-01T12:00:00Z` - ISO 8601 UTC格式
- `2024-01-01` - 仅日期（开始时间自动设置为 00:00:00，结束时间自动设置为 23:59:59）

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": 1595,
            "name": "定时任务1_clone_20200907043931",
            "category": "其它",
            "create_method": "app",
            "creator": "admin",
            "executor": "admin",
            "start_time": "2020-09-15T06:24:00.840Z",
            "finish_time": "2020-09-15T07:12:51.128Z",
            "is_started": true,
            "is_finished": true,
            "template_source": "project",
            "template_id": "2",
            "project_id": 1,
            "project_name": "蓝鲸",
            "bk_biz_id": 2,
            "bk_biz_name": "蓝鲸",
            "auth_actions": [
                "task_view",
                "task_edit",
                "task_operate",
                "task_claim",
                "task_delete",
                "task_clone"
            ]
        },
        {
            "id": 166,
            "name": "定时测试1_20200623072621",
            "category": "运维工具",
            "create_method": "app",
            "creator": "admin",
            "executor": "admin",
            "start_time": "2020-06-23T07:26:29.522Z",
            "finish_time": null,
            "is_started": true,
            "is_finished": false,
            "template_source": "project",
            "template_id": "243",
            "project_id": 1,
            "project_name": "蓝鲸",
            "bk_biz_id": 2,
            "bk_biz_name": "蓝鲸",
            "auth_actions": [
                "task_view",
                "task_edit",
                "task_operate",
                "task_claim",
                "task_delete",
                "task_clone"
            ]
        },
        {
            "id": 159,
            "name": "新定时_20200610033932_20200610200000",
            "category": "其它",
            "create_method": "periodic",
            "creator": "sops",
            "executor": "sops",
            "start_time": "2020-06-10T12:00:00.474Z",
            "finish_time": null,
            "is_started": true,
            "is_finished": false,
            "template_source": "project",
            "template_id": "246",
            "project_id": 1,
            "project_name": "蓝鲸",
            "bk_biz_id": 2,
            "bk_biz_name": "蓝鲸",
            "auth_actions": [
                "task_view",
                "task_edit",
                "task_operate",
                "task_claim",
                "task_delete",
                "task_clone"
            ]
        },
        {
            "id": 158,
            "name": "新定时_20200610033932_20200610195200",
            "category": "其它",
            "create_method": "periodic",
            "creator": "sops",
            "executor": "sops",
            "start_time": "2020-06-10T11:52:01.245Z",
            "finish_time": null,
            "is_started": true,
            "is_finished": false,
            "template_source": "project",
            "template_id": "246",
            "project_id": 1,
            "project_name": "蓝鲸",
            "bk_biz_id": 2,
            "bk_biz_name": "蓝鲸",
            "auth_actions": [
                "task_view",
                "task_edit",
                "task_operate",
                "task_claim",
                "task_delete",
                "task_clone"
            ]
        },
        {
            "id": 157,
            "name": "新定时_20200610033932_20200610193900",
            "category": "其它",
            "create_method": "periodic",
            "creator": "sops",
            "executor": "sops",
            "start_time": "2020-06-10T11:39:00.194Z",
            "finish_time": null,
            "is_started": true,
            "is_finished": false,
            "template_source": "project",
            "template_id": "246",
            "project_id": 1,
            "project_name": "蓝鲸",
            "bk_biz_id": 2,
            "bk_biz_name": "蓝鲸",
            "auth_actions": [
                "task_view",
                "task_edit",
                "task_operate",
                "task_claim",
                "task_delete",
                "task_clone"
            ]
        }
    ],
    "count": 5,
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    list    |      result=true 时成功数据，详细信息请见下面说明     |
|  message     |    string  |      result=false 时错误信息     |
|  count       |    int     |      data列表数量                |
|  trace_id     |    string  |      open telemetry trace_id     |

##### data[item]

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  id          |    int     | 任务ID |
|  name        |    string  | 任务名 |
|  category    |    string  | 任务类型 |
|  create_method |  string  | 任务创建方式 |
|  creator     |  string    | 任务创建者 |
|  executor    |  string    | 任务执行者 |
|  start_time  |  string    | 任务开始时间 |
|  finish_time |  string    | 任务结束时间 |
|  is_started  |  bool      | 任务是否已开始 |
|  is_finished |  bool      | 任务是否已结束 |
|  template_source |  string      | 任务模版来源，如项目模版project和公共模版common |
|  template_id     |  string      | 任务模版ID |
|  project_id      |  int         | 项目ID    |
|  project_name    |  string      | 项目名称   |
|  bk_biz_id       |  int         | 业务ID    |
|  bk_biz_name     |  string      | 业务名称   |
|  auth_actions      |    array   |      用户对该资源有权限的操作   |

---

## get_task_count

### 功能描述

获取某个业务下的任务列表，支持任务名关键词搜索

#### 接口参数

| 字段          | 类型 | 必选   |  描述             |
|-------------|--|---------|------------------|
| bk_biz_id   | string |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
| scope       | string |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
| keyword     | string |   否   |  根据任务名关键词过滤任务列表，默认不过滤 |
| is_started  | bool |   否   |  根据任务是否已开始过滤任务列表，默认不过滤 |
| is_finished | bool |   否   |  根据任务是否已结束过滤任务列表，默认不过滤 |
| executor    | string |   否   |  根据任务执行人过滤任务列表，默认不过滤 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "keyword": "定时",
    "is_started": true,
    "is_finished": "false",
    "scope":"cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": 5
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict    |      result=true 时成功数据，详细信息请见下面说明     |
|  message     |    string  |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |


---

## query_task_count

### 功能描述

查询任务实例分类统计总数

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   group_by     |   string     |   是   |  分类统计维度，status：按任务状态（未执行、执行中、已完成）统计，category：按照任务类型统计，flow_type：按照流程类型统计，create_method：按照创建方式 |
|   conditions     |   dict     |   否   |  任务过滤条件 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

#### conditions

| 字段      | 类型      | 必选 | 描述      |
| ------------ | ---------- |--------| ------------------------------ |
|  template_id      |    string    |   否   |      创建任务的模板ID    |
|  name      |    string    |   否   |      任务名称   |
|  creator      |    string    |   否   |      创建人    |
|  create_time__gte      |    string    |   否   |      任务创建时间起始时间   |
|  create_time__lte      |    string    |   否   |      任务创建时间截止时间   |
|  executor      |    string    |   否   |      执行人    |
|  start_time__gte      |    string   |   否   |      任务执行时间起始时间  |
|  start_time__lte      |    string   |   否   |      任务执行时间截止时间  |
|  is_started      |    bool   |   否   |      任务是否启动  |
|  is_finished      |    bool   |   否   |      任务是否完成  |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "conditions": {
        "template_id": "1",
        "name": "template"
        "create_time__gte": "2018-07-12 10:00:00",
        "create_time__lte": "2018-07-13 15:00:00",
        "start_time__gte": "2018-07-13 11:00:00",
        "start_time__lte": "2018-07-13 12:00:00",
        "is_started": true,
        "creator": admin,
        "executor": admin,
        "is_started": true,
        "is_finished": true,
    },
    "group_by": "flow_type",
    "scope": "cmdb_biz"
}
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
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      | bool    |      true/false 操作是否成功     |
|  data        | dict  |      result=true 时返回分类统计信息，详细信息见下面说明    |
|  message     | string  |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  total      |    int    |      按照过滤条件获取的任务总数    |
|  groups     |    list   |      按照过滤条件分类分类统计详情   |

#### data.groups[]
| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  code      |    string    |      分类统计类型编码    |
|  name      |    string    |      分类统计类型名称    |
|  value     |    string    |      当前分类任务数量    |

---

## get_task_detail

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

---

## get_task_status

### 功能描述

查询任务或任务节点执行状态

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述            |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string   |   是   |  模板所属业务ID   |
|   task_id     |   string   |   是   |  任务或节点ID     |
|   subprocess_id |   string   |   否   |  任务中的子流程节点 ID   |
|   with_ex_data     |   bool   |   否   |  是否返回错误节点异常数据 |
|   with_failed_node_info | bool | 否 | 是否返回失败节点详细信息，默认 false |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "subprocess_id": "xxx",
    "with_ex_data": true,
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "id": "ndf194ddb9e6365da1902dbd51610e9a",
        "state": "FAILED",
        "name": "<class 'pipeline.core.pipeline.Pipeline'>",
        "retry": 0,
        "loop": 1,
        "skip": false,
        "error_ignorable": false,
        "version": "",
        "state_refresh_at": "2020-08-17T12:13:53.320Z",
        "elapsed_time": 55035,
        "children": {
            "n00e3a0396403a19a4517d8e2eb0b015": {
                "id": "n00e3a0396403a19a4517d8e2eb0b015",
                "state": "FINISHED",
                "name": "<class 'pipeline.core.flow.event.EmptyStartEvent'>",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "22daf98a558737e39a5ae8d3876fac7d",
                "state_refresh_at": "2020-08-17T12:13:53.254Z",
                "elapsed_time": 0,
                "children": {},
                "start_time": "2020-08-17 20:13:53 +0800",
                "finish_time": "2020-08-17 20:13:53 +0800"
            },
            "nb346e202d17387082189f95dd3f80ca": {
                "id": "nb346e202d17387082189f95dd3f80ca",
                "state": "FAILED",
                "name": "定时",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "e74df19258f535509cb104ad1ca94f00",
                "state_refresh_at": "2020-08-17T12:13:53.279Z",
                "elapsed_time": 0,
                "children": {},
                "start_time": "2020-08-17 20:13:53 +0800",
                "finish_time": "2020-08-17 20:13:53 +0800"
            }
        },
        "start_time": "2020-08-17 20:13:53 +0800",
        "finish_time": "",
        "ex_data": {
            "nb346e202d17387082189f95dd3f80ca": "定时时间需晚于当前时间"
        }
    },
    "code": 0,
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

当请求来源于网关MCP时，响应中不会过滤任何字段。

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  state      |    string    |      任务或节点状态，详细信息见下面说明    |
|  id      |    string    |      任务或节点执行态ID，不等于 task_id    |
|  skip      |    bool    |      是否跳过执行    |
|  retry      |    int    |      重试和跳过总次数   |
|  start_time      |    string    |      任务或节点执行开始时间   |
|  finish_time      |    string    |      任务或节点执行结束时间    |
|  children      |    dict   |      任务节点执行详情，详细信息见下面说明   |
|  name      |    string    |      节点名称    |
|  ex_data  |  dict  | key为失败节点ID，value为失败节点错误数据 |

#### data.state

| 返回值    | 描述      |
|----------|-----------|
| CREATED   | 未执行   |
| RUNNING   | 执行中   |
| FAILED    | 失败     |
| SUSPENDED | 暂停     |
| REVOKED   | 已终止   |
| FINISHED  | 已完成   |

#### data.children KEY

任务节点执行态ID

#### data.children VALUE

同 data 格式

---

## get_tasks_status

### 功能描述

批量查询任务执行状态

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   task_id_list     |   array     |   是   |  任务 ID 列表，限制最多查询50个任务  |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
|   include_children_status     |   bool     |   否   |  返回的结果中是否需要包含任务中节点的状态  |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id_list": [30000105, 30000101, 30000100],
    "scope": "cmdb_biz",
    "include_children_status": false
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": 30000105,
            "name": "task test tree",
            "status": {
                "id": "n580c9bf42a93bfc9a6cfe309bb3b418",
                "state": "FINISHED",
                "name": "<class 'pipeline.core.pipeline.Pipeline'>",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "",
                "elapsed_time": 41,
                "start_time": "2020-03-18 17:22:05 +0800",
                "finish_time": "2020-03-18 17:22:46 +0800"
            },
            "flow_type": "common",
            "current_flow": "finished",
            "is_deleted": false,
            "create_time": "2020-03-18 17:21:24 +0800",
            "start_time": "2020-03-18 17:22:04 +0800",
            "finish_time": "2020-03-18 17:22:46 +0800",
            "url": "url"
        },
        {
            "id": 30000101,
            "name": "task test1111",
            "status": {
                "id": "nd68a418afd23d64a6f0e69338130787",
                "state": "FAILED",
                "name": "<class 'pipeline.core.pipeline.Pipeline'>",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "",
                "elapsed_time": 1375959,
                "start_time": "2020-03-18 17:15:34 +0800",
                "finish_time": ""
            },
            "flow_type": "common",
            "current_flow": "finished",
            "is_deleted": false,
            "create_time": "2020-03-18 17:14:44 +0800",
            "start_time": "2020-03-18 17:15:33 +0800",
            "finish_time": "",
            "url": "url"
        },
        {
            "id": 30000100,
            "name": "task_name",
            "status": {
                "id": "nd14eca299643b958761e7a3e5e4b7de",
                "state": "RUNNING",
                "name": "<class 'pipeline.core.pipeline.Pipeline'>",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "",
                "elapsed_time": 1381417,
                "start_time": "2020-03-18 15:44:36 +0800",
                "finish_time": ""
            },
            "flow_type": "common",
            "current_flow": "finished",
            "is_deleted": false,
            "create_time": "2020-03-18 15:44:31 +0800",
            "start_time": "2020-03-18 15:44:35 +0800",
            "finish_time": "",
            "url": "url"
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 查询成功与否     |
|  data        |    dict      |      result=true 时返回数据，详细信息见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data 说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  id      |    string    |      任务 ID    |
|  name      |    string    |    任务名    |
|  status      |    dict    |    状态详情，详细信息见下面说明    |
|  create_time      |    string    |     任务创建时间   |
|  start_time      |    string    |     任务开始时间   |
|  finish_time      |    string    |      任务完成时间    |
| flow_type | stirng | 任务流程类型（common:普通流程任务, common_func: 职能化任务） |
| current_flow | string | 任务当前流程，详细信息见下面说明 |
| is_deleted | bool | 任务当前是否删除 |
|  children      |    dict   |      任务节点执行详情，详细信息见下面说明   |

#### data.status 说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  id      |    string    |      节点 ID    |
|  state        | string     | 执行状态，CREATED：未执行，RUNNING：执行中，FAILED：失败，NODE_SUSPENDED：暂停，FINISHED：成功 |
|  name      |    string    |     节点名   |
|  retry      |    int    |     重试次数   |
|  loop      |    int    |     循环次数   |
|  skip      |    bool    |     是否跳过   |
|  error_ignorable      |    bool    |     是否忽略错误   |
|  version      |    string    |     节点版本   |
|  elapsed_time      |    int    |     节点耗时(秒)   |
|  start_time      |    string    |     节点开始时间   |
|  finish_time      |    string    |      节点完成时间    |

#### data.children KEY

任务节点 执行态ID

#### data.children VALUE

同 status 格式

#### data.current_flow（flow_type为common）

| 名称         | 含义     |
| ------------ | -------- |
| select_steps | 步骤选择 |
| fill_params  | 参数填写 |
| execute_task | 任务执行 |
| finished     | 完成     |

#### data.current_flow（flow_type为common_func）

| 名称         | 含义       |
| ------------ | ---------- |
| select_steps | 步骤选择   |
| func_submit  | 提交需求   |
| func_claim   | 职能化认领 |
| execute_task | 任务执行   |
| finished     | 完成       |


---

## get_task_effective_time

### 功能描述

统计任务的有效执行时间（排除人工节点）

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述            |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string   |   是   |  模板所属业务ID   |
|   task_id     |   string   |   是   |  任务实例ID     |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "task_instance_id": 123456,
        "instance_id": 789012,
        "template_id": "abc123",
        "task_template_id": "456",
        "project_id": 2,
        "creator": "admin",
        "create_method": "app",
        "create_time": "2024-01-01 10:00:00",
        "start_time": "2024-01-01 10:01:00",
        "finish_time": "2024-01-01 10:30:00",
        "total_elapsed_time": 1740,
        "effective_time": 1310,
        "excluded_node_count": 2,
        "total_node_count": 10,
        "excluded_component_codes": ["bk_approve", "pause_node", "sleep_timer", "bot-approval"],
        "category": "Default"
    },
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    dict    |      result=true 时返回数据，详细信息见下面说明     |
|  message  |    string  |      result=false 时错误信息     |
|  code     |    int     |      错误码，0表示成功     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  task_instance_id      |    int    |      任务实例ID    |
|  instance_id      |    int    |      Pipeline实例ID    |
|  template_id      |    string    |      Pipeline模板ID    |
|  task_template_id      |    string    |      任务模板ID    |
|  project_id      |    int    |      项目ID    |
|  creator      |    string    |      创建者    |
|  create_method      |    string    |      任务创建方式（app/api/app_maker/periodic/clocked/mobile）    |
|  create_time      |    string    |      创建时间，格式：YYYY-MM-DD HH:MM:SS    |
|  start_time      |    string    |      启动时间，格式：YYYY-MM-DD HH:MM:SS    |
|  finish_time      |    string    |      结束时间，格式：YYYY-MM-DD HH:MM:SS    |
|  total_elapsed_time      |    int    |      总执行时间（秒）    |
|  effective_time      |    int    |      有效执行时间（秒），排除人工节点后的耗时    |
|  excluded_node_count      |    int    |      排除节点数量（人工节点数量）    |
|  total_node_count      |    int    |      总节点数量    |
|  excluded_component_codes      |    list    |      排除的节点组件代码列表，从环境变量 MANUAL_WAITING_COMPONENT_CODES 中获取，如果未配置则使用默认值：["bk_approve", "pause_node", "sleep_timer", "bot-approval"]    |
|  category      |    string    |      任务分类    |

### 说明

1. **排除节点**：人工节点（审批节点、暂停节点、定时节点等）的耗时会被排除。排除的节点类型通过环境变量 `MANUAL_WAITING_COMPONENT_CODES` 配置，多个组件代码用逗号分隔。如果未配置，则使用默认值：`bk_approve`（审批节点）、`pause_node`（暂停节点）、`sleep_timer`（定时节点）、`bot-approval`（机器人审批节点）。

2. **被终止的任务**：如果任务有终止操作（revoke），接口会返回错误，因为被终止的任务无法准确计算有效执行时间。

3. **任务状态要求**：只有已完成的任务才能统计有效执行时间，如果任务尚未完成，接口会返回错误。


---

## modify_constants_for_task

### 功能描述

修改任务名称和变量

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   task_id      |   string     |   是   |  任务ID，需要任务状态是未开始的 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   constants    |   dict       |   是   |  任务全局参数，详细信息见下面说明 |
|   name         |   string     |   否   |  任务新名称  |
|   scope        |   string     |   否   |  bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

#### constants KEY

变量 KEY，${key} 格式

#### constants VALUE

变量值

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "constants": {
        "${bk_timing}": "100"
    },
    "name":"",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "data": "success",
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    string  |      result=true 时成功数据, "success" |
|  message     |    string  |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

---

# 节点操作

## get_task_node_data

### 功能描述

获取任务节点的数据

#### 接口参数

| 字段          |  类型       | 必选   | 描述                                                                                        |
|-----------------|-------------|---------|-------------------------------------------------------------------------------------------|
|   bk_biz_id       |   string     |   是   | 项目唯一 ID，项目 ID 或 CMDB 业务 ID                                                                |
|   task_id       |   int     |   是   | 任务 ID                                                                                     |
|   scope       |   string     |   否   | 唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
| node_id        | string     | 是         | 节点 ID                                                                                     |
| component_code| string     | 是         | 原子编码                                                                                      |
| subprocess_stack| string   | 否         | 子流程堆栈，json 格式的列表                                                                          |
| template_node_id| string   | 否         | 模板节点 ID，传入后可返回节点历史执行时间                                                                    |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": 11,
    "node_id": "ndfbcbdc77e9350ba18222dc4a0a435f",
    "component_code": "sleep_timer",
    "scope": "cmdb_biz",
    "subprocess_stack":"[1, 2]",
    "template_node_id":"node3b8d4f3b06b1dc37cf1a748c77ed"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "inputs": {
            "bk_timing": "123"
        },
        "outputs": [
            {
                "name": "执行结果",
                "key": "_result",
                "value": "",
                "preset": true
            },
            {
                "name": "循环次数",
                "key": "_loop",
                "value": "",
                "preset": true
            }
        ],
        "ex_data": "",
        "execution_time": [
            {
                "archived_time": "2022-11-17T19:10:27+08:00",
                "elapsed_time": 40
            },
            {
                "archived_time": "2022-11-17T17:35:56+08:00",
                "elapsed_time": 20
            }
        ]
    },
    "message": "",
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | object     | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  inputs       | object     | 输入参数，key：value格式       |
|  outputs      | array      | 输出参数，详情见下面说明       |
|  ex_data      | string     | 节点执行失败详情，json字符串或者HTML字符串、普通字符串 |
| execution_time | array    | 节点执行时间，详情见下面说明   |

##### outputs[]

| 名称     | 类型                        | 说明             |
|--------|---------------------------|----------------|
| name   | string                    | 输出参数名称         |
| value  | string、int、bool、dict、list | 输出参数值          |
| key    | string                    | 输出参数 KEY       |
| preset | bool                      | 是否是原子定义中预设输出变量 |


##### execution_time[]
| 名称            | 类型     | 说明          |
|---------------|--------|-------------|
| archived_time | string | 节点执行时间      |
| elapsed_time  | int    | 节点执行耗时，单位为秒 |


---

## get_task_node_detail

### 功能描述

查询任务节点执行详情

#### 接口参数

| 字段               | 类型     | 必选  | 描述                  |
|------------------|--------|-----|---------------------|
| bk_biz_id        | string | 是   | 所属业务ID              |
| task_id          | string | 是   | 任务ID                |
| node_id          | string | 是   | 节点 ID               |
| component_code   | string | 否   | 标准插件编码，请求标准插件执行详情必填 |
| subprocess_stack | string | 否   | 子流程堆栈，json 格式的列表    |
| loop             | int    | 否   | 节点循环次数              |
| max_histories    | int    | 否   | MCP 请求时返回最近 N 条重试记录，默认 3。0 表示不返回。非 MCP 请求忽略此参数 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd"
    "subprocess_stack": "[\"nodeaaa0ce51d2143aa9b0dbc27cb7df\"]",
    "component_code": "job_fast_execute_script",
    "loop": 1,
}
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
                "key": "job_inst_id",
                "preset": true
            },
            {
                "value": "",
                "name": "JOB任务链接",
                "key": "job_inst_url",
                "preset": true
            },
            {
                "value": true,
                "name": "执行结果",
                "key": "_result",
                "preset": true
            }
        ],
        "state": "FINISHED",
        "version": "23ac8c29f62b3337aafcf1f538d277f8",
        "error_ignorable": false,
        "id": "node0df0431f8f553925af01a94854bd",
        "loop": 1
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

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  id           | string     | 节点 ID                        |
|  start_time   | string     | 最后一次执行开始时间           |
|  finish_time  | string     | 最后一次执行结束时间           |
|  elapsed_time | int        | 最后一次执行耗时，单位秒       |
|  state        | string     | 最后一次执行状态，CREATED：未执行，RUNNING：执行中，FAILED：失败，NODE_SUSPENDED：暂停，FINISHED：成功 |
|  skip         | bool       | 是否手动跳过                   |
|  retry        | int        | 重试次数                       |
|  inputs       | dict       | 输入参数，key：value格式       |
|  outputs      | list       | 输出参数，详情见下面说明       |
|  ex_data      | string     | 节点执行失败详情，json字符串或者HTML字符串、普通字符串 |
|  histories    | list       | 重试记录详情，详情见下面说明   |

#### outputs[]
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  name         | string     | 输出字段                   |
|  value        | string、int、bool、dict、list | 输出参数值  |
|  key          | string     | 输出参数 KEY                   |
|  preset       | bool       | 是否是标准插件定义中预设输出变量   |


#### histories[]
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  start_time   | string     | 执行开始时间                   |
|  finish_time  | string     | 执行结束时间                   |
|  elapsed_time | int        | 执行耗时                       |
|  state        | string     | 执行状态，CREATED：未执行，RUNNING：执行中，FAILED：失败，NODE_SUSPENDED：暂停，FINISHED：成功 |
|  skip         | bool       | 是否手动跳过                   |
|  retry        | int        | 重试次数                       |
|  histories    | list       | 重试记录详情，详情见下面说明   |
|  inputs       | dict       | 输入参数，key：value格式       |
|  outputs      | dict       | 输出参数，key：value格式       |
|  ex_data      | string     | 节点执行失败详情，json字符串或者HTML字符串、普通字符串 |

### MCP 请求说明

当请求来源于网关MCP时，`histories` 字段仅返回最近 3 条重试记录（可通过 `max_histories` 参数调整）：

- `data.histories` - 默认返回最近 3 条，`max_histories=0` 时不返回，`max_histories=N` 时返回最近 N 条

---

## operate_node

### 功能描述

操作节点

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id       |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   task_id       |   int     |   是   |  任务 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
| node_id        | string     | 是         | 节点 ID                        |
| action        | string     | 是         | 操作类型，可选值有：callback（节点回调）, skip_exg（跳过执行失败的分支网关）, retry（重试失败节点）, skip（跳过失败的节点）, pause_subproc（暂停正在执行的子流程）, resume_subproc（继续暂停的子流程） |
| data | object   | 否         | action 为 callback 时传入的数据    |
| inputs | object   | 否         | action 为 retry 时重试节点时节点的输入数据    |
| flow_id | string   | 否         | action 为 skip_exg 时选择执行的分支 id    |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "12",
    "node_id": "node_id",
    "action": "skip",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": "success",
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | string     | result=true 时返回的信息 |
|  message      | string     | result=false 时错误信息        |
|  trace_id     |    string  |      open telemetry trace_id     |

---

## node_callback

### 功能描述

回调指定的节点（通常用于暂停等待类节点的人工审批回调场景）

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id      |   string     |   是   |  任务ID |
|   node_id      |   string     |   是   |  节点 ID |
|   callback_data |  dict       |   否   |  回调数据，传递给节点的回调参数 |
|   version      |   string     |   否   |  节点版本号，用于指定回调的节点版本 |
|   scope        |   string     |   否   |  bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

### 请求参数示例

```
{
    "bk_app_code": "app_code",
    "bk_app_secret": "app_secret",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd",
    "callback_data": {
        "data": {}
    },
    "version": "23ac8c29f62b3337aafcf1f538d277f8",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "message": "success",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 操作成功与否     |
|  message  |    string  |      result=false 时错误信息     |
|  trace_id |    string  |      open telemetry trace_id     |

---

## get_tasks_manual_intervention_state

### 功能描述

获取一批任务的是否需要人工干预的判断状态

当流程中存在以下情况时，就判定为需要人工介入：

- 存在运行中的暂停插件节点
- 存在失败的节点
- 存在处于暂停状态的子流程
- 流程处于暂停状态

#### 接口参数

| 字段         | 类型   | 必选 | 描述                                                                                                                     |
| ------------ | ------ | ---- | ------------------------------------------------------------------------------------------------------------------------ |
| bk_biz_id    | string | 是   | 模板所属业务ID                                                                                                           |
| task_id_list | array  | 是   | 任务 ID 列表                                                                                                             |
| scope        | string | 否   | 唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id_list": [30000105, 30000101, 30000100],
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": 81,
            "manual_intervention_required": false
        },
        {
            "id": 80,
            "manual_intervention_required": true
        },
        {
            "id": 79,
            "manual_intervention_required": true
        },
        {
            "id": 78,
            "manual_intervention_required": false
        },
        {
            "id": 77,
            "manual_intervention_required": false
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 名称    | 类型   | 说明                                       |
| ------- | ------ | ------------------------------------------ |
| result  | bool   | true/false 查询成功与否                    |
| data    | dict   | result=true 时返回数据，详细信息见下面说明 |
| message | string | result=false 时错误信息                    |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data 说明
| 名称                         | 类型 | 说明             |
| ---------------------------- | ---- | ---------------- |
| id                           | int  | 任务 ID          |
| manual_intervention_required | bool | 是否需要人工干预 |

---

# 周期任务

## create_periodic_task

### 功能描述

创建周期任务

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   template_id    |   string     |   是   |  用于创建任务的模板ID |
| template_source | string   | 否     | 流程模板来源，business:默认值，业务流程，common：公共流程 |
|   bk_biz_id    |   string     |   是   |  任务所属业务ID |
|   name    |   string     |   是   |  要创建的周期任务名称 |
|   cron    |   dict     |   是   |  要创建的周期任务调度策略 |
|   constants    |   dict     |   否   | 任务全局参数，详细信息见下面说明 |
|   exclude_task_nodes_id    |   list     |   否   |  跳过执行的节点ID列表 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

#### constants KEY

变量 KEY，${key} 格式

#### constants VALUE

变量值

#### cron

|   参数名称   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   minute    |   string     |   否   |  分，默认为 * |
|   hour    |   string     |   否   |  时，默认为 * |
|   day_of_week    |   string     |   否   |  一周内的某些天，默认为 * |
|   day_of_month    |   string     |   否   |  一个月中的某些天，默认为 * |
|   month_of_year    |   string     |   否   |  一年中的某些月份，默认为 * |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "template_id": "1",
    "bk_biz_id": "2",
    "template_source": "business",
	"name": "from api 3",
	"cron" : {
	    "minute": "*/1", 
	    "hour": "15", 
	    "day_of_week":"*", 
	    "day_of_month":"*", 
	    "month_of_year":"*"
    },
	"constants": {
	    "${bk_timing}": "100"
    },
	"exclude_task_nodes_id": ["nodea5c396a3ef0f9f3cd7d4d7695f78"],
	"scope":"cmdb_biz"
}
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
        "template_id": 2,
        "template_source": "business"
    },
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

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
| template_source | string    | 流程模板来源，business:默认值，业务流程，common：公共流程 |
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

#### data.form KEY, data.pipeline_tree.constants KEY

全局变量 KEY，${key} 格式

#### data.form VALUE, data.pipeline_tree.constants VALUE

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

---

## get_periodic_task_list

### 功能描述

查询某个业务下所有的周期任务

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   是   |  任务所属业务ID |
| include_edit_info | bool | 否 | 是否包含编辑信息，默认 false |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|
| expected_timezone | string |   否   |  任务时间相关字段期望返回的时区，形如Asia/Shanghai |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "scope": "cmdb_biz"
}
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
            "template_id": "2",
            "auth_actions": [
                "periodic_task_view",
                "periodic_task_delete",
                "periodic_task_edit"
            ]
        },
        {
            "cron": "1,2,3-19/2 2 3 4 5 (m/h/d/dM/MY)",
            "total_run_count": 0,
            "name": "from api 1",
            "creator": "admin",
            "last_run_at": "",
            "enabled": false,
            "id": 6,
            "template_id": "2",
            "auth_actions": [
                "periodic_task_view",
                "periodic_task_delete",
                "periodic_task_edit"
            ]
        },
        {
            "cron": "*/5 * * * * (m/h/d/dM/MY)",
            "total_run_count": 0,
            "name": "定时",
            "creator": "admin",
            "last_run_at": "",
            "enabled": false,
            "id": 4,
            "template_id": "2",
            "auth_actions": [
                "periodic_task_view",
                "periodic_task_delete",
                "periodic_task_edit"
            ]
        }
    ],
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |


#### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  cron      |    string    |      周期调度表达式    |
|  total_run_count      |    int    |    周期任务运行次数   |
|  name      |    string    |    周期任务名   |
|  creator      |    string    |    创建者   |
|  last_run_at      |    string    |    上次运行时间   |
|  enabled      |    bool    |    是否激活   |
|  id      |    int    |    周期任务ID   |
|  template_id      |    string    |    用于创建该任务的模板ID   |
|  auth_actions      |    array   |      用户对该资源有权限的操作   |


---

## get_periodic_task_info

### 功能描述

查询某个周期任务的详情

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   task_id    |   string     |   是   |  周期任务ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "scope":"cmdb_biz"
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
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

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

#### data.form KEY, data.pipeline_tree.constants KEY

全局变量 KEY，${key} 格式

#### data.form VALUE, data.pipeline_tree.constants VALUE

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

---

## modify_cron_for_periodic_task

### 功能描述

修改周期任务的调度策略

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   task_id    |   string     |   是   |  周期任务ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   cron    |   dict     |   否   | 调度策略对象 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

#### cron
 
 |   参数名称   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   minute    |   string     |   否   |  分，默认为 * |
|   hour    |   string     |   否   |  时，默认为 * |
|   day_of_week    |   string     |   否   |  一周内的某些天，默认为 * |
|   day_of_month    |   string     |   否   |  一个月中的某些天，默认为 * |
|   month_of_year    |   string     |   否   |  一年中的某些月份，默认为 * |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "cron" : {
	    "minute": "*/1", 
	    "hour": "15", 
	    "day_of_week":"*", 
	    "day_of_month":"*", 
	    "month_of_year":"*"
    },
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "data": {
        "cron": "*/1 15 * * * (m/h/d/dM/MY)"
    },
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  cron      |    string    |      调度策略表达式    |

---

## modify_constants_for_periodic_task

### 功能描述

修改周期任务的全局参数

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   task_id    |   string     |   是   |  周期任务ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   constants    |   dict     |   否   | 任务全局参数，详细信息见下面说明 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

#### constants KEY

变量 KEY，${key} 格式

#### constants VALUE

变量值

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "constants": {
        "${bk_timing}": "100"
    },
    "scope": "cmdb_biz"
}
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
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data KEY
全局变量 KEY，${key} 格式

#### data VALUE

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

---

## set_periodic_task_enabled

### 功能描述

设置某个周期任务是否激活

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   task_id    |   string     |   是   |  周期任务ID |
|   bk_biz_id    |   string     |   是   |  任务所属业务ID |
|   enabled    |   bool     |   否   | 该周期任务是否激活，不传则为 false |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "enabled": false,
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "data": {
        "enabled": false
    },
    "result": true,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  enabled      |    bool    |      当前周期任务是否已经激活    |

---

# 计划任务

## create_clocked_task

### 功能描述

创建计划任务

### 请求参数

#### 接口参数

| 字段               | 类型     | 必选  | 描述                                                                                                       |
|------------------|--------|-----|----------------------------------------------------------------------------------------------------------|
| bk_biz_id        | string | 是   | 任务所属业务ID                                                                                                 |
| template_id      | string | 是   | 用于创建任务的模板ID                                                                                              |
| task_name        | string | 是   | 要创建的计划任务名称                                                                                               |
| plan_start_time  | string | 是   | 计划任务开始时间，推荐带上时区信息，格式如 `2022-05-16 20:26:40+0800`                                                         |
| task_parameters  | dict   | 否   | 任务参数, 详见下面说明                                                                                             |
| scope            | string | 否   | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

#### task_parameters

| 参数名称          | 参数类型  | 必须 |     参数说明     |
|---------------|-------|--| ---------------- |
| constants     | dict  | 否 |  计划任务参数，对应变量key和value，默认为 `{}` |
| template_schemes_id    | list     | 否 | 计划任务使用的执行方案列表，默认为 `[]`，代表执行所有流程节点 |

#### constants KEY

变量 KEY，${key} 格式

#### constants VALUE

变量值

### 请求参数示例

```
{
    "bk_app_code": "app_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "template_id": "1",
    "bk_biz_id": "2",
	"scope":"cmdb_biz",
    "task_name": "test_clocked_task",
    "plan_start_time": "2022-05-16 20:26:40+0800",
    "task_parameters": {
        "constants": {},
        "template_schemes_id": []
    },
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "id": 72,
        "task_parameters": {
            "constants": {},
            "template_schemes_id": []
        },
        "creator": "",
        "plan_start_time": "2022-05-16 20:26:40+0800",
        "project_id": 1,
        "task_id": null,
        "task_name": "test_clocked_task",
        "template_id": 508,
        "template_name": "测试模版",
        "template_source": "project",
        "clocked_task_id": 88
    },
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 名称         | 类型     | 说明                           |
|------------|--------|------------------------------|
| result     | bool   | true/false 操作是否成功            |
| data       | dict   | result=true 时成功数据，详细信息请见下面说明 |
| message    | string | result=false 时错误信息           |
| trace_id   | string | open telemetry trace_id      |

#### data

| 名称               | 类型     | 说明                 |
|------------------|--------|--------------------|
| id               | int    | 计划任务 ID            |
| task_id          | int    | 任务 ID，任务未创建时为 null |
| task_name        | string | 任务名                |
| task_parameters  | dict   | 任务参数               |
| creator          | string | 创建者                |
| plan_start_time  | string | 计划任务开始时间           |
| project_id       | int    | 项目 ID              |
 | template_id      | int    | 模板 ID              |
| template_name    | string | 模板名称               |
| template_source  | string | 模板来源               |

---

# 职能化任务

## get_functionalization_task_list

### 功能描述

获取职能化任务列表，支持根据任务状态、原任务id和职能化任务id进行筛选。

#### 接口参数

| 字段                | 类型     | 必选  | 描述                                                                                 |
|-------------------|--------|-----|------------------------------------------------------------------------------------|
| status            | string | 否   | 职能化任务状态（任务阶段），对应关系：submitted:未认领, claimed:已认领, rejected:已驳回, executed:已执行, finished:已完成。 |
| execute_status    | string | 否   | 任务执行状态，可选值：nonExecution（未执行）、running（未完成）、revoked（终止）、finished（完成），默认不过滤。 |
| id_in             | string | 否   | 职能化任务筛选id来源列表，以逗号`,`分隔                                                             |
| task_id_in        | string | 否   | 职能化任务筛选原任务id来源列表，以逗号`,`分隔（对应页面”任务ID“）                                              |
| expected_timezone | string | 否   | 任务时间相关字段期望返回的时区，形如Asia/Shanghai                                                    |
| project_id        | int    | 否   | 项目id作为过滤条件，仅支持标准运维项目id，非ccid                                                       | 
| creator           | string | 否   | 根据提单人过滤任务列表，支持模糊搜索（使用`icontains`），默认不过滤。**注意：不支持多个用户同时筛选**                                   |
| claimant          | string | 否   | 根据认领人过滤任务列表，支持模糊搜索（使用`icontains`），默认不过滤。**注意：不支持多个用户同时筛选**                                   |
| limit             | int    | 否   | 分页，返回任务列表任务数，默认为100                                                                |
| offset            | int    | 否   | 分页，返回任务列表起始任务下标，默认为0                                                               |
| create_time_gte   | string | 否   | 职能化任务创建时间起始时间                                                                   |
| create_time_lte   | string | 否   | 职能化任务创建时间截止时间                                                              |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "id_in": "412,411"
    "task_id_in": "414,413",
    "status": "submitted",
    "limit": 50,
    "offset": 0
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": 6,
            "name": "定时测试_20201110041712",
            "creator": "admin",
            "create_time": "2020-11-10T04:17:15.586Z",
            "claimant": "",
            "claim_time": null,
            "rejecter": "",
            "reject_time": null,
            "predecessor": "",
            "transfer_time": null,
            "status": "submitted",
            "task": {
                "id": 414,
                "name": "定时测试_20201110041712",
                "category": "监控告警",
                "create_method": "app",
                "creator": "admin",
                "executor": "",
                "start_time": null,
                "finish_time": null,
                "is_started": false,
                "is_finished": false,
                "template_source": "project",
                "template_id": "306"
            }
        },
        {
            "id": 5,
            "name": "定时测试_20201110034326",
            "creator": "admin",
            "create_time": "2020-11-10T03:43:29.104Z",
            "claimant": "",
            "claim_time": null,
            "rejecter": "",
            "reject_time": null,
            "predecessor": "",
            "transfer_time": null,
            "status": "submitted",
            "task": {
                "id": 413,
                "name": "定时测试_20201110034326",
                "category": "监控告警",
                "create_method": "app",
                "creator": "admin",
                "executor": "",
                "start_time": null,
                "finish_time": null,
                "is_started": false,
                "is_finished": false,
                "template_source": "project",
                "template_id": "306"
            }
        }
    ],
    "code": 0,
    "count": 2,
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    list    |      result=true 时成功数据，详细信息请见下面说明     |
|  message     |    string  |      result=false 时错误信息     |
| count | int | data列表数量 |
|  trace_id     |    string  |      open telemetry trace_id     |

##### data[item]

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  id          |    int     | 职能化任务ID |
|  name        |    string  | 任务名称 |
| creator |    string  | 创建人 |
| create_time |  string  | 创建时间 |
| claimant |  string    | 认领人 |
| claim_time |  string    | 认领时间 |
|  rejecter  |  string    | 驳回人 |
| reject_time |  string    | 驳回时间 |
|  predecessor  |  string    | 转单人 |
| transfer_time |  string    | 转单时间 |
| status |  string      | 职能化任务状态，对应关系：submitted:未认领, claimed:已认领, rejected:已驳回, executed:已执行, finished:已完成。 |
|  task |  dict  | 职能化任务对应流程任务对象，详细信息见下面说明 |

##### data.task

| 名称            | 类型   | 说明           |
| --------------- | ------ | -------------- |
| id              | int    | 任务ID         |
| name            | string | 任务名称       |
| category        | string | 任务类型       |
| create_method   | string | 创建方式       |
| creator         | string | 创建人         |
| executor        | string | 执行人         |
| start_time      | string | 开始时间       |
| is_started      | bool   | 任务是否已开始 |
| finish_time     | string | 任务完成时间   |
| is_finished     | bool   | 任务是否已完成 |
| template_id     | string | 模版id         |
| template_source | string | 模版来源       |





---

## claim_functionalization_task

### 功能描述

职能化任务认领

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   task_id      |   string     |   是   |  任务ID，需要任务状态是未开始的 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   constants    |   dict       |   是   |  任务全局参数，详细信息见下面说明 |
|   name         |   string     |   否   |  任务新名称  |
|   scope        |   string     |   否   |  bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

#### constants KEY

变量 KEY，${key} 格式

#### constants VALUE

变量值

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username":"xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "constants": {
        "${bk_timing}": "100"
    },
    "name": "xxx",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "data": "success",
    "result": true, 
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    string  |      result=true 时成功数据, "success" |
|  code        |    int     |      结果状态码                  |
|  message     |    string  |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

---

# 轻应用

## get_mini_app_list

### 功能描述

获取业务下的轻应用列表

### 请求参数

#### 接口参数

| 字段        | 类型     | 必选  | 描述                                                                                                       |
|-----------|--------|-----|----------------------------------------------------------------------------------------------------------|
| bk_biz_id | string | 是   | 任务所属业务ID                                                                                                 |
| scope     | string | 否   | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |
| limit     | int    | 否   | 分页，返回任务列表任务数，默认为100，最大为200                                                                               |
| offset    | int    | 否   | 分页，返回任务列表起始任务下标，默认为0                                                                                     |

### 请求参数示例

```
{
    "bk_app_code": "app_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
	"scope":"cmdb_biz",
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "auth_actions": [
                "mini_app_view",
                "mini_app_edit",
                "mini_app_delete",
                "mini_app_create_task"
            ],
            "id": 1,
            "name": "new20210813065242",
            "code": "bk_sops20210816112820",
            "link": "xxxx",
            "category": "OpsTools",
            "task_template_id": 155,
            "template_scheme_id": ""
        }
    ],
    "count": 1,
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 名称         | 类型     | 说明                           |
|------------|--------|------------------------------|
| result     | bool   | true/false 操作是否成功            |
| data       | dict   | result=true 时成功数据，详细信息请见下面说明 |
| message    | string | result=false 时错误信息           |
| count      | int    | data列表数量                     |
| trace_id   | string | open telemetry trace_id      |

#### data

| 名称                 | 类型     | 说明           |
|--------------------|--------|--------------|
| id                 | int    | 轻应用 ID       |
| name               | string | 轻应用名         |
| code               | string | 轻应用编码        |
| link               | string | 轻应用链接        |
| task_template_id   | int    | 轻应用对应流程 ID   |
| template_scheme_id | string | 轻应用对应执行方案 ID |
| auth_actions       | array  | 用户对该资源有权限的操作 |

---

# 插件

## get_plugin_list

### 功能描述

获取某个业务下所有的可用插件

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id       |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |


### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "inputs": [],
            "outputs": [
                {
                    "name": "执行结果",
                    "key": "_result",
                    "type": "bool",
                    "schema": {
                        "type": "boolean",
                        "description": "是否执行成功",
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
            "code": "job_push_local_files",
            "name": "分发本地文件",
            "group_name": "作业平台(JOB)",
            "version": "1.0.0",
            "form": "/static/components/atoms/job/job_push_local_files.js"
        }
    ],
    "trace_id": "xxx"
}
```

### 返回结果说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
|  trace_id     |    string  |      open telemetry trace_id     |

##### data[item]
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

---

## get_plugin_detail

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
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |
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

---

# 其他

## apply_webhook_configs

### 功能描述

批量修改模板的webhook配置

### 请求参数

#### 接口参数

| 字段              | 类型      | 必选     | 描述                 |
|-----------------|---------|--------|--------------------|
| endpoint        | string  | 是      | webhook请求地址        |
| events          | list    | 是      | 订阅事件               |
| extra_info      | dict    | 否      | 额外参数，包含认证、请求头和重试信息 |
| enable_webhook  | bool    | 否      | webhook配置开关，默认开启   |
| template_ids    | list    | 是      | 需要修改的模板id列表        |

#### events 目前的订阅事件 task_failed（任务失败）和 task_finished（任务完成）

### 请求参数示例

```
{
     "endpoint": "https://xxx.com",
     "events": ["*"],
     "extra_info": {
          "authorization": {
               "type": "basic",  # bearer:token认证，basic：密码认证
               "username": "xxx",
               "password": "xxx",
               "token": "xxx"
          },
          "headers": [
               {
                    "key": "Content-Type",
                    "value": "application/json",
                    "doc": ""
               }
          ],
          "timeout": 10,
          "retry_times": 2,
          "interval": 60
     },
     "template_ids": [1]
}
```

关闭并清空指定模板的所有 webhook 配置
```json

{
   "enable_webhook": false,
   "template_ids": [1, 2]
}
```

### 返回结果示例

```
{
    "result": true,
    "message": "success",
    "code": 0,
    "trace_id": "00-3ada3cec713520ede2ab03b156d1a33d-66b28b7e5e7f59fe-01"
}
```

### 返回结果参数说明

| 字段         | 类型       | 描述                        |
|------------|----------|---------------------------|
| result     | bool     | true/false 操作是否成功         |
| message    | string   | result=false 时错误信息        |
| trace_id   | string   | open telemetry trace_id   |

---

## create_template

### 功能描述

创建项目流程模板

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   是   |  项目ID |
|   name     |   string     |   否   |  模板名称，为空时自动生成默认名称（格式：new+当前时间戳） |
|   pipeline_tree     |   dict/string     |   是   |  流程树数据。format=json 时支持传入 dict 或 JSON 字符串；format=yaml 时传入 YAML schema 字符串（与页面导出格式一致） |
|   format     |   string     |   否   |  pipeline_tree 的输入格式，可选值 json（默认）、yaml。设为 yaml 时 name 和 description 可从 YAML meta 中自动提取。注意：YAML 中只能包含一个模板定义，包含多个模板时将返回错误 |
|   description     |   string     |   否   |  模板描述，默认为空 |
|   category     |   string     |   否   |  模板分类，默认为 Default |
|   notify_type     |   dict     |   否   |  通知类型，默认为 {"success": [], "fail": []} |
|   notify_receivers     |   dict     |   否   |  通知接收人，默认为 {"receiver_group": [], "more_receiver": ""} |
|   timeout     |   int     |   否   |  超时时间（分钟），默认为 20 |
|   default_flow_type     |   string     |   否   |  流程类型，默认为 common |
|   template_labels     |   list     |   否   |  模板标签ID列表，默认为空列表 |
|   executor_proxy     |   string     |   否   |  执行代理人，默认为空 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "1",
    "name": "my_template",
    "description": "模板描述",
    "category": "Default",
    "notify_type": {
        "success": ["weixin"],
        "fail": ["weixin", "email"]
    },
    "notify_receivers": {
        "receiver_group": ["Maintainers"],
        "more_receiver": "admin"
    },
    "timeout": 30,
    "default_flow_type": "common",
    "template_labels": [1, 2],
    "executor_proxy": "",
    "pipeline_tree": {
        "activities": {
            "node9b5ae13799d63e179f0ce3088b62": {
                "outgoing": "line27bc7b4ccbcf37ddb9d1f6572a04",
                "incoming": "lineb83161d6e0593ad68d9ec73a961b",
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
            "lineb83161d6e0593ad68d9ec73a961b": {
                "is_default": false,
                "source": "noded383bc1d7387391f889c6bab18b8",
                "id": "lineb83161d6e0593ad68d9ec73a961b",
                "target": "node9b5ae13799d63e179f0ce3088b62"
            },
            "line27bc7b4ccbcf37ddb9d1f6572a04": {
                "is_default": false,
                "source": "node9b5ae13799d63e179f0ce3088b62",
                "id": "line27bc7b4ccbcf37ddb9d1f6572a04",
                "target": "node5c48f37aa9f0351e8b43ab6a2295"
            }
        },
        "gateways": {},
        "start_event": {
            "type": "EmptyStartEvent",
            "outgoing": "lineb83161d6e0593ad68d9ec73a961b",
            "incoming": "",
            "id": "noded383bc1d7387391f889c6bab18b8",
            "name": ""
        },
        "constants": {},
        "line": [
            {
                "source": {
                    "id": "noded383bc1d7387391f889c6bab18b8",
                    "arrow": "Right"
                },
                "target": {
                    "id": "node9b5ae13799d63e179f0ce3088b62",
                    "arrow": "Left"
                },
                "id": "lineb83161d6e0593ad68d9ec73a961b"
            },
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
            }
        ],
        "location": [
            {
                "y": 150,
                "x": 80,
                "type": "startpoint",
                "id": "noded383bc1d7387391f889c6bab18b8"
            },
            {
                "stage_name": "步骤1",
                "name": "timing",
                "y": 135,
                "x": 300,
                "type": "tasknode",
                "id": "node9b5ae13799d63e179f0ce3088b62"
            },
            {
                "y": 150,
                "x": 600,
                "type": "endpoint",
                "id": "node5c48f37aa9f0351e8b43ab6a2295"
            }
        ]
    },
    "scope": "cmdb_biz"
}
```

#### format=yaml 时子流程复用说明

当 `format=yaml` 时，YAML 中的 SubProcess 节点可以通过 `template_id` 引用系统中已有的流程模板作为子流程，无需在 YAML 中重复定义子流程内容。使用方式：

1. 先通过本接口或页面创建好子流程模板，获取其 `template_id`
2. 在 YAML 的 SubProcess 节点中直接引用该 `template_id`
3. 系统会自动从数据库获取被引用子流程的参数定义（constants）

示例 YAML 片段（引用已有子流程）：

```yaml
metadata:
  version: "v1"

my_template:
  meta:
    name: "主流程"
    description: "引用已有子流程的示例"
  spec:
    nodes:
      - id: node_start
        type: EmptyStartEvent
      - id: node_subprocess
        type: SubProcess
        name: "调用已有子流程"
        template_id: "123"  # 已有流程模板的 ID
      - id: node_end
        type: EmptyEndEvent
```

> **注意**：YAML 中只能定义一个模板。如果流程需要引用子流程，请先通过本接口分别创建好各子流程模板，再在主流程的 YAML 中通过 `template_id` 引用它们。

### 返回结果示例

```
{
    "result": true,
    "data": {
        "template_id": 1,
        "template_name": "my_template",
        "pipeline_template_id": "n8d35e3c1a3f3290b9fabd3e69a5b7"
    },
    "code": 0,
    "message": "success",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时成功数据，详细信息请见下面说明      |
|  message     |    string  |      result=false 时错误信息     |
|  code        |    int     |      返回码，0 表示成功     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  template_id      |    int    |      模板ID     |
|  template_name     |    string     |    模板名称     |
|  pipeline_template_id     |    string     |    流程模板ID     |

---

## get_clocked_task_list

### 功能描述

查询业务下的计划任务列表

### 请求参数

#### 接口参数

| 字段                 | 类型      | 必选 | 描述                                                                                                                              |
|--------------------|---------|----|---------------------------------------------------------------------------------------------------------------------------------|
| bk_biz_id          | string  | 是  | 项目唯一 ID，项目 ID 或 CMDB 业务 ID                                                                                                        |
| scope              | string  | 否  | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |
| id                 | integer | 否  | 根据计划任务ID过滤列表，默认不过滤                                                                                                              |
| task_name          | string  | 否  | 根据计划任务名称关键词过滤列表，支持模糊搜索，默认不过滤                                                                                                    |
| creator            | string  | 否  | 根据创建者过滤列表，支持模糊搜索，默认不过滤                                                                                                          |
| editor             | string  | 否  | 根据编辑者过滤列表，支持模糊搜索，默认不过滤                                                                                                          |
| state              | string  | 否  | 根据计划任务状态过滤列表，默认不过滤                                                                                                              |
| expected_timezone  | string  | 否  | 时间相关字段期望返回的时区，形如 Asia/Shanghai                                                                                                  |
| limit              | integer | 否  | 分页，返回列表条目数，默认为 100                                                                                                              |
| offset             | integer | 否  | 分页，返回列表起始条目下标，默认为 0                                                                                                              |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "id": 1,
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": 1,
            "task_parameters": {
                "constants": {},
                "template_schemes_id": []
            },
            "creator": "xxxx",
            "editor": "",
            "state": "not_started",
            "plan_start_time": "2026-04-11 00:00:00+0800",
            "create_time": "2026-04-10 17:01:20+0800",
            "edit_time": "2026-04-10 17:01:20+0800",
            "project_id": 1,
            "task_id": null,
            "task_name": "xxxx",
            "template_id": 1,
            "template_name": "xxxx",
            "template_source": "project",
            "clocked_task_id": 15,
            "auth_actions": [
                "clocked_task_view",
                "clocked_task_edit",
                "clocked_task_delete",
                "flow_view"
            ]
        }
    ],
    "count": 1,
    "code": 0,
    "trace_id": "xxxx"
}
```

### 返回结果参数说明

| 字段        | 类型      | 描述                           |
|-----------|---------|------------------------------|
| result    | bool    | true/false 查询成功与否             |
| data      | list    | result=true 时计划任务列表，item 信息见下面说明 |
| count     | integer | data 列表数量                     |
| code      | integer | 错误码                          |
| message   | string  | result=false 时错误信息            |
| trace_id  | string  | open telemetry trace_id      |

#### data

| 字段              | 类型      | 描述                |
|-----------------|---------|-------------------|
| id              | integer | 任务唯一标识符           |
| clocked_task_id | integer | 计划任务 Celery 任务 ID |
| auth_actions    | list    | 当前用户对该任务所拥有的操作权限  |
| creator         | string  | 创建者               |
| create_time     | string  | 任务创建时间            |
| editor          | string  | 编辑者               |
| edit_time       | string  | 任务编辑时间            |
| plan_start_time | string  | 计划开始时间            |
| project_id      | integer | 项目 ID             |
| state           | string  | 计划任务状态            |
| task_id         | integer | taskflow 任务 ID（可能为 null） |
| task_name       | string  | 计划任务名称            |
| task_parameters | object  | 任务参数，详见下方说明       |
| template_id     | integer | 模板 ID             |
| template_name   | string  | 模板名称              |
| template_source | string  | 模板来源              |

#### data.task_parameters

| 字段                  | 类型     | 描述         |
|---------------------|--------|------------|
| constants           | object | 计划任务参数     |
| template_schemes_id | list   | 计划任务使用的执行方案列表 |

### MCP 请求说明

当请求来源于网关 MCP 时，以下字段会在响应中被过滤，不会返回：

- `data.[].auth_actions` - 数组中每个计划任务项的权限操作列表

---

## get_node_job_executed_log

### 功能描述

获取任务节点的JOB平台执行日志

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id      |   string     |   是   |  任务ID |
|   node_id      |   string     |   是   |  节点ID |
|   target_ip    |   string     |   否   |  目标IP，用于过滤指定机器的日志 |
|   scope        |   string     |   否   |  bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd",
    "target_ip": "127.0.0.1",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "message": "success",
    "logs": "[127.0.0.1] GSE AGENT 正常\n[127.0.0.1] 开始执行脚本...\n[127.0.0.1] 脚本执行完成，返回码: 0"
}
```

### 返回结果说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  logs     |    string  |      JOB平台执行日志内容     |
|  message  |    string  |      result=false 时错误信息     |

---

## get_plugin_base_info

### 功能描述

获取某个业务下可用插件的基础信息列表（仅返回插件编码和名称），免用户认证

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   scope        |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "code": "sleep_timer",
            "name": "定时"
        },
        {
            "code": "job_fast_execute_script",
            "name": "快速执行脚本"
        },
        {
            "code": "pause_node",
            "name": "暂停"
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    array   |      result=true 时插件基础信息列表，详细信息请见下面说明     |
|  message     |    string  |      result=false 时错误信息     |
|  trace_id    |    string  |      open telemetry trace_id     |

#### data[]

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  code        |    string  |      插件编码     |
|  name        |    string  |      插件名称     |

---

## get_task_node_log

### 功能描述

获取任务节点的执行日志

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id      |   string     |   是   |  任务ID |
|   node_id      |   string     |   是   |  节点ID |
|   version      |   string     |   是   |  节点执行版本号 |
|   page         |   int        |   否   |  页码，默认为 1 |
|   page_size    |   int        |   否   |  每页条目数，默认为 30 |
|   scope        |   string     |   否   |  bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd",
    "version": "23ac8c29f62b3337aafcf1f538d277f8",
    "page": 1,
    "page_size": 30,
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "message": "success",
    "data": "2026-03-11 10:00:01: 开始执行脚本...\n2026-03-11 10:00:05: 脚本执行完成，返回码: 0",
    "page": {
        "page": 1,
        "page_size": 30,
        "total": 2
    },
    "trace_id": "xxx"
}
```

### 返回结果说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    string  |      日志内容（纯文本格式）     |
|  message  |    string  |      result=false 时错误信息     |
|  page     |    dict    |      分页信息     |
|  trace_id |    string  |      open telemetry trace_id     |

#### page

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  page      |    int    |      当前页码     |
|  page_size |    int    |      每页条目数   |
|  total     |    int    |      总条目数     |

---

## get_task_plugin_log

### 功能描述

获取任务节点的插件执行日志

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id      |   string     |   是   |  任务ID |
|   plugin_code  |   string     |   是   |  插件服务编码 |
|   trace_id     |   string     |   是   |  Trace ID |
|   scroll_id    |   string     |   否   |  翻页标识字段，获取下一页时传入上一次返回的该值 |
|   scope        |   string     |   否   |  bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "plugin_code": "sleep_timer",
    "trace_id": "aaa0ce51d2143aa9b0dbc27cb7df",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "logs": "[2026-03-11 10:00:01]INFO-execute: 插件开始执行\n[2026-03-11 10:00:05]INFO-execute: 插件执行完成",
        "total": 2,
        "scroll_id": "abc123"
    },
    "message": "",
    "trace_id": "xxx"
}
```

### 返回结果说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    dict    |      result=true 时返回数据，详细信息见下面说明     |
|  message  |    string  |      result=false 时错误信息     |
|  trace_id |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  logs      |    string  |      日志内容（格式化后的纯文本）     |
|  total     |    int     |      日志总条数     |
|  scroll_id |    string  |      翻页标识符，获取下一页时传入该值     |

---

## modify_project_executor_proxy

### 功能描述

修改项目执行代理人配置

### 请求参数

#### 接口参数

| 字段                       |  类型       | 必选   |  描述             |
|----------------------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   executor_proxy           |   string   |   是   |  执行代理人；仅允许设置为调用方本人用户名，允许传空串表示清空该配置 |
|   executor_proxy_exempts   |   string   |   是   |  执行代理人豁免列表，多个用英文逗号分隔；允许传空串表示清空豁免列表 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "admin",
    "executor_proxy": "admin",
    "executor_proxy_exempts": "user1,user2"
}
```

### 返回结果示例

```
{
    "code": 0,
    "data": {
        "executor_proxy": "admin",
        "executor_proxy_exempts": "user1,user2",
        "project_id": 123
    },
    "result": true,
    "message": "",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称       |  类型     |           说明                    |
| ------------ | --------- | --------------------------------- |
|  code        |  integer  |  错误码                           |
|  result      |  bool     |  true/false 操作是否成功          |
|  data        |  object   |  result=true 时成功数据           |
|  message     |  string   |  result=false 时错误信息          |
|  trace_id    |  string   |  open telemetry trace_id          |

#### data 字段说明

|   名称                    |  类型     |           说明                             |
| ------------------------- | --------- | ------------------------------------------ |
|  executor_proxy           |  string   |  执行代理人（仅允许为调用方本人用户名）    |
|  executor_proxy_exempts   |  string   |  执行代理人豁免列表，多个用英文逗号分隔    |
|  project_id               |  integer  |  项目ID                                    |

---

## modify_template_executor_proxy

### 功能描述

修改流程模板的执行代理人（executor_proxy）

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   template_id    |   string     |   是   |  模板ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   executor_proxy    |   string     |   是   | 执行代理人用户名。仅可设置为当前登录用户本人；传空字符串代表清空执行代理人 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "template_id": "1",
    "executor_proxy": "11111",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "template_id": 1,
        "executor_proxy": "11111"
    },
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict    |      result=true 时成功数据，详细信息请见下面说明     |
|  code        |    int     |      错误码     |
|  message     |    string  |      result=false 时错误信息     |
|  trace_id    |    string  |      open telemetry trace_id     |

#### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  template_id      |    int    |      模板ID    |
|  executor_proxy   |    string |      更新后的执行代理人用户名    |

---

## modify_template_notify

### 功能描述

修改模板通知配置

**请求方法**: POST

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   template_id    |   string     |   是   |  模板ID |
|   bk_biz_id     |   string     |   是   |  项目ID |
|   notify_type     |   dict     |   是   |  流程事件通知方式，包含success和fail两个key，详细信息见下面说明 |
|   notify_receivers     |   dict     |   是   |  通知接收人配置，详细信息见下面说明 |
|   common     |   bool     |   否   |  是否为公共流程模板，默认false |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|


#### notify_type

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  success      |    list    |      执行成功时发送的通知类型列表     |
|  fail      |    list    |      执行失败时发送的通知类型列表    |

#### notify_receivers

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  receiver_group      |    list    |      接收用户组列表     |
|  more_receiver      |    string    |      额外接收人    |
|  extra_info      |    dict    |      额外通知配置信息，详细信息见下面说明    |

#### notify_receivers.extra_info

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  bkchat      |    dict    |      蓝鲸聊天通知配置，包含success和fail两个key    |

#### notify_receivers.extra_info.bkchat

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  success      |    string    |      执行成功时的蓝鲸聊天通知配置     |
|  fail      |    string    |      执行失败时的蓝鲸聊天通知配置    |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx", 
    "bk_username": "xxx",
    "notify_type": {
        "success": [
            "bkchat",
            "rtx"],
        "fail": [
            "weixin",
            "voice",
            "mail",
            "sms"
        ]
    },
    "notify_receivers": {
        "receiver_group": ["Developer", "Maintainers"],
        "more_receiver": "",
        "extra_info": {
            "bkchat": {
                "success": "3654",
                "fail": "123"
            }
        }
    },
    "common": false
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "notify_type": {
            "success": [
                "bkchat",
                "rtx"],
            "fail": [
                "weixin",
                "voice",
                "mail",
                "sms"
            ]
        },
        "notify_receivers": {
            "receiver_group": ["Developer", "Maintainers"],
            "more_receiver": "",
            "extra_info": {
                "bkchat": {
                    "success": "3654",
                    "fail": "123"
                }
            }
        },
        "template_id": 123
    },
    "code": 0
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时成功数据，详细信息请见下面说明      |
|  message     |    string  |      result=false 时错误信息     |
|  code     |    int  |      返回码，0表示成功     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  notify_type      |    dict    |      设置的通知类型配置     |
|  notify_receivers     |    dict     |      设置的通知接收人配置     |
|  template_id     |    int     |      模板ID     |

### 错误码说明

| 错误码      | 描述      |
|-----------|----------|
|  0      |      成功     |

---

## plugin_gateway_cancel_run

### 功能描述

取消一条插件执行记录。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `run_id` | `string` | 是 | 运行 ID |

### 请求参数示例

```text
POST /apigw/plugin-gateway/runs/4f3c2b1a0d9e8f7766554433221100aa/cancel/
```

兼容无尾斜杠路径：

```text
POST /apigw/plugin-gateway/runs/4f3c2b1a0d9e8f7766554433221100aa/cancel
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
    "status": "CANCELLED"
  },
  "code": 0,
  "trace_id": "xxx"
}
```

运行记录被置为 `CANCELLED` 后，网关还会尽力再投递一次终态回调。

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.open_plugin_run_id` | `string` | 运行 ID |
| `data.status` | `string` | 更新后的状态 |

---

## plugin_gateway_create_run

### 功能描述

创建一条插件执行记录。记录创建后会进入 `CREATED`，再由 `open_plugin_dispatch` 队列调度组件运行壳执行。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `source_key` | `string` | 是 | 来源标识 |
| `plugin_id` | `string` | 是 | 插件 ID |
| `plugin_version` | `string` | 是 | 插件版本 |
| `client_request_id` | `string` | 是 | 调用方内的幂等键 |
| `callback_url` | `string` | 是 | 回调地址 |
| `callback_token` | `string` | 是 | 回调时写入 `X-Callback-Token` 的 token |
| `inputs` | `object` | 否 | 插件输入 |
| `context` | `object` | 否 | 业务上下文。推荐传 `scope_type`、`scope_value`、`operator`，可选透传 `space_id`、`task_id`、`node_id`、`task_name` |
| `operator` | `string` | 否 | 兼容字段；未传 `context.operator` 时会写入运行上下文，未传时若网关请求带用户名则自动复用 |
| `project_id` | `int` | 否 | 兼容字段；新接入方推荐使用 `context` 由标准运维侧解析项目 |

### 请求参数示例

```json
{
  "source_key": "bkflow",
  "plugin_id": "builtin__job_execute_task",
  "plugin_version": "legacy",
  "client_request_id": "task_1_node_1_attempt_1",
  "callback_url": "https://bkflow.example.com/api/plugin-gateway/callback",
  "callback_token": "token-001",
  "inputs": {
    "target_ip": "127.0.0.1"
  },
  "context": {
    "scope_type": "biz",
    "scope_value": "2",
    "operator": "bkflow-user",
    "space_id": "bkflow-space-1",
    "task_id": "task_1",
    "node_id": "node_1",
    "task_name": "demo task"
  }
}
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
    "status": "CREATED"
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.open_plugin_run_id` | `string` | 运行 ID |
| `data.status` | `string` | 当前运行状态 |

### 上下文与项目解析

- `context.scope_type=biz` 或 `cmdb_biz` 且 `scope_value` 为业务 ID 时，优先按 `Project.bk_biz_id` 自动解析标准运维项目。
- 未解析到业务项目时，按来源配置 `scope_project_map["<scope_type>:<scope_value>"]` 映射项目。
- 仍未解析到项目时，回退来源配置 `default_project_id`。
- 都拿不到项目时，本次 run 会失败并返回明确错误。
- `context.operator` 会写入插件运行上下文，供 JOB/CC 等底层系统做真实操作人与权限校验。

### 错误字段说明

失败响应会额外返回 `error_type`，用于区分常见联调错误：

- `plugin_not_enabled`
- `plugin_version_unavailable`
- `plugin_removed`
- `source_unreachable`

---

## plugin_gateway_get_categories

### 功能描述

查询插件网关的插件分类。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `plugin_source` | `string` | 否 | 插件来源过滤，可选 `builtin` 或 `third_party`；不传表示合并两个来源 |

### 请求参数示例

```text
GET /apigw/plugin-gateway/categories/?plugin_source=builtin
```

### 返回结果示例

```json
{
  "result": true,
  "data": [
    {"id": "all", "name": "全部"},
    {"id": "DEVOPS", "name": "研发工具"},
    {"id": "JOB", "name": "JOB"}
  ],
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `result` | `bool` | 是否成功 |
| `data` | `list` | 插件分类列表；`all` 表示不过滤，其他 ID 与插件列表中的 `category` 一致 |
| `message` | `string` | 失败时错误信息 |
| `trace_id` | `string` | open telemetry trace_id |

---

## plugin_gateway_get_plugin_detail

### 功能描述

按插件 ID 和版本查询插件详情。内置插件 ID 使用 `builtin__<component_code>`，第三方插件 ID 兼容裸 `code`。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `plugin_id` | `string` | 是 | 插件 ID |
| `version` | `string` | 否 | 插件版本；不传时使用默认版本 |
| `source_key` | `string` | 否 | 来源标识；不传时保持旧 detail 行为，不解析 `form_context` |
| `scope_type` | `string` | 否 | 项目解析使用的范围类型；仅在提供 `source_key` 时参与解析 |
| `scope_value` | `string` | 否 | 项目解析使用的范围值；仅在提供 `source_key` 时参与解析 |

操作人不作为接口参数传入。不传 `source_key` 时沿用旧 detail 行为；提供 `source_key` 时，标准运维只使用 APIGW 已认证且获该资源权限的调用应用代传、由 signed JWT 携带的非空 username。该路径不读取 query/body 中的 `operator`，不要求 `user.verified=true` 或浏览器 user token；APIGW 资源权限只应授予受信任调用应用。

### 请求参数示例

```text
GET /apigw/plugin-gateway/plugins/builtin__job_execute_task/?version=legacy&source_key=bkflow&scope_type=biz&scope_value=2
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "id": "builtin__job_execute_task",
    "name": "作业执行",
    "plugin_source": "builtin",
    "plugin_code": "job_execute_task",
    "plugin_version": "legacy",
    "version": "v4.0.0",
    "wrapper_version": "v4.0.0",
    "description": "",
    "desc": "",
    "url": "https://bk-sops.example/apigw/plugin-gateway/runs/",
    "methods": ["POST"],
    "inputs": [
      {
        "key": "biz_id",
        "name": "业务 ID",
        "type": "int",
        "desc": "业务 ID",
        "description": "业务 ID",
        "required": true
      }
    ],
    "forms": {
      "input": {
        "type": "component_js",
        "key": "job_execute_task",
        "data": "https://bk-sops.example/static/components/job_execute_task.js",
        "is_embedded": false,
        "base": null
      },
      "output": null
    },
    "form_context": {
      "project": {
        "id": 2001,
        "bk_biz_id": 2,
        "from_cmdb": true
      },
      "biz_cc_id": 2,
      "site_url": "https://bk-sops.example/",
      "component": "https://bk-sops.example/api/v3/component/",
      "variable": "https://bk-sops.example/api/v3/variable/",
      "template": "https://bk-sops.example/api/v3/template/",
      "instance": "https://bk-sops.example/api/v3/taskflow/",
      "bk_plugin_api_host": {}
    },
    "outputs": [
      {
        "key": "job_instance_id",
        "name": "作业实例 ID",
        "type": "int",
        "desc": "JOB instance id",
        "description": "JOB instance id"
      }
    ],
    "polling": {
      "url": "https://bk-sops.example/apigw/plugin-gateway/runs/status/",
      "task_tag_key": "open_plugin_run_id",
      "success_tag": {
        "key": "data.status",
        "value": "SUCCEEDED",
        "data_key": "data.outputs"
      },
      "fail_tag": {
        "key": "data.status",
        "value": "FAILED",
        "msg_key": "data.error_message"
      },
      "running_tag": {
        "key": "data.status",
        "value": "RUNNING"
      }
    }
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.id` | `string` | 插件 ID |
| `data.plugin_source` | `string` | 插件来源，取值为 `builtin` 或 `third_party` |
| `data.plugin_code` | `string` | 插件原始 code |
| `data.plugin_version` | `string` | 当前返回的插件版本 |
| `data.version` | `string` | uniform_api 运行壳版本，当前为 `v4.0.0` |
| `data.wrapper_version` | `string` | uniform_api 运行壳版本，当前为 `v4.0.0` |
| `data.url` | `string` | 创建执行记录的地址 |
| `data.methods` | `list` | 允许的调用方法 |
| `data.inputs` | `list` | 插件输入 schema 列表；类型使用 `string`、`int`、`bool`、`list`、`json`，作为兼容渲染路径 |
| `data.forms` | `object` | 原生表单协议；固定包含 `input` 和 `output`，每项为表单描述符或 `null` |
| `data.forms.input` | `object` / `null` | 输入表单描述符；没有原生输入表单时为 `null` |
| `data.forms.output` | `object` / `null` | 输出表单描述符；没有原生输出表单时为 `null` |
| `data.forms.*.type` | `string` | 表单类型：`component_js`、`renderform`，或消费端支持的可选 provider 扩展 `jsonschema` |
| `data.forms.*.key` | `string` | 表单注册 key；内置 input/output 表单均使用组件 code（`<component_code>`） |
| `data.forms.*.data` | `string` / `object` | 原始表单数据或非内嵌表单的绝对 URL；`jsonschema` 时为原始 JSON Schema |
| `data.forms.*.is_embedded` | `boolean` | `data` 是否内嵌在响应中 |
| `data.forms.*.base` | `string` / `null` | 表单依赖基地址；不存在时为 `null` |
| `data.form_schema` | `object` | 过渡期兼容字段，仍可能存在；新接入应读取 `forms` |
| `data.form_context` | `object` | 可选的 JSON 表单上下文；仅在请求提供 `source_key` 时返回 |
| `data.form_context.project` | `object` | 已解析的标准运维项目，固定包含 `id`、`bk_biz_id` 和 `from_cmdb` |
| `data.form_context.project.id` | `integer` | Project 主键，非空 |
| `data.form_context.project.bk_biz_id` | `integer` | Project 对应的 CMDB 业务 ID，非空 |
| `data.form_context.project.from_cmdb` | `boolean` | Project 是否来自 CMDB，非空 |
| `data.form_context.biz_cc_id` | `integer` | 与 `project.bk_biz_id` 一致的业务 ID |
| `data.form_context.site_url` | `string` | 标准运维站点根地址 |
| `data.form_context.component` | `string` | 组件 API 根地址 |
| `data.form_context.variable` | `string` | 变量 API 根地址 |
| `data.form_context.template` | `string` | 模板 API 根地址 |
| `data.form_context.instance` | `string` | 任务实例 API 根地址 |
| `data.form_context.bk_plugin_api_host` | `object` | 插件 code 到 data API 根地址的映射；第三方插件包含当前插件，内置插件为空对象 |
| `data.outputs` | `list` | 插件输出 schema 列表 |
| `data.polling.url` | `string` | 轮询状态地址 |
| `data.polling.task_tag_key` | `string` | 轮询时使用的任务标识字段 |
| `data.polling.running_tag` | `object` | 运行中状态匹配规则，当前值为 `RUNNING` |

`forms` 按以下四种语义消费：

1. `component_js`：内置插件的原生输入或输出表单；`is_embedded=true` 时 `data` 是内嵌表单 JavaScript，否则是可访问的绝对静态 URL。
2. `renderform`：第三方插件原始 `renderform`；不转换为标准运维声明式 schema。
3. `jsonschema`：消费端支持的可选 provider 扩展；provider 提供时保留原始 JSON Schema 对象，但不保证所有当前标准插件 provider 都会返回。
4. `null`：该方向没有原生表单，接入方使用兼容的 `inputs`/`outputs` 渲染路径。

`form_schema` 中的标准控件名包括 `input`、`textarea`、`password`、`codeEditor`、`select`、`radio`、`checkbox`、`switcher` 和 `table`。其中 `codeEditor` 的配置可包含 `language`、`height` 和 `showMiniMap`。该字段只用于过渡期兼容；新接入不应依赖它。

---

## plugin_gateway_get_plugin_list

### 功能描述

查询插件网关可消费的插件列表，返回内置插件和第三方插件。来源配置中的 `do_not_open_list` 会在列表阶段统一过滤。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `plugin_source` | `string` | 否 | 插件来源过滤，可选 `builtin` 或 `third_party`；不传表示合并两个来源 |
| `category` | `string` | 否 | 插件分类；`all` 或不传表示不过滤 |
| `key` | `string` | 否 | 按插件 ID、名称或原始 code 模糊搜索 |

### 请求参数示例

```text
GET /apigw/plugin-gateway/plugins/?plugin_source=builtin
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "total": 2,
    "apis": [
      {
        "id": "builtin__job_execute_task",
        "name": "作业执行",
        "plugin_source": "builtin",
        "plugin_code": "job_execute_task",
        "group": "JOB",
        "wrapper_version": "v4.0.0",
        "default_version": "legacy",
        "latest_version": "legacy",
        "versions": ["legacy"],
        "category": "JOB",
        "category_name": "作业平台",
        "description": "",
        "meta_url_template": "https://bk-sops.example/apigw/plugin-gateway/plugins/builtin__job_execute_task/?version={version}"
      },
      {
        "id": "bk_plugin_demo",
        "name": "Demo Plugin",
        "plugin_source": "third_party",
        "plugin_code": "bk_plugin_demo",
        "group": "DEVOPS",
        "wrapper_version": "v4.0.0",
        "default_version": "1.1.0",
        "latest_version": "1.1.0",
        "versions": ["1.0.0", "1.1.0"],
        "category": "DEVOPS",
        "category_name": "研发工具",
        "description": "Demo plugin",
        "meta_url_template": "https://bk-sops.example/apigw/plugin-gateway/plugins/bk_plugin_demo/?version={version}"
      }
    ]
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.total` | `int` | 插件总数 |
| `data.apis` | `list` | 插件列表 |
| `data.apis[].id` | `string` | 插件 ID；内置插件格式为 `builtin__<component_code>`，第三方插件兼容裸 `code` |
| `data.apis[].plugin_source` | `string` | 插件来源，取值为 `builtin` 或 `third_party` |
| `data.apis[].plugin_code` | `string` | 插件原始 code |
| `data.apis[].group` | `string` | 插件分组 |
| `data.apis[].category` | `string` | 稳定的插件分类 ID，用于筛选和缓存匹配 |
| `data.apis[].category_name` | `string` | 插件分类展示名；缺失独立展示名时回退为分类 ID |
| `data.apis[].wrapper_version` | `string` | uniform_api 运行壳版本，当前固定为 `v4.0.0` |
| `data.apis[].default_version` | `string` | 默认版本 |
| `data.apis[].latest_version` | `string` | 最新版本 |
| `data.apis[].versions` | `list` | 可选业务版本列表，版本字符串按提供方原样返回 |
| `data.apis[].meta_url_template` | `string` | 查询详情的 URL 模板 |

---

## plugin_gateway_get_run_detail

### 功能描述

查询单条插件执行记录详情。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `run_id` | `string` | 是 | 运行 ID |

### 请求参数示例

```text
GET /apigw/plugin-gateway/runs/4f3c2b1a0d9e8f7766554433221100aa/
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
    "status": "SUCCEEDED",
    "plugin_id": "builtin__job_execute_task",
    "plugin_version": "legacy",
    "outputs": {
      "job_instance_id": 1001
    },
    "error_message": ""
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.open_plugin_run_id` | `string` | 运行 ID |
| `data.status` | `string` | 运行状态 |
| `data.plugin_id` | `string` | 插件 ID |
| `data.plugin_version` | `string` | 插件版本 |
| `data.outputs` | `object` | 输出数据 |
| `data.error_message` | `string` | 错误信息 |

### 状态说明

`status` 可能为 `CREATED`、`RUNNING`、`WAITING_CALLBACK`、`SUCCEEDED`、`FAILED`、`CANCELLED`。

---

## plugin_gateway_get_run_status

### 功能描述

按运行 ID 轮询插件执行状态。该接口用于 `uniform_api v4.0.0` 的 polling 协议。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `task_tag` | `string` | 是 | 运行 ID，对应 `open_plugin_run_id` |

### 请求参数示例

```text
GET /apigw/plugin-gateway/runs/status/?task_tag=4f3c2b1a0d9e8f7766554433221100aa
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "status": "SUCCEEDED",
    "outputs": {
      "job_instance_id": 1001
    },
    "error_message": ""
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.status` | `string` | 运行状态 |
| `data.outputs` | `object` | 输出数据 |
| `data.error_message` | `string` | 失败时的错误信息 |

### 状态说明

`status` 可能为 `CREATED`、`RUNNING`、`WAITING_CALLBACK`、`SUCCEEDED`、`FAILED`、`CANCELLED`。其中 `RUNNING` 对应插件详情中的 `polling.running_tag`。

---

## plugin_gateway_internal_callback

### 功能描述

接收回调型插件写回的内部回调数据，并异步推进插件网关运行记录。

该接口由标准运维插件运行壳使用，不建议普通接入方直接调用。终态 run 重复回调会幂等返回当前状态。

#### 接口参数

| 字段 | 类型 | 必选 | 描述 |
|------|------|------|------|
| `run_id` | `string` | 是 | 运行 ID |
| `callback_data` | `object` | 否 | 插件回调数据 |

### 请求参数示例

```text
POST /apigw/plugin-gateway/runs/4f3c2b1a0d9e8f7766554433221100aa/internal-callback/
```

```json
{
  "callback_data": {
    "status": "success",
    "job_instance_id": 1001
  }
}
```

### 返回结果示例

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "4f3c2b1a0d9e8f7766554433221100aa",
    "status": "WAITING_CALLBACK"
  },
  "code": 0,
  "trace_id": "xxx"
}
```

### 返回结果说明

| 名称 | 类型 | 说明 |
|------|------|------|
| `data.open_plugin_run_id` | `string` | 运行 ID |
| `data.status` | `string` | 当前运行状态 |

---
