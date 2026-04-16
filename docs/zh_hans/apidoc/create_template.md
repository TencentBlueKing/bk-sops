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
