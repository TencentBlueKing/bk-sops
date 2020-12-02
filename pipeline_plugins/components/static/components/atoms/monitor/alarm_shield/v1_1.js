(function () {
    $.atoms.monitor_alarm_shield = [
        {
            tag_code: "bk_alarm_shield_info",
            type: "combine",
            attrs: {
                name: gettext("屏蔽范围"),
                hookable: true,
                children: [
                    {
                        tag_code: "bk_alarm_shield_scope",
                        type: "select",
                        attrs: {
                            name: gettext("屏蔽范围"),
                            hookable: true,
                            items: [
                                {text: gettext("业务"), value: "business"},
                                {text: "IP", value: "IP"},
                                {text: gettext("结点"), value: "node"},
                            ],
                            validation: [
                                {
                                    type: "required"
                                }
                            ],
                            default: "business"
                        },
                    },
                    {
                        tag_code: "bk_alarm_shield_business",
                        type: "select",
                        attrs: {
                            name: gettext("业务"),
                            hookable: true,
                            remote: true,
                            remote_url: $.context.get('site_url') + 'pipeline/cc_get_business_list/',
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
                        },
                        events: [
                            {
                                source: "bk_alarm_shield_scope",
                                type: "init",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'business') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            },
                            {
                                source: "bk_alarm_shield_scope",
                                type: "change",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'business') {
                                        self.show();
                                    } else {
                                        self.hide();
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "bk_alarm_shield_node",
                        type: "combine",
                        attrs: {
                            name: gettext("结点"),
                            hookable: true,
                            children: [
                                {
                                    tag_code: "bk_set_method",
                                    type: "radio",
                                    attrs: {
                                        name: gettext("大区获取方式"),
                                        hookable: false,
                                        items: [
                                            {value: "select", name: gettext("从CMDB获取")},
                                            {value: "text", name: gettext("手动输入")},
                                        ],
                                        default: "select"
                                    },
                                    events: [
                                        {
                                            source: "bk_set_method",
                                            type: "init",
                                            action: function () {
                                                this.emit_event(this.tagCode, "change", this.value)
                                            }
                                        },
                                    ]
                                },
                                {
                                    tag_code: "bk_set_select",
                                    type: "select",
                                    attrs: {
                                        name: gettext("集群"),
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
                                        }
                                    },
                                    events: [
                                        {
                                            source: "biz_cc_id",
                                            type: "init",
                                            action: function () {
                                                const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                                                this.items = [];
                                                if (cc_id !== '') {
                                                    this.remote_url = $.context.get('site_url') + 'pipeline/cc_get_set_list/' + $.context.getBkBizId() + '/' + '?&all=true';
                                                    this.remoteMethod();
                                                }
                                            }
                                        },
                                        {
                                            source: "biz_cc_id",
                                            type: "change",
                                            action: function (value) {
                                                if ($.context.canSelectBiz()) {
                                                    this._set_value('');
                                                }
                                                this.items = [];
                                                if (value !== '') {
                                                    this.remote_url = $.context.get('site_url') + 'pipeline/cc_get_set_list/' + $.context.getBkBizId() + '/' + '?&all=true';
                                                    this.remoteMethod();
                                                }
                                            }
                                        },
                                        {
                                            // 监听 bk_set_select_method 单选框变化，选择select时显示该树形组件
                                            source: "bk_set_method",
                                            type: "change",
                                            action: function (value) {
                                                let self = this;
                                                if (value === "select") {
                                                    self.show();
                                                } else {
                                                    self.hide();
                                                }
                                            }
                                        },
                                    ]
                                },
                                {
                                    tag_code: "bk_set_text",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("集群"),
                                        hookable: true,
                                        placeholder: gettext("请输入集群名，多个目标集群用英文逗号`,`分隔")
                                    },
                                    events: [
                                        {
                                            source: "bk_set_method",
                                            type: "change",
                                            action: function (value) {
                                                let self = this;
                                                if (value === "text") {
                                                    self.show();
                                                } else {
                                                    self.hide();
                                                }
                                            }
                                        },
                                    ]
                                },
                                {
                                    tag_code: "bk_module_method",
                                    type: "radio",
                                    attrs: {
                                        name: gettext("服务模板获取方式"),
                                        hookable: false,
                                        items: [
                                            {value: "select", name: gettext("从CMDB获取")},
                                            {value: "text", name: gettext("手动输入")},
                                        ],
                                        default: "select"
                                    },
                                    events: [
                                        {
                                            source: "bk_module_method",
                                            type: "init",
                                            action: function () {
                                                this.emit_event(this.tagCode, "change", this.value);
                                            }
                                        },
                                    ]
                                },
                                {
                                    tag_code: "bk_module_select",
                                    type: "select",
                                    attrs: {
                                        name: gettext("服务模板"),
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
                                        }
                                    },
                                    events: [
                                        {
                                            source: "biz_cc_id",
                                            type: "init",
                                            action: function () {
                                                const cc_id = this.get_parent && this.get_parent().get_child('biz_cc_id')._get_value();
                                                this.items = [];
                                                if (cc_id !== '') {
                                                    this.remote_url = $.context.get('site_url') + 'pipeline/cc_get_service_template_list/' + $.context.getBkBizId() + '/' + '?&all=true',
                                                    this.remoteMethod();
                                                }
                                            }
                                        },
                                        {
                                            source: "biz_cc_id",
                                            type: "change",
                                            action: function (value) {
                                                if ($.context.canSelectBiz()) {
                                                    this._set_value('');
                                                }
                                                this.items = [];
                                                if (value !== '') {
                                                    this.remote_url = $.context.get('site_url') + 'pipeline/cc_get_service_template_list/' + $.context.getBkBizId() + '/' + '?&all=true',
                                                    this.remoteMethod();
                                                }
                                            }
                                        },
                                        {
                                            // 监听 bk_module_select_method 单选框变化，选择select时显示该树形组件
                                            source: "bk_module_method",
                                            type: "change",
                                            action: function (value) {
                                                let self = this;
                                                if (value === "select") {
                                                    self.show();
                                                } else {
                                                    self.hide();
                                                }
                                            }
                                        },
                                    ],
                                    methods: {}
                                },
                                {
                                    tag_code: "bk_module_text",
                                    type: "textarea",
                                    attrs: {
                                        name: gettext("模块"),
                                        hookable: true,
                                        placeholder: gettext("请输入模块名，多个目标模块用英文逗号`,`分隔")
                                    },
                                    events: [
                                        {
                                            source: "bk_module_method",
                                            type: "change",
                                            action: function (value) {
                                                let self = this;
                                                if (value === "text") {
                                                    self.show();
                                                } else {
                                                    self.hide();
                                                }
                                            }
                                        },
                                    ]
                                },
                            ]
                        },
                        events: [
                            {
                                source: "bk_alarm_shield_scope",
                                type: "init",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'node') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            },
                            {
                                source: "bk_alarm_shield_scope",
                                type: "change",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'node') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                    {
                        tag_code: "bk_alarm_shield_IP",
                        type: "textarea",
                        attrs: {
                            name: gettext("IP"),
                            hookable: true,
                            placeholder: gettext("请输入主机IP，多个用逗号分隔"),
                            validation: [
                                {
                                    type: "custom",
                                    args: function (value, parent_data) {
                                        var result = {
                                            result: true,
                                            error_message: ""
                                        };
                                        if (
                                            parent_data.hasOwnProperty('bk_alarm_shield_scope') &&
                                            (parent_data.bk_alarm_shield_scope === 'IP') &&
                                            (value.length === 0)
                                        ) {
                                            result.result = false;
                                            result.error_message = gettext("IP不可为空");
                                        }
                                        return result;
                                    }
                                }
                            ]

                        },
                        events: [
                            {
                                source: "bk_alarm_shield_scope",
                                type: "init",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'IP') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            },
                            {
                                source: "bk_alarm_shield_scope",
                                type: "change",
                                action: function (value) {
                                    var self = this;
                                    if (value === 'IP') {
                                        self.show();
                                    } else {
                                        self.hide()
                                    }
                                }
                            }
                        ]
                    },
                ],
            }
        },

        {
            tag_code: "bk_alarm_shield_target",
            type: "select",
            attrs: {
                name: gettext("指标"),
                hookable: true,
                multiple: true,
                items: [
                    {"text": gettext("所有告警"), "value": "all"},
                    {"text": gettext("5分钟平均负载"), "value": "bk_monitor.system.load.load5"},
                    {"text": gettext("CPU总使用率"), "value": "bk_monitor.system.cpu_summary.usage"},
                    {"text": gettext("CPU单核使用率"), "value": "bk_monitor.system.cpu_detail.usage"},
                    {"text": gettext("接收字节流量"), "value": "bk_monitor.system.net.speedRecv"},
                    {"text": gettext("发送字节流量"), "value": "bk_monitor.system.net.speedSent"},
                    {"text": gettext("发送包速率"), "value": "bk_monitor.system.net.speedPacketsSent"},
                    {"text": gettext("接收包速率"), "value": "bk_monitor.system.net.speedPacketsRecv"},
                    {"text": gettext("可用物理内存"), "value": "bk_monitor.system.mem.free"},
                    {"text": gettext("交换分区使用量"), "value": "bk_monitor.system.swap.used"},
                    {"text": gettext("物理内存使用率"), "value": "bk_monitor.system.mem.psc_pct_used"},
                    {"text": gettext("磁盘使用率"), "value": "bk_monitor.system.disk.in_use"},
                    {"text": gettext("读速率"), "value": "bk_monitor.system.io.r_s"},
                    {"text": gettext("写速率"), "value": "bk_monitor.system.io.w_s"},
                    {"text": gettext("磁盘IO使用率"), "value": "bk_monitor.system.io.util"},
                    {"text": gettext("物理内存使用量"), "value": "bk_monitor.system.mem.psc_used"},
                    {"text": gettext("应用内存使用量"), "value": "bk_monitor.system.mem.used"},
                    {"text": gettext("应用内存使用率"), "value": "bk_monitor.system.mem.pct_used"},
                    {"text": gettext("ESTABLISHED连接数"), "value": "bk_monitor.system.netstat.cur_tcp_estab"},
                    {"text": gettext("TIME_WAIT连接数"), "value": "bk_monitor.system.netstat.cur_tcp_timewait"},
                    {"text": gettext("SYN_RECV连接数"), "value": "bk_monitor.system.netstat.cur_tcp_syn_recv"},
                    {"text": gettext("UDP接收包量"), "value": "bk_monitor.system.netstat.cur_udp_indatagrams"},
                    {"text": gettext("UDP发送包量"), "value": "bk_monitor.system.netstat.cur_udp_outdatagrams"},
                    {"text": gettext("CPU使用率"), "value": "bk_monitor.system.proc.cpu_usage_pct"},
                    {"text": gettext("内存使用率"), "value": "bk_monitor.system.proc.mem_usage_pct"},
                    {"text": gettext("进程物理内存使用量"), "value": "bk_monitor.system.proc.mem_res"},
                    {"text": gettext("进程虚拟内存使用量"), "value": "bk_monitor.system.proc.mem_virt"},
                    {"text": gettext("文件句柄数"), "value": "bk_monitor.system.proc.fd_num"},
                    {"text": gettext("系统进程数"), "value": "bk_monitor.system.env.procs"},
                    {"text": gettext("CLOSE_WAIT连接数"), "value": "bk_monitor.system.netstat.cur_tcp_closewait"},
                    {"text": gettext("系统重新启动"), "value": "bk_monitor.os_restart"},
                    {"text": gettext("进程端口"), "value": "bk_monitor.proc_port"},
                    {"text": gettext("Agent心跳丢失"), "value": "bk_monitor.agent-gse"},
                    {"text": gettext("磁盘只读"), "value": "bk_monitor.disk-readonly-gse"},
                    {"text": gettext("磁盘写满"), "value": "bk_monitor.disk-full-gse"},
                    {"text": gettext("Corefile产生"), "value": "bk_monitor.corefile-gse"},
                    {"text": gettext("PING不可达告警"), "value": "bk_monitor.ping-gse"},
                ],
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "bk_alarm_time_type",
            type: "radio",
            attrs: {
                name: gettext("时间选择"),
                hookable: false,
                items: [
                    {name: gettext("手动输入"), value: "0"},
                    {name: gettext("从当前时间开始，仅输入持续时间"), value: "1"},
                    {name: gettext("输入开始时间和持续时间"), value: "2"}
                ],
                default: "0",
                validation: [
                    {
                        type: "required"
                    }
                ],
                events: [
                    {
                        source: "bk_alarm_time_type",
                        type: "init",
                        action: function () {
                            this.emit_event(this.tagCode, "change", this.value)
                        }
                    }
                ]
            },
        },
        {
            tag_code: "bk_alarm_shield_begin_time",
            type: "input",
            attrs: {
                name: gettext("开始时间"),
                hookable: true,
                placeholder: "请输入`yyyy-MM-dd HH:mm:ss`格式，建议引用自定义日期时间类型变量",
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
                            let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                            if ((bk_alarm_time_type.value === '0' || bk_alarm_time_type.value === '2') && this.value.length === 0) {
                                result.result = false;
                                result.error_message = gettext("开始时间不可为空");
                            }
                            return result;
                        }
                    }
                ]
            },
            events: [
                {
                    source: "bk_alarm_time_type",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === '0' || value === '2') {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
                {
                    source: "bk_alarm_shield_begin_time",
                    type: "init",
                    action: function () {
                        let self = this;
                        let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                        if (bk_alarm_time_type.value === '0' || bk_alarm_time_type.value === '2') {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                }
            ]
        },
        {
            tag_code: "bk_alarm_shield_end_time",
            type: "input",
            attrs: {
                name: gettext("结束时间"),
                hookable: true,
                placeholder: "请输入`yyyy-MM-dd HH:mm:ss`格式，建议引用自定义日期时间类型变量",
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
                            let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                            if (bk_alarm_time_type.value === '0' && this.value.length === 0) {
                                result.result = false;
                                result.error_message = gettext("结束时间不可为空");
                            }
                            return result;
                        }
                    }
                ]
            },
            events: [
                {
                    source: "bk_alarm_time_type",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === '0') {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                },
                {
                    source: "bk_alarm_shield_end_time",
                    type: "init",
                    action: function () {
                        let self = this;
                        let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                        if (bk_alarm_time_type.value === '0') {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                }
            ]
        },
        {
            tag_code: "bk_alarm_shield_duration",
            type: "input",
            hide: true,
            attrs: {
                name: gettext("持续时间(分钟)"),
                placeholder: gettext("输入屏蔽的分钟数"),
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
                            let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                            if ((bk_alarm_time_type.value === '1' || bk_alarm_time_type.value === '2') && this.value.length === 0) {
                                result.result = false;
                                result.error_message = gettext("持续时间不可为空");
                            }
                            return result;
                        }
                    }
                ]
            },
            events: [
                {
                    source: "bk_alarm_time_type",
                    type: "change",
                    action: function (value) {
                        let self = this;
                        if (value === '1' || value === '2') {
                            self.show();
                        } else {
                            self._set_value('');
                            self.hide();
                        }
                    }
                },
                {
                    source: "bk_alarm_shield_duration",
                    type: "init",
                    action: function () {
                        let self = this;
                        let bk_alarm_time_type = self.get_parent().get_child('bk_alarm_time_type');
                        if (bk_alarm_time_type.value === '1' || bk_alarm_time_type.value === '2') {
                            self.show();
                        } else {
                            self.hide();
                        }
                    }
                }
            ]
        },
    ]
})();
