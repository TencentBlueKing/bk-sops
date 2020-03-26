/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
(function () {
    $.atoms.var_cmdb_ip_selector = [
        {
            tag_code: "ip_selector",
            type: "ip_selector",
            attrs: {
                name: gettext("选择服务器"),
                hookable: true,
                isMultiple: false,
                validation: [
                    {
                        type: "required"
                    }
                ],
                default: {
                    "selectors": ["ip"],
                    "topo": [],
                    "ip": [],
                    "filters": [],
                    "excludes": [],
                    "with_cloud_id": false
                },
                remote_url: function () {
                    if (!$.context.canSelectBiz()) {
                        return {
                            "cc_search_host": $.context.get("site_url") + "pipeline/cc_search_host/" + $.context.getBkBizId() + "/",
                            "cc_search_topo_tree": $.context.get("site_url") + "pipeline/cc_search_topo_tree/" + $.context.getBkBizId() + "/",
                            "cc_get_mainline_object_topo": $.context.get("site_url") + "pipeline/cc_get_mainline_object_topo/" + $.context.getBkBizId() + "/"
                        }
                    } else {
                        show_msg(gettext("该变量只能在关联CMDB业务的项目下使用"), "error");
                        return {
                            "cc_search_host": "",
                            "cc_search_topo_tree": "",
                            "cc_get_mainline_object_topo": ""
                        }
                    }
                }
            }
        },
    ]
})();
