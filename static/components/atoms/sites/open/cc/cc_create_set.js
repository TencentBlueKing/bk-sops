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
    $.atoms.cc_create_set = [
        {
            tag_code: "cc_set_parent_select",
            type: "tree",
            attrs: {
                name: gettext("父实例"),
                hookable: true,
                remote: true,
                remote_url: $.context.site_url + 'pipeline/cc_search_topo/set/prev/' + $.context.biz_cc_id + '/',
                remote_data_init: function (resp) {
                    return resp.data;
                },
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            methods: {}
        },
        {
            tag_code: "cc_set_info",
            type: "datatable",
            attrs: {
                name: gettext("集群信息"),
                remote_url: $.context.site_url + 'pipeline/cc_search_create_object_attribute/set/' + $.context.biz_cc_id + '/',
                remote_data_init: function(resp) {
                    return resp.data;
                },
                hookable: true,
                add_btn: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();
