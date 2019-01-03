# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import datetime
import json
import logging

from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.http import (HttpResponse,
                         HttpResponseRedirect,
                         JsonResponse,
                         HttpResponseForbidden)
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import check_for_language

from bk_api import is_user_functor, is_user_auditor
from common.mymako import render_mako_context

from gcloud import exceptions
from gcloud.conf import settings
from gcloud.core.models import UserBusiness
from gcloud.core.utils import (prepare_user_business,
                               prepare_business, convert_group_name)
from gcloud.core.roles import (CC_ROLES,
                               FUNCTOR,
                               ROLES_DECS,
                               MAINTAINERS)


logger = logging.getLogger("root")


def page_not_found(request):
    user = authenticate(request=request)
    # 未登录重定向到首页，跳到登录页面
    if not user:
        return HttpResponseRedirect(settings.SITE_URL)
    request.user = user
    return render_mako_context(request, '/core/base_vue.html', {})


def home(request):
    username = request.user.username
    try:
        biz_list = prepare_user_business(request)
    except exceptions.Unauthorized:
        return HttpResponseRedirect(settings.SITE_URL + 'error/401/')
    except exceptions.Forbidden:
        return HttpResponseRedirect(settings.SITE_URL + 'error/403/')
    except exceptions.APIError as e:
        ctx = {
            'system': e.system,
            'api': e.api,
            'message': e.message,
        }
        return HttpResponse(status=503, content=json.dumps(ctx))
    if biz_list:
        try:
            obj = UserBusiness.objects.get(user=username)
            biz_cc_id = obj.default_buss
            biz_cc_id_list = [item.cc_id for item in biz_list]
            if biz_cc_id not in biz_cc_id_list:
                biz_cc_id = biz_cc_id_list[0]
                obj.default_buss = biz_cc_id
                obj.save()
        except UserBusiness.DoesNotExist:
            biz_cc_id = biz_list[0].cc_id
            UserBusiness.objects.create(user=username, default_buss=biz_cc_id)
        return HttpResponseRedirect(settings.SITE_URL + 'business/home/' + str(biz_cc_id) + '/')
    else:
        return HttpResponseRedirect(settings.SITE_URL + 'error/406/')


def biz_home(request, biz_cc_id):
    """
    @note: only use to authentication
    @param request:
    @param biz_cc_id:
    @return:
    """
    ctx = {
        'biz_cc_id': biz_cc_id
    }
    return render_mako_context(request, '/core/base_vue.html', ctx)


def change_user_default_biz(request, biz_cc_id):
    """
    @summary: 切换用户默认业务
    @param request:
    """
    username = request.user.username
    if biz_cc_id:
        user_business, created = UserBusiness.objects.get_or_create(
            user=username,
            defaults={"default_buss": biz_cc_id})
        if not created:
            user_business.default_buss = biz_cc_id
            user_business.save()
    return JsonResponse({
        'result': True,
        'message': _(u"更换用户默认业务成功！")
    })


def get_authorized_biz_list(request):
    """
    @summary 获取用户可操作列表
    @param request:
    @return:
    """
    biz_list = prepare_user_business(request)
    data = [{"text": biz.cc_name,
             "id": biz.cc_id}
            for biz in biz_list]

    return JsonResponse({"result": True, "data": data})


def get_biz_person_list(request, biz_cc_id):
    """
    @summary: 获取业务相关人员信息
    @param request:
    @param biz_cc_id:
    @return:
    """
    original = request.GET.get('original', '')
    role_list = CC_ROLES
    # 模板授权需要去掉运维角色，运维默认有所有权限
    if original == 'tasktmpl_list':
        role_list = [role for role in role_list if
                     role != MAINTAINERS]

        # 并添加职能化人员
        role_list.append(FUNCTOR)

    try:
        prepare_business(request, cc_id=biz_cc_id)
    except Exception as e:
        logger.error('get_biz_person_list error, biz_cc_id=%s, error=%s' % (biz_cc_id, e))

    person_list = []
    for key in role_list:
        name = ROLES_DECS[key]
        group_name = convert_group_name(biz_cc_id, key)
        group = Group.objects.get(name=group_name)
        user_list = group.user_set.all()
        data_list = []
        for user in user_list:
            openid = user.username
            data_list.append({
                "text": user.full_name,
                "id": openid,
            })
        # if data_list:
        data_list.insert(0, {
            "text": _(u"所有%s") % name,
            "id": key
        })
        person_list.append({
            "text": name,
            "children": data_list
        })
    return JsonResponse({
        "result": True,
        "data": person_list
    })


def set_language(request):

    next = None
    if request.method == 'GET':
        next = request.GET.get('next', None)
    elif request.method == 'POST':
        next = request.POST.get('next', None)

    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)

    if request.method == 'GET':
        lang_code = request.GET.get('language', None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session["blueking_language"] = lang_code
            max_age = 60 * 60 * 24 * 365
            expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                                                 "%a, %d-%b-%Y %H:%M:%S GMT")
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code, max_age, expires)
    return response
