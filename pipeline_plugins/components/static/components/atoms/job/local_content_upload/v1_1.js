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
    $.atoms.job_local_content_upload = [
        {
            tag_code: "local_name",
            type: "input",
            attrs: {
                name: gettext("生成文件名[后缀]"),
                placeholder: gettext("输入生成文件名"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "local_content",
            type: "textarea",
            attrs: {
                name: gettext("文本内容"),
                hookable: true,
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
                name: gettext("目标服务器"),
                placeholder: gettext("请输入IP 地址，多IP可用空格、换行分隔\n 非本业务IP请输入云区域:IP，并确保已在作业平台添加白名单"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "file_account",
            type: "input",
            attrs: {
                name: gettext("执行账号"),
                placeholder: gettext("请输入在蓝鲸作业平台上注册的账户名"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "file_path",
            type: "input",
            attrs: {
                name: gettext("目标路径"),
                placeholder: gettext("输入目标路径"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            },
        },
        {
            tag_code: "job_rolling_execute",
            type: "checkbox",
            attrs: {
                name: gettext("滚动执行"),
                hookable: true,
                items: [
                    {name: gettext(""), value: "open"},
                ],
                validation: []
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
                                if (self.get_parent().get_child('job_rolling_execute').value.includes("open") && !value.toString()) {
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
                        if (value.includes("open")) {
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
                        if (job_rolling_execute.includes("open")) {
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
                                if (self.get_parent().get_child('job_rolling_execute').value.includes("open") && !value.toString()) {
                                    result.result = false;
                                    result.error_message = gettext("滚动执行开启时滚动机制为必填项");
                                }
                            }
                            return result
                        }
                    }
                ],
                items: [
                    {text: '默认（执行失败则暂停）', value: 1},
                    {text: '忽略失败，自动滚动下一批', value: 2},
                    {text: '不自动，每批次都人工确认', value: 3},
                ]
            },
            events: [
                {
                    source: "job_rolling_execute",
                    type: "change",
                    action: function (value) {
                        var self = this
                        if (value.includes("open")) {
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
                        if (job_rolling_execute.includes("open")) {
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
