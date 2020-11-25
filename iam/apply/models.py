# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import abc
import six


"""
build the application

# 无资源实例的操作权限, 例如 访问开发者中心
{
  "system_id": "bk_job",  # 权限的系统
  "actions": [
    {
      "id": "execute_job",  # 操作id
      "related_resource_types": []
    }
  ]
}

# 有资源实例的操作权限, 例如 管理应用framework
{
  "system_id": "bk_job",  # 权限的系统
  "actions": [
    {
      "id": "execute_job",  # 操作id
      "related_resource_types": [  # 关联的资源类型, 无关联资源类型的操作, 可以为空
        {
          "system_id": "bk_job",  # 资源类型所属的系统id
          "type": "job",  # 资源类型
          "instances": [  # 申请权限的资源实例
            [  # 带层级的实例表示
              {
                "type": "job",  # 层级节点的资源类型
                "id": "job1",  # 层级节点的资源实例id
                "name": "作业1"  # 层级节点的资源名称
              }
            ]
          ]
        },
        {
          "system_id": "bk_cmdb",  # 资源类型所属的系统id
          "type": "host",  # 操作依赖的另外一个资源类型
          "instances": [
            [
              {
                "type": "biz",
                "id": "biz1",
                "name": "业务1"
              }, {
                "type": "set",
                "id": "set1",
                "name": "集群1"
              }, {
                "type": "module",
                "id": "module1",
                "name": "模块1"
              }, {
                "type": "host",
                "id": "host1",
                "name": "主机1"
              }
            ]
          ]
        }
      ]
    }
  ],
  "environment": {  # 权限的可用条件
    "source_system_id": ""  # 选填, 来源系统, 如果需要限制权限的来源系统可填
  }
}
"""
# =========== resource


class ResourceNode(object):
    def __init__(self, type, id, name):
        self.type = type
        self.id = id
        self.name = name

    def to_dict(self):
        return {
            "type": self.type,
            "id": self.id,
            "name": self.name,
        }


class ResourceInstance(object):
    def __init__(self, resource_nodes):
        # should not be empty and should be type of ResourceNode
        self.resource_nodes = resource_nodes

    def validate(self):
        if not self.resource_nodes:
            raise ValueError(
                "ResourceInstance.resource_nodes invalid: should contain at least 1 iam.apply.models.ResourceNode"
            )

        if not isinstance(self.resource_nodes, list):
            raise TypeError("ResourceInstance.resource_nodes should be a list of iam.apply.models.ResourceNode")

        for i, r in enumerate(self.resource_nodes):
            if not isinstance(r, ResourceNode):
                raise ValueError("ResourceInstance.resource_instances[%d] should be instance of ResourceNode" % i)

    def to_dict(self):
        return [n.to_dict() for n in self.resource_nodes]


class RelatedResourceType(object):
    def __init__(self, system_id, type, instances):
        self.system_id = system_id
        self.type = type
        # should not be empty and should be type of Resource
        self.instances = instances

    def validate(self):
        if not isinstance(self.instances, list):
            raise TypeError("ResourceInstance.instances should be a list of iam.apply.models.ResourceInstance")

        for i, r in enumerate(self.instances):
            try:
                r.validate()
            except Exception as e:
                raise ValueError("RelatedResourceType.instances[%d] invalid: %s" % (i, e))

    def to_dict(self):
        return {"system_id": self.system_id, "type": self.type, "instances": [r.to_dict() for r in self.instances]}


# =========== action
@six.add_metaclass(abc.ABCMeta)
class BaseAction(object):
    def __init__(self, id):
        self.id = id

    @abc.abstractmethod
    def validate(self):
        pass

    @abc.abstractmethod
    def to_dict(self):
        pass

    def __repr__(self):
        return "action:{}".format(self.id)


class ActionWithoutResources(BaseAction):
    def __init__(self, id):
        super(ActionWithoutResources, self).__init__(id)

    def validate(self):
        pass

    def to_dict(self):
        return {"id": self.id, "related_resource_types": []}


class ActionWithResources(BaseAction):
    def __init__(self, id, related_resource_types):
        super(ActionWithResources, self).__init__(id)
        # TODO: should not be empty, a list of ResourceType
        self.related_resource_types = related_resource_types

    def validate(self):
        if not self.related_resource_types:
            raise ValueError("Action.related_resource_types invalid: should contain at least 1 RelatedResourceType")

        if not isinstance(self.related_resource_types, list):
            raise TypeError("Action.related_resource_types should be a list of iam.apply.models.RelatedResourceType")

        for i, rt in enumerate(self.related_resource_types):
            if not isinstance(rt, RelatedResourceType):
                raise TypeError(
                    "Action.related_resource_types[%d] should be instance of " "iam.apply.model.RelatedResourceType" % i
                )
            try:
                rt.validate()
            except Exception as e:
                raise ValueError("Action.related_resource_types[%d] invalid: %s" % (i, e))

    def to_dict(self):
        return {"id": self.id, "related_resource_types": [r.to_dict() for r in self.related_resource_types]}


# =========== application
class Application(object):
    def __init__(self, system_id, actions, environment=None):
        self.system_id = system_id
        self.actions = actions
        # self.environment = environment or {}

    def to_dict(self):
        return {
            "system_id": self.system_id,
            "actions": [a.to_dict() for a in self.actions],
            # "environment": self.environment
        }

    def validate(self):
        if not self.actions:
            raise ValueError("Application.actions invalid: should contain at least 1 Action")

        if not isinstance(self.actions, list):
            raise TypeError("Application.actions should be a list of iam.apply.models.Action")

        for i, action in enumerate(self.actions):
            if not isinstance(action, BaseAction):
                raise TypeError(
                    "Application.actions[%d] should be instance of "
                    "iam.apply.models.ActionWithResources/ActionWithoutResources" % i
                )
            try:
                action.validate()
            except Exception as e:
                raise ValueError("Application.actions[%d] invalid: %s" % (i, e))
