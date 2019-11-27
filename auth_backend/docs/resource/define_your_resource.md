# 定义系统中的资源

auth backend 提供的功能都是围绕着 resource 来实现的，可以说 resource 是 auth backend 中最基础的元素。

## 资源的定义

我们的系统中可能存在各种类型的资源，这些资源需要被有效的定义和管理起来。下面我们以最常见的 Django Model 类型的资源为例子，来看看如何为系统中存在的资源类型定义一个资源模型。

假设我们的系统中有一个名为 `Project` 的 Django Model，并且我们需要对用户在这些项目实例上的操作进行权限的控制，那么我们第一步就是要为 `Project` 定义一个资源模型，首先我们先看看 `Project` 的定义：

```python
class Project(models.Model):
    name = models.CharField(_(u"项目名"), max_length=256)
    time_zone = models.CharField(_(u"项目时区"), max_length=100, blank=True)
    creator = models.CharField(_(u"创建者"), max_length=256)
    desc = models.CharField(_(u"项目描述"), max_length=512, blank=True)
    create_at = models.DateTimeField(_(u"创建时间"), auto_now_add=True)
    from_cmdb = models.BooleanField(_(u"是否是从 CMDB 业务同步过来的项目"), default=False)
    bk_biz_id = models.IntegerField(_(u"业务同步项目对应的 CMDB 业务 ID"), default=-1)
    is_disable = models.BooleanField(_(u"是否已停用"), default=False)
```

在了解了 `Project` 的定义后，我们来看看其对应的资源模型的定义：

```python
from auth_backend.resources.base import Action
from auth_backend.resources.django import DjangoModelResource
from auth_backend.resources.inspect import FixedCreatorFieldInspect

from somewhere import Project

project_resource = DjangoModelResource(
    rtype='project',
    name=u"项目",
    scope_type='system',
    scope_type_name=u"系统",
    scope_id='bk_sops',
    scope_name=u"标准运维",
    actions=[
        Action(id='create', name=u"新建", is_instance_related=False),
        Action(id='view', name=u"查看", is_instance_related=True),
        Action(id='edit', name=u"编辑", is_instance_related=True),
    ],
    operations=[
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
    id_field='id',
    inspect=FixedCreatorFieldInspect(creator_type='user',
                                     creator_id_f='creator',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f=None,
                                     scope_id_f=None))
```

一个基础的资源模型（`Resource`）的定义必须包括以下几个字段：

- `type`：资源类型 ID
- `name`：资源类型名
- `scope_type`：资源所述作用域类型
- `scope_type_name`：资源所属作用域类型名
- `scope_name`：资源所述作用域名
- `actions`：该资源上需要进行权限控制的操作集合
- `inspect`：[资源实例探测器](resource_instance_inspect.md)，用于从这种资源的实例中获取特定的信息
- `parent`（可选）：该资源的父资源模型
- `parent_getter`（可选）：该资源的父资源模型
- `operations`（可选）：该资源上可能进行的操作，一个操作可能需要多个动作的权限（操作不会被注册到权限中心）
- `backend`（可选）：该资源类型所使用的权限后端
- `scope_id`（可选）：资源所属作用域 ID，对于作用域实例不固定的资源类型，该值传 `None` 即可

由于我们这里使用的是为 Django Model 类型的资源实现的 `DjangoModelResource`，所以还会有以下字段需要在资源声明时完善：

- `resource_cls`：该资源所对应的 Django Model 类
- `id_field`：能唯一定位到某个资源实例的 ID 字段
- `auto_register`（可选）：当 Django Model 创建和删除新的实例时，是否自动向权限后端注册该实例
- `tomb_field`（可选）：对于某些进行伪删除的 Model，其对应的墓碑标志位的字段名

最我们需要在 Django `AppConfig` 的 `ready` 方法进行一次模型实例的 import 操作：

```python

class ExampleAppConfig(AppConfig):

    def ready(self):
        from somewhere import project_resource  # noqa

```

至此，我们就完成了一个资源模型的定义。

## 父资源

如果我们系统中的资源存在一定的层级关系，例如*模块*资源隶属于*集群*资源下，那么我们认为*集群*是*模块*的父资源。在创建权限模型时，我们能够通过 `parent` 字段来声明这种关系：

```python

set_resource = DjangoModelResource(...)

module_resource = DjangoModelResource(
    ...,
    parent=set_resource,
    ...
)
```
