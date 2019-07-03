# auth_backend 使用说明

## 基本配置

```python
BK_IAM_SYSTEM_ID = os.getenv('BKAPP_BK_IAM_SYSTEM_ID', APP_CODE)  # 系统注册到权限中心的系统名
BK_IAM_SYSTEM_NAME = os.getenv('BKAPP_BK_IAM_SYSTEM_NAME', u"测试系统")  # 系统注册到权限中心的系统名
BK_IAM_SYSTEM_DESC = ''  # 系统注册到权限中心的系统描述
BK_IAM_QUERY_INTERFACE = '' # 权限中心获取资源接口，目前填空即可
BK_IAM_RELATED_SCOPE_TYPES = 'system' # 系统关联的作用域类型，多个作用域用 ; 分隔
BK_IAM_SYSTEM_MANAGERS = 'admin' # 系统管理员，多个管理员用 ; 分隔
BK_IAM_SYSTEM_CREATOR = 'admin' # 系统创建者
BK_IAM_HOST = os.getenv('BK_IAM_HOST', '') # 权限中心的 HOST
BK_IAM_APP_CODE = os.getenv('BKAPP_BK_IAM_SYSTEM_ID', 'bk_iam_app') # 权限中心的 APP CODE
AUTH_BACKEND_CLS = os.getenv('BKAPP_AUTH_BACKEND_CLS', 'auth_backend.backends.bkiam.BkIAMBackend') # 使用的鉴权后端类，默认使用权限中心作为鉴权后端
```

## 资源模型

auth_backend 提供了资源的抽象和定义，开发者只需要在代码中定义自己系统中的资源，auth_backend 即可检测到该模型。同时，auth_backend 还提供了一些常用的便捷模型定义。

如果 auth_backend 中目前提供的便捷资源类型不能满足您的需求，您可以尝试继承抽象基类 `Resource` 来定义您所需的资源模型。

**资源注册后，请在 Django `AppConfig` 的 `ready` 方法进行一次模型实例的 import 操作。**

## DjangoModelResource

`DjangoModelResource` 是针对以某个 Django Model 作为资源的场景下提供的资源模型，`DjangoModelResource` 会在 Model 创建和删除时自动向权限中心注册资源实例，下面是一个资源类型定义的示例：


```python

from auth_backend.resources.base import Action
from auth_backend.resources.django import DjangoModelResource
from auth_backend.resources.inspect import FixedCreatorFieldInspect
from auth_backend.backends import get_backend_from_config

from somewhere import Project

project_resource = DjangoModelResource(
    rtype='project',
    name=u"项目",
    scope_type='system',
    scope_id='bk_sops',
    scope_name=u"标准运维",
    actions=[
        Action(id='create', name=u"新建", is_instance_related=False),
        Action(id='view', name=u"查看", is_instance_related=True),
        Action(id='edit', name=u"编辑", is_instance_related=True),
    ],
    operations=[ # operation 指的是系统中存在，但是没有注册到权限中心的操作，可能是多个 action 组成的复合操作
        {
            'operate_id': 'create',
            'actions_id': ['create']
        },
        {
            'operate_id': 'view',
            'actions_id': ['view']
        },
        {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        }
    ],
    resource_cls=Project,
    backend=get_backend_from_config(),
    inspect=FixedCreatorFieldInspect(creator_type='user',  # 模型探测器，便于 Resource 中模型实例中获取相关信息
                                     creator_id_f='creator',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f=None))
```

## 模型变更

resource migration 模块提供了系统中权限模型变更的检测机制，在检测到变更后，resource migration 会自动生成当前系统中权限模型的快照，并在应用部署时向权限中心提交本次变更，保持权限中心的权限模型与系统中定义模型的一致性。

### 检测系统中权限模型的变更

执行 `python manage.py perms_makemigrations` 命令，框架会扫描当前系统中的资源模型，并生成对应的快照和变更数据。

### 执行权限模型的变更

执行 `python manage.py migrate` 命令，则会将当前变更注册到权限中心。如果是第一次生成权限模型快照，框架会自动向权限中心进行系统注册的初始化操作。

### 相关配置

```python
AUTH_BACKEND_RESOURCE_MIGRATION_CLASS = 'auth_backend.resources.migrations.migration.BKIAMResourceMigration'  # 资源模型变更执行时所使用的类，若该配置为空，则不会向权限中心注册变更，请将该配置添加到生产环境和预发布环境中
```

### 注意事项

由于 resource migration 复用了 Django Migration 的变更执行功能，并且将变更文件存储在 `auth_backend/migrations` 目录下，若您需要为 auth_backend 添加 Django Model，请在子 APP 的方式进行 Model 的声明，防止 Django 生成的 Model Migration 文件污染 `auth_backend/migrations` 目录。

## 权限模板

auth_backend 还提供了更新系统在权限中心中的权限模板的便捷函数，首先只需要声明系统需要的权限模板：

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

然后在某个时刻调用注册模板的方法即可：

```python
from auth_backend.plugins.bkiam.shortcuts import upsert_perm_templates

upsert_perm_templates()
```


### 相关配置

```python
BK_IAM_PERM_TEMPLATES = 'config.perms.bk_iam_perm_templates'  # 权限模板声明路径

BK_IAM_SYNC_TEMPLATES = True  # 是否需要同步权限模板，该配置为 None 或 False 时不会向权限中心更新权限模板
```