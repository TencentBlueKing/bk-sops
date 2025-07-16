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

import logging

import requests
import ujson as json
from django.utils.translation import gettext_lazy as _

import env
from gcloud.conf import settings
from gcloud.core.models import EnvironmentVariables

logger = logging.getLogger("component")
ENV = "stag" if settings.IS_LOCAL else "prod"
LIGHT_APP_API = "{}/{}/system/light-applications/".format(
    env.BK_APIGW_URL_TMPL.format(api_name=env.PAASV3_APIGW_NAME), ENV
)

try:
    PAASV3_TOKEN = EnvironmentVariables.objects.get_var("PAASV3_APIGW_API_TOKEN")
except Exception as error:
    PAASV3_TOKEN = None
    logger.exception("get PAASV3_APIGW_API_TOKEN from EnvironmentVariables raise error: {}".format(error))


def _request_paasv3_light_app_api(url, method, params=None, data=None):
    method_func = getattr(requests, method)

    headers = {"Content-Type": "application/json"}
    if PAASV3_TOKEN:
        headers["Authorization"] = "Bearer {}".format(PAASV3_TOKEN)

    logger.debug(
        "paasv3 request({method}) {url} with headers: {headers}, data: {data}, params: {params}".format(
            method=method, url=url, headers=headers, data=data, params=params
        )
    )

    try:
        response = method_func(url, data=json.dumps(data or {}), headers=headers, params=params or {})
    except Exception as e:
        message = _(f"轻应用请求Paas接口报错: 请求url: {url}, 报错内容: {e}")
        logger.error(message)

        return {"result": False, "message": message}

    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        message = _(
            f"轻应用请求Paas接口报错: 请求url: {response.request.url}, 报错内容: {e}, 响应内容: {response.text}"
        )
        logger.error(message)

        return {"result": False, "message": message}

    try:
        resp_data = response.json()
        logger.debug("paasv3 request({url}) return: {data}".format(url=response.request.url, data=resp_data))
        if not resp_data["result"]:
            logger.error(
                "paasv3 return error, message {message}, request_id={request_id}, "
                "url={url}, headers={headers}, params={params}, data={data}, "
                "response={response}".format(
                    message=resp_data.get("bk_error_msg"),
                    request_id=resp_data.get("request_id"),
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    response=response.text,
                )
            )
            resp_data["message"] = resp_data.get("bk_error_msg")
        return resp_data
    except Exception as e:
        message = _(
            f"轻应用请求PaaS接口报错: 请求url {response.request.url}, 接口响应json格式转换失败 {e}，响应内容 {response.content}"
        )
        logger.error(message)

        return {"result": False, "message": message}


def create_maker_app(
    creator,
    app_name,
    app_url,
    developer="",
    app_tag="",
    introduction="",
    add_user="",
    company_code="",
):
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

    data = {
        "bk_app_code": settings.APP_CODE,
        "bk_app_secret": settings.SECRET_KEY,
        "parent_app_code": settings.APP_CODE,
        "app_name": app_name,
        "app_url": app_url,
        "developers": developer.split(","),
        "app_tag": app_tag,
        "creator": creator,
        "introduction": introduction or app_name,
    }

    resp = _request_paasv3_light_app_api(url=LIGHT_APP_API, method="post", data=data)

    if resp["result"]:
        resp["data"]["bk_light_app_code"] = resp["data"]["light_app_code"]

    return resp


def edit_maker_app(
    operator,
    app_maker_code,
    app_name="",
    app_url="",
    developer="",
    app_tag="",
    introduction="",
    add_user="",
    company_code="",
):
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

    data = {
        "bk_app_code": settings.APP_CODE,
        "bk_app_secret": settings.SECRET_KEY,
        "light_app_code": app_maker_code,
        "app_name": app_name,
    }

    if app_url:
        data["app_url"] = app_url

    if developer:
        data["developers"] = developer.split(",")

    if app_tag:
        data["app_tag"] = app_tag

    if introduction:
        data["introduction"] = introduction

    resp = _request_paasv3_light_app_api(url=LIGHT_APP_API, method="patch", data=data)

    return resp


def del_maker_app(operator, app_maker_code):
    """
    @summary: 删除 maker app
    @param operator：操作者英文id
    @param app_maker_code: maker app编码
    @return: {'result': True, 'message':u"APP Maker 删除成功"}
    {'result': False, 'message':u"APP Maker 删除失败"}
    """

    params = {
        "bk_app_code": settings.APP_CODE,
        "bk_app_secret": settings.SECRET_KEY,
        "light_app_code": app_maker_code,
    }

    resp = _request_paasv3_light_app_api(url=LIGHT_APP_API, method="delete", params=params)

    return resp


def modify_app_logo(operator, app_maker_code, logo):
    """
    @summary: 修改轻应用的 logo
    @param operator：操作者英文id
    @param app_maker_code: maker app编码
    @param logo: maker app编码
    @return: {'result': True, 'message':u"APP LOGO 修改成功"}
    {'result': False, 'message':u"APP LOGO 修改失败"}
    """
    data = {
        "bk_app_code": settings.APP_CODE,
        "bk_app_secret": settings.SECRET_KEY,
        "light_app_code": app_maker_code,
        "logo": logo.decode("ascii"),
    }

    resp = _request_paasv3_light_app_api(url=LIGHT_APP_API, method="patch", data=data)

    return resp


def get_app_logo_url(app_code):

    params = {
        "bk_app_code": settings.APP_CODE,
        "bk_app_secret": settings.SECRET_KEY,
        "light_app_code": app_code,
    }

    resp = _request_paasv3_light_app_api(url=LIGHT_APP_API, method="get", params=params)

    if not resp["result"]:
        return ""

    return resp["data"]["logo"]
