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

import time

from blueapps.utils.esbclient import get_client_by_user

from gcloud.conf import settings


def create_maker_app(creator, app_name, app_url, developer='', app_tag='', introduction='', add_user='',
                     company_code=''):
    """
    @summary: 创建 maker app
    @param creator：创建者英文id
    @param app_name：app名称
    @param app_url：app链接, 请填写绝对地址
    @param developer: 填写开发者英文id列表，请用英文分号";"隔开
                                只有开发者才有操作该maker app的权限
    @param app_tag: 可选	String	轻应用分类
    @param introduction: 可选	String	轻应用描述
    @param add_user: 冗余字段，多版本兼容
    @param company_code: 冗余字段，多版本兼容
    @return: {'result': True, 'message':'', 'data': {'bk_light_app_code': 'xxxxx'}}
    {'result': False, 'message':u"APP Maker 创建出错", 'app_code':''}
    """
    client = get_client_by_user(creator)
    kwargs = {
        'creator': creator,
        'bk_app_code': settings.APP_CODE,
        'bk_light_app_name': app_name,
        'app_url': app_url,
        'developer': developer,
        'app_tag': app_tag,
        'introduction': introduction
    }
    result = client.bk_paas.create_app(kwargs)
    return result


def edit_maker_app(operator, app_maker_code, app_name='', app_url='', developer='', app_tag='', introduction='',
                   add_user='', company_code=''):
    """
    @summary: 修改 maker app
    @param operator：操作者英文id
    @param app_maker_code: maker app编码
    @param app_name：app名称,可选参数，为空则不修改名称
    @param app_url：app链接，可选参数，为空则不修改链接
    @param developer: 填写开发者英文id列表，请用英文分号";"隔开, 可选参数，为空则不修改开发者
                                    需传入修改后的所有开发者信息
    @param app_tag: 可选	String	轻应用分类
    @param introduction: 可选	String	轻应用描述
    @param add_user: 冗余字段，多版本兼容
    @param company_code: 冗余字段，多版本兼容
    @return: {'result': True, 'message':u"APP Maker 修改成功"}
    {'result': False, 'message':u"APP Maker 修改出错"}
    """
    client = get_client_by_user(operator)
    kwargs = {
        'operator': operator,
        'bk_light_app_code': app_maker_code,
        'bk_light_app_name': app_name,
        'app_url': app_url,
        'developer': developer,
        'app_tag': app_tag,
        'introduction': introduction
    }
    result = client.bk_paas.edit_app(kwargs)
    return result


def del_maker_app(operator, app_maker_code):
    """
    @summary: 删除 maker app
    @param operator：操作者英文id
    @param app_maker_code: maker app编码
    @return: {'result': True, 'message':u"APP Maker 删除成功"}
    {'result': False, 'message':u"APP Maker 删除失败"}
    """
    client = get_client_by_user(operator)
    kwargs = {
        'operator': operator,
        'bk_light_app_code': app_maker_code,
    }
    result = client.bk_paas.del_app(kwargs)
    return result


def modify_app_logo(operator, app_maker_code, logo):
    """
    @summary: 修改轻应用的 logo
    @param operator：操作者英文id
    @param app_maker_code: maker app编码
    @param logo: maker app编码
    @return: {'result': True, 'message':u"APP LOGO 修改成功"}
    {'result': False, 'message':u"APP LOGO 修改失败"}
    """
    client = get_client_by_user(operator)
    kwargs = {
        'operator': operator,
        'bk_light_app_code': app_maker_code,
        'logo': logo,
    }
    result = client.bk_paas.modify_app_logo(kwargs)
    return result


def get_app_logo_url(app_code):
    url_prefix = settings.BK_URL if settings.OPEN_VER == 'enterprise' else settings.BK_PAAS_HOST

    return '%s/media/applogo/%s.png?v=%s' % (
        url_prefix,
        app_code,
        time.time())
