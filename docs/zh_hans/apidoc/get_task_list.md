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
