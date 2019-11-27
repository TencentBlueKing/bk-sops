# 资源实例探测器

## 了解实例探测器

现实世界中的资源类型可谓是多种多样，我们编写的系统中定义的资源内部的结构亦是如此。auth backend 需要借助资源实例探测器（后文简称为 inspect）来从我们创建的资源实例中获取特定的信息，inspect 需要从资源实例中获取以下信息：

- 创建者类型
- 创建者 ID
- 资源实例 ID
- 资源实例名
- 资源实例的父实例
- 资源实例所属的作用域 ID

假设我们的系统中有一个名为 `Project` 的 Django Model，为了让 auth backend 能够获取到 `Project` 实例的相关信息，我们就需要在定义资源模型的时候传入特定的 inspect 来保证 auth backend 能够如期的获取到资源实例相关的信息，`Project` 的定义如下：

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

像创建者，资源实例 ID，资源实例名等信息都存储在 `Project` 实例的字段中，假设 `Project` 只会由用户来进行创建，这个时候我们就能够使用 auth backend 中已经实现的 `FixedCreatorFieldInspect`：

```python
project_inspect = FixedCreatorFieldInspect(creator_type='user',
                                           creator_id_f='creator',
                                           resource_id_f='id',
                                           resource_name_f='name',
                                           scope_id_f=None,
                                           parent_f=None)
```

`project_inspect` 会尝试从 `Project` 实例的 `creator`，`id`，`name` 字段中获取该实例的创建者，ID 以及名称。

## 现有的实例探测器

### FieldInspect

`FieldInspect` 会尝试从资源实例的属性中获取以下信息：

- 创建者类型
- 创建者 ID
- 资源实例 ID
- 资源实例名
- 资源实例的父实例
- 资源实例所属的作用域 ID

示例如下：

```python
inspect = FieldInspect(
    creator_type_f='creator_type',
    creator_id_f='creator',
    resource_id_f='id',
    resource_name_f='name',
    scope_id_f='scope_id',
    parent_f='parent'
)
```

### FixedCreatorTypeFieldInspect


`FixedCreatorTypeFieldInspect` 是 `FieldInspect` 的一个子类，用于创建者类型固定的资源模型上，其会尝试从资源实例属性中获取以下信息：

- 创建者 ID
- 资源实例 ID
- 资源实例名
- 资源实例的父实例

示例如下：

```python
inspect = FixedCreatorTypeFieldInspect(
    creator_type='user',
    creator_id_f='creator',
    resource_id_f='id',
    resource_name_f='name',
    scope_id_f='scope_id',
    parent_f='parent'
)
```

## 定义你自己的探测器

auth backend 中默认提供的探测器可能不能满足某些特殊的场景，这个时候，你可以为这种特殊的场景定义特定的资源探测器，这个探测器只需要继承 `InstanceInspect` 即可，`InstanceInspect` 的声明如下：

```python
class InstanceInspect(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, resource_unique_key):
        self.resource_unique_key = resource_unique_key

    @abc.abstractmethod
    def creator_type(self, instance):
        raise NotImplementedError()

    @abc.abstractmethod
    def creator_id(self, instance):
        raise NotImplementedError()

    @abc.abstractmethod
    def resource_id(self, instance):
        raise NotImplementedError()

    @abc.abstractmethod
    def resource_name(self, instance):
        raise NotImplementedError()

    @abc.abstractmethod
    def parent(self, instance):
        raise NotImplementedError()

    @abc.abstractmethod
    def scope_id(self, instance):
        raise NotImplementedError()
```

### 示例

假设我们的系统中拥有一种名为 `DictAttrObject` 的资源，这种类型的资源会将所有的属性存储在自身内部的一个字典中（这是一个十分勉强的例子，只是为了说明 inspect 子类定义的方法）：

```python
class DictAttrObject(object):

    def __init__(self, create_from, creator, uid, name):
        self._attr = {
            'create_from': create_from,
            'creator': creator,
            'uid': uid,
            'name': name
        }
```

那么针对这种特殊的类型，我们能够实现一个 `DictAttrObjectInspect` 来处理：

```python

class DictAttrObjectInspect(InstanceInspect):
    
    def creator_type(self, instance):
        return instance._attr['create_from']

    def creator_id(self, instance):
        return instance._attr['creator']

    def resource_id(self, instance):
        return instance._attr['uid']

    def resource_name(self, instance):
        return instance._attr['name']

    def parent(self, instance):
        return None
    
    def scope_id(self, instance):
        return None
```

