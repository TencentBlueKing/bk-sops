### 功能描述

获取某个业务下的任务列表，支持任务名关键词搜索

#### 通用参数

|   字段           |  类型       | 必选     |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   是    |  应用ID |
|   bk_app_secret |   string    |   是    |  安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
|   bk_token      |   string    |   否    |  当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取  |
|   bk_username   |   string    |   否    |  当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户              |

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id   |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
|   keyword     |   string     |   否   |  根据任务名关键词过滤任务列表，默认不过滤 |
|   is_started  |   bool       |   否   |  根据任务是否已开始过滤任务列表，默认不过滤 |
|   is_finished |   bool       |   否   |  根据任务是否已结束过滤任务列表，默认不过滤 |
|   limit       |   int        |   否   |  分页，返回任务列表任务数，默认为15 |
|   offset      |   int        |   否   |  分页，返回任务列表起始任务下标，默认为0 |



### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "keyword": "定时",
    "is_started": true,
    "limit": 5,
}
```

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
            "bk_biz_name": "蓝鲸"
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
            "bk_biz_name": "蓝鲸"
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
            "bk_biz_name": "蓝鲸"
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
            "bk_biz_name": "蓝鲸"
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
            "bk_biz_name": "蓝鲸"
        }
    ]
}
```

### 返回结果说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    list    |      result=true 时成功数据，详细信息请见下面说明     |
|  message     |    string  |      result=false 时错误信息     |

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






