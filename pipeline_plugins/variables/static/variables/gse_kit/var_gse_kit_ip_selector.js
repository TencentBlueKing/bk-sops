/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

(function () {
    $.atoms.gse_kit_ip_selector = [
        {
            tag_code: "ip_selector",
            type: "combine",
            name: gettext("GSEKit IP 选择器"),
            attrs: {
                name: gettext("GSEKit IP 选择器"),
                hookable: true,
                children: [
                   {
                        tag_code: "var_set_env",
                        type: "select",
                        attrs: {
                            name: gettext("集群环境类型"),
                            placeholder: gettext("集群环境类型"),
                            remote: true,
                            remote_url: $.context.get('site_url') + 'pipeline/cc_get_set_env/set' + '/' + $.context.getBkBizId() + '/',
                            hookable: true,
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value) {
                                        var self = this
                                        var result = {
                                            result: true,
                                            error_message: ""
                                        }
                                        if (!self.get_parent) {
                                            return result
                                        } else if (!value) {
                                            result.result = false;
                                            result.error_message = gettext("请选择集群环境类型");
                                        }
                                        return result
                                    }
                                }
                            ],
                            remote_data_init: function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, 'error');
                                }
                                return resp.data;
                            },
                        },
                    },
                    {
                        tag_code: "var_set_name",
                        type: "input",
                        attrs: {
                            name: gettext("集群"),
                            placeholder: gettext("集群，默认值为 *"),
                            hookable: true,
                        },
                    },
                    {
                        tag_code: "var_module_name",
                        type: "input",
                        attrs: {
                            name: gettext("模块"),
                            placeholder: gettext("模块，默认值为 *"),
                            hookable: true,
                        },
                    },
                    {
                        tag_code: "var_service_instance_name",
                        type: "input",
                        attrs: {
                            name: gettext("服务实例"),
                            placeholder: gettext("服务实例，默认值为 *"),
                            hookable: true,
                        },
                    },
                    {
                        tag_code: "var_process_name",
                        type: "input",
                        attrs: {
                            name: gettext("进程"),
                            placeholder: gettext("进程，默认值为 *"),
                            hookable: true,
                        },
                    },
                    {
                        tag_code: "var_process_instance_id",
                        type: "input",
                        attrs: {
                            name: gettext("进程实例"),
                            placeholder: gettext("进程实例，默认值为 *"),
                            hookable: true,
                        },
                    },
                ]
            }
            },
    ]
})();
