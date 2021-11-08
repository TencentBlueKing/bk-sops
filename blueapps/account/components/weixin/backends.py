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

import logging

from django.contrib.auth.backends import ModelBackend

from blueapps.account import get_user_model
from blueapps.account.conf import ConfFixture
from blueapps.account.utils.http import send

logger = logging.getLogger("component")


class WeixinBackend(ModelBackend):
    def authenticate(self, request=None, code=None, is_wechat=True):
        """
        is_wechat 参数是为了使得 WeixinBackend 与其他 Backend 参数个数不同，在框架选择
        认证 backend 时，快速定位
        """
        logger.debug(u"进入 WEIXIN 认证 Backend")
        if not code:
            return None

        result, user_info = self.verify_weixin_code(code)
        logger.debug(u"微信 CODE 验证结果，result：{}，user_info：{}".format(result, user_info))

        if not result:
            return None

        user_model = get_user_model()
        try:
            user, _ = user_model.objects.get_or_create(username=user_info["username"])
            user.nickname = user_info["username"]
            user.avatar_url = user_info["avatar"]
            user.save()
        except Exception:  # pylint: disable=broad-except
            logger.exception(u"自动创建 & 更新 User Model 失败")
        else:
            return user

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None

    @staticmethod
    def verify_weixin_code(code):
        """
        验证 WEIXIN 认证返回的授权码
        @param {string} code WEIXIN 认证返回的授权码
        @return {tuple} ret
        @return {boolean} ret[0] 是否认证通过
        @return {dict} ret[1] 当 result=True，该字段为用户信息，举例
            {
                u'username': u'',
                u'avatar': u''
            }
        """
        api_params = {
            "code": code,
        }
        try:
            response = send(ConfFixture.WEIXIN_INFO_URL, "GET", api_params)
            ret = response.get("ret")
            if ret == 0:
                return True, response["data"]
            else:
                logger.error(
                    u"通过微信授权码，获取用户信息失败，error={}，ret={}".format(response["msg"], ret)
                )
                return False, None
        except Exception:  # pylint: disable=broad-except
            logger.exception(u"通过微信授权码，获取用户信息异常")
            return False, None
