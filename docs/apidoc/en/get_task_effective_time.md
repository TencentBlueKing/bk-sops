### Description

Calculate the effective execution time of a task (excluding manual intervention nodes and their waiting time, as well as failure wait time)

### Request Parameters

#### Path Parameters

| Field          |  Type       | Required   |  Description            |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string   |   Yes   |  Business ID   |
|   task_id     |   string   |   Yes   |  Task instance ID     |

### Request Example

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

### Response Example

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
        "excluded_time": 300,
        "failure_wait_time": 120,
        "retry_node_time_adjustment": 10,
        "effective_time": 1310,
        "excluded_node_count": 2,
        "total_node_count": 10,
        "has_excluded_nodes": true,
        "excluded_component_codes": ["bk_approve", "pause_node", "sleep_timer", "bot-approval"],
        "category": "Default"
    },
    "code": 0,
    "trace_id": "xxx"
}
```

### Response Parameters

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |     true/false indicates success or failure     |
|  data     |    dict    |     data returned when result=true, see details below     |
|  message  |    string  |     error message when result=false     |
|  code     |    int     |     error code, 0 indicates success     |
|  trace_id     |    string  |     open telemetry trace_id     |

#### data

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  task_instance_id      |    int    |     Task instance ID    |
|  instance_id      |    int    |     Pipeline instance ID    |
|  template_id      |    string    |     Pipeline template ID    |
|  task_template_id      |    string    |     Task template ID    |
|  project_id      |    int    |     Project ID    |
|  creator      |    string    |     Creator    |
|  create_method      |    string    |     Task creation method (app/api/app_maker/periodic/clocked/mobile)    |
|  create_time      |    string    |     Creation time, format: YYYY-MM-DD HH:MM:SS    |
|  start_time      |    string    |     Start time, format: YYYY-MM-DD HH:MM:SS    |
|  finish_time      |    string    |     Finish time, format: YYYY-MM-DD HH:MM:SS    |
|  total_elapsed_time      |    int    |     Total execution time (seconds)    |
|  excluded_time      |    int    |     Excluded node time (seconds), total time of manual intervention nodes    |
|  failure_wait_time      |    int    |     Failure wait time (seconds), waiting time from the first failed node to user operation    |
|  retry_node_time_adjustment      |    int    |     Retry node time adjustment (seconds), ignoring waiting time between old retry node end and new retry node start    |
|  effective_time      |    int    |     Effective execution time (seconds), formula: total_elapsed_time - excluded_time - failure_wait_time - retry_node_time_adjustment    |
|  excluded_node_count      |    int    |     Number of excluded nodes (manual intervention nodes)    |
|  total_node_count      |    int    |     Total number of nodes    |
|  has_excluded_nodes      |    bool    |     Whether there are manual intervention nodes    |
|  excluded_component_codes      |    list    |     List of excluded node component codes, obtained from environment variable MANUAL_WAITING_COMPONENT_CODES. If not configured, default values are used: ["bk_approve", "pause_node", "sleep_timer", "bot-approval"]    |
|  category      |    string    |     Task category    |

### Notes

1. **Excluded Nodes**: The time spent on manual intervention nodes (approval nodes, pause nodes, timer nodes, etc.) will be excluded. The excluded node types are configured through the environment variable `MANUAL_WAITING_COMPONENT_CODES`, with multiple component codes separated by commas. If not configured, default values are used: `bk_approve` (approval node), `pause_node` (pause node), `sleep_timer` (timer node), `bot-approval` (bot approval node).

2. **Failure Wait Time**: When there are failed nodes in the process, the waiting time from the first failed node to user operation (terminate task or skip node) will be calculated and excluded from the effective execution time.

3. **Retry Node Time Adjustment**: For retry nodes, the waiting time between the end of the old retry node execution and the start of the new retry node is ignored.

5. **Revoked Tasks**: If a task has a revoke operation, the API will return an error because revoked tasks cannot accurately calculate effective execution time.

6. **Task Status Requirement**: Only finished tasks can calculate effective execution time. If the task is not finished yet, the API will return an error.

