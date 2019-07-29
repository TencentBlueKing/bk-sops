### 功能描述

查询任务节点执行详情

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
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id     |   string   |   是   |  任务ID     |
|   node_id        | string     | 是         | 节点 ID                        |
|   component_code| string     | 否         | 标准插件编码，请求标准插件执行详情必填 |
|   subprocess_stack| string   | 否         | 子流程堆栈，json 格式的列表    |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd"
    "subprocess_stack": "[\"nodeaaa0ce51d2143aa9b0dbc27cb7df\"]",
    "component_code": "job_fast_execute_script"
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

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    dict    |      result=true 时返回数据，详细信息见下面说明     |
|  message  |    string  |      result=false 时错误信息     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
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
|  state        | string     | 执行状态，CREATED：未执行，RUNNING：执行中，FAILED：失败，NODE_SUSPENDED：暂停，SUSPENDED：成功 |
|  skip         | bool       | 是否手动跳过                   |
|  retry        | int        | 重试次数                       |
|  histories    | list       | 重试记录详情，详情见下面说明   |
|  inputs       | dict       | 输入参数，key：value格式       |
|  outputs      | dict       | 输出参数，key：value格式       |
|  ex_data      | string     | 节点执行失败详情，json字符串或者HTML字符串、普通字符串 |
