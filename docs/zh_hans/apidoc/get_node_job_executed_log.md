### 功能描述

获取任务节点的JOB平台执行日志

支持快速执行脚本、执行作业等只提交单个 JOB 实例的插件，也支持快速分发文件、分发本地文件等会提交多个 JOB 实例的插件（此时会汇总所有 JOB 实例的日志，需配合传入 component_code）。

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id      |   string     |   是   |  任务ID |
|   node_id      |   string     |   是   |  节点ID |
|   target_ip    |   string     |   否   |  目标IP，用于过滤指定机器的日志 |
|   component_code |   string   |   否   |  节点对应的插件 code。只提交单个 JOB 实例的插件（如 job_fast_execute_script 快速执行脚本、job_execute_task 执行作业）可不传；会提交多个 JOB 实例的插件（如 job_fast_push_file 快速分发文件、job_push_local_files 分发本地文件、all_biz_job_fast_push_file 业务集快速分发文件）必须传入，否则接口只按单个 JOB 实例（job_inst_id）处理，无法汇总多个实例的日志 |
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
    "component_code": "job_fast_push_file",
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
