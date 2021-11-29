# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from functools import wraps

from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

from pipeline.component_framework.models import ComponentModel

from plugin_service.plugin_client import PluginServiceApiClient
from plugin_service import env
from gcloud.analysis_statistics.models import TemplateNodeStatistics

# 缓存时间 1小时
REMOTE_PLUGIN_NAME_CACHE_KEY = "remote_plugin_name"
REMOTE_PLUGIN_NAME_CACHE_TIME = 60 * 60
REMOTE_PLUGIN_DETAIL_CACHE_KEY = "remote_plugin_detail"
REMOTE_PLUGIN_DETAIL_CACHE_TIME = 60 * 60


def query_cache(key, expires):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = cache.get(key)
            if value:
                return value
            value = func(*args, **kwargs)
            cache.set(key, value, expires)
            return value

        return wrapper

    return decorator


@query_cache(REMOTE_PLUGIN_NAME_CACHE_KEY, REMOTE_PLUGIN_NAME_CACHE_TIME)
def get_remote_plugin_name(limit=100, offset=0):
    """
    @summary: 拉取第三方插件名
    @param: limit: 拉取第三方插件数据默认limit，默认为100
    @param: offset: 拉取第三方插件分页起点，默认为0
    return plugin_info:dict() 第三方插件信息
    """
    TOTAL = limit
    CUR_TOTAL = 0

    plugin_info = {}
    if not env.USE_PLUGIN_SERVICE == "1":
        return plugin_info
    while CUR_TOTAL < TOTAL:
        result = PluginServiceApiClient.get_paas_plugin_info(
            search_term=None, environment="prod", limit=limit, offset=offset
        )
        if result.get("result") is False:
            return plugin_info
        for plugin in result["results"]:
            plugin_info.setdefault(plugin["code"], plugin["name"])
            CUR_TOTAL += 1
        TOTAL = result.get("count", 0)
        offset += 1
    return plugin_info


@query_cache(REMOTE_PLUGIN_DETAIL_CACHE_KEY, REMOTE_PLUGIN_DETAIL_CACHE_TIME)
def get_remote_plugin_detail_list(limit=100, offset=0):
    """
    @summary: 拉取第三方插件详细信息
    @param: limit: 拉取第三方插件数据默认limit，默认为100
    @param: offset: 拉取第三方插件分页起点，默认为0
    return plugin_info:list() 第三方插件信息
    """
    TOTAL = limit
    CUR_TOTAL = 0

    plugin_info = []
    if not env.USE_PLUGIN_SERVICE == "1":
        return plugin_info

    # 取所有第三方插件code和version
    remote_plugins = list(
        TemplateNodeStatistics.objects.filter(is_remote=True).values_list("component_code", "version")
    )
    remote_plugin_dict = {}
    for plugin in remote_plugins:
        # plugin ["code","version"]
        remote_plugin_dict.setdefault(plugin[0], {plugin[1]}).add(plugin[1])
    while CUR_TOTAL < TOTAL:
        result = PluginServiceApiClient.get_paas_plugin_info(
            search_term=None, environment="prod", limit=limit, offset=offset
        )
        if result.get("result") is False:
            return plugin_info
        for plugin in result["results"]:
            CUR_TOTAL += 1
            versions = remote_plugin_dict.get(plugin["code"])
            if not versions:
                continue
            plugin_info.extend(
                [
                    {
                        "name": plugin["name"],
                        "version": version,
                        "code": plugin["code"],
                        "group_name": "第三方插件",
                        "is_remote": True,
                    }
                    for version in versions
                ]
            )
        TOTAL = result.get("count", 0)
        offset += 1
    return plugin_info


def component_name(group_name, name, version):
    return "{}-{}-{}".format(_(group_name), _(name), version)


def format_component_name(components: list, components_list: list):
    """
    @summary: 插件名格式化
    @param: components: component对象列表
    @param: components_list: 插件数据列表
    return groups
    """
    groups = []
    for comp in components:
        version = comp["version"]
        # 插件名国际化
        name = comp["name"].split("-")
        name = component_name(name[0], name[1], version)
        code = "{}-{}".format(comp["code"], comp["version"])
        value = 0
        for oth_com_tmp in components_list:
            if comp["code"] == oth_com_tmp["component_code"] and comp["version"] == oth_com_tmp["version"]:
                value += oth_com_tmp["value"]
        groups.append({"code": code, "name": name, "value": value})
    return groups


def format_component_name_with_remote(components: list, comp_name_dict: dict):
    """
    @summary: 插件名格式化
    @param: components: 插件数据
    @param: comp_name_dict: 插件code:name字典
    return groups
    """
    remote_plugin_dict = get_remote_plugin_name()
    groups = []
    for comp in components:
        version = comp["version"]
        # 插件名国际化
        if not comp["is_remote"]:
            # 系统内置插件
            name = comp_name_dict.get(comp["component_code"], comp["component_code"]).split("-")
            name = component_name(name[0], name[1], version)
        else:
            # 第三方插件
            name = remote_plugin_dict.get(comp["component_code"], comp["component_code"]).split("-")
            name = component_name("第三方插件", name[0], version)
        code = "{}-{}".format(comp["component_code"], comp["version"])
        value = comp["value"]
        groups.append({"code": code, "name": name, "value": value})
    return groups


def get_inner_components():
    components = ComponentModel.objects.values("code", "version", "name")
    component_list = []
    for comp in components:
        code = comp["code"]
        name = comp["name"].split("-")
        group_name = _(name[0])
        name = _(name[1])
        version = comp["version"]
        component_list.append(
            {"name": name, "group_name": group_name, "version": version, "code": code, "is_remote": False}
        )
    return component_list


def get_all_components():
    inner_components = get_inner_components()
    remote_components = get_remote_plugin_detail_list()
    return inner_components + remote_components
