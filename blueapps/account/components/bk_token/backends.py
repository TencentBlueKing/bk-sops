# -*- coding: utf-8 -*-
import logging
import traceback

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.db import IntegrityError

from blueapps.account import get_user_model
from blueapps.account.conf import ConfFixture
from blueapps.account.utils.http import send
from blueapps.utils import client

logger = logging.getLogger('component')

ROLE_TYPE_ADMIN = '1'


class TokenBackend(ModelBackend):
    def authenticate(self, request=None, bk_token=None):
        logger.debug(u"Enter in TokenBackend")
        # 判断是否传入验证所需的bk_token,没传入则返回None
        if not bk_token:
            return None

        verify_result, username = self.verify_bk_token(bk_token)
        # 判断bk_token是否验证通过,不通过则返回None
        if not verify_result:
            return None

        user_model = get_user_model()
        try:
            user, _ = user_model.objects.get_or_create(username=username)
            get_user_info_result, user_info = self.get_user_info(bk_token)
            # 判断是否获取到用户信息,获取不到则返回None
            if not get_user_info_result:
                return None
            user.set_property(key='qq', value=user_info.get('qq', ''))
            user.set_property(key='language',
                              value=user_info.get('language', ''))
            user.set_property(key='time_zone',
                              value=user_info.get('time_zone', ''))
            user.set_property(key='role', value=user_info.get('role', ''))
            user.set_property(key='phone', value=user_info.get('phone', ''))
            user.set_property(key='email', value=user_info.get('email', ''))
            user.set_property(key='wx_userid',
                              value=user_info.get('wx_userid', ''))
            user.set_property(key='chname', value=user_info.get('chname', ''))

            # 用户如果不是管理员，则需要判断是否存在平台权限，如果有则需要加上
            if not user.is_superuser and not user.is_staff:
                role = user_info.get('role', '')
                is_admin = True if str(role) == ROLE_TYPE_ADMIN else False
                user.is_superuser = is_admin
                user.is_staff = is_admin
                user.save()

            return user

        except IntegrityError:
            logger.exception(traceback.format_exc())
            logger.exception(
                u"get_or_create UserModel fail or update_or_create UserProperty"
            )
            return None
        except Exception:
            logger.exception(traceback.format_exc())
            logger.exception(u"Auto create & update UserModel fail")
            return None

    @staticmethod
    def get_user_info(bk_token):
        """
        请求平台ESB接口获取用户信息
        @param bk_token: bk_token
        @type bk_token: str
        @return:True, {
            u'message': u'\u7528\u6237\u4fe1\u606f\u83b7\u53d6\u6210\u529f',
            u'code': 0,
            u'data': {
                u'qq': u'',
                u'wx_userid': u'',
                u'language': u'zh-cn',
                u'username': u'test',
                u'time_zone': u'Asia/Shanghai',
                u'role': 2,
                u'phone': u'11111111111',
                u'email': u'test',
                u'chname': u'test'
            },
            u'result': True,
            u'request_id': u'eac0fee52ba24a47a335fd3fef75c099'
        }
        @rtype: bool,dict
        """
        api_params = {
            'bk_token': bk_token
        }

        try:
            response = client.bk_login.get_user(api_params)
        except Exception as e:
            logger.exception(u"Abnormal error in get_user_info...:%s" % e)
            return False, {}

        if response.get('result') is True:
            # 由于v1,v2的get_user存在差异,在这里屏蔽字段的差异,返回字段相同的字典
            origin_user_info = response.get('data', '')
            user_info = dict()
            # v1,v2字段相同的部分
            user_info['wx_userid'] = origin_user_info.get('wx_userid', '')
            user_info['language'] = origin_user_info.get('language', '')
            user_info['time_zone'] = origin_user_info.get('time_zone', '')
            user_info['phone'] = origin_user_info.get('phone', '')
            user_info['chname'] = origin_user_info.get('chname', '')
            user_info['email'] = origin_user_info.get('email', '')
            user_info['qq'] = origin_user_info.get('qq', '')
            # v2版本特有的字段
            if settings.DEFAULT_BK_API_VER == 'v2':
                user_info['username'] = origin_user_info.get('bk_username', '')
                user_info['role'] = origin_user_info.get('bk_role', '')
            # v1版本特有的字段
            elif settings.DEFAULT_BK_API_VER == '':
                user_info['username'] = origin_user_info.get('username', '')
                user_info['role'] = origin_user_info.get('role', '')
            return True, user_info
        else:
            error_msg = response.get('message', '')
            error_data = response.get('data', '')
            logger.error(u"Failed to Get User Info: error=%(err)s, ret=%(ret)s"
                         % {
                             u'err': error_msg,
                             u'ret': error_data,
                         })
            return False, {}

    @staticmethod
    def verify_bk_token(bk_token):
        """
        请求VERIFY_URL,认证bk_token是否正确
        @param bk_token: "_FrcQiMNevOD05f8AY0tCynWmubZbWz86HslzmOqnhk"
        @type bk_token: str
        @return: False,None True,username
        @rtype: bool,None/str
        """
        api_params = {
            'bk_token': bk_token
        }

        try:
            response = send(ConfFixture.VERIFY_URL, 'GET', api_params,
                            verify=False)
        except Exception:
            logger.exception(u"Abnormal error in verify_bk_token...")
            return False, None

        if response.get('result'):
            data = response.get('data')
            username = data.get('username')
            return True, username
        else:
            error_msg = response.get('message', '')
            error_data = response.get('data', '')
            logger.error(u"Fail to verify bk_token, error=%s, ret=%s" % (
                error_msg, error_data))
            return False, None
