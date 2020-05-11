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
    $.atoms.alarm_shield_scope = [
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
                                {text: gettext("模块"), value: "node"},
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
                        type: "tree",
                        attrs: {
                            name: gettext("模块"),
                            hookable: true,
                            remote: true,
                            remote_url: $.context.get('site_url') + "pipeline/cc_search_topo/module/normal/" + $.context.getBkBizId() + "/",
                            remote_data_init: function (resp) {
                                return resp.data;
                            },
                            default_expand_all: false,
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
                                            (parent_data.bk_alarm_shield_scope === 'node') &&
                                            (value.length === 0)
                                        ) {
                                            result.result = false;
                                            result.error_message = gettext("节点不可为空");
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
                        type: "input",
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
            tag_code: "bk_alarm_shield_begin_time",
            type: "input",
            attrs: {
                name: gettext("开始时间"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "bk_alarm_shield_end_time",
            type: "input",
            attrs: {
                name: gettext("结束时间"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();