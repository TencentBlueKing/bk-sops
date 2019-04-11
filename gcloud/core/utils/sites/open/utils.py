# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import calendar
import datetime
import json
import re
import logging
import time
import pytz

from django.core.cache import cache
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils import six
from guardian.shortcuts import assign_perm

from gcloud.conf import settings
from gcloud import exceptions
from gcloud.core import roles
from gcloud.core.constant import AE
from gcloud.core.models import Business, BusinessGroupMembership
from gcloud.core.api_adapter import (
    is_user_functor,
    get_operate_user_list,
    is_user_auditor,
    get_auditor_user_list,
    get_user_info,
    adapt_get_user_data
)

logger = logging.getLogger("root")

CACHE_PREFIX = __name__.replace('.', '_')
DEFAULT_CACHE_TIME_FOR_CC = settings.DEFAULT_CACHE_TIME_FOR_CC


# LifeCycle：'1'：测试中， '2'：已上线， '3'： 停运， 其他如'0'、''是非法值
def _get_user_business_list(request, use_cache=True):
    """Get authorized business list for a exact username.

    :param object request: django request object.
    :param bool use_cache: (Optional)
    """
    user = request.user
    cache_key = "%s_get_user_business_list_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        user_info = _get_user_info(request)
        client = settings.ESB_GET_CLIENT_BY_USER(request.user.username)
        result = client.cc.search_business({
            'bk_supplier_account': user_info['bk_supplier_account'],
            'condition': {
                'bk_data_status': {'$in': ['enable', 'disabled', None]},
                '$or': [{'bk_biz_developer': {"$regex": user.username}},
                        {'bk_biz_productor': {"$regex": user.username}},
                        {'bk_biz_maintainer': {"$regex": user.username}},
                        {'bk_biz_tester': {"$regex": user.username}}]
            }
        })

        if result['result']:
            data = result['data']['info']
            cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        elif result.get('code') in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result.get('code') in ('20103', 20103, '20201', 20201,
                                    '20202', 20202):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(
                'cc',
                'search_business',
                result.get('detail_message', result['message'])
            )

    return data


def _get_user_info(request, use_cache=True):
    """
    获取用户基本信息
    @param request:
    @param use_cache:
    @return:
    """
    user = request.user
    cache_key = "%s_get_user_info_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)
    if not (use_cache and data):
        userinfo = get_user_info(request)
        userinfo.setdefault('code', -1)
        if userinfo['result']:
            data = userinfo['data']
            if data:
                cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        elif userinfo.get('code') in ('20101', 20101):
            raise exceptions.Unauthorized(userinfo['message'])
        elif userinfo.get('code') in ('20103', 20103, '20201', 20201,
                                      '20202', 20202):
            raise exceptions.Forbidden(userinfo['message'])
        else:
            raise exceptions.APIError(
                'bk_api',
                'get_user_info',
                userinfo.get('detail_message', userinfo['message'])
            )
    return data


def _get_business_info(request, app_id, use_cache=True, use_maintainer=False):
    """Get detail infomations for a exact app_id.

    @param object request: django request object.
    @param int app_id: cc_id of core.business model.
    @param use_maintainer: 使用运维身份请求
    """
    username = request.user.username
    business = Business.objects.get(cc_id=app_id)
    cache_key = "%s_get_business_info_%s_%s" % (CACHE_PREFIX, app_id, username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        if use_maintainer:
            client = get_client_by_user_and_biz_id(username, app_id)
        else:
            client = settings.ESB_GET_CLIENT_BY_REQUEST(request)
        result = client.cc.search_business({
            'bk_supplier_account': business.cc_owner,
            'condition': {
                'bk_biz_id': int(app_id)
            }
        })
        if result['result']:
            data = result['data']['info'][0]
        elif result.get('code') in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result.get('code') in ('20103', 20103, '20201', 20201,
                                    '20202', 20202):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(
                'cc',
                'get_app_by_id',
                result.get('detail_message', result['message'])
            )

        cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)

    return data


def add_maintainer_to_biz(user, business_list):
    user_group_name = [g.name for g in user.groups.all()]

    for business in business_list:
        group_name = convert_group_name(business.cc_id, roles.MAINTAINERS)
        if group_name in user_group_name:
            continue

        group, _ = Group.objects.get_or_create(name=group_name)

        # assign view business perm for all roles
        assign_perm('view_business', group, business)
        assign_perm('manage_business', group, business)

        BusinessGroupMembership.objects.get_or_create(
            business=business,
            group=group
        )
        user.groups.add(group)


def update_relationships(request, obj, extras, created=False, use_cache=True):
    """
    Update business-group(role) relationships & group-user memberships
    """
    cache_key = "%s_update_relationships_%s" % (CACHE_PREFIX, obj.cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        groups = {}
        # first, create related groups if not exist
        for role in roles.ALL_ROLES:
            group_name = convert_group_name(obj.cc_id, role)
            group, group_created = Group.objects.get_or_create(name=group_name)  # TODO
            groups[group_name] = (group, group_created)

            if group_created:
                # assign view business perm for all roles
                assign_perm('view_business', group, obj)

                # assign manage business perm only for admin roles
                if role in roles.ADMIN_ROLES:
                    assign_perm('manage_business', group, obj)

        with transaction.atomic():
            try:
                Business.objects.select_for_update().get(pk=obj.pk)
            except Business.DoesNotExist:
                return None

            data = cache.get(cache_key)

            if not (use_cache and data):
                # If not created, clear business to group memberships
                if not created:
                    obj.groups.clear()

                for group_name in groups:
                    group, created = groups[group_name]
                    # If not created, clear group to user memberships
                    if not created:
                        group.user_set.clear()

                    BusinessGroupMembership.objects.get_or_create(
                        business=obj,
                        group=group
                    )

                    role = group_name.split('\x00')[1]
                    resp_data_role = '{}'.format(roles.CC_V2_ROLE_MAP.get(role, role))
                    role_users = extras.get(resp_data_role) or ''
                    user_model = get_user_model()
                    user_list = role_users.split(',')

                    # 职能化人员单独授权
                    if role == roles.FUNCTOR:
                        user_list = get_operate_user_list(request)

                    # 审计人员单独授权
                    if role == roles.AUDITOR:
                        user_list = get_auditor_user_list(request)

                    for username in user_list:
                        if username:
                            user, _ = user_model.objects.get_or_create(
                                username=username)
                            user.groups.add(group)

                cache.set(cache_key, True, DEFAULT_CACHE_TIME_FOR_CC)


def prepare_view_all_business(request):
    """
    @summary：职能化和审计人员授权所有业务的查看权限
    """
    bizs = Business.objects.all()
    User = get_user_model()
    user = User.objects.get(username=request.user.username)

    for obj in bizs:
        group_name = convert_group_name(obj.cc_id, roles.AUDITOR)
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            # assign view business perm for all roles
            assign_perm('view_business', group, obj)

        BusinessGroupMembership.objects.get_or_create(
            business=obj,
            group=group
        )

        user.groups.add(group)


def get_business_obj(request, cc_id, use_cache=True, use_maintainer=False):
    cache_key = "%s_get_business_obj_%s" % (CACHE_PREFIX, cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        info = _get_business_info(request, cc_id, use_cache, use_maintainer)
        defaults = {
            'cc_name': info['bk_biz_name'],
            'cc_owner': info['bk_supplier_account'],
            'cc_company': info.get('bk_supplier_id') or 0,
            'time_zone': info['time_zone'],
            'life_cycle': info.get('life_cycle', '')
        }
        obj, created = Business.objects.update_or_create(
            cc_id=info['bk_biz_id'],
            defaults=defaults
        )

        data = (obj, created, info)

        cache.set(cache_key, (obj, False, info), DEFAULT_CACHE_TIME_FOR_CC)

    return data


def _update_user_info(info):
    info = adapt_get_user_data(info)
    User = get_user_model()
    User.objects.update_or_create(
        username=info['uin'],
        defaults=info
    )


def update_user_info(request, cc_id, use_cache=True):
    cache_key = "%s_update_user_info_%s" % (CACHE_PREFIX, cc_id)
    data = cache.get(cache_key)

    if not (use_cache and data):
        result = get_user_info(request)
        if result['result']:
            _update_user_info(result['data'])
        elif result['code'] in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result['code'] in ('20103', 20103):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(
                settings.ESB_AUTH_COMPONENT_SYSTEM,
                'get_user',
                result.get('detail_message', result['message'])
            )

        cache.set(cache_key, True, DEFAULT_CACHE_TIME_FOR_CC)


def prepare_business(request, cc_id, use_cache=True):
    # first, get the business object
    user = request.user
    if user.is_superuser or is_user_functor(request) or is_user_auditor(request):
        try:
            obj, created, extras = get_business_obj(request, cc_id, use_cache)
        except Exception:
            objs = Business.objects.filter(cc_id=cc_id)
            if not objs.exists():
                raise exceptions.Forbidden()
            obj = objs[0]
            extras = {}
    else:
        obj, created, extras = get_business_obj(request, cc_id, use_cache)

    # then, update business object relationships
    if extras:
        update_relationships(request, obj, extras)

    # update user info (uin and nick name)
    update_user_info(request, cc_id)

    return obj


def is_user_relate_business(user, biz):
    biz_roles = set()
    for role in roles.CC_V2_ROLE_MAP.values():
        members = str(biz[role]).split(',')
        biz_roles.update(members)

    return user.username in biz_roles


def prepare_user_business(request, use_cache=True):
    user = request.user
    cache_key = "%s_prepare_user_business_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)
    maintainer_key = roles.CC_V2_ROLE_MAP[roles.MAINTAINERS]

    if not (use_cache and data):
        data = []
        biz_list = _get_user_business_list(request, use_cache)
        maintainer_business = []

        for biz in biz_list:
            if biz['bk_biz_name'] == u"资源池":
                continue
            defaults = {
                'cc_name': biz['bk_biz_name'],
                'cc_owner': biz['bk_supplier_account'],
                'cc_company': biz.get('bk_supplier_id') or 0,
                'time_zone': biz.get('time_zone', ''),
                'life_cycle': biz.get('life_cycle', ''),
                'status': biz.get('bk_data_status', 'enable')
            }

            if defaults['status'] == 'disabled':
                try:
                    Business.objects.get(cc_id=biz['bk_biz_id'])
                except Business.DoesNotExist:
                    continue

            obj, _ = Business.objects.update_or_create(
                cc_id=biz['bk_biz_id'],
                defaults=defaults
            )

            if obj not in data and is_user_relate_business(user, biz):
                data.append(obj)

                if user.username in set(str(biz[maintainer_key]).split(',')):
                    maintainer_business.append(obj)

        # 为该用户有运维权限的业务添加运维角色，防止第一次进入时拉取不到业务列表
        add_maintainer_to_biz(user, maintainer_business)

        cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)

    return data


def get_biz_maintainer_info(biz_cc_id, username='', use_in_context=False):
    """
    获取当前业务下登录过的运维人员信息，包括 operator和auth_token
    @param biz_cc_id:
    @param username: 当前操作者
    @return: operator   业务运维
    @return: auth_token  业务运维的认证信息
    """
    business = Business.objects.get(cc_id=biz_cc_id)
    role = roles.MAINTAINERS
    group_name = convert_group_name(biz_cc_id, role)
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        logger.error('get_biz_maintainer_info raise error, group[%s] does not exist' % group_name)
        return '', ''
    maintainers = group.user_set.order_by('last_login')

    # 如果是用在流程的 context 中且业务打开了一直使用任务执行这开关
    if use_in_context and business.always_use_executor and business.executor:
        user = maintainers.filter(username=business.executor)
        if user.exists():
            return user[0].username, user[0].auth_token

    # 如果操作者就是运维，则首先尝试返回自己的信息
    if username:
        user = maintainers.filter(username=username)
        if user.exists():
            return username, user[0].auth_token

    # 如果业务执行者未从业务运维列表中删除，则使用业务执行者
    if business.executor:
        user = maintainers.filter(username=business.executor)
        if user.exists():
            return user[0].username, user[0].auth_token

    # 随机取包含 ESB 鉴权信息的运维
    authorized_maintainer = ''
    auth_token = ''
    for item in maintainers:
        if item.auth_token:
            authorized_maintainer = item.username
            auth_token = item.auth_token
            break

    return authorized_maintainer, auth_token


def get_client_by_user_and_biz_id(username, biz_cc_id):
    """
    @summary: 根据用户和业务获取运维身份的client
    :param username:
    :param biz_cc_id:
    :return:
    """
    # 首先以存在auth_token的运维身份调用接口
    maintainer, __ = get_biz_maintainer_info(biz_cc_id, username)
    if maintainer:
        return settings.ESB_GET_CLIENT_BY_USER(maintainer)

    # 无任何业务的运维auth_token信息，只能以自己身份执行
    return settings.ESB_GET_CLIENT_BY_USER(username)


def time_now_str():
    return timezone.localtime(timezone.now()).strftime('%Y%m%d%H%M%S')


def strftime_with_timezone(utc_time):
    if utc_time:
        return timezone.localtime(utc_time).strftime('%Y-%m-%d %H:%M:%S %z')
    else:
        return ''


def convert_readable_username(username):
    """将用户名转换成昵称"""
    return username


def name_handler(name, max_length):
    """名称处理"""
    # 替换特殊字符
    name_str = re.compile(r'[<>.,;~!@#^&*￥\'\"]+').sub('', name)
    # 长度截取
    return name_str[:max_length]


def timestamp_to_datetime(timestamp):
    """
    时间戳转为datetime类型
    :param timestamp:
    :return:
    """
    try:
        # 前端是传过来的是毫秒需要进行转换为秒
        timestamp = timestamp / 1000
        # 时间戳转为 datetime
        return timezone.datetime.fromtimestamp(timestamp, tz=pytz.utc)
    except ValueError:
        logger.error("illegal parameter format :%s" % time)
        return None


def format_datetime(dt):
    """
    时间转换为字符串格式（附带时区）
    :param dt: type:datetime.datetime
    :return:
    """
    # translate to time in local timezone
    if not dt:
        return ''
    if timezone.is_aware(dt):
        dt = timezone.localtime(dt)
    return dt.strftime("%Y-%m-%d %H:%M:%S %z")


def check_and_rename_params(conditions, group_by, group_by_check=AE.group_list):
    """
    检验参数是否正确
    :param conditions:参数是一个dict
    :param group_by:分组凭据
    :param group_by_check:分组检查内容
    :return:
    """
    # conditions 是否是一个dict.
    # 本地测试时请注释该try
    result_dict = {'success': False, 'content': None, "conditions": conditions, "group_by": None}
    try:
        conditions = json.loads(conditions)
    except Exception:
        message = u"param conditions[%s] cannot be converted to dict" % conditions
        logger.error(message)
        result_dict['content'] = message
        return result_dict
    if 'biz_cc_id' in conditions:
        conditions.update(business__cc_id=conditions.pop('biz_cc_id'))
    if not isinstance(conditions, dict):
        message = u"params conditions[%s] are invalid dict data" % conditions
        logger.error(message)
        result_dict['content'] = message
        return result_dict
    # 检查传递分组是否有误
    if group_by not in group_by_check:
        message = u"params group_by[%s] is invalid" % group_by
        logger.error(message)
        result_dict['content'] = message
        return result_dict
    # 如果是 biz_cc_id 需要转换
    # 为了防止显示出现外键调用
    if group_by == 'biz_cc_id':
        group_by = 'business__cc_id'
    result_dict['success'] = True
    result_dict['group_by'] = group_by
    result_dict['conditions'] = conditions
    return result_dict


def convert_group_name(biz_cc_id, role):
    return '%s\x00%s' % (biz_cc_id, role)


def camel_case_to_underscore_naming(source):
    """
    将驼峰形式字符串转为下划线形式
    :param source:
    :return:
    """
    if not isinstance(source, six.string_types):
        return source
    result = ''
    for i, s in enumerate(source):
        if i == 0:
            result += s.lower()
        else:
            if s.isupper():
                if source[i - 1].islower():
                    result += '_' + s.lower()
                else:
                    result += s.lower()
            else:
                result += s
    return result


def gen_day_dates(start_time, days):
    """
        获取两个日期之间的所有日期
        :param start_time: 开始时间:
        :param days: 相差日期:
        :return:
        """
    day = datetime.timedelta(days=1)
    for index in range(days):
        yield start_time + day * index


def get_month_dates(start_time, end_time):
    """
    获取两个日期之间的所有月份
    :param start_time: 开始时间:
    :param end_time: 结束时间
    :return:
    """
    out_dates = []
    # 需要额外是最后一天的情况，需要增加一天
    _, last_day = calendar.monthrange(start_time.year, start_time.month)
    if last_day == start_time.day:
        start_time += datetime.timedelta(days=1)
    while start_time <= end_time:
        date_str = start_time.strftime('%Y-%m')
        if date_str not in out_dates:
            out_dates.append(date_str)
        start_time = add_months(start_time, 1)
    return out_dates


def add_months(dt, months):
    """
    添加N个月份
    :param dt: 开始时间:
    :param months: 增加的月份
    :return:
    """
    month = dt.month - 1 + months
    year = dt.year + month / 12
    month = month % 12 + 1
    return dt.replace(year=year, month=month)
