# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.backends import ModelBackend

from blueapps.account.utils.http import send
from blueapps.account import get_user_model
from blueapps.account.conf import ConfFixture

logger = logging.getLogger('component')


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
        logger.debug(u"微信 CODE 验证结果，result：%s，user_info：%s" % (
            result, user_info)
        )

        if not result:
            return None

        user_model = get_user_model()
        try:
            user, _ = user_model.objects.get_or_create(
                username=user_info['username'])
            user.nickname = user_info['username']
            user.avatar_url = user_info['avatar']
            user.save()
        except Exception:
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
            'code': code,
        }
        try:
            response = send(ConfFixture.WEIXIN_INFO_URL, 'GET', api_params)
            ret = response.get('ret')
            if ret == 0:
                return True, response['data']
            else:
                logger.error(u"通过微信授权码，获取用户信息失败，error=%s，ret=%s" % (
                    response['msg'], ret))
                return False, None
        except Exception:
            logger.exception(u"通过微信授权码，获取用户信息异常")
            return False, None
