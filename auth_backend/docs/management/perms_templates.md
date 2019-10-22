# 权限模板（权限中心专用）

auth_backend 还提供了创建/更新系统在权限中心中的权限模板的功能。

## 声明权限模板

```python

from somewhere import project_resource

bk_iam_perm_templates = [
    {
        'name': u"运维角色",  # 模板名
        'id': 'operation',  # 模板 ID
        'desc': '',  # 模板描述
        'resource_actions': [  # 模板中对应的资源模型及其操作
            {
                'resource': project_resource,
                'actions': [
                    project_resource.actions.create,
                    project_resource.actions.view,
                    project_resource.actions.edit,
                    project_resource.actions.create_template,
                    project_resource.actions.use_common_template,
                ]
            },
            {
                'resource': another_resource,
                'actions': [
                    another_resource.actions.view,
                    ...
                ]
            },
            ...
        ]
    },
    {
        'name': u"开发角色",  # 模板名
        'id': 'developer',  # 模板 ID
        'desc': '',  # 模板描述
        'resource_actions': [
            ...
        ]  # 模板中对应的资源模型及其操作
    }
    ...
]
```

## 创建/更新权限模板

只需要调用以下函数，即可创建/更新权限模板。

```python
from auth_backend.plugins.bkiam.shortcuts import upsert_perm_templates

upsert_perm_templates()
```

## 相关配置

### BK_IAM_PERM_TEMPLATES

权限模板的声明路径。

示例：

```python
BK_IAM_PERM_TEMPLATES = 'config.perms.bk_iam_perm_templates'
```

### BK_IAM_SYNC_TEMPLATES

是否需要同步权限模板，该配置为 None 或 False 时不会向权限中心更新权限模板。

示例：

```python
BK_IAM_SYNC_TEMPLATES = True
```