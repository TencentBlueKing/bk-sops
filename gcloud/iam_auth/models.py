from dataclasses import dataclass, field


@dataclass(frozen=True)
class Action:
    id: str

    def to_dict(self):
        return {"id": self.id}


@dataclass(frozen=True)
class Subject:
    type: str
    id: str

    def to_dict(self):
        return {"type": self.type, "id": self.id}


@dataclass(frozen=True)
class Resource:
    system: str
    type: str
    id: str
    attribute: dict = field(default_factory=dict, compare=False)

    def to_dict(self):
        return {
            "system": self.system,
            "type": self.type,
            "id": self.id,
            "attribute": self.attribute,
        }


class Request:
    def __init__(self, system, subject, action, resources=None, environment=None, context=None):
        self.system = system
        self.subject = subject
        self.action = action
        self.resources = resources or []
        self.environment = environment or {}
        self.context = context or {}

    def to_dict(self):
        return {
            "system": self.system,
            "subject": self.subject.to_dict(),
            "action": self.action.to_dict(),
            "resources": [resource.to_dict() for resource in self.resources],
            "environment": self.environment,
        }


class MultiActionRequest:
    def __init__(self, system, subject, actions, resources=None, environment=None, context=None):
        self.system = system
        self.subject = subject
        self.actions = actions
        self.resources = resources or []
        self.environment = environment or {}
        self.context = context or {}

    def to_dict(self):
        return {
            "system": self.system,
            "subject": self.subject.to_dict(),
            "actions": [action.to_dict() for action in self.actions],
            "resources": [resource.to_dict() for resource in self.resources],
            "environment": self.environment,
        }


class BaseObject:
    def __init__(self, *args, **kwargs):
        self.validate()

    def validate(self):
        return None
