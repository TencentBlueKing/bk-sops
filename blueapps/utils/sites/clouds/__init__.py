# -*- coding: utf-8 -*-
import logging
from bkoauth import get_access_token_by_user

from blueapps.account import get_user_model

logger = logging.getLogger('blueapps')


def get_component_client_common_args():
    """
    获取ComponentClient需要的common_args
    @return:
    {
        access_token = 'xxx'
    }
    @rtype: dict
    """
    try:
        last_login_user = \
            get_user_model().objects.all().order_by("-last_login")[0]
    except IndexError:
        logger.exception("There is not a last_login_user")
        raise IndexError("There is not a last_login_user")
    access_token = get_access_token_by_user(
        last_login_user.username).access_token
    return dict(access_token=access_token)
