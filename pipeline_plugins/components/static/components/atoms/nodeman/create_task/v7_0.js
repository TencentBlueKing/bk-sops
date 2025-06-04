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
            self.show();
        } else {
            self.hide();
        }
    }

    function is_install_op(self, value) {
        is_display_tag(self, ["INSTALL", "REINSTALL"], value);
    }


    function init_columns(self, node_type, op_type) {
        let common_columns = [
            {
                tag_code: "nodeman_bk_cloud_id",
                type: "select",
                attrs: {
                    name: gettext("管控区域ID"),
                    width: "180px",
                    remote: true,
                    items: [],
                    remote_url: $.context.get("site_url") + "pipeline/nodeman_get_cloud_area/",
                    remote_data_init: function (resp) {
                        if (resp.result === false) {
                            show_msg(resp.message, "error");
                        }
                        resp.data.unshift({"text": gettext("直连区域"), "value": 0});
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
                tag_code: "nodeman_bk_install_channel",
                type: "select",
                attrs: {
                    name: gettext("安装通道"),
                    width: "180px",
                    remote: true,
                    remote_url: "",
                    remote_data_init: function (resp) {
                        if (resp.result === false) {
                            show_msg(resp.message, 'error');
                        }
                        resp.data.unshift({"text": gettext("默认通道"), "value": -1});
                        this._set_value(resp.data[0]["value"]);
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
                        source: "nodeman_bk_cloud_id",
                        type: "init",
                        action: function (cloud_id) {
                            if (cloud_id !== '') {
                                this.remote_url = $.context.get('site_url') + 'pipeline/nodeman_get_install_channel/' + cloud_id + '/';
                                this.remoteMethod();
                            }
                        }
                    },
                    {
                        source: "nodeman_bk_cloud_id",
                        type: "change",
                        action: function (cloud_id) {
                            if (cloud_id !== '') {
                                this.remote_url = $.context.get('site_url') + 'pipeline/nodeman_get_install_channel/' + cloud_id + '/';
                                this.remoteMethod();
                            }else{
                                this._set_value("");
                            }
                        }
                    },
                ]
            },
            {
                tag_code: "nodeman_ap_id",
                type: "select",
                attrs: {
                    name: gettext("接入点"),
                    width: "180px",
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
                }
            },
            {
                tag_code: "inner_ip",
                type: "textarea",
                attrs: {
                    name: gettext("内网IP"),
                    placeholder: gettext("多个用英文逗号 `,` 或换行分隔"),
                    width: "180px",
                    editable: true
                }
            },
            {
                tag_code: "inner_ipv6",
                type: "textarea",
                attrs: {
                    name: gettext("内网IP(IPV6)"),
                    placeholder: gettext("可为空，如纯ipv6主机，内网ipv和外网IP(IPV6)两个必须填一个"),
                    width: "180px",
                    editable: true,
                }
            },
            {
                tag_code: "os_type",
                type: "select",
                attrs: {
                    name: gettext("操作系统类型"),
                    width: "180px",
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
                    ],
                }
            },
        ];

        let agent_columns = [
            {
                tag_code: "bk_addressing",
                type: "select",
                attrs: {
                    name: gettext("寻址方式"),
                    width: "180px",
                    items: [
                        {value: "static", text: gettext("静态")},
                        {value: "dynamic", text: gettext("动态")},
                    ],
                    default: "static",
                    validation: [
                        {
                            type: "required"
                        }
                    ],
                }
            },
        ]

        let proxy_columns = [
            {
                tag_code: "outer_ip",
                type: "textarea",
                attrs: {
                    name: gettext("外网IP"),
                    placeholder: gettext("可选,如填写需与内网ip一一对应,多个用英文逗号 `,` 或换行分隔"),
                    width: "180px",
                    editable: true,
                    validation: []
                },
            },
            {
                tag_code: "data_ip",
                type: "textarea",
                attrs: {
                    name: gettext("数据IP"),
                    placeholder: gettext("可为空，如填写需与内网ip一一对应，适配复杂网络时填写,多个用英文逗号 `,` 或换行分隔"),
                    width: "180px",
                    editable: true,
                }
            },
            {
                tag_code: "outer_ipv6",
                type: "textarea",
                attrs: {
                    name: gettext("外网IP(IPV6)"),
                    placeholder: gettext("可为空，如纯ipv6主机，外网ipv和外网IP(IPV6)两个必须填一个"),
                    width: "180px",
                    editable: true,
                },
            },
        ];

        let auth_columns = [
            {
                tag_code: "login_ip",
                type: "textarea",
                attrs: {
                    name: gettext("登录IP"),
                    placeholder: gettext("可为空，如填写需与内网ip一一对应，适配复杂网络时填写,多个用英文逗号 `,` 或换行分隔"),
                    width: "180px",
                    editable: true
                }
            },
            {
                tag_code: "account",
                type: "input",
                attrs: {
                    name: gettext("登录账号"),
                    width: "180px",
                    editable: true,
                    validation: [
                        {
                            type: "required"
                        }
                    ],
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
                    ],
                }
            },
            {
                tag_code: "auth_type",
                type: "select",
                attrs: {
                    name: gettext("认证方式"),
                    width: "180px",
                    items: [
                        {value: "PASSWORD", text: gettext("PASSWORD")},
                        {value: "KEY", text: gettext("KEY")},
                        {value: "TJJ_PASSWORD", text: gettext("TJJ")}

                    ],
                    default: "PASSWORD",
                    validation: [
                        {
                            type: "required"
                        }
                    ],
                }
            },
            {
                tag_code: "auth_key",
                type: "password",
                attrs: {
                    name: gettext("认证密钥"),
                    width: "400px",
                    editable: true,
                    textareaMode: true,
                    validation: [
                        {
                            type: "custom",
                            args: function (value, parent_value) {
                                let auth_type = parent_value.auth_type;
                                let result = {
                                    result: true,
                                    error_message: ""
                                };
                                if (auth_type !== "TJJ_PASSWORD" && !value.value.length) {
                                    result.result = false;
                                    result.error_message = gettext("请输入认证密钥");
                                }
                                return result;
                            }
                        }
                    ]
                },
            },
        ];

        let config_columns = [
            {
                tag_code: "peer_exchange_switch_for_agent",
                type: "radio",
                attrs: {
                    name: gettext("BT节点探测"),
                    items: [
                        {value: 1, name: gettext("是")},
                        {value: 0, name: gettext("否")}
                    ],
                    default: 0,
                    validation: [
                        {
                            type: "required"
                        },
                    ]
                },
            },
            {
                tag_code: "speed_limit",
                type: "input",
                attrs: {
                    name: gettext("传输限速 M/s"),
                    width: "100px",
                    placeholder: gettext("请输入"),
                    validation: [
                        {
                            type: "custom",
                            args: function (value) {
                                var result = {
                                    result: true,
                                    error_message: ""
                                };
                                if (value && !Number(value)) {
                                    result.result = false;
                                    result.error_message = gettext("请输入数字");
                                }
                                return result;
                            }
                        }
                    ]
                },
            },
            {
                tag_code: "force_update_agent_id",
                type: "radio",
                attrs: {
                    name: gettext("重新注册Agent_id"),
                    items: [
                        {value: true, name: gettext("是")},
                        {value: false, name: gettext("否")}
                    ],
                    default: false,
                    validation: [
                        {
                            type: "required"
                        },
                    ]
                },
            },
        ];

        self.columns = common_columns;

        // Agent类型独有字段
        if (node_type === "AGENT") {
            self.columns.push(...agent_columns);
        }
        // 如果是 Proxy，补充 Proxy 信息
        if (node_type === "PROXY") {
            self.columns.push(...proxy_columns);
        }
        // 安装 / 重装 / 卸载需要认证信息
        if (op_type === "INSTALL" || op_type === "UNINSTALL" || op_type === "REINSTALL") {
            self.columns.push(...auth_columns);
        }
        // 非卸载场景需要配置信息
        if (op_type !== "UNINSTALL") {
            self.columns.push(...config_columns);
        }
    };

    let NODEMAN_TJJ_IS_HIDDEN = true;

    $.ajax({
        url: $.context.get('site_url') + 'pipeline/nodeman_is_support_tjj/',
        type: 'GET',
        dataType: 'json',
        async: false,
        success: function (resp) {
            if (resp.data) {
                NODEMAN_TJJ_IS_HIDDEN = false;
            }
        },
        error: function () {
            show_msg('request nodeman is support tjj error', 'error');
        }
    });
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
                    this._set_value($.context.getBkBizId());
                }
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
                            ],
                            events: [
                                {
                                    source: "nodeman_node_type",
                                    type: "init",
                                    action: function (value) {
                                        // 统一以 change 事件抛出
                                        this.emit_event(this.tagCode, "change", this.value);
                                    }
                                },
                            ]
                        }
                    },
                    {
                        tag_code: "nodeman_op_type",
                        type: "select",
                        attrs: {
                            name: gettext("操作类型"),
                            items: [
                                {value: "INSTALL", text: gettext("安裝")},
                                {value: "REINSTALL", text: gettext("重新安装")},
                                {value: "UNINSTALL", text: gettext("卸载")},
                                {value: "UPGRADE", text: gettext("升级")},
                                {value: "RESTART", text: gettext("重启")},
                                {value: "RELOAD", text: gettext("配置重载")},
                            ],
                            default: "INSTALL",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodeman_op_type",
                                type: "init",
                                action: function (value) {
                                    this.emit_event(this.tagCode, "change", this.value);
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodeman_install_latest_plugins",
                        type: "radio",
                        attrs: {
                            name: gettext("是否安装最新版本插件"),
                            items: [
                                {value: true, name: gettext("是")},
                                {value: false, name: gettext("否")}
                            ],
                            default: true,
                            validation: [
                                {
                                    type: "required"
                                },
                            ]
                        },
                        events: [
                            {
                                source: "nodeman_op_type",
                                type: "change",
                                action: function (value) {
                                    is_install_op(this, value);
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodeman_hosts",
                        type: "datatable",
                        attrs: {
                            pagination: true,
                            name: gettext("主机"),
                            table_buttons: [
                                {
                                    type: "add_row",
                                    text: gettext("添加"),
                                    callback: function () {
                                        this.add_row();
                                    }
                                },
                                {
                                    type: "import",
                                    text: gettext("导入")
                                },
                                {
                                    type: "export",
                                    text: gettext("导出"),
                                    callback: function () {
                                        this.export2Excel();
                                    }
                                },

                            ],
                            columns: [],
                            hookable: true,
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value) {
                                        let self = this;
                                        let result = {
                                            result: true,
                                            error_message: ""
                                        };
                                        let op_type = self.get_parent && self.get_parent().get_child("nodeman_op_type").value;
                                        let install_type = ["INSTALL", "REINSTALL"];
                                        if (install_type.indexOf(op_type) !== -1 && value === "") {
                                            result.result = false;
                                            result.error_message = gettext("请完善主机信息");
                                        }
                                        return result;

                                    }
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodeman_op_type",
                                type: "change",
                                action: function (value) {
                                    let node_type = this.get_parent().get_child("nodeman_node_type").value;
                                    init_columns(this, node_type, value);
                                    let op_type = ["INSTALL", "REINSTALL", "RELOAD"];
                                    if (node_type === "AGENT") {
                                        op_type = ["INSTALL", "REINSTALL", "UNINSTALL", "RELOAD"];
                                    }
                                    is_display_tag(this, op_type, value);
                                }
                            },
                            {
                                source: "nodeman_node_type",
                                type: "change",
                                action: function (value) {
                                    init_columns(this, value, this.get_parent().get_child("nodeman_op_type").value);
                                    let op_type = ["INSTALL", "REINSTALL", "RELOAD"];
                                    if (value === "AGENT") {
                                        op_type = ["INSTALL", "REINSTALL", "UNINSTALL", "RELOAD"];
                                    }
                                    is_display_tag(this, op_type, this.get_parent().get_child("nodeman_op_type").value);
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodeman_other_hosts",
                        type: "datatable",
                        attrs: {
                            pagination: true,
                            name: gettext("主机"),
                            table_buttons: [
                                {
                                    type: "add_row",
                                    text: gettext("添加"),
                                    callback: function () {
                                        this.add_row();
                                    }
                                },
                                {
                                    type: "import",
                                    text: gettext("导入")
                                },
                                {
                                    type: "export",
                                    text: gettext("导出"),
                                    callback: function () {
                                        this.export2Excel();
                                    }
                                },

                            ],
                            columns: [
                                {
                                    tag_code: "nodeman_bk_cloud_id",
                                    type: "input",
                                    attrs: {
                                        name: gettext("管控区域ID"),
                                        placeholder: gettext("一行只能对应一个管控区域ID"),
                                        hookable: true,
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    }
                                },
                                {
                                    tag_code: "nodeman_ip_str",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("IP"),
                                        placeholder: gettext("多个用英文逗号 `,` 分隔"),
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
                                        let self = this;
                                        let result = {
                                            result: true,
                                            error_message: ""
                                        };
                                        let op_type = self.get_parent && self.get_parent().get_child("nodeman_op_type").value;
                                        let install_type = ["UNINSTALL", "UPGRADE"];
                                        if (install_type.indexOf(op_type) !== -1 && value === "") {
                                            result.result = false;
                                            result.error_message = gettext("请完善主机信息");
                                        }
                                        return result;

                                    }
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodeman_op_type",
                                type: "change",
                                action: function (value) {
                                    let op_type = ["UPGRADE", "RESTART"];
                                    if (this.get_parent().get_child("nodeman_node_type").value === "PROXY") {
                                        op_type = ["UPGRADE", "RESTART", "UNINSTALL"];
                                    }
                                    is_display_tag(this, op_type, value);
                                }
                            },
                            {
                                source: "nodeman_node_type",
                                type: "change",
                                action: function (value) {
                                    let op_type = ["UPGRADE", "RESTART"];
                                    if (value === "PROXY") {
                                        op_type = ["UPGRADE", "RESTART", "UNINSTALL"];
                                    }
                                    is_display_tag(this, op_type, this.get_parent().get_child("nodeman_op_type").value);
                                }
                            },
                        ]
                    },
                ],
            },
        },
    ];
})();
