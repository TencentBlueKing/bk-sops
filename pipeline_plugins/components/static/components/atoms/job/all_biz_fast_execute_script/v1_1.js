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

    var fixed = /^([1-9]\d*)$/;
    var fixedIn = /^\+([1-9]\d*)$/;
    var fixedMu = /^\*([1-9]\d*)$/;
    var per = /^([1-9]\d?)%$/;
    var all = /^100%$/;

    function validate_job_rolling_expression(exprStr) {
        var batchStack = exprStr.trim().split(' ');
        if (batchStack.length < 1) {
            return '';
        }

        var lastFixedNum = 0;
        var lastPerNum = '';

        var lastBatchPre = batchStack.length > 1 ? '后面' : '';

        var translateSequence = (value) => {
            var batchTotal = value.length;

            var parse = (atoms, batchNum) => {
                var fixedData = atoms.match(fixed);
                if (fixedData) {
                    var fixedNum = parseInt(fixedData[1], 10);

                    lastPerNum = '';
                    lastFixedNum = fixedNum;

                    if (batchNum === batchTotal) {
                        return [`${lastBatchPre}按每${fixedNum}台一批直至结束`];
                    }
                    return [`第${batchNum}批${fixedNum}台`];
                }

                var perData = atoms.match(per);
                if (perData) {
                    var perNum = parseInt(perData[1], 10);

                    lastFixedNum = 0;
                    lastPerNum = perNum;

                    if (batchNum === batchTotal) {
                        return [`${lastBatchPre}按每${perNum}%台一批直至结束`];
                    }
                    return [`第${batchNum}批${perNum}%台`];
                }

                var fixedInData = atoms.match(fixedIn);
                if (fixedInData) {
                    if (batchNum === 1) {
                        throw new Error(`${atoms} 不能出现在开头`);
                    }
                    if (batchNum < batchTotal) {
                        throw new Error(`${atoms} 必须出现在最后一位`);
                    }

                    var step = parseInt(fixedInData[1], 10);

                    var textQueue = [];
                    if (lastPerNum) {
                        textQueue.push(`第${batchNum}批${lastPerNum}%+${step}台`);
                        textQueue.push(`第${batchNum + 1}批${lastPerNum}%+${step + step}台`);
                    } else if (lastFixedNum) {
                        textQueue.push(`第${batchNum}批${step + lastFixedNum}台`);
                        textQueue.push(`第${batchNum + 1}批${step + step + lastFixedNum}台`);
                    }
                    textQueue.push(`...之后“每批增加${step}”台直至结束`);
                    return textQueue;
                }

                var fixedMuData = atoms.match(fixedMu);
                if (fixedMuData) {
                    if (batchNum === 1) {
                        throw new Error(`${atoms} 不能出现在开头`);
                    }
                    if (batchNum < batchTotal) {
                        throw new Error(`${atoms} 必须出现在最后一位`);
                    }

                    var rate = parseInt(fixedMuData[1], 10);
                    var textQueue = [];
                    if (lastPerNum) {
                        textQueue.push(`第${batchNum}批${rate * lastPerNum}%台`);
                        textQueue.push(`第${batchNum + 1}批${rate * rate * lastPerNum}%台`);
                    } else if (lastFixedNum) {
                        textQueue.push(`第${batchNum}批${rate * lastFixedNum}台`);
                        textQueue.push(`第${batchNum + 1}批${rate * rate * lastFixedNum}台`);
                    }
                    textQueue.push(`...之后“每批乘于${rate}”台直至结束`);
                    return textQueue;
                }

                if (all.test(atoms)) {
                    if (batchNum < batchTotal) {
                        throw new Error(`${atoms} 必须出现在最后一位`);
                    }
                    if (batchNum === 1) {
                        return ['全部执行'];
                    }

                    return [`第${batchNum}批执行所有剩余主机`];
                }

                throw new Error(`不支持的配置规则 ${atoms}`);
            };
            var result = [];
            value.forEach((atoms, index) => {
                result.push.apply(result, parse(atoms, index + 1));
            });
            return result.join('，');
        };

        return translateSequence(batchStack);
    }


    $.atoms.all_biz_job_fast_execute_script = [
        {
            tag_code: "all_biz_cc_id",
            type: "select",
            attrs: {
                name: gettext("业务集"),
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
                placeholder: gettext("可为空, 脚本执行时传入的参数，同脚本在终端执行时的传参格式， 如:./test.sh xxxx xxx xxx"),
                hookable: true
            },
        },
        {
            tag_code: "job_script_timeout",
            type: "input",
            attrs: {
                name: gettext("超时时间"),
                placeholder: gettext("单位为秒(1 - 86400)，为空时使用 JOB 默认值"),
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
                            var reg = /^[\d]+$/;
                            if (!reg.test(value)) {
                                result.result = false;
                                result.error_message = gettext("超时时间必须为整数")
                            }
                            if (+value < 1 || +value > 86400) {
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
                name: gettext("执行账号"),
                placeholder: gettext("请输入在蓝鲸作业平台上注册的账户名"),
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
                placeholder: gettext("请输入IP 地址，多IP可用空格、换行分隔非本业务IP请输入云区域:IP，并确保已在作业平台添加白名单"),
                hookable: true,
                empty_text: gettext("请输入IP 地址，多IP可用空格、换行分隔, 非本业务IP请输入云区域:IP，并确保已在作业平台添加白名单"),
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
            tag_code: "job_rolling_config",
            type: "combine",
            attrs: {
                name: "滚动执行配置",
                hookable: true,
                children: [
                    {
                        tag_code: "job_rolling_execute",
                        type: "checkbox",
                        attrs: {
                            name: gettext("滚动执行"),
                            hookable: false,
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
                            hookable: false,
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
                                        if (value) {
                                            try {
                                                validate_job_rolling_expression(value)
                                            } catch (err) {
                                                result.result = false;
                                                result.error_message = err.message;
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
                            hookable: false,
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
            }
        }
    ]
})();
