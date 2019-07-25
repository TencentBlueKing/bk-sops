### 功能描述

修改周期任务的调度策略

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
|   cron    |   dict     |   否   | 调度策略对象 |

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
    "bk_biz_id": "2",
    "task_id": "8",
    "cron" : {
	    "minute": "*/1", 
	    "hour": "15", 
	    "day_of_week":"*", 
	    "day_of_month":"*", 
	    "month_of_year":"*"
    }
}
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

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

#### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  cron      |    string    |      调度策略表达式    |
