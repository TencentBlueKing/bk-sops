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


@six.add_metaclass(abc.ABCMeta)
class BaseObject(object):
    __slots__ = ()

    @abc.abstractmethod
    def to_dict(self):
        pass

    @abc.abstractmethod
    def validate(self):
        pass


class Subject(BaseObject):
    __slots__ = ("type", "id")

    def __init__(self, type, id):
        self.type = type
        self.id = id

    def validate(self):
        # Type Check
        if not isinstance(self.type, six.string_types):
            raise TypeError("Subject.type should be a string")

        if not isinstance(self.id, six.string_types):
            raise TypeError("Subject.id should be a string")

        # Value Check
        if not self.type:
            raise ValueError("Subject.type should not be empty")

        if not self.id:
            raise ValueError("Subject.id should not be empty")

    def to_dict(self):
        return {"type": self.type, "id": self.id}


class Action(BaseObject):
    __slots__ = ("id",)

    def __init__(self, id):
        self.id = id

    def validate(self):
        # Type Check
        if not isinstance(self.id, six.string_types):
            raise TypeError("Action.id should be a string")

        # Value Check
        if not self.id:
            raise ValueError("Action.id should not be empty")

    def to_dict(self):
        return {"id": self.id}


class Resource(BaseObject):
    __slots__ = ("system", "type", "id", "attribute")

    def __init__(self, system, type, id, attribute):
        self.system = system
        self.type = type
        self.id = id
        # allow to be empty or none
        self.attribute = attribute

    def validate(self):
        # Type check
        if not isinstance(self.system, six.string_types):
            raise TypeError("system should be a string")

        if not isinstance(self.type, six.string_types):
            raise TypeError("type should be a string")

        if not isinstance(self.id, six.string_types):
            raise TypeError("id should be a string")

        if self.attribute and (not isinstance(self.attribute, dict)):
            raise TypeError("attribute should be a dict")

        # Value check
        if not self.system:
            raise ValueError("Resource.system should not be empty")

        if not self.type:
            raise ValueError("Resource.type should not be empty")

        if not self.id:
            raise ValueError("Resource.id should not be empty")

    def to_dict(self):
        return {
            "system": self.system,
            "type": self.type,
            "id": self.id,
            "attribute": self.attribute or {},
        }


@six.add_metaclass(abc.ABCMeta)
class BaseRequest(BaseObject):
    def __init__(self, system, subject, environment):
        self.system = system
        self.subject = subject
        self.environment = environment

    def _validate_type(self):
        # Type check
        if not isinstance(self.system, six.string_types):
            raise TypeError("system should be a string")

        # subject can be empty for some query
        if self.subject and (not isinstance(self.subject, Subject)):
            raise TypeError("subject should be a instance of iam.auth.models.Subject")

        if self.environment and (not isinstance(self.environment, dict)):
            raise TypeError("environment should be a dict")

    def _validate_value(self):
        # Value check
        if not self.system:
            raise ValueError("Request.system should not be empty")

        if self.subject:
            try:
                self.subject.validate()
            except Exception as e:
                raise ValueError("Request.subject invalid: %s" % e)

    def validate(self):
        BaseRequest._validate_type(self)
        BaseRequest._validate_value(self)


class Request(BaseRequest):
    __slots__ = ("system", "subject", "action", "resources", "environment")

    def __init__(self, system, subject, action, resources, environment):
        super(Request, self).__init__(system, subject, environment)
        self.action = action
        self.resources = resources

    def _validate_type(self):
        if not isinstance(self.action, Action):
            raise TypeError("action should be a instance of iam.auth.models.Action")

        if self.resources and (not isinstance(self.resources, list)):
            raise TypeError("resources should be a list of iam.auth.models.Resource")

        if self.resources and (not all([isinstance(resource, Resource) for resource in self.resources])):
            raise TypeError("resources should be a list of iam.auth.models.Resource")

    def _validate_value(self):
        # Value check
        try:
            self.action.validate()
        except Exception as e:
            raise ValueError("Request.action invalid: %s" % e)

        # resources can be empty
        if self.resources:
            for i, r in enumerate(self.resources):
                try:
                    r.validate()
                except Exception as e:
                    raise ValueError("Request.resources[%d] invalid: %s" % (i, e))

    def validate(self):
        super(Request, self).validate()
        self._validate_type()
        self._validate_value()

    def to_dict(self):
        return {
            "system": self.system,
            "subject": self.subject.to_dict() if self.subject else {},
            "action": self.action.to_dict(),
            "resources": [r.to_dict() for r in self.resources] if self.resources else [],
            "environment": self.environment or {},
        }


class MultiActionRequest(BaseRequest):
    __slots__ = ("system", "subject", "actions", "resources", "environment")

    def __init__(self, system, subject, actions, resources, environment):
        super(MultiActionRequest, self).__init__(system, subject, environment)
        self.actions = actions
        self.resources = resources

    def _validate_type(self):
        if not isinstance(self.actions, list):
            raise TypeError("actions should be a list")

        if not all([isinstance(action, Action) for action in self.actions]):
            raise TypeError("actions should be a list of iam.auth.models.Action")

        if self.resources and (not isinstance(self.resources, list)):
            raise TypeError("resources should be a list")

        if not all([isinstance(resource, Resource) for resource in self.resources]):
            raise TypeError("resources should be a list of iam.auth.models.Resource")

    def _validate_value(self):
        # Value check
        if self.actions:
            for i, a in enumerate(self.actions):
                try:
                    a.validate()
                except Exception as e:
                    raise ValueError("Request.actions[%d] invalid: %s" % (i, e))

        # resources can be empty
        if self.resources:
            for i, r in enumerate(self.resources):
                try:
                    r.validate()
                except Exception as e:
                    raise ValueError("Request.resources[%d] invalid: %s" % (i, e))

    def validate(self):
        super(MultiActionRequest, self).validate()
        self._validate_type()
        self._validate_value()

    def to_dict(self):
        return {
            "system": self.system,
            "subject": self.subject.to_dict() if self.subject else {},
            "actions": [a.to_dict() for a in self.actions] if self.actions else [],
            "resources": [r.to_dict() for r in self.resources] if self.resources else [],
            "environment": self.environment or {},
        }
