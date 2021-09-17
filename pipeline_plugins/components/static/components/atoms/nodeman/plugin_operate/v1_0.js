/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
 * Edition) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

(function () {
    $.atoms.nodeman_plugin_operate = [
        {
            tag_code: "biz_cc_id",
            type: "select",
            attrs: {
                name: gettext("业务"),
                allowCreate: true,
                hookable: true,
                remote: true,
                remote_url: $.context.get("site_url") + "pipeline/cc_get_business_list/",
                remote_data_init: function (resp) {
                    if (resp.result === false) {
                        show_msg(resp.message, 'error');
                    }
                    return resp.data;
                },
                disabled: !$.context.canSelectBiz(),
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
            methods: {
                _tag_init: function () {
                    if (this.value) {
                        return
                    }
                    this._set_value($.context.getBkBizId())
                }
            }
        },
        {
            tag_code: "nodeman_host_os_type",
            type: "radio",
            attrs: {
                name: gettext("主机系统类型"),
                hookable: true,
                items: [
                    {"name": gettext("LINUX"), "value": "linux"},
                    {"name": gettext("WINDOWS"), "value": "windows"},
                ],
                default: "linux",
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "nodeman_host_info",
            type: "combine",
            attrs: {
                name: gettext("填写主机"),
                hookable: true,
                children: [
                    {
                        tag_code: "nodeman_host_input_type",
                        type: "radio",
                        attrs: {
                            name: gettext("填写方式"),
                            hookable: true,
                            items: [
                                {"name": gettext("主机IP"), "value": "host_ip"},
                                {"name": gettext("主机ID"), "value": "host_id"},
                            ],
                            default: "host_ip",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "nodeman_bk_cloud_id",
                        type: "select",
                        attrs: {
                            name: gettext("云区域ID"),
                            hookable: true,
                            remote: true,
                            items: [],
                            remote_url: $.context.get("site_url") + "pipeline/nodeman_get_cloud_area/",
                            remote_data_init: function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, "error");
                                }
                                resp.data.unshift({"text": gettext("直连区域"), "value": 0})
                                return resp.data;
                            },
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value) {
                                        let self = this
                                        let result = {
                                            result: true,
                                            error_message: ""
                                        }
                                        if (!self.get_parent) {
                                            return result
                                        } else if (self.get_parent().get_child('nodeman_host_input_type')) {
                                            if (self.get_parent().get_child('nodeman_host_input_type').value === "host_ip" && !value.toString()) {
                                                result.result = false;
                                                result.error_message = gettext("请选云区域");
                                            }
                                        }
                                        return result
                                    }
                                }

                            ],

                        },
                        events: [
                            {
                                source: "nodeman_host_input_type",
                                type: "init",
                                action: function (value) {
                                    if (value === "host_ip") {
                                        this.show()
                                    } else {
                                        this.hide()
                                    }
                                }
                            },
                            {
                                source: "nodeman_host_input_type",
                                type: "change",
                                action: function (value) {
                                    if (value === "host_ip") {
                                        this.show()
                                    } else {
                                        this.hide()
                                    }
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodeman_host_ip",
                        type: "textarea",
                        attrs: {
                            name: gettext("主机IP"),
                            placeholder: gettext("多个用英文逗号 `,` 或换行分隔"),
                            hookable: true,
                            validation: []
                        },
                        events: [
                            {
                                source: "nodeman_host_input_type",
                                type: "init",
                                action: function (value) {
                                    if (value === "host_ip") {
                                        this.show()
                                    } else {
                                        this.hide()
                                    }
                                }
                            },
                            {
                                source: "nodeman_host_input_type",
                                type: "change",
                                action: function (value) {
                                    if (value === "host_ip") {
                                        this.show()
                                    } else {
                                        this.hide()
                                    }
                                }
                            },
                        ]

                    },
                    {
                        tag_code: "nodeman_host_id",
                        type: "textarea",
                        attrs: {
                            name: gettext("主机ID"),
                            placeholder: gettext("多个用英文逗号 `,` 分隔"),
                            hookable: true,
                            validation: []
                        },
                        events: [
                            {
                                source: "nodeman_host_input_type",
                                type: "init",
                                action: function (value) {
                                    if (value === "host_id") {
                                        this.show()
                                    } else {
                                        this.hide()
                                    }
                                }
                            },
                            {
                                source: "nodeman_host_input_type",
                                type: "change",
                                action: function (value) {
                                    if (value === "host_id") {
                                        this.show()
                                    } else {
                                        this.hide()
                                    }
                                }
                            },
                        ]

                    },

                ]
            }
        },


        {
            tag_code: "nodeman_plugin_operate",
            type: "combine",
            attrs: {
                name: gettext("插件操作"),
                hookable: true,
                children: [
                    {
                        tag_code: "nodeman_op_type",
                        type: "select",
                        attrs: {
                            name: gettext("操作类型"),
                            items: [
                                {value: "MAIN_INSTALL_PLUGIN", text: gettext("安裝")},
                            ],
                            default: "MAIN_INSTALL_PLUGIN",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]

                        },

                    },

                    {
                        tag_code: "nodeman_plugin_type",
                        type: "select",
                        attrs: {
                            name: gettext("插件类型"),
                            items: [
                                {value: "official", text: gettext("官方插件")},
                                {value: "external", text: gettext("第三方插件")},
                                {value: "scripts", text: gettext("脚本插件")},
                            ],
                            default: "official",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },

                    },

                    {
                        tag_code: "nodeman_plugin",
                        type: "select",
                        attrs: {
                            name: gettext("选择插件"),
                            hookable: true,
                            remote: true,
                            items: [],
                            remote_url: "",
                            remote_data_init: function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, "error");
                                }
                                return resp.data;
                            },
                            validation: [
                                {type: "required"}
                            ]
                        },
                        events: [
                            {
                                source: "nodeman_plugin_type",
                                type: "init",
                                action: function (value) {
                                    this.remote_url = $.context.get('site_url') + 'pipeline/nodeman_get_plugin_list/' + value + '/';
                                    this.remoteMethod();
                                }
                            },
                            {
                                source: "nodeman_plugin_type",
                                type: "change",
                                action: function (value) {
                                    this.value = "";
                                    this.remote_url = $.context.get('site_url') + 'pipeline/nodeman_get_plugin_list/' + value + '/';
                                    this.remoteMethod();
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodeman_plugin_version",
                        type: "select",
                        attrs: {
                            name: gettext("选择插件版本"),
                            hookable: true,
                            remote: true,
                            items: [],
                            remote_url: "",
                            value: "",
                            remote_data_init: function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, "error");
                                }
                                return resp.data;
                            },
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodeman_plugin",
                                type: "init",
                                action: function (value) {
                                    if (value) {
                                        let os = this.get_parent().get_parent().get_child("nodeman_host_os_type").value
                                        this.remote_url = $.context.get('site_url') + 'pipeline/nodeman_get_plugin_version/' + value + '/' + os + '/';
                                        this.remoteMethod()
                                    }

                                }
                            },
                            {
                                source: "nodeman_plugin",
                                type: "change",
                                action: function (value) {
                                    this.value = ""
                                    let os = this.get_parent().get_parent().get_child("nodeman_host_os_type").value
                                    this.remote_url = $.context.get('site_url') + 'pipeline/nodeman_get_plugin_version/' + value + '/' + os + '/';
                                    this.remoteMethod()
                                }
                            },
                            {
                                source: "nodeman_plugin_type",
                                type: "change",
                                action: function (value) {
                                    this.items = []
                                    this.value = ""
                                }
                            }
                        ]
                    },

                    {
                        tag_code: "install_config",
                        type: "checkbox",
                        attrs: {
                            name: gettext(" "),
                            hookable: true,
                            items: [
                                {name: gettext("保留原有配置文件"), value: "keep_config"},
                                {name: gettext("仅更新文件，不重启进程"), value: "no_restart"}
                            ],
                            validation: []
                        },
                        events: [
                            {
                                source: "nodeman_op_type",
                                type: "init",
                                action: function (value) {
                                    if (value === "MAIN_INSTALL_PLUGIN") {
                                        this.show()
                                    } else {
                                        this.hide()
                                    }
                                }
                            },
                            {
                                source: "nodeman_op_type",
                                type: "change",
                                action: function (value) {
                                    if (value === "MAIN_INSTALL_PLUGIN") {
                                        this.show()
                                    } else {
                                        this.hide()
                                    }
                                }
                            },
                        ]
                    },
                ]
            }
        }
    ]
})();