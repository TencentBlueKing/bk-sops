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

import copy

from pipeline.core.constants import PE
from pipeline.component_framework.constants import LEGACY_PLUGINS_VERSION

from gcloud.commons.template.models import replace_template_id

from pipeline_web.wrapper import PipelineTemplateWebWrapper
from pipeline_web.plugin_management.models import DeprecatedPlugin


def find_deprecated_plugins_in_unfold_tree(tree, template_model, phases=None):
    """查找子流程未展开的树中已经下线的插件

    :param tree: 子流程未展开的树
    :type tree: dict
    :param template_model: 子流程引用的模板模型
    :type template_model: Model
    :return: {
        "found": True or False,
        "plugins": {
            "activities": [
                {
                    "id": "act_id",
                    "name": "act_name",
                    "component": "component_code",
                    "version": "component_version",
                    "subprocess": "subprocess_name"
                },
                ...
            ],
            "variables": [
                {
                    "key": "var_key",
                    "name": "var_name",
                    "custom_type": "var_code",
                    "version": "var version",
                    "subprocess": "subprocess_name"
                },
                ...
            ]
        }
    }
    :rtype: dict
    """

    check_tree = copy.deepcopy(tree)

    # replace template id to pipeline id
    replace_template_id(template_model, check_tree)

    # unfold subprocess reference
    PipelineTemplateWebWrapper.unfold_subprocess(check_tree, template_model)

    phases = phases or [DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED]

    return find_deprecated_plugins_in_spread_tree(tree=check_tree, phases=phases)


def find_deprecated_plugins_in_spread_tree(tree, phases=None):
    found_plugins = {"activities": [], "variables": []}

    # params process
    phases = phases or [DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED]

    deprecated_plugins = DeprecatedPlugin.objects.filter(phase__in=phases)

    if not deprecated_plugins.exists():
        return {"found": False, "plugins": found_plugins}

    deprecated_components = set()
    deprecated_variables = set()
    plugin_type_map = {
        DeprecatedPlugin.PLUGIN_TYPE_COMPONENT: deprecated_components,
        DeprecatedPlugin.PLUGIN_TYPE_VARIABLE: deprecated_variables,
    }

    # collect plugins according to code and version
    for plugin in deprecated_plugins:
        plugin_type_map[plugin.type].add(_code_ver_combine(plugin.code, plugin.version))

    def recursive_find(tree, found_plugins, subprocess_name):

        # find deprecated variables
        if deprecated_variables:
            for key, var in tree[PE.constants].items():
                if not var[PE.custom_type]:
                    continue

                code = var[PE.custom_type]
                version = var.get(PE.version, LEGACY_PLUGINS_VERSION)
                plugin_id = _code_ver_combine(code, version)

                if plugin_id in deprecated_variables:
                    found_plugins["variables"].append(
                        {
                            "key": key,
                            "name": var[PE.name],
                            "custom_type": code,
                            "version": version,
                            "subprocess": subprocess_name,
                        }
                    )

        if deprecated_components:
            # find deprecated components
            for act in tree[PE.activities].values():

                if act[PE.type] == PE.ServiceActivity:
                    code = act[PE.component][PE.code]
                    version = act[PE.component].get(PE.version, LEGACY_PLUGINS_VERSION)
                    plugin_id = _code_ver_combine(code, version)

                    if plugin_id in deprecated_components:
                        found_plugins["activities"].append(
                            {
                                "id": act[PE.id],
                                "name": act[PE.name],
                                "component": code,
                                "version": version,
                                "subprocess": subprocess_name,
                            }
                        )

                elif act[PE.type] == PE.SubProcess:
                    recursive_find(act[PE.pipeline], found_plugins, act[PE.name])

    recursive_find(tree, found_plugins, None)

    return {"found": bool(found_plugins["activities"] or found_plugins["variables"]), "plugins": found_plugins}


def _code_ver_combine(code, version):
    return "{}_{}".format(code, version)
