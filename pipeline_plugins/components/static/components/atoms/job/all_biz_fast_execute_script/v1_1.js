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
    $.atoms.all_biz_job_fast_execute_script = [
        {
            tag_code: "all_biz_cc_id",
            type: "select",
            attrs: {
                name: gettext("业务集ID"),
                hookable: true,
                remote_url: function () {
                    const url = $.context.get('site_url') + 'pipeline/list_business_set/'
                    return url
                },
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
                ],

            },
        },
        {
            tag_code: "job_script_type",
            type: "radio",
            attrs: {
                name: gettext("脚本类型"),
                hookable: true,
                items: [
                    {value: "1", name: "shell"},
                    {value: "2", name: "bat"},
                    {value: "3", name: "perl"},
                    {value: "4", name: "python"},
                    {value: "5", name: "powershell"}
                ],
                default: "1",
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_content",
            type: "code_editor",
            attrs: {
                name: gettext("脚本内容"),
                hookable: true,
                placeholder: gettext("填写执行脚本内容"),
                language: "shell",
                showLanguageSwitch: false,
                height: "400px",
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "job_script_param",
            type: "input",
            attrs: {
                name: gettext("脚本参数"),
                placeholder: gettext("可为空"),
                hookable: true
            },
        },
        {
            tag_code: "job_script_timeout",
            type: "input",
            attrs: {
                name: gettext("超时时间"),
                placeholder: gettext("单位为秒(60 - 86400)，为空时使用 JOB 默认值"),
                hookable: true,
                validation: [
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
                            if (+value < 60 || +value > 86400) {
                                result.result = false;
                                result.error_message = gettext("超时时间必须在 60 - 86400 范围内")
                            }
                            return result
                        }
                    }
                ]
            }
        },
        {
            tag_code: "job_target_account",
            type: "input",
            attrs: {
                name: gettext("目标账户"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "job_target_ip_table",
            type: "datatable",
            attrs: {
                name: gettext("执行目标"),
                pagination: true,
                placeholder: gettext("格式为【云区域ID:IP】或者【IP】格式之一，多个用换行分隔,需要保证所填写的内网IP在配置平台(CMDB)的该业务中是唯一的"),
                hookable: true,
                empty_text: gettext("请添加目标IP信息"),
                table_buttons: [
                    {
                        type: "add_row",
                        text: gettext("添加"),
                        callback: function () {
                            this.add_row()
                        }
                    },
                    {
                        type: "export",
                        text: gettext("导出"),
                        callback: function () {
                            this.export2Excel()
                        }
                    },
                    {
                        type: "import",
                        text: gettext("导入")
                    }
                ],
                columns: [
                    {
                        tag_code: "bk_cloud_id",
                        type: "input",
                        attrs: {
                            name: gettext("云区域ID(默认为0)"),
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "ip",
                        type: "textarea",
                        attrs: {
                            name: "IP",
                            placeholder: gettext("多个IP以,分隔"),
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                ],

                validation: [
                    {
                        type: "required"
                    }
                ],
            },
        },
        {
            tag_code: "job_rolling_execute",
            type: "radio",
            attrs: {
                name: gettext("滚动执行"),
                hookable: true,
                items: [
                    {value: true, name: gettext("是")},
                    {value: false, name: gettext("否")},
                ],
                default: false,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "job_rolling_expression",
            type: "input",
            attrs: {
                name: gettext("滚动策略"),
                placeholder: gettext("详情请查看JOB使用指引"),
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
                            if (!self.get_parent) {
                                return result
                            } else if (self.get_parent().get_child('job_rolling_execute')) {
                                if (self.get_parent().get_child('job_rolling_execute').value && !value.toString()) {
                                    result.result = false;
                                    result.error_message = gettext("滚动执行开启时滚动策略为必填项");
                                }
                            }
                            return result
                        }
                    }
                ]
            },
            events: [
                {
                    source: "job_rolling_execute",
                    type: "change",
                    action: function (value) {
                        var self = this
                        console.log(value);
                        if (value) {
                            self.show()
                        } else {
                            self.hide()
                        }
                    }
                },
                {
                    source: "job_rolling_execute",
                    type: "init",
                    action: function () {
                        const job_rolling_execute = this.get_parent && this.get_parent().get_child('job_rolling_execute')._get_value();
                        if (job_rolling_execute) {
                            this.show()
                        } else {
                            this.hide()
                        }
                    }
                },
            ]
        },
        {
            tag_code: "job_rolling_mode",
            type: "select",
            attrs: {
                name: gettext("滚动机制"),
                hookable: true,
                default: 1,
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
                            } else if (self.get_parent().get_child('job_rolling_execute')) {
                                if (self.get_parent().get_child('job_rolling_execute').value && !value.toString()) {
                                    result.result = false;
                                    result.error_message = gettext("滚动执行开启时滚动机制为必填项");
                                }
                            }
                            return result
                        }
                    }
                ],
                items: [
                    {text: '执行失败则暂停', value: 1},
                    {text: '忽略失败，自动滚动下一批', value: 2},
                    {text: '人工确认', value: 3},
                ]
            },
            events: [
                {
                    source: "job_rolling_execute",
                    type: "change",
                    action: function (value) {
                        var self = this
                        if (value) {
                            self.show()
                        } else {
                            self.hide()
                        }
                    }
                },
                {
                    source: "job_rolling_execute",
                    type: "init",
                    action: function () {
                        const job_rolling_execute = this.get_parent && this.get_parent().get_child('job_rolling_execute')._get_value();
                        if (job_rolling_execute) {
                            this.show()
                        } else {
                            this.hide()
                        }
                    }
                },
            ]
        },
    ]
})();
