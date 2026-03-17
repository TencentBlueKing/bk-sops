### Functional description

Create a project flow template

### Request Parameters

#### Interface Parameters

| Field         |  Type      | Required   |  Description |
|---------------|------------|--------|------------------|
|   bk_biz_id    |   string     |   YES   |  the business ID |
|   name     |   string     |   NO   |  template name, auto-generated if empty (format: new+current timestamp) |
|   pipeline_tree     |   dict/string     |   YES   |  pipeline tree data. When format=json, supports dict or JSON string; when format=yaml, pass a YAML schema string (same as page export format) |
|   format     |   string     |   NO   |  input format for pipeline_tree, accepted values: json (default), yaml. When set to yaml, name and description can be auto-extracted from YAML meta |
|   description     |   string     |   NO   |  template description, default is empty |
|   category     |   string     |   NO   |  template category, default is Default |
|   notify_type     |   dict     |   NO   |  notification type, default is {"success": [], "fail": []} |
|   notify_receivers     |   dict     |   NO   |  notification receivers, default is {"receiver_group": [], "more_receiver": ""} |
|   timeout     |   int     |   NO   |  timeout in minutes, default is 20 |
|   default_flow_type     |   string     |   NO   |  flow type, default is common |
|   template_labels     |   list     |   NO   |  template label ID list, default is empty list |
|   executor_proxy     |   string     |   NO   |  executor proxy, default is empty |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which bindded cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project' |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "1",
    "name": "my_template",
    "description": "template description",
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
                "stage_name": "stage1",
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
                "stage_name": "stage1",
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

### Return Result Example

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

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result      |    bool    |   true/false, indicate success or failure     |
|  data        |    dict  |   data returned when result is true, details are described below        |
|  message     |    string  |   error message returned when result is false |
|  code        |    int     |   return code, 0 indicates success     |
|  trace_id     |    string  | open telemetry trace_id        |

#### data

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  template_id      |    int    |   the template ID    |
|  template_name     |    string     |    template name     |
|  pipeline_template_id     |    string     |    pipeline template ID     |
