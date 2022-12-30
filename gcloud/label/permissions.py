# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import abc

from iam import Subject, Action
from iam.shortcuts import allow_or_raise_auth_failed

from gcloud.constants import COMMON, PROJECT
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory

iam = get_iam_client()


class LabelIAMAdapter:
    VALID_LABEL_TYPE = {PROJECT, COMMON}

    def __init__(self, handler_type):
        if handler_type not in self.VALID_LABEL_TYPE:
            raise ValueError(f"LabelIAMAdapter has no handler type named '{handler_type}'.")
        self.handler = ProjectLabelIAMHandler() if handler_type is PROJECT else CommonLabelIAMHandler()

    def handle(self, request, action, scope_id, *args, **kwargs):
        self.handler.handle(request, action, scope_id, *args, **kwargs)


class LabelIAMHandler(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def handle(self, request, action, scope_id, *args, **kwargs):
        raise NotImplementedError


class ProjectLabelIAMHandler(LabelIAMHandler):
    DEFAULT_ACTION = IAMMeta.PROJECT_VIEW_ACTION
    ACTION_MAPPINGS = {
        "destroy": IAMMeta.PROJECT_EDIT_ACTION,
        "update": IAMMeta.PROJECT_EDIT_ACTION,
        "create": IAMMeta.PROJECT_EDIT_ACTION,
    }

    def handle(self, request, action, scope_id, *args, **kwargs):
        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(self.ACTION_MAPPINGS.get(action, self.DEFAULT_ACTION)),
            resources=res_factory.resources_for_project(scope_id),
        )


class CommonLabelIAMHandler(LabelIAMHandler):
    def handle(self, request, action, scope_id, *args, **kwargs):
        pass
