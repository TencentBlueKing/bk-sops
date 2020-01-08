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

from functools import wraps

from django.utils.decorators import available_attrs

from .accounts import WeixinAccount


def weixin_login_exempt(view_func):
    """登录豁免,被此装饰器修饰的action可以不校验登录."""
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.weixin_login_exempt = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)


def weixin_login_required(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        # 验证OK
        weixin_account = WeixinAccount()
        if weixin_account.is_weixin_visit(request) and not request.weixin_user.is_authenticated():
            return weixin_account.redirect_weixin_login(request)
        return view_func(request, *args, **kwargs)

    return _wrapped_view
