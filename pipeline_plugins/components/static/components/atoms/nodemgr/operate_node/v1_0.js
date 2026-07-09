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

(function(){
    function is_display_tag(self, op_type, value) {
        if (op_type.indexOf(value) !== -1) {
            self.disabled = false;
            self.show();
        } else {
            self.disabled = true;
            self.hide();
        }
    }

    function is_install_op(self, value) {
        is_display_tag(self, ["install"], value);
    }

    function is_upgrade_or_restart_op(self, value) {
        is_display_tag(self, ["upgrade", "restart"], value);
    }

    function is_upgrade_op(self, value) {
        is_display_tag(self, ["upgrade"], value);
    }

    function is_restart_op(self, value) {
        is_display_tag(self, ["restart"], value);
    }

    function is_uninstall_op(self, value) {
        is_display_tag(self, ["uninstall"], value);
    }

    function validate_not_empty(self, value, allow_op_type, description) {
        let result = {
            result: true,
            error_message: ""
        };

        if (!self.get_parent) {
            return result;
        }

        let op_type = self.get_parent().get_parent().get_child('nodemgr_operation_type');
        if (op_type && op_type.value === allow_op_type) {
            if (value === '') {
                result.result = false;
                result.error_message = gettext(description);
            }
        }

        return result;
    }

    function init_columns(self, node_role, op_type) {
        let networkarea_columns = [
            {
                tag_code: "bk_networkarea_id",
                type: "select",
                attrs: {
                    name: gettext("管控区域"),
                    width: "200px",
                    remote: true,
                    items: [],
                    remote_url: $.context.get("site_url") + "pipeline/nodemgr_get_networkarea/",
                    remote_data_init: function (resp) {
                        if (resp.result === false) {
                            show_msg(resp.message, "error");
                        }

                        return resp.data;
                    },
                    validation: [
                        {
                            type: "required",
                        }
                    ]
                },
            }]

        let networkunit_columns = [
            {
                tag_code: "bk_networkunit_id",
                type: "select",
                attrs: {
                    name: gettext("管控单元"),
                    width: "180px",
                    remote: true,
                    items: [],
                    remote_url: "",
                    remote_data_init: function (resp) {
                        if (resp.result === false) {
                            show_msg(resp.message, "error");
                        }

                        // 仅在当前未回填值时执行自动选择，避免覆盖已保存的用户选项
                        var current_value = this.value;
                        var is_empty = current_value === "" || current_value === undefined || current_value === null;
                        if (resp.data.length === 1) {
                            if (is_empty) {
                                this._set_value(resp.data[0].value);
                            }
                        } else if (resp.data.length > 1 && this.get_parent().get_parent().get_child("nodemgr_node_role").value === "agent") {
                            resp.data.unshift({"text": gettext("自动选择"), "value": -1});
                            if (is_empty) {
                                this._set_value(-1);
                            }
                        }

                        return resp.data;
                    },
                    validation: [
                        {
                            type: "required",
                        }
                    ]
                },
                events: [
                    {
                        source: "bk_networkarea_id",
                        type: "init",
                        action: function (networkarea_id) {
                            if (networkarea_id !== '') {
                                this.remote_url = $.context.get('site_url') + 'pipeline/nodemgr_get_networkunit/' + networkarea_id + '/';
                                this.remoteMethod();
                            }
                        }
                    },
                    {
                        source: "bk_networkarea_id",
                        type: "change",
                        action: function (networkarea_id) {
                            this._set_value("");
                            if (networkarea_id !== '') {
                                this.remote_url = $.context.get('site_url') + 'pipeline/nodemgr_get_networkunit/' + networkarea_id + '/';
                                this.remoteMethod();
                            }
                        }
                    }
                ]
            }
        ]

        let agent_install_columns = [
            {
                tag_code: "bk_host_innerip",
                type: "textarea",
                attrs: {
                    name: gettext("内网IPv4"),
                    placeholder: gettext("支持一台主机的多个IP, 多个用英文逗号 `,` 或换行分隔"),
                    width: "180px",
                    editable: true
                }
            },
            {
                tag_code: "bk_host_innerip_v6",
                type: "textarea",
                attrs: {
                    name: gettext("内网IPv6"),
                    placeholder: gettext("支持一台主机的多个IP, 多个用英文逗号 `,` 或换行分隔"),
                    width: "180px",
                    editable: true,
                }
            },
            {
                tag_code: "bk_addressing",
                type: "select",
                attrs: {
                    name: gettext("寻址方式"),
                    width: "150px",
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
            {
                tag_code: "os_type",
                type: "select",
                attrs: {
                    name: gettext("操作系统"),
                    width: "180px",
                    remote: true,
                    items: [],
                    remote_url: $.context.get("site_url") + 'pipeline/nodemgr_get_os_type/' + node_role + '/',
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
                    ],
                }
            },
        ]

        let login_columns = [
            {
                tag_code: "login_ip",
                type: "textarea",
                attrs: {
                    name: gettext("登录IP"),
                    placeholder: gettext("可为空, 默认为第一个内网IP"),
                    width: "180px",
                    editable: true
                }
            },
            {
                tag_code: "login_port",
                type: "input",
                attrs: {
                    name: gettext("登录端口号"),
                    width: "100px",
                    editable: true,
                    validation: [
                        {
                            type: "required"
                        },
                        {
                            type: "custom",
                            args: function (value) {
                                let result = {
                                    result: true,
                                    error_message: ""
                                };
                                if (!value) {
                                    return result
                                }
                                var reg = /^[\d]+$/;
                                if (!reg.test(value)) {
                                    result.result = false;
                                    result.error_message = gettext("端口号必须为整数")
                                }
                                if (+value < 1 || +value > 65535) {
                                    result.result = false;
                                    result.error_message = gettext("端口号必须在 1 - 65535 范围内")
                                }
                                return result
                            }
                        }
                    ]
                },
                events: [
                    {
                        source: "os_type",
                        type: "change",
                        action: function (os_type) {
                            var columns = this.get_parent().columns;
                            for (var i = 0; i < columns.length; i++) {
                                if (columns[i].property === "os_type") {
                                    var items = this.get_parent().$children[i].$children[1].items;
                                    for (var j = 0; j < items.length; j++) {
                                        var item = items[j];
                                        if (item.value === os_type && item.default_info.port) {
                                            this._set_value(item.default_info.port);
                                            break;
                                        }
                                    }
                                    break;
                                }
                            }
                        }
                    }
                ]
            },
            {
                tag_code: "login_user",
                type: "input",
                attrs: {
                    name: gettext("登录账号"),
                    width: "100px",
                    editable: true,
                    validation: [
                        {
                            type: "required"
                        }
                    ]
                },
                events: [
                    {
                        source: "os_type",
                        type: "change",
                        action: function (os_type) {
                            var columns = this.get_parent().columns;
                            for (var i = 0; i < columns.length; i++) {
                                if (columns[i].property === "os_type") {
                                    var items = this.get_parent().$children[i].$children[1].items;
                                    for (var j = 0; j < items.length; j++) {
                                        var item = items[j];
                                        if (item.value === os_type && item.default_info.user) {
                                            this._set_value(item.default_info.user);
                                            break;
                                        }
                                    }
                                    break;
                                }
                            }
                        }
                    }
                ]
            },
            {
                tag_code: "login_mode",
                type: "select",
                attrs: {
                    name: gettext("认证方式"),
                    width: "150px",
                    items: [
                        {value: "password", text: gettext("密码")},
                        {value: "keyfile", text: gettext("密钥")},
                        {value: "password_vault", text: gettext("密码库(TJJ)")},
                    ],
                    default: "password",
                    validation: [
                        {
                            type: "required"
                        }
                    ],
                }
            },
            {
                tag_code: "login_password",
                type: "password",
                attrs: {
                    name: gettext("密码/密钥"),
                    width: "400px",
                    editable: true,
                    textareaMode: true,
                    validation: [
                    ]
                },
                events: [
                    {
                        source: "login_mode",
                        type: "change",
                        action: function (login_mode) {
                            this._set_value("");
                            if (login_mode === "password_vault") {
                                this.hide();
                            } else {
                                this.show();
                            }
                        }
                    }
                ]
            },
            {
                tag_code: "re_register",
                type: "radio",
                attrs: {
                    name: gettext("重新注册Agent-ID"),
                    width: "150px",
                    items: [
                        {value: true, name: gettext("是")},
                        {value: false, name: gettext("否")}
                    ],
                    tips: gettext("<p>非必要情况下应尽量避免重新注册Agent-ID, 同一台主机频繁变更可能导致多个平台上下游数据错位, 带来安全隐患</p>"),
                    default: false,
                    validation: [
                        {
                            type: "required"
                        },
                    ]
                },
            },
        ]

        let agent_upgrade_columns = [
            {
                tag_code: "inner_ip",
                type: "textarea",
                attrs: {
                    name: gettext("IP"),
                    placeholder: gettext("这里填写的IP对应的是一台主机, 多台主机请分行填写"),
                    width: "220px",
                    editable: true
                }
            },
            {
                tag_code: "upgrade_version",
                type: "select",
                attrs: {
                    name: gettext("版本"),
                    width: "220px",
                    remote: true,
                    items: [],
                    remote_url: $.context.get("site_url") + 'pipeline/nodemgr_get_release_version/' + node_role + '/',
                    remote_data_init: function (resp) {
                        if (resp.result === false) {
                            show_msg(resp.message, "error");
                        }

                        resp.data.unshift({"text": gettext("最新稳定版本"), "value": ""});
                        this._set_value("");

                        return resp.data;
                    },
                    validation: [
                    ]
                }
            }
        ]

        let agent_restart_columns = [
            {
                tag_code: "inner_ip",
                type: "textarea",
                attrs: {
                    name: gettext("IP"),
                    placeholder: gettext("这里填写的IP对应的是一台主机, 多台主机请分行填写"),
                    width: "220px",
                    editable: true
                }
            }
        ]

        let agent_uninstall_columns = [
            {
                tag_code: "inner_ip",
                type: "textarea",
                attrs: {
                    name: gettext("IP"),
                    placeholder: gettext("这里填写的IP对应的是一台主机, 多台主机请分行填写"),
                    width: "220px",
                    editable: true
                }
            }
        ]

        self.columns = []

        if (op_type === "install") {
            self.columns.push(...networkarea_columns);
            self.columns.push(...networkunit_columns);
            self.columns.push(...agent_install_columns);
            self.columns.push(...login_columns);
        }
        if (op_type === "upgrade") {
            self.columns.push(...networkarea_columns);
            self.columns.push(...agent_upgrade_columns);
        }
        if (op_type === "restart") {
            self.columns.push(...networkarea_columns);
            self.columns.push(...agent_restart_columns);
        }
        if (op_type === "uninstall") {
            self.columns.push(...networkarea_columns);
            self.columns.push(...agent_uninstall_columns);
        }
    }

    $.atoms.nodemgr_operate_node = [
        {
            tag_code: "nodemgr_biz_id",
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
            tag_code: "nodemgr_op_info",
            type: "combine",
            attrs: {
                name: gettext("操作类型"),
                hookable: true,
                children: [
                    {
                        tag_code: "nodemgr_node_role",
                        type: "radio",
                        attrs: {
                            name: gettext("节点类型"),
                            hookable: true,
                            items: [
                                {value: "agent", name: gettext("Agent")},
                                {value: "proxy", name: gettext("Proxy")},
                            ],
                            default: "agent",
                            validation: [
                                {
                                    type: "required"
                                }
                            ],
                        },
                        events: [
                            {
                                source: "nodemgr_node_role",
                                type: "init",
                                action: function (value) {
                                    // 统一以 change 事件抛出
                                    this.emit_event(this.tagCode, "change", this.value);
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodemgr_operation_type",
                        type: "select",
                        attrs: {
                            name: gettext("操作类型"),
                            hookable: true,
                            items: [
                                {value: "install", text: gettext("安装")},
                                {value: "upgrade", text: gettext("升级")},
                                {value: "restart", text: gettext("重启")},
                                {value: "uninstall", text: gettext("卸载")}
                            ],
                            default: "install",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "init",
                                action: function (value) {
                                    // 统一以 change 事件抛出
                                    this.emit_event(this.tagCode, "change", this.value);
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodemgr_install_plugin",
                        type: "radio",
                        attrs: {
                            name: gettext("同时安装插件"),
                            hookable: true,
                            items: [
                                {value: true, name: gettext("是")},
                                {value: false, name: gettext("否")}
                            ],
                            tips: gettext("<p>安装GSE Agent/Proxy之后, 同时安装预设的插件</p><p>若在安装Proxy时不勾选此项可能导致Proxy部分服务无法开启</p>"),
                            default: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (value) {
                                    is_install_op(this, value);
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "nodemgr_reload_config",
                        type: "radio",
                        attrs: {
                            name: gettext("同时重载配置"),
                            hookable: true,
                            items: [
                                {value: true, name: gettext("是")},
                                {value: false, name: gettext("否")}
                            ],
                            tips: gettext("<p>若不勾选此项, 则保留原有配置, 原地重启进程</p>"),
                            default: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (value) {
                                    is_restart_op(this, value);
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "nodemgr_force_restart",
                        type: "radio",
                        attrs: {
                            name: gettext("重启模式"),
                            hookable: true,
                            items: [
                                {value: true, name: gettext("强制")},
                                {value: false, name: gettext("无损")}
                            ],
                            tips: gettext("<p>过低版本的Agent可能无法支持无损重启</p>"),
                            default: false,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (value) {
                                    is_upgrade_or_restart_op(this, value);

                                    if (this.get_parent().get_child("nodemgr_node_role").value === "proxy") {
                                        this._set_value(true);
                                        this.disabled = true;
                                    } else {
                                        this.disabled = false;
                                    }
                                }
                            },
                            {
                                source: "nodemgr_node_role",
                                type: "change",
                                action: function (value) {
                                    if (value === "proxy") {
                                        this._set_value(true);
                                        this.disabled = true;
                                    } else {
                                        this.disabled = false;
                                    }
                                }
                            },
                            {
                                source: "nodemgr_force_restart",
                                type: "init",
                                action: function (value) {
                                    // 统一以 change 事件抛出
                                    this.emit_event(this.tagCode, "change", this.value);
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodemgr_graceful_restart_timeout",
                        type: "input",
                        attrs: {
                            name: gettext("无损重启超时时间(秒)"),
                            hookable: true,
                            width: "100px",
                            default: 120,
                            tips: gettext("<p>若Agent持续繁忙无法无损重启, 超过改时间后任务自动放弃</p>"),
                            validation: [
                                {
                                    type: "required"
                                },
                                {
                                    type: "custom",
                                    args: function (value) {
                                        let result = {
                                            result: true,
                                            error_message: ""
                                        };
                                        if (!value) {
                                            return result
                                        }
                                        var reg = /^[\d]+$/;
                                        if (!reg.test(value)) {
                                            result.result = false;
                                            result.error_message = gettext("超时时间必须为整数")
                                        }
                                        if (+value < 1 || +value > 3600) {
                                            result.result = false;
                                            result.error_message = gettext("超时时间必须在 1 - 3600 范围内")
                                        }
                                        return result
                                    }
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (value) {
                                    if (this.get_parent().get_child("nodemgr_force_restart").value === false) {
                                        is_upgrade_or_restart_op(this, value);
                                    } else {
                                        this.hide();
                                    }
                                }
                            },
                            {
                                source: "nodemgr_force_restart",
                                type: "change",
                                action: function (value) {
                                    if (value === false) {
                                        is_upgrade_or_restart_op(this, this.get_parent().get_child("nodemgr_operation_type").value);
                                    } else {
                                        this.hide();
                                    }
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodemgr_hosts_param_mode",
                        type: "radio",
                        attrs: {
                            name: gettext("主机参数模式"),
                            hookable: true,
                            items: [
                                {value: "batch", name: gettext("单批次模式")},
                                {value: "list", name: gettext("列表模式")}
                            ],
                            tips: gettext("<p>单批次: 每个IP对应一台主机, 支持通过IP列表批量操作主机</p><p>列表模式: 每行数据对应一台主机, 支持导入拥有多网卡IP的主机</p>"),
                            default: "batch",
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_hosts_param_mode",
                                type: "init",
                                action: function (value) {
                                    // 统一以 change 事件抛出
                                    this.emit_event(this.tagCode, "change", this.value);
                                }
                            },
                        ]
                    },
                    {
                        tag_code: "nodemgr_hosts",
                        type: "datatable",
                        attrs: {
                            pagination: true,
                            name: gettext("主机列表"),
                            hookable: true,
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
                            validation: [
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (op_type) {
                                    init_columns(this, this.get_parent().get_child("nodemgr_node_role").value, op_type);
                                }
                            },
                            {
                                source: "nodemgr_node_role",
                                type: "change",
                                action: function (node_role) {
                                    init_columns(this, node_role, this.get_parent().get_child("nodemgr_operation_type").value);
                                }
                            },
                            {
                                source: "nodemgr_hosts_param_mode",
                                type: "change",
                                action: function (value) {
                                    if (value === "list") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "nodemgr_batch_install",
                        type: "combine",
                        attrs: {
                            name: gettext("主机批量"),
                            hookable: true,
                            children: [
                                {
                                    tag_code: "bk_networkarea_id",
                                    type: "select",
                                    attrs: {
                                        name: gettext("管控区域"),
                                        remote: true,
                                        items: [],
                                        remote_url: $.context.get("site_url") + "pipeline/nodemgr_get_networkarea/",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '管控区域不可为空');
                                                }
                                            }
                                        ]
                                    },
                                },
                                {
                                    tag_code: "bk_networkunit_id",
                                    type: "select",
                                    attrs: {
                                        name: gettext("管控单元"),
                                        width: "180px",
                                        remote: true,
                                        items: [],
                                        remote_url: "",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            // 仅在当前未回填值时执行自动选择，避免覆盖已保存的用户选项
                                            var current_value = this.value;
                                            var is_empty = current_value === "" || current_value === undefined || current_value === null;
                                            if (resp.data.length === 1) {
                                                if (is_empty) {
                                                    this._set_value(resp.data[0].value);
                                                }
                                            } else if (resp.data.length > 1 && this.get_parent().get_parent().get_child("nodemgr_node_role").value === "agent") {
                                                resp.data.unshift({"text": gettext("自动选择"), "value": -1});
                                                if (is_empty) {
                                                    this._set_value(-1);
                                                }
                                            }

                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '管控单元不可为空');
                                                }
                                            }
                                        ]
                                    },
                                    events: [
                                        {
                                            source: "bk_networkarea_id",
                                            type: "init",
                                            action: function (networkarea_id) {
                                                if (networkarea_id !== '') {
                                                    this.remote_url = $.context.get('site_url') + 'pipeline/nodemgr_get_networkunit/' + networkarea_id + '/';
                                                    this.remoteMethod();
                                                }
                                            }
                                        },
                                        {
                                            source: "bk_networkarea_id",
                                            type: "change",
                                            action: function (networkarea_id) {
                                                this._set_value("");
                                                if (networkarea_id !== '') {
                                                    this.remote_url = $.context.get('site_url') + 'pipeline/nodemgr_get_networkunit/' + networkarea_id + '/';
                                                    this.remoteMethod();
                                                }
                                            }
                                        },
                                    ]
                                },
                                {
                                    tag_code: "inner_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("内网IP"),
                                        placeholder: gettext("一个IP是一台主机, 支持IPv4和IPv6混合填写, 多个用英文逗号 `,` 或换行分隔"),
                                        editable: true,
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '内网IP不可为空');
                                                }
                                            }
                                        ],
                                    }
                                },
                                {
                                    tag_code: "bk_addressing",
                                    type: "select",
                                    attrs: {
                                        name: gettext("寻址方式"),
                                        items: [
                                            {value: "static", text: gettext("静态")},
                                            {value: "dynamic", text: gettext("动态")},
                                        ],
                                        default: "static",
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '寻址方式不可为空');
                                                }
                                            }
                                        ],
                                    }
                                },
                                {
                                    tag_code: "os_type",
                                    type: "select",
                                    attrs: {
                                        name: gettext("操作系统"),
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
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '操作系统不可为空');
                                                }
                                            }
                                        ],
                                    },
                                    events: [
                                        {
                                            source: "os_type",
                                            type: "init",
                                            action: function (value) {
                                                this.remote_url = $.context.get("site_url") + 'pipeline/nodemgr_get_os_type/' + this.get_parent().get_parent().get_child("nodemgr_node_role").value + '/'
                                                this.remoteMethod();
                                            }
                                        }
                                    ]
                                },
                                {
                                    tag_code: "login_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("登录IP"),
                                        placeholder: gettext("可为空, 如不为空, 则需与内网IP一一对应, 多个用英文逗号 `,` 或换行分隔"),
                                        editable: true
                                    }
                                },
                                {
                                    tag_code: "login_port",
                                    type: "input",
                                    attrs: {
                                        name: gettext("登录端口号"),
                                        editable: true,
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    let result = {
                                                        result: true,
                                                        error_message: ""
                                                    };

                                                    let self = this;
                                                    if (!self.get_parent) {
                                                        return result;
                                                    }

                                                    let op_type = self.get_parent().get_parent().get_child('nodemgr_operation_type');
                                                    if (op_type && op_type.value === 'install') {
                                                        var reg = /^[\d]+$/;
                                                        if (!reg.test(value)) {
                                                            result.result = false;
                                                            result.error_message = gettext("端口必须为整数")
                                                        } else if (+value < 1 || +value > 65535) {
                                                            result.result = false;
                                                            result.error_message = gettext("端口必须在 1 - 65535 范围内")
                                                        }
                                                    }

                                                    return result
                                                }
                                            }
                                        ]
                                    },
                                    events: [
                                        {
                                            source: "os_type",
                                            type: "change",
                                            action: function (os_type) {
                                                var items = this.get_parent().get_child("os_type").items;
                                                for (var i = 0; i < items.length; i++) {
                                                    var item = items[i];
                                                    if (item.value === os_type && item.default_info.port) {
                                                        this._set_value(item.default_info.port);
                                                        break;
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                },
                                {
                                    tag_code: "login_user",
                                    type: "input",
                                    attrs: {
                                        name: gettext("登录账号"),
                                        editable: true,
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'install', '登录账号不可为空');
                                                }
                                            }
                                        ]
                                    },
                                    events: [
                                        {
                                            source: "os_type",
                                            type: "change",
                                            action: function (os_type) {
                                                var items = this.get_parent().get_child("os_type").items;
                                                for (var i = 0; i < items.length; i++) {
                                                    var item = items[i];
                                                    if (item.value === os_type && item.default_info.user) {
                                                        this._set_value(item.default_info.user);
                                                        break;
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                },
                                {
                                    tag_code: "login_mode",
                                    type: "select",
                                    attrs: {
                                        name: gettext("认证方式"),
                                        items: [
                                            {value: "password", text: gettext("密码")},
                                            {value: "keyfile", text: gettext("密钥")},
                                            {value: "password_vault", text: gettext("密码库(TJJ)")},
                                        ],
                                        default: "password",
                                        validation: [
                                        ],
                                    }
                                },
                                {
                                    tag_code: "login_password",
                                    type: "password",
                                    attrs: {
                                        name: gettext("密码/密钥"),
                                        editable: true,
                                        textareaMode: true,
                                        validation: [
                                        ]
                                    },
                                    events: [
                                        {
                                            source: "login_mode",
                                            type: "change",
                                            action: function (login_mode) {
                                                this._set_value("");
                                                if (login_mode === "password_vault") {
                                                    this.hide();
                                                } else {
                                                    this.show();
                                                }
                                            }
                                        }
                                    ]
                                },
                                {
                                    tag_code: "re_register",
                                    type: "radio",
                                    attrs: {
                                        name: gettext("重新注册Agent-ID"),
                                        items: [
                                            {value: true, name: gettext("是")},
                                            {value: false, name: gettext("否")}
                                        ],
                                        tips: gettext("<p>非必要情况下应尽量避免重新注册Agent-ID, 同一台主机频繁变更可能导致多个平台上下游数据错位, 带来安全隐患</p>"),
                                        default: false,
                                        validation: [
                                            {
                                                type: "required"
                                            }
                                        ]
                                    },
                                },
                            ],
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (value) {
                                    if (value === "install" && this.get_parent().get_child("nodemgr_hosts_param_mode").value === "batch") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            },
                            {
                                source: "nodemgr_node_role",
                                type: "change",
                                action: function (value) {
                                    // 刷新操作系统
                                    let os_type = this.get_child("os_type");
                                    os_type.remote_url = $.context.get("site_url") + 'pipeline/nodemgr_get_os_type/' + value + '/'
                                    os_type.remoteMethod();
                                }
                            },
                            {
                                source: "nodemgr_hosts_param_mode",
                                type: "change",
                                action: function (value) {
                                    if (value === "batch" && this.get_parent().get_child("nodemgr_operation_type").value === "install") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "nodemgr_batch_upgrade",
                        type: "combine",
                        attrs: {
                            name: gettext("主机批量"),
                            hookable: true,
                            children: [
                                {
                                    tag_code: "bk_networkarea_id",
                                    type: "select",
                                    attrs: {
                                        name: gettext("管控区域"),
                                        remote: true,
                                        items: [],
                                        remote_url: $.context.get("site_url") + "pipeline/nodemgr_get_networkarea/",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'upgrade', '管控区域不可为空');
                                                }
                                            }
                                        ]
                                    },
                                },
                                {
                                    tag_code: "inner_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("内网IP"),
                                        placeholder: gettext("一个IP是一台主机, 支持IPv4和IPv6混合填写, 多个用英文逗号 `,` 或换行分隔"),
                                        editable: true,
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'upgrade', '内网IP不可为空');
                                                }
                                            }
                                        ],
                                    }
                                },
                                {
                                    tag_code: "upgrade_version",
                                    type: "select",
                                    attrs: {
                                        name: gettext("目标版本"),
                                        remote: true,
                                        items: [],
                                        remote_url: "",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            resp.data.unshift({"text": gettext("最新稳定版本"), "value": ""});
                                            this._set_value("");

                                            return resp.data;
                                        },
                                        validation: [
                                        ]
                                    },
                                    events: [
                                        {
                                            source: "upgrade_version",
                                            type: "init",
                                            action: function (value) {
                                                this.remote_url = $.context.get("site_url") + 'pipeline/nodemgr_get_release_version/' + this.get_parent().get_parent().get_child("nodemgr_node_role").value + '/'
                                                this.remoteMethod();
                                            }
                                        }
                                    ]
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (value) {
                                    if (value === "upgrade" && this.get_parent().get_child("nodemgr_hosts_param_mode").value === "batch") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            },
                            {
                                source: "nodemgr_node_role",
                                type: "change",
                                action: function (value) {
                                    // 刷新版本
                                    let upgrade_version = this.get_child("upgrade_version");
                                    upgrade_version.remote_url = $.context.get("site_url") + 'pipeline/nodemgr_get_release_version/' + value + '/'
                                    upgrade_version.remoteMethod();
                                }
                            },
                            {
                                source: "nodemgr_hosts_param_mode",
                                type: "change",
                                action: function (value) {
                                    if (value === "batch" && this.get_parent().get_child("nodemgr_operation_type").value === "upgrade") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "nodemgr_batch_restart",
                        type: "combine",
                        attrs: {
                            name: gettext("主机批量"),
                            hookable: true,
                            children: [
                                {
                                    tag_code: "bk_networkarea_id",
                                    type: "select",
                                    attrs: {
                                        name: gettext("管控区域"),
                                        remote: true,
                                        items: [],
                                        remote_url: $.context.get("site_url") + "pipeline/nodemgr_get_networkarea/",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'restart', '管控区域不可为空');
                                                }
                                            }
                                        ]
                                    },
                                },
                                {
                                    tag_code: "inner_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("内网IP"),
                                        placeholder: gettext("一个IP是一台主机, 支持IPv4和IPv6混合填写, 多个用英文逗号 `,` 或换行分隔"),
                                        editable: true,
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'restart', '内网IP不可为空');
                                                }
                                            }
                                        ],
                                    }
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (value) {
                                    if (value === "restart" && this.get_parent().get_child("nodemgr_hosts_param_mode").value === "batch") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            },
                            {
                                source: "nodemgr_hosts_param_mode",
                                type: "change",
                                action: function (value) {
                                    if (value === "batch" && this.get_parent().get_child("nodemgr_operation_type").value === "restart") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "nodemgr_batch_uninstall",
                        type: "combine",
                        attrs: {
                            name: gettext("主机批量"),
                            hookable: true,
                            children: [
                                {
                                    tag_code: "bk_networkarea_id",
                                    type: "select",
                                    attrs: {
                                        name: gettext("管控区域"),
                                        remote: true,
                                        items: [],
                                        remote_url: $.context.get("site_url") + "pipeline/nodemgr_get_networkarea/",
                                        remote_data_init: function (resp) {
                                            if (resp.result === false) {
                                                show_msg(resp.message, "error");
                                            }

                                            return resp.data;
                                        },
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'uninstall', '管控区域不可为空');
                                                }
                                            }
                                        ]
                                    },
                                },
                                {
                                    tag_code: "inner_ip",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("内网IP"),
                                        placeholder: gettext("一个IP是一台主机, 支持IPv4和IPv6混合填写, 多个用英文逗号 `,` 或换行分隔"),
                                        editable: true,
                                        validation: [
                                            {
                                                type: "custom",
                                                args: function (value) {
                                                    return validate_not_empty(this, value, 'uninstall', '内网IP不可为空');
                                                }
                                            }
                                        ],
                                    }
                                }
                            ]
                        },
                        events: [
                            {
                                source: "nodemgr_operation_type",
                                type: "change",
                                action: function (value) {
                                    if (value === "uninstall" && this.get_parent().get_child("nodemgr_hosts_param_mode").value === "batch") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            },
                            {
                                source: "nodemgr_hosts_param_mode",
                                type: "change",
                                action: function (value) {
                                    if (value === "batch" && this.get_parent().get_child("nodemgr_operation_type").value === "uninstall") {
                                        this.show();
                                    } else {
                                        this.hide();
                                    }
                                }
                            }
                        ]
                    }
                ],
            }
        }
    ]
})();
