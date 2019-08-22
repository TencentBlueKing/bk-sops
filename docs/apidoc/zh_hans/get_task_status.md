### 功能描述

查询任务或任务节点执行状态

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
|   bk_biz_id   |   string   |   是   |  模板所属业务ID   |
|   task_id     |   string   |   是   |  任务或节点ID     |

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

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    dict    |      result=true 时返回数据，详细信息见下面说明     |
|  message  |    string  |      result=false 时错误信息     |

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

#### data.state

| 返回值    | 描述      |
|----------|-----------|
| CREATED   | 未执行   |  
| RUNNING   | 执行中   |
| FAILED    | 失败     |
| SUSPENDED | 暂停     |
| REVOKED   | 已终止   |
| FINISHED  | 已完成   |  

#### data.children.KEY
任务节点执行态ID

#### data.children.VALUE
同 data 格式
