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

import json
import logging
import re

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from .utils import check_script, html_escape, html_escape_name, url_escape

SITE_URL = settings.SITE_URL
logger = logging.getLogger("app")


class CheckXssMiddleware(MiddlewareMixin):
    def __init__(self, *args, **kwargs):
        self.__escape_param_list = []
        super(CheckXssMiddleware, self).__init__(*args, **kwargs)

    def process_view(self, request, view, args, kwargs):
        try:
            # 判断豁免权
            if getattr(view, "escape_exempt", False):
                return None

            # 获取豁免参数名
            self.__escape_param_list = (
                getattr(view, "escape_exempt_param", [])
                if getattr(view, "escape_exempt_param", False)
                else []
            )

            escape_type = None
            if getattr(view, "escape_script", False):
                escape_type = "script"
            elif getattr(view, "escape_url", False):
                escape_type = "url"
            # get参数转换
            request.GET = self.__escape_data(request.path, request.GET, escape_type)
            # post参数转换
            request.POST = self.__escape_data(request.path, request.POST, escape_type)
        except Exception as err:  # pylint: disable=broad-except
            logger.error(u"CheckXssMiddleware 转换失败！%s" % err)
        return None

    def __escape_data(self, path, query_dict, escape_type=None):
        """
        GET/POST参数转义
        """
        data_copy = query_dict.copy()
        for _get_key, _get_value_list in data_copy.lists():
            new_value_list = []
            for _get_value in _get_value_list:
                new_value = _get_value
                # json串不进行转义
                try:
                    json.loads(_get_value)
                    is_json = True
                except Exception:  # pylint: disable=broad-except
                    is_json = False
                # 转义新数据
                if not is_json:
                    try:
                        if escape_type is None:
                            use_type = self.__filter_param(path, _get_key)
                        else:
                            use_type = escape_type

                        if use_type == "url":
                            new_value = url_escape(_get_value)
                        elif use_type == "script":
                            new_value = check_script(_get_value)
                        elif use_type == "name":
                            new_value = html_escape_name(_get_value)
                        elif _get_key in self.__escape_param_list:
                            new_value = _get_value
                        else:
                            new_value = html_escape(_get_value, 1)
                    except Exception as err:  # pylint: disable=broad-except
                        logger.error(u"CheckXssMiddleware GET/POST参数 转换失败！%s" % err)
                        new_value = _get_value
                else:
                    try:
                        new_value = html_escape(_get_value, 1, True)
                    except Exception as err:  # pylint: disable=broad-except
                        logger.error(u"CheckXssMiddleware GET/POST参数 转换失败！%s" % err)
                        new_value = _get_value
                new_value_list.append(new_value)
            data_copy.setlist(_get_key, new_value_list)
        return data_copy

    def __filter_param(self, path, param):
        """
        特殊path处理
        @param path: 路径
        @param param: 参数
        @return: 'html/name/url/script/exempt'
        """
        use_name, use_url, use_script = self.__filter_path_list()
        try:
            result = "html"
            # name过滤
            for name_path, name_v in use_name.items():
                is_path = re.match(r"^%s" % name_path, path)
                if is_path and param in name_v:
                    result = "name"
                    break
            # url过滤
            if result == "html":
                for url_path, url_v in use_url.items():
                    is_path = re.match(r"^%s" % url_path, path)
                    if is_path and param in url_v:
                        result = "url"
                        break
            # script过滤
            if result == "html":
                for script_path, script_v in use_script.items():
                    is_path = re.match(r"^%s" % script_path, path)
                    if is_path and param in script_v:
                        result = "script"
                        break
        except Exception as err:  # pylint: disable=broad-except
            logger.error(u"CheckXssMiddleware 特殊path处理失败！%s" % err)
            result = "html"
        return result

    def __filter_path_list(self):
        """
        特殊path注册
        """
        use_name = {}
        use_url = {
            "%saccounts/login" % SITE_URL: ["next"],
            "%saccounts/login_page" % SITE_URL: ["req_url"],
            "%saccounts/login_success" % SITE_URL: ["req_url"],
            "%s" % SITE_URL: ["url"],
        }
        use_script = {}
        return (use_name, use_url, use_script)
