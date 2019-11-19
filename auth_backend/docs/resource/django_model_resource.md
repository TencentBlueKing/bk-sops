# DjangoModelResource

通常来说，我们的系统中大部分的资源都是 Django 中的 Model，所以 auth backend 提供了对应的 `DjangoModelResource`，借助 `DjangoModelResource`，你能够省去手动注册和删除资源实例的烦恼。

## DjangoModelResource 的使用

假设我们的系统中有一个名为 `Project` 的 Django Model：

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

我们可以为其定义一个资源模型：

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

完成了 `project_resource` 的定义后，每当有一个 `Project` 对象被创建或删除，`project_resource` 就会自动向权限系统注册或删除实例。

**P.S. 资源注册后，请在 Django `AppConfig` 的 `ready` 方法进行一次模型实例的 import 操作。**

## 自动注册功能

如果你不想使用 `DjangoModelResource` 提供的自动注册功能，那么可以在创建资源模型的时候使用 `auto_register` 参数来控制该行为：

```python
a_resource = DjangoModelResoure(
    ...,
    auto_register=False,
    ...
)
```

> **`DjangoModelResource` 并不能自动处理通过 `batch_create` 方法批量创建出来的资源实例，若系统中存在这种场景，请手动对这些资源进行注册。**

## 伪删除的处理

有时候我们并不会真正的删除 Django Model 的实例，而是使用一个标志位去标志其是否被删除了，为了能够在资源被标记为删除时从权限系统中删除实例，`DjangoModelResource` 提供了 `tomb_field` 字段来标记 Model 的删除标志位。

假设你使用 `is_delete` 字段来标志某个资源是否被删除，那么只需要在创建资源模型时将 `tomb_field` 设置该字段即可：

```python
a_resource = DjangoModelResoure(
    ...,
    tomb_field='is_delete',
    ...
)
```

> **P.S. 设置了 `tomb_field` 时，`DjangoModelResource` 将不会再处理 Model 真实的删除操作。**