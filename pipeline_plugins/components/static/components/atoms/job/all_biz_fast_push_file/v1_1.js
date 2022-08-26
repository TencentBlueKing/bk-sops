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
    $.atoms.all_biz_job_fast_push_file = [
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
            tag_code: "job_source_files",
            type: "datatable",
            attrs: {
                name: gettext("源文件"),
                editable: true,
                table_buttons: [
                    {
                        type: "add_row",
                        text: gettext("添加"),
                        callback: function(){
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
                            name: gettext("云区域ID"),
                            placeholder: gettext("默认为0"),
                            width: '90px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "ip",
                        type: "input",
                        attrs: {
                            name: gettext("IP"),
                            width: '150px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "files",
                        type: "textarea",
                        attrs: {
                            name: gettext("文件路径"),
                            placeholder: gettext("多个用换行分隔"),
                            width: '170px',
                            editable: true,
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
                            name: gettext("执行账户"),
                            width: '80px',
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
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "upload_speed_limit",
            type: "input",
            attrs: {
                name: gettext("上传限速"),
                placeholder: gettext("MB/s 若不限速则不填写"),
                hookable: true,
            }
        },
        {
            tag_code: "download_speed_limit",
            type: "input",
            attrs: {
                name: gettext("下载限速"),
                placeholder: gettext("MB/s 若不限速则不填写"),
                hookable: true,
            }
        },
        {
            tag_code: "job_dispatch_attr",
            type: "datatable",
            attrs: {
                name: gettext("分发配置"),
                table_buttons: [
                    {
                        type: "add_row",
                        text: gettext("添加"),
                        callback: function(){
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
                hookable: true,
                columns: [
                    {
                        tag_code: "bk_cloud_id",
                        type: "input",
                        attrs: {
                            name: gettext("云区域ID"),
                            placeholder: gettext("默认为0"),
                            width: '90px',
                            editable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },


                    {
                        tag_code: "job_ip_list",
                        type: "textarea",
                        attrs: {
                            name: gettext("IP"),
                            placeholder: gettext("多IP请使用;分隔"),
                            hookable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "job_target_path",
                        type: "input",
                        attrs: {
                            name: gettext("目标路径"),
                            placeholder: gettext("请输入绝对路径（可用[FILESRCIP]代替源IP）"),
                            hookable: true,
                            validation: [
                                {
                                    type: "required"
                                }
                            ]
                        }
                    },
                    {
                        tag_code: "job_target_account",
                        type: "input",
                        attrs: {
                            name: gettext("执行账户"),
                            placeholder: gettext("请输入在蓝鲸作业平台上注册的账户名"),
                            hookable: true,
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
                ]
            },
            events: [],
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
            tag_code: "job_timeout",
            type: "input",
            attrs: {
                name: gettext("超时时间"),
                placeholder: gettext("单位为秒(60 - 86400)，为空时使用JOB默认值"),
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
            tag_code: "job_rolling_execute",
            type: "radio",
            attrs: {
                name: gettext("滚动执行"),
                hookable: true,
                items: [
                    {value: false, name: gettext("否")},
                    {value: true, name: gettext("是")},
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
