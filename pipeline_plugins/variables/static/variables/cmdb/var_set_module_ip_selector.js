/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */
(function () {
    $.atoms.set_module_ip_selector = [
        {
            tag_code: "ip_selector",
            type: "combine",
            name: gettext("集群模块IP选择器"),
            attrs: {
                name: gettext("集群模块IP选择器"),
                hookable: true,
                children: [
                    {
                        tag_code: "var_ip_method",
                        type: "radio",
                        attrs: {
                            name: gettext("填参方式"),
                            items: [
                                {value: "custom", name: gettext("自定义输入IP")},
                                {value: "select", name: gettext("选择集群模块")},
                                {value: "manual", name: gettext("手动输入集群模块")},
                            ],
                            default: "custom",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "init",
                                action: function () {
                                     var self = this;

                                    function init_self(self) {
                                        setTimeout(function () {
                                            self.emit_event(self.tag_code, "change", self.value)
                                        }, 500)
                                    }
                                    init_self(self);
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_ip_custom_value",
                        type: "textarea",
                        hookable: true,
                        attrs: {
                            name: gettext("IP"),
                            placeholder: gettext("IP必须填写【云区域ID:IP】或者【IP】格式之一，多个用换行分隔；【IP】格式需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的"),
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "init",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'custom') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            },
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'custom') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_ip_select_value",
                        type: "combine",
                        attrs: {
                            name: gettext("集群模块IP选择器"),
                            hookable: true,
                            children: [
                                {
                                    tag_code: "var_set",
                                    type: "select",
                                    attrs: {
                                        name: gettext("选择集群"),
                                        multiple: true,
                                        searchable: true,
                                        hookable: true,
                                        placeholder: gettext("请选择集群"),
                                        remote: true,
                                        remote_url: $.context.get('site_url') + 'pipeline/cc_get_set_list/' + $.context.getBkBizId() + '/' + '?&all=true',
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, 'error');
                                            }
                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    },
                                },
                                {
                                    tag_code: "var_module",
                                    type: "select",
                                    attrs: {
                                        name: gettext("选择服务模板"),
                                        hookable: true,
                                        multiple: true,
                                        placeholder: gettext("请选择服务模板"),
                                        remote: true,
                                        remote_url: $.context.get('site_url') + 'pipeline/cc_get_service_template_list/' + $.context.getBkBizId() + '/' + '?&all=true',
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, 'error');
                                            }
                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    },
                                },
                                {
                                    tag_code: "var_module_name",
                                    type: "textarea",
                                    hookable: true,
                                    attrs: {
                                        name: gettext("使用模块属性名"),
                                        placeholder: gettext("请输入需要使用的模块属性，多个用英文逗号分隔，不填默认为ip属性")
                                    },
                                }
                            ]
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "init",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'select') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            },
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'select') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_ip_manual_value",
                        type: "combine",
                        attrs: {
                            name: gettext("手动输入集群模块"),
                            hookable: true,
                            children: [
                                {
                                    tag_code: "var_manual_set",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("输入集群"),
                                        placeholder: gettext("请输入集群，多个使用英文逗号分隔，可输入all选择所有集群"),
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    },
                                },
                                {
                                    tag_code: "var_manual_module",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("输入服务模板"),
                                        placeholder: gettext("请输入服务模板，多个使用英文逗号分隔，可输入all选择所有服务模板"),
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    },
                                },
                                {
                                    tag_code: "var_module_name",
                                    type: "textarea",
                                    hookable: true,
                                    attrs: {
                                        name: gettext("使用模块属性名"),
                                        placeholder: gettext("请输入需要使用的模块属性，多个用英文逗号分隔，不填默认为ip属性")
                                    },
                                }
                            ]
                        },
                        events: [
                            {
                                source: "var_ip_method",
                                type: "init",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'manual') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            },
                            {
                                source: "var_ip_method",
                                type: "change",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'manual') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "var_filter_set",
                        type: "textarea",
                        hookable: true,
                        attrs: {
                            name: gettext("筛选集群"),
                            placeholder: gettext("请输入需要筛选的集群名称，多个使用英文逗号分隔，为空则不做筛选")
                        },
                    },
                    {
                        tag_code: "var_filter_module",
                        type: "textarea",
                        hookable: true,
                        attrs: {
                            name: gettext("筛选服务模板"),
                            placeholder: gettext("请输入需要筛选的服务模板名称，多个使用英文逗号分隔，为空则不做筛选")
                        },
                    },
                ]
            }
        }
    ]
})();
