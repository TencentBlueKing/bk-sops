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
    function is_display_tag(self, op_type, value) {
        if (op_type.indexOf(value) !== -1) {
            self.show()
        } else {
            self.hide()
        }
    }

    $.atoms.nodeman_create_task = [
        {
            tag_code: "bk_biz_id",
            type: "select",
            attrs: {
                name: gettext("业务"),
                allowCreate: true,
                hookable: true,
                remote: true,
                remote_url: $.context.get("site_url") + "pipeline/cc_get_business_list/",
                remote_data_init: function (resp) {
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
            tag_code: "nodeman_op_target",
            type: "combine",
            attrs: {
                name: gettext("操作对象"),
                hookable: true,
                children: [
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
                                    type: "required",
                                }
                            ]
                        },

                    },
                    {
                        tag_code: "nodeman_node_type",
                        type: "radio",
                        attrs: {
                            name: gettext("节点类型"),
                            hookable: true,
                            items: [
                                {value: "AGENT", name: gettext("AGENT")},
                                {value: "PROXY", name: gettext("PROXY")},
                            ],
                            default: "AGENT",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodeman_bk_cloud_id",
                                type: "init",
                                action: function (value) {
                                    if (value === 0) {
                                        this.items = [
                                            {value: "AGENT", name: gettext("AGENT")},
                                        ]
                                    } else {
                                        this.items = [
                                            {value: "AGENT", name: gettext("AGENT")},
                                            {value: "PROXY", name: gettext("PROXY")},
                                        ]
                                    }
                                }
                            },
                            {
                                source: "nodeman_bk_cloud_id",
                                type: "change",
                                action: function (value) {
                                    if (value === 0) {
                                        this.items = [
                                            {value: "AGENT", name: gettext("AGENT")},
                                        ]
                                    } else {
                                        this.items = [
                                            {value: "AGENT", name: gettext("AGENT")},
                                            {value: "PROXY", name: gettext("PROXY")},
                                        ]
                                    }
                                }
                            },
                        ]
                    },
                ]
            }
        },
        {
            tag_code: "nodeman_op_info",
            type: "combine",
            attrs: {
                name: gettext("操作类型"),
                hookable: true,
                children: [
                    {
                        tag_code: "nodeman_op_type",
                        type: "select",
                        attrs: {
                            name: gettext("操作类型"),
                            items: [
                                {value: "INSTALL", text: gettext("安裝")},
                                {value: "REINSTALL", text: gettext("重新安装")},
                                {value: "UNINSTALL", text: gettext("卸载")},
                                {value: "REMOVE", text: gettext("移除")},
                                {value: "UPGRADE", text: gettext("升级")},
                            ],
                            default: "INSTALL",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },

                    },
                    {
                        tag_code: "nodeman_ap_id",
                        type: "select",
                        attrs: {
                            name: gettext("接入点"),
                            hookable: true,
                            remote: true,
                            items: [],
                            remote_url: $.context.get("site_url") + "pipeline/nodeman_get_ap_list/",
                            remote_data_init: function (resp) {
                                if (resp.result === false) {
                                    show_msg(resp.message, "error");
                                }
                                return resp.data;
                            },
                            validation: []
                        },
                        events: [
                            {
                                source: "nodeman_op_type",
                                type: "init",
                                action: function (value) {
                                    let op_type = ["INSTALL", "REINSTALL"]
                                    is_display_tag(this, op_type, value)
                                }
                            },
                            {
                                source: "nodeman_op_type",
                                type: "change",
                                action: function (value) {
                                    let op_type = ["INSTALL", "REINSTALL"]
                                    is_display_tag(this, op_type, value)
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodeman_hosts",
                        type: "datatable",
                        attrs: {
                            name: gettext("主机"),
                            editable: true,
                            add_btn: true,
                            columns: [
                                {
                                    tag_code: "inner_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("内网IP"),
                                        placeholder: gettext("多个用,隔开"),
                                        width: "100px",
                                        editable: true,
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    }
                                },
                                {
                                    tag_code: "outer_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("外网IP"),
                                        placeholder: gettext("可选"),
                                        width: "100px",
                                        editable: true,
                                        validation: []
                                    }
                                },
                                {
                                    tag_code: "login_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("登录IP"),
                                        placeholder: gettext("可为空，适配复杂网络时填写"),
                                        width: "100px",
                                        editable: true
                                    }
                                },
                                {
                                    tag_code: "data_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("数据IP"),
                                        placeholder: gettext("可为空，适配复杂网络时填写"),
                                        width: "100px",
                                        editable: true,

                                    }
                                },
                                {
                                    tag_code: "os_type",
                                    type: "select",
                                    attrs: {
                                        name: gettext("操作系统类型"),
                                        width: "100px",
                                        items: [
                                            {value: "LINUX", text: gettext("LINUX")},
                                            {value: "WINDOWS", text: gettext("WINDOWS")},
                                            {value: "AIX", text: gettext("AIX")}
                                        ],
                                        default: "LINUX",
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    }
                                },
                                {
                                    tag_code: "account",
                                    type: "input",
                                    attrs: {
                                        name: gettext("登录账号"),
                                        width: "100px",
                                        editable: true
                                    }
                                },
                                {
                                    tag_code: "port",
                                    type: "input",
                                    attrs: {
                                        name: gettext("端口号"),
                                        width: "100px",
                                        editable: true,
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    }
                                },
                                {
                                    tag_code: "auth_type",
                                    type: "select",
                                    attrs: {
                                        name: gettext("认证方式"),
                                        width: "100px",
                                        items: [
                                            {value: "PASSWORD", text: gettext("PASSWORD")},
                                            {value: "KEY", text: gettext("KEY")}
                                        ],
                                        default: "PASSWORD",
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    }
                                },
                                {
                                    tag_code: "auth_key",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("认证密钥"),
                                        width: "100px",
                                        editable: true,
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    }
                                }
                            ],
                            hookable: true,
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value) {
                                        let self = this
                                        let result = {
                                            result: true,
                                            error_message: ""
                                        }
                                        let op_type = self.get_parent && self.get_parent().get_child("nodeman_op_type").value;
                                        let install_type = ["INSTALL", "REINSTALL"]
                                        if (install_type.indexOf(op_type) !== -1 && value === "") {
                                            result.result = false;
                                            result.error_message = gettext("请完善主机信息");
                                        }
                                        return result

                                    }
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodeman_op_type",
                                type: "init",
                                action: function (value) {
                                    let op_type = ["INSTALL", "REINSTALL"]
                                    is_display_tag(this, op_type, value)
                                }
                            },
                            {
                                source: "nodeman_op_type",
                                type: "change",
                                action: function (value) {
                                    let op_type = ["INSTALL", "REINSTALL"]
                                    is_display_tag(this, op_type, value)
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodeman_ip_str",
                        type: "textarea",
                        attrs: {
                            name: gettext("IP"),
                            placeholder: gettext("多个用英文逗号 `,` 分隔"),
                            hookable: true,
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value) {
                                        let self = this
                                        let result = {
                                            result: true,
                                            error_message: ""
                                        }
                                        let op_type = self.get_parent && self.get_parent().get_child("nodeman_op_type").value;
                                        let install_type = ["UNINSTALL", "UPGRADE", "REMOVE"]
                                        if (install_type.indexOf(op_type) !== -1 && value === "") {
                                            result.result = false;
                                            result.error_message = gettext("请填写IP");
                                        }
                                        return result

                                    }
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodeman_op_type",
                                type: "init",
                                action: function (value) {
                                    let op_type = ["UNINSTALL", "UPGRADE", "REMOVE"]
                                    is_display_tag(this, op_type, value)
                                }
                            },
                            {
                                source: "nodeman_op_type",
                                type: "change",
                                action: function (value) {
                                    let op_type = ["UNINSTALL", "UPGRADE", "REMOVE"]
                                    is_display_tag(this, op_type, value)
                                }
                            },
                        ]
                    }
                ]
            }
        },

    ]
})();
