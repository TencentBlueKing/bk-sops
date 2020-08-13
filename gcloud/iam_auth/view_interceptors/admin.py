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

from iam import Action, Subject, Request
from iam.exceptions import AuthFailedException

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client
from gcloud.iam_auth.intercept import ViewInterceptor

iam = get_iam_client()


class AdminSingleActionViewInpterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):

        subject = Subject("user", request.user.username)
        action = Action(self.action)

        request = Request(IAMMeta.SYSTEM_ID, subject, action, [], {})
        allowed = iam.is_allowed(request)

        if not allowed:
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, [])


class AdminViewViewInterceptor(AdminSingleActionViewInpterceptor):
    action = IAMMeta.ADMIN_VIEW_ACTION


class AdminEditViewInterceptor(AdminSingleActionViewInpterceptor):
    action = IAMMeta.ADMIN_EDIT_ACTION
