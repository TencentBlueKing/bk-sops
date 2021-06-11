# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


class ConfFixture(object):
    """
    登录模块项目变量汇总
    """

    #################
    # 浏览器参数说明 #
    #################

    # 登录模块,可选项为 components 目录下的模块,如 qcloud_tlogin
    BACKEND_TYPE = None

    # 用户验证 Backend  qcloud_tlogin.backends.QPtloginBackend
    USER_BACKEND = None

    # 用户登录验证中间件 qcloud_tlogin.middlewares.LoginRequiredMiddleware
    LOGIN_REQUIRED_MIDDLEWARE = None

    # 用户模型 qcloud_tlogin.models.UserProxy
    USER_MODEL = None

    # 登录平台弹窗链接 http://xxxx.com/accounts/login_page/
    CONSOLE_LOGIN_URL = None

    # 登录平台链接 http://login.o.qcloud.com
    LOGIN_URL = None

    # 内嵌式的登录平台链接（可嵌入弹框、IFrame）http://xxx.com/plain/
    LOGIN_PLAIN_URL = None

    # 是否提供内嵌式的统一登录页面
    HAS_PLAIN = True

    # 跳转至登录平台是否加跨域前缀标识
    # http://xxx.com/login/?c_url={CROSS_PREFIX}http%3A//xxx.com%3A8000/
    ADD_CROSS_PREFIX = True
    CROSS_PREFIX = ""

    # 跳转至登录平台是否加上APP_CODE
    # http://xxx.com/login/?c_url=http%3A//xxx.com%3A8000/&app_code=xxx
    ADD_APP_CODE = True
    # http://xxx.com/login/?c_url=http%3A//xxx.com%3A8000/&{APP_KEY}=xxx
    APP_KEY = "app_code"
    SETTINGS_APP_KEY = "APP_CODE"

    # 跳转至登录平台，回调参数名称
    # http://xxx.com/login/?{C_URL}=http%3A//xxx.com%3A8000/
    C_URL = "c_url"

    # 内嵌式的登录平台的尺寸大小，决定前端适配的弹框大小
    IFRAME_HEIGHT = 490
    IFRAME_WIDTH = 460

    ###############
    # 微信参数说明 #
    ###############

    # 登录模块 weixin
    WEIXIN_BACKEND_TYPE = None

    # 用户认证中间件 bk_ticket.middlewares.LoginRequiredMiddleware
    WEIXIN_MIDDLEWARE = None

    # 用户认证 Backend bk_ticket.backends.TicketBackend
    WEIXIN_BACKEND = None

    # 用户信息链接 http://xxx.com/user/weixin/get_user_info/
    WEIXIN_INFO_URL = None

    # 用户 OAUTH 认证链接 https://xxx.com/connect/oauth2/authorize
    WEIXIN_OAUTH_URL = None

    # 在微信端的应用ID 'xxxx'
    WEIXIN_APP_ID = None
